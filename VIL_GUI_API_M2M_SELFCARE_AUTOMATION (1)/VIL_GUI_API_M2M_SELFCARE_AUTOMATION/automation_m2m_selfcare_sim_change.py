import csv
import os
import shutil
import paramiko
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import tkinter as tk
from tkinter import messagebox

# -------------------- CONFIGURATION --------------------
INNER_HOST = "172.26.55.149"
INNER_USER = "stsuser"
INNER_PASS = "Vilsts#user"

OUTER_HOST = "10.0.10.206"
OUTER_USER = "vilnewuser"
OUTER_PASS = "V!lNew#useR"

LOG_FILE = "automation_m2m_selfcare_sim_change_log.txt"
artefacts_folder = "m2m_selfcare_sim_change_artifacts"

# Safe remove of previous log file
if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)
    print(f"✅ Removed file: {LOG_FILE}")
else:
    print(f"ℹ️ No previous log file found. Creating new one: {LOG_FILE}")

# Safe remove of previous folder or file
if os.path.exists(artefacts_folder):
    if os.path.isfile(artefacts_folder):
        os.remove(artefacts_folder)
        print(f"✅ Removed file: {artefacts_folder}")
    else:
        shutil.rmtree(artefacts_folder)
        print(f"✅ Removed folder: {artefacts_folder}")

# -------------------------------------------------------
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_user_inputs():
    """Display a simple Tkinter window to collect user inputs."""
    user_data = {}

    def submit():
        if not CIRCLE_ID.get() or not count.get() or not msisdn_no.get() or not username.get():
            messagebox.showerror("Error", "Please fill all fields.")
            return

        # ✅ Store values before destroying the window
        user_data["CIRCLE_ID"] = CIRCLE_ID.get().strip()
        user_data["count"] = count.get().strip()
        user_data["msisdn_no"] = msisdn_no.get().strip()
        user_data["username"] = username.get().strip()

        root.destroy()  # now it's safe to close

    root = tk.Tk()
    root.title("M2M Selfcare SIM change Automation Input")
    root.geometry("400x300")
    root.resizable(False, False)

    # Labels and entries
    tk.Label(root, text="Enter Circle ID:").pack(pady=5)
    CIRCLE_ID = tk.Entry(root, width=40)
    CIRCLE_ID.pack()

    tk.Label(root, text="Enter Count(only 1 mandatory):").pack(pady=5)
    count = tk.Entry(root, width=40)
    count.pack()

    # Labels and entries
    tk.Label(root, text="Enter MSISDN Number:").pack(pady=5)
    msisdn_no = tk.Entry(root, width=40)
    msisdn_no.pack()

    # Labels and entries
    tk.Label(root, text="Enter Username for Selfcare:").pack(pady=5)
    username = tk.Entry(root, width=40)
    username.pack()

    tk.Button(root, text="Submit", command=submit, bg="#4CAF50", fg="white", width=15).pack(pady=15)
    root.mainloop()

    # ✅ Return collected values
    return user_data["CIRCLE_ID"], user_data["count"], user_data["msisdn_no"], user_data["username"]

