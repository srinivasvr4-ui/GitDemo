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
import pandas as pd

# -------------------- CONFIGURATION --------------------
INNER_HOST = "172.26.55.149"
INNER_USER = "stsuser"
INNER_PASS = "Vilsts#user"

OUTER_HOST = "10.0.10.206"
OUTER_USER = "vilnewuser"
OUTER_PASS = "V!lNew#useR"

LOG_FILE = "automation_m2m_selfcare_bulk_sim_change_log.txt"
artefacts_folder = "m2m_selfcare_bulk_sim_change_artifacts"

# Read the CAF.csv file
df = pd.read_csv('CAF.csv')
sample_file = "m2m_selfcare_change_sim.csv"

# Safe remove of previous log file
if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)
    print(f"✅ Removed file: {LOG_FILE}")
else:
    print(f"ℹ️ No previous log file found. Creating new one: {LOG_FILE}")

# Safe remove of previous file
if os.path.exists(sample_file):
    os.remove(sample_file)
    print(f"✅ Removed file: {sample_file}")
else:
    print(f"ℹ️ No previous file found. Creating new one: {sample_file}")

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
        if not CIRCLE_ID.get() or not username.get():
            messagebox.showerror("Error", "Please fill all fields.")
            return

        # ✅ Store values before destroying the window
        user_data["CIRCLE_ID"] = CIRCLE_ID.get().strip()
        user_data["username"] = username.get().strip()

        root.destroy()  # now it's safe to close

    root = tk.Tk()
    root.title("M2M Selfcare Bulk Caf SIM change Automation Input")
    root.geometry("400x300")
    root.resizable(False, False)

    # Labels and entries
    tk.Label(root, text="Enter Circle ID:").pack(pady=5)
    CIRCLE_ID = tk.Entry(root, width=40)
    CIRCLE_ID.pack()

    # Labels and entries
    tk.Label(root, text="Enter Username for Selfcare:").pack(pady=5)
    username = tk.Entry(root, width=40)
    username.pack()

    tk.Button(root, text="Submit", command=submit, bg="#4CAF50", fg="white", width=15).pack(pady=15)
    root.mainloop()

    # ✅ Return collected values
    return user_data["CIRCLE_ID"], user_data["username"]

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