# -------------------- TWO-LEVEL SSH FUNCTION --------------------
def execute_mysql_on_server(CIRCLE_ID, count):
    logging.info("Connecting to outer SSH server...")
    outer_client = paramiko.SSHClient()
    outer_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    inner_client = None

    try:
        # Connect to outer (jump) host
        outer_client.connect(OUTER_HOST, username=OUTER_USER, password=OUTER_PASS)
        logging.info("Connected to outer SSH server.")

        # Create a transport channel from outer → inner
        transport = outer_client.get_transport()
        dest_addr = (INNER_HOST, 22)
        local_addr = (OUTER_HOST, 22)
        channel = transport.open_channel("direct-tcpip", dest_addr, local_addr)

        # Connect to inner server through the channel
        logging.info("Connecting to inner SSH server through outer...")
        inner_client = paramiko.SSHClient()
        inner_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        inner_client.connect(INNER_HOST, username=INNER_USER, password=INNER_PASS, sock=channel)
        logging.info("Connected to inner SSH server.")

        mysql_command = (
            f"mysql -h172.26.55.190 -P6139 -ustsuser -pStsuser@123 ARM_MIG -A -e \""
            f"select a.serialnumber,a.status_id,n.ICCID,n.imsi,n.status,n.msisdn,n.EID,n.CIRCLE_ID "
            f"from ARM_MIG.asset_details a "
            f"INNER JOIN NMS_MIG.SIM_CREATED n on a.serialnumber = n.ICCID "
            f"where a.status_id='4' and n.status='9' and n.EID=' ' and n.CIRCLE_ID='{CIRCLE_ID}' "
            f"order by a.id desc limit {count};\""
        )

        print(mysql_command)

        logging.info(f"Executing mysql command on inner server...")

        # Execute first MySQL query
        stdin, stdout, stderr = inner_client.exec_command(mysql_command)
        output1 = stdout.read().decode().strip()
        error1 = stderr.read().decode().strip()
        strip1 = [line for line in output1.splitlines() if line.strip()]  # remove blanks

        # Log outputs
        logging.info("=== MYSQL COMMAND 1 OUTPUT START ===")
        logging.info(output1)
        logging.info("=== MYSQL COMMAND 1 OUTPUT END ===")

        # Log errors if any
        if error1:
            logging.error(f"MYSQL COMMAND 1 STDERR: {error1}")

        logging.info("=== MYSQL OUTPUTS CAPTURED ===")

        # ---- Parse Query 1 (ICCID list) ----
        iccid_list = []
        for line in strip1[1:]:  # Skip header
            cols = line.split('\t')
            if len(cols) >= 3:
                iccid_list.append(cols[2])  # ICCID

        logging.info(f"ICCID Output lines: {strip1}")

        newline = ""

        # ---- Combine and Write to CSV ----
        output_file = "ICCID.csv"
        with open(output_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, lineterminator="\r\n")  # ✅ force single newline only
            writer.writerow(["iccid"])

            for iccid in iccid_list:
                writer.writerow([iccid])

        logging.info(f"✅ Combined CSV generated successfully: {output_file}")

        # file data printing
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                csv_content = f.read().strip()
                logging.info("=== CSV FILE CONTENT START ===")
                logging.info("\n" + csv_content)
                logging.info("=== CSV FILE CONTENT END ===")
        except Exception as e:
            logging.error(f"Error while reading CSV for logging: {e}")

    except Exception as e:
        logging.error(f"SSH Execution failed: {e}")

    finally:
        if inner_client:
            inner_client.close()
        outer_client.close()
        logging.info("=== Automation Script Completed ===")