if __name__ == "__main__":
    logging.info("=== Automation Script Started ===")

    # ---- STEP 1: Read CSV to get how many entries it has ----
    csv_file_path = "CAF.csv"
    with open(csv_file_path, "r") as file:
        reader = csv.reader(file)
        next(reader)  # skip header if present
        csv_entries = list(reader)

    count = len(csv_entries)
    print(f"Number of entries in CSV: {count}")

    # ✅ Get user input via GUI
    CIRCLE_ID, username = get_user_inputs()

    # Execute mysql via SSH
    execute_mysql_on_server(CIRCLE_ID, count)

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

    combined_rows = []

    # Take equal pairs (stop at shortest list)
    for msisdn, iccid in zip(df['msisdn'], iccid_list):
        combined_rows.append({
            'msisdn': msisdn,
            'iccId': iccid,
            'reason': 'abcde'
        })

    new_df = pd.DataFrame(combined_rows)
    new_df.to_csv(sample_file, index=False)
    print(f"✅ Final sample file created successfully: {sample_file}")

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
        TARGET_PAGE = "https://172.26.55.85:8090/#/orders"

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

        # bulk menu
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div[1]/div[1]/div[2]/ul/li[8]/a/span/a").click()
        time.sleep(2)

        # bulk transactions select
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div[1]/div[1]/div[2]/ul/li[8]/ul/li[2]/div/a").click()
        time.sleep(4)

        # file upload button
        driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div[1]/div[1]/div[2]/button").click()
        time.sleep(3)

        # category
        driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div[1]/div/div/div[1]").click()
        time.sleep(2)

        # category others
        driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div[3]").click()
        time.sleep(2)

        # action type select
        driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div/div[1]").click()
        time.sleep(2)

        # change sim
        driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div/div[4]").click()
        time.sleep(2)

        #inserting ecode
        #driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div[3]/div/div/div[1]/div[2]/div/input").send_keys(eCode)
        #time.sleep(5)

        #particular ecode
        #driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div[3]/div/div[2]/div/div").click()
        #time.sleep(2)

        # uploading file

        file_input = driver.find_element(By.XPATH, "//input[@type='file']")
        file_input.send_keys(fr"C:\Users\naveen.basavaraj\PycharmProjects\VIL_GUI_API_M2M_SELFCARE_AUTOMATION\{sample_file}")
        time.sleep(3)

        # next page
        driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[2]/div/button[2]").click()
        time.sleep(3)

        # submit button
        driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[2]/div/button[3]").click()
        #time.sleep(2)

        # yes after submit button
        #driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[5]/div/div/div/div[3]/div/button[2]").click()
        time.sleep(10)

        wait = WebDriverWait(driver, 30)

        # --- STEP 1: Wait for table and extract FIRST Batch ID ---
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        # Wait until at least 1 row is visible
        first_row = wait.until(EC.visibility_of_element_located((
            By.XPATH, "(//tbody//tr[1]/td[1]//div[@id='PopoverFocus'])[1]"
        )))

        # Re-fetch directly to avoid stale element
        batch_id = driver.find_element(
            By.XPATH, "(//tbody//tr[1]/td[1]//div[@id='PopoverFocus'])[1]"
        ).get_attribute("title").strip()

        print(f"✅ Extracted Batch ID: {batch_id}")

        # --- STEP 3: Wait for the input box ---
        batch_input = wait.until(EC.presence_of_element_located((By.ID, "filed_batchId")))

        # --- STEP 4: Set value directly using JavaScript ---
        driver.execute_script("""
                            const input = arguments[0];
                            const value = arguments[1];

                            // Get the native setter from the element's prototype
                            const nativeSetter = Object.getOwnPropertyDescriptor(
                                window.HTMLInputElement.prototype, 'value'
                            ).set;

                            // Set the value using the native setter (so React notices)
                            nativeSetter.call(input, value);

                            // Trigger the proper events
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            input.dispatchEvent(new Event('change', { bubbles: true }));
                        """, batch_input, str(batch_id))

        time.sleep(3)  # small buffer for UI update
        time.sleep(100)

        # search button
        driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[1]/div/div[2]/div/div[2]/button[1]").click()
        time.sleep(3)

        # locate the status cell (5th column in the row)
        status_element = driver.find_element(
            By.XPATH,
            "(//tr[contains(@class, 'row_entire_selection')])[1]/td[5]/div"
        )

        status_text = status_element.text.strip()

        # check if status == "Success"
        if status_text.lower() == "success":
            print("✅ Operation succeeded.")
        else:
            print(f"❌ Operation failed. Status was: {status_text}")

        # Create folder for storing screenshots
        screenshot_dir = f"{artefacts_folder}"
        os.makedirs(screenshot_dir, exist_ok=True)

        # 1️⃣ Vertical scroll screenshot
        element = driver.find_element(By.CSS_SELECTOR, "div.text-truncate")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(2)
        driver.save_screenshot(os.path.join(screenshot_dir, f"{batch_id}_vertical.png"))
        print("Vertical scroll screenshot taken.")

        # refresh freshly
        driver.refresh()
        time.sleep(5)

        # dashboard
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div[1]/div[1]/div[2]/ul/li[1]/a/span/a").click()
        time.sleep(3)

        # Path to your CSV file
        csv_file = f"{sample_file}"

        # Empty list to store MSISDNs
        msisdn_list = []

        # --- Step 1: Read the CSV file ---
        with open(csv_file, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                msisdn = row['msisdn'].strip()
                if msisdn:  # skip empty lines
                    msisdn_list.append(msisdn)

            # --- Step 2: Use in loop ---
            print("✅ Extracted MSISDNs:", msisdn_list)

            for number in msisdn_list:
                print(f"Processing MSISDN: {number}")
                # your logic here, e.g. driver.find_element(...) or API call

                # global serach
                driver.find_element(By.XPATH,
                                    "/html/body/div/div[1]/div[4]/div[1]/input").send_keys(number)
                time.sleep(5)

                # global serach snap
                driver.save_screenshot(os.path.join(screenshot_dir, f"{number}_global_search.png"))

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
                time.sleep(2)

                # serach filter button
                driver.find_element(By.XPATH,
                                    "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div/div[7]/div/div[1]/div/div/div[2]/div/div[2]/button[1]").click()
                time.sleep(3)

                # 1️⃣ Vertical scroll screenshot
                element = driver.find_element(By.CSS_SELECTOR, "div.table-responsive")
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                time.sleep(2)
                driver.save_screenshot(os.path.join(screenshot_dir, f"{number}_vertical.png"))
                print("Vertical scroll screenshot taken.")

                # 2️⃣ Horizontal scroll screenshot
                table_container = driver.find_element(By.CSS_SELECTOR, "div.table-responsive")
                driver.execute_script("arguments[0].scrollLeft = arguments[0].scrollWidth;", table_container)
                time.sleep(2)
                driver.save_screenshot(os.path.join(screenshot_dir, f"{number}_horizontal.png"))
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
                        file_path = os.path.join(screenshot_dir, f"{number}_order_page.png")
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

                # scrolling window
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
                driver.save_screenshot(os.path.join(screenshot_dir, f"{number}_final_vertical.png"))
                print("Vertical scroll screenshot taken.")

                driver.refresh()
                time.sleep(4)

        logging.info("=== Automation Script Completed ===")

    finally:
        time.sleep(5)
        driver.quit()