# -------------------- MAIN --------------------
if __name__ == "__main__":
    logging.info("=== Automation Script Started ===")

    # ✅ Get user input via GUI
    CIRCLE_ID, count, msisdn_no, username = get_user_inputs()

    # Execute mysql via SSH
    execute_mysql_on_server(CIRCLE_ID, count)

    # ui admin login creds
    USERNAME = f"{username}"
    PASSWORD = "Admin@123"

    # -------------------- SELENIUM OPTIONS --------------------
    options = Options()
    options.add_argument("--ignore-certificate-errors")  # ignore SSL certificate errors
    options.add_argument("--incognito")  # incognito mode
    # options.add_argument("--headless")                  # uncomment if you want headless

    # Use webdriver-manager to handle driver automatically
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Maximize the window
    driver.maximize_window()

    try:
        # regression url's login & deal page
        WEB_URL = "https://172.26.55.85:8090/"

        # Open login page
        driver.get(WEB_URL)

        # Wait for username input and enter credentials
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(USERNAME)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)
        time.sleep(3)

        # Click login
        login_button = driver.find_element(By.ID, "kc-login")
        driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
        time.sleep(1)
        login_button.click()

        # Wait a bit and navigate to target page
        time.sleep(3)

        # global serach
        driver.find_element(By.XPATH,
                            "/html/body/div/div[1]/div[4]/div[1]/input").send_keys(msisdn_no)
        time.sleep(5)

        # selecting msisdn number
        driver.find_element(By.XPATH,
                            "/html/body/div/div[1]/div[4]/div[1]/div[3]/div/div[2]/div").click()
        time.sleep(5)

        # scrolling window
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")

        #cliecking sim no
        edit_icon = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//span[@class='labelEditIcon' and @title='click to change SIM']//img[contains(@class, 'editIcon')]"
            ))
        )
        edit_icon.click()
        time.sleep(4)

        # Create folder for storing screenshots
        screenshot_dir = f"{artefacts_folder}"
        os.makedirs(screenshot_dir, exist_ok=True)
        driver.save_screenshot(os.path.join(screenshot_dir, f"{msisdn_no}_before_iccid_change.png"))

        # Path to your CSV file
        csv_file = "ICCID.csv"

        # Empty list to store MSISDNs
        iccid_list = []

        # --- Step 1: Read the CSV file ---
        with open(csv_file, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                iccid = row['iccid'].strip()
                if iccid:  # skip empty lines
                    iccid_list.append(iccid)

        # --- Step 2: Use in loop ---
        print("✅ Extracted ICCID:", iccid_list)

        for number in iccid_list:
            print(f"Processing ICCID: {number}")

            #sending iccid number
            driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[5]/div[1]/div/div/div[2]/div[2]/div/div[1]/span/div/input").send_keys(number)
            time.sleep(3)

            #validating iccid
            driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[5]/div[1]/div/div/div[2]/div[2]/div/div[1]/label/span/a").click()
            time.sleep(5)
            driver.save_screenshot(os.path.join(screenshot_dir, f"{msisdn_no}_iccid_validation.png"))
            time.sleep(5)

            #sending text comments
            driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[5]/div[1]/div/div/div[2]/div[2]/div/div[2]/span/div/textarea").send_keys("sim change")
            time.sleep(2)

            #submit button
            driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[5]/div[1]/div/div/div[3]/div/div/button[2]").click()
            time.sleep(10)

            driver.refresh()
            time.sleep(5)

            # global serach
            driver.find_element(By.XPATH,
                                "/html/body/div/div[1]/div[4]/div[1]/input").send_keys(msisdn_no)
            time.sleep(5)

            # selecting msisdn number
            driver.find_element(By.XPATH,
                                "/html/body/div/div[1]/div[4]/div[1]/div[3]/div/div[2]/div").click()
            time.sleep(5)

            # order page
            driver.find_element(By.XPATH,
                                "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/ul/li[6]/button").click()
            time.sleep(5)

            # order type filter
            driver.find_element(By.XPATH,
                                "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div/div[7]/div/div[1]/div/div/div[2]/div/div[1]/div[3]/div/div/div[1]").click()
            time.sleep(2)

            # change sim filter
            driver.find_element(By.XPATH,
                                "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div/div[7]/div/div[1]/div/div/div[2]/div/div[1]/div[3]/div/div[2]/div/div[21]").click()
            time.sleep(2)

            # Order status
            driver.find_element(By.XPATH,
                                "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div/div[7]/div/div[1]/div/div/div[2]/div/div[1]/div[2]/div/div/div[1]").click()
            time.sleep(2)

            # select completed
            driver.find_element(By.XPATH,
                                "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div/div[7]/div/div[1]/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div/div[1]").click()
            time.sleep(20)

            # serach filter button
            driver.find_element(By.XPATH,
                                "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div/div[7]/div/div[1]/div/div/div[2]/div/div[2]/button[1]").click()
            time.sleep(3)

            # 1️⃣ Vertical scroll screenshot
            element = driver.find_element(By.CSS_SELECTOR, "div.table-responsive")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(2)
            driver.save_screenshot(os.path.join(screenshot_dir, f"{msisdn_no}_vertical.png"))
            print("Vertical scroll screenshot taken.")

            # 2️⃣ Horizontal scroll screenshot
            table_container = driver.find_element(By.CSS_SELECTOR, "div.table-responsive")
            driver.execute_script("arguments[0].scrollLeft = arguments[0].scrollWidth;", table_container)
            time.sleep(2)
            driver.save_screenshot(os.path.join(screenshot_dir, f"{msisdn_no}_horizontal.png"))
            print("Horizontal scroll screenshot taken.")
            time.sleep(2)

            # eye button open
            driver.find_element(By.XPATH,
                                "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div/div[7]/div/div[2]/div[1]/div[2]/table/tbody/tr/td[12]/div/img").click()
            time.sleep(3)

            try:
                wait = WebDriverWait(driver, 15)

                # Wait for the order status element (Completed or Failed)
                status_element = wait.until(
                    EC.visibility_of_element_located((
                        By.XPATH,
                        "//div[contains(@class, 'orderStateCompleted') or contains(@class, 'orderStateFailed')]"
                    ))
                )

                # Get text inside the div
                attr_value = status_element.text.strip()
                print(f"Order status found: {attr_value}")

                # Save screenshot if Completed
                if "Completed" in attr_value:
                    file_path = os.path.join(screenshot_dir, f"{msisdn_no}_order_page.png")
                    driver.save_screenshot(file_path)
                    print(f"✅ Screenshot saved: {file_path}")
                else:
                    print("⚠️ Order not completed — please check manually")

            except Exception as e:
                print(f"❌ Could not locate order status element: {e}")

            # cancel button for exiting that page
            time.sleep(2)
            driver.find_element(By.XPATH,
                                "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div/div[7]/div/div[2]/div[2]/div[1]/div/div/div[3]/div/button").click()
            time.sleep(3)

            # basic details page
            element = driver.find_element(By.CSS_SELECTOR, "div.table-responsive")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'top'});", element)
            time.sleep(2)
            driver.find_element(By.XPATH,
                                "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/ul/li[1]/button").click()
            time.sleep(4)

            # 1️⃣ Vertical scroll screenshot
            # scrolling window
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            driver.save_screenshot(os.path.join(screenshot_dir, f"{msisdn_no}_after_iccid_change.png"))
            print("Vertical scroll screenshot taken.")

            logging.info("=== Automation Script Completed ===")

    finally:
        time.sleep(5)
        driver.quit()