import csv
import os
import shutil
import paramiko
import logging
from selenium import webdriver
from selenium.webdriver import Keys
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

#-------------------- CONFIGURATION --------------------
INNER_HOST = "172.26.55.149"
INNER_USER = "stsuser"
INNER_PASS = "Vilsts#user"

OUTER_HOST = "10.0.10.206"
OUTER_USER = "vilnewuser"
OUTER_PASS = "V!lNew#useR"

LOG_FILE = "automation_m2m_selfcare_bulk_active_to_test_log.txt"
URL = "http://172.26.55.149:8899/cmp-gateway/deal"

# Read the CAF.csv file
df = pd.read_csv('CAF.csv')
sample_file = "M2M_selfcare_state+deal.csv"
artefacts_folder = "m2m_selfcare_bulk_active_to_teste_artifacts"

# Safe remove of previous file
if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)
    print(f"✅ Removed file: {LOG_FILE}")
else:
    print(f"ℹ️ No previous file found. Creating new one: {LOG_FILE}")

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
else:
    print(f"ℹ️ No previous file/folder found. Creating new one: {artefacts_folder}")

# Create a new dataframe with required columns
new_df = pd.DataFrame()
new_df['msisdn'] = df['msisdn']
new_df['comment'] = 'bulkatos'

# Write to Addon_activation.csv
new_df.to_csv(f'{sample_file}', index=False)

print("✅ Sample file created successfully:", sample_file)

# -------------------------------------------------------
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def sefcare_login(username):

    # ui admin login creds
    USERNAME = f"{username}"
    PASSWORD = "Admin@123"

    # Wait for username input and enter credentials
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    time.sleep(3)

    # Click login
    login_button = driver.find_element(By.ID, "kc-login")
    driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
    time.sleep(1)
    login_button.click()

    # Optional: wait for page elements to load
    time.sleep(3)

def admin_login():

    # ui admin login creds
    USERNAME = "cmpadmin"
    PASSWORD = "Admin@123"

    # Wait for username input and enter credentials
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    time.sleep(3)

    # Click login
    login_button = driver.find_element(By.ID, "kc-login")
    driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
    time.sleep(1)
    login_button.click()

    # Optional: wait for page elements to load
    time.sleep(3)

def get_user_inputs():
    """Display a simple Tkinter window to collect user inputs."""
    user_data = {}

    def submit():
        if not deal_name.get() or not base_Plan_Id.get() or not deal_Circle.get() or not eCode.get() or not life_cycle.get() or not uatdeal.get() or not username.get():
            messagebox.showerror("Error", "Please fill all fields.")
            return

        # ✅ Store values before destroying the window
        user_data["deal_name"] = deal_name.get().strip()
        user_data["base_Plan_Id"] = base_Plan_Id.get().strip()
        user_data["deal_Circle"] = deal_Circle.get().strip()
        user_data["eCode"] = eCode.get().strip()
        user_data["life_cycle"] = life_cycle.get().strip()
        user_data["uatdeal"] = uatdeal.get().strip()
        user_data["username"] = username.get().strip()

        root.destroy()  # now it's safe to close

    root = tk.Tk()
    root.title("Bulk Deal Change Automation Input")
    root.geometry("500x400")
    root.resizable(False, False)

    # Labels and entries
    tk.Label(root, text="Enter Deal Name:").pack(pady=5)
    deal_name = tk.Entry(root, width=40)
    deal_name.pack()

    tk.Label(root, text="Enter Base Plan Name:").pack(pady=5)
    base_Plan_Id = tk.Entry(root, width=40)
    base_Plan_Id.pack()

    tk.Label(root, text="Enter Deal Circle:").pack(pady=5)
    deal_Circle = tk.Entry(root, width=40)
    deal_Circle.pack()

    tk.Label(root, text="Enter Ecode:").pack(pady=5)
    eCode = tk.Entry(root, width=40)
    eCode.pack()

    tk.Label(root, text="Enter Lifecycle(Active, Ready, Test, Safe Custody):").pack(pady=5)
    life_cycle = tk.Entry(root, width=40)
    life_cycle.pack()

    tk.Label(root, text="Enter whether its UAT Deal or not(Yes,No):").pack(pady=5)
    uatdeal = tk.Entry(root, width=40)
    uatdeal.pack()

    # Labels and entries
    tk.Label(root, text="Enter Username of Selfcare:").pack(pady=5)
    username = tk.Entry(root, width=40)
    username.pack()

    tk.Button(root, text="Submit", command=submit, bg="#4CAF50", fg="white", width=15).pack(pady=15)
    root.mainloop()

    # ✅ Return collected values
    return user_data["deal_name"], user_data["base_Plan_Id"], user_data["deal_Circle"], user_data["eCode"], user_data["life_cycle"], user_data["uatdeal"], user_data["username"]

def execute_curl_deal_on_server(dealName, basePlanId, dealCircle, eCode, requestId):
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

        # Build the curl command with mandatory inputs
        curl_command = f"""
        curl -i \
          -H "Accept: application/json" \
          -H "Content-Type: application/json" \
          -X POST \
          --data '{{
            "deal": {{
              "dealName": "{dealName}",
              "dealStartDate": "2023-10-12",
              "basePlanId": "{basePlanId}",
              "accountType": "M2M",
              "dealCircle": "{dealCircle}",
              "dealEndDate": "2027-12-31",
              "contractId": "",
              "eCode": "{eCode}",
              "addOns": [
                {{"addOnId": ""}},
                {{"addOnId": ""}},
                {{"addOnId": ""}}
              ],
              "discounts": [
                {{"discountId": "", "discountValidity": ""}}
              ]
            }},
            "requestId": "{requestId}",
            "requestTimeStamp": "2022-11-29 10:23:46",
            "source": "ViBh",
            "operation": "CREATE_DEAL"
          }}' {URL}
        """

        print(curl_command)
        logging.info(f"Executing curl command on inner server...")
        stdin, stdout, stderr = inner_client.exec_command(curl_command)

        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        logging.info("=== CURL STDOUT START ===")
        logging.info(output)
        logging.info("=== CURL STDOUT END ===")

        if error:
            logging.error(f"CURL STDERR: {error}")

        # --- Parse JSON and extract dealId ---
        import json

        try:
            # Curl with -i includes HTTP headers; the last line is usually the JSON body
            json_body = output.splitlines()[-1]  # get last line, which should be JSON
            response_data = json.loads(json_body)

            # Extract dealId safely
            deal_id = response_data.get("deal", {}).get("dealId")
            if deal_id:
                logging.info(f"Deal created successfully with dealId = {deal_id}")
                print(f"Deal ID: {deal_id}")
            else:
                logging.error("dealId not found in response.")

        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON response: {e}")



    except Exception as e:
        logging.error(f"SSH Execution failed: {e}")

    finally:
        if inner_client:
            inner_client.close()
        outer_client.close()

    return deal_id

if __name__ == "__main__":

    logging.info("=== Automation Script Started ===")

    # Mandatory inputs

    # ✅ Get user input via GUI
    dealName, basePlanId, dealCircle, eCode, lifecycle, uat_deal, username = get_user_inputs()

    import uuid

    # Generate a unique numeric requestId (15-16 digits)
    requestId = str(uuid.uuid4().int)[:11]
    print(f"Generated unique requestId: {requestId}")

    # ui admin login creds
    USERNAME = "cmpadmin"
    PASSWORD = "Admin@123"

    # mandatory params
    if not all([dealName, basePlanId, eCode, dealCircle, requestId]):
        print("Error: All parameters are mandatory.")
        logging.error("All input parameters were not provided. Exiting script.")
        exit(1)

    # Execute curl via SSH
    deal_id = execute_curl_deal_on_server(dealName, basePlanId, dealCircle, eCode, requestId)
    print(f"The dealId from function is: {deal_id}")

    # -------------------- SELENIUM OPTIONS --------------------
    options = Options()
    options.add_argument("--ignore-certificate-errors")  # ignore SSL certificate errors
    options.add_argument("--incognito")  # incognito mode
    # options.add_argument("--headless")                  # uncomment if you want headless

    # Use webdriver-manager to handle driver automatically
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Maximize the window
    driver.maximize_window()

    # Create folder for storing screenshots
    screenshot_dir = "m2m_selfcare_bulk_active_to_teste_artifacts"
    os.makedirs(screenshot_dir, exist_ok=True)

    try:
        # regression url's login & deal page
        WEB_URL = "https://172.26.55.85:8090/"
        DEAL_PAGE = "https://172.26.55.85:8090/#/deal"
        TARGET_PAGE = "https://172.26.55.85:8090/#/orders"

        # Open login page
        driver.get(WEB_URL)

        # admin login
        admin_login()

        # Wait a bit and navigate to target page
        time.sleep(3)
        driver.get(DEAL_PAGE)
        print(f"Opened page: {DEAL_PAGE}")

        # Optional: wait for page elements to load
        time.sleep(3)

        # Apply dealId in the filter input using the exact ID
        deal_id_filter_input = driver.find_element(By.ID, "filed_dealId")
        deal_id_filter_input.clear()
        deal_id_filter_input.send_keys(deal_id)
        time.sleep(3)

        # Click the Search button
        search_button = driver.find_element(By.XPATH,
                                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[1]/div/div[2]/div/div[2]/button[1]")
        search_button.click()

        # Wait for table to refresh
        time.sleep(3)

        # 1️⃣ Vertical scroll screenshot
        element = driver.find_element(By.CSS_SELECTOR, "div.text-truncate")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(2)
        driver.save_screenshot(os.path.join(screenshot_dir, f"{deal_id}_vertical.png"))
        print("Vertical scroll screenshot taken.")

        # 2️⃣ Horizontal scroll screenshot
        table_container = driver.find_element(By.CSS_SELECTOR, "div.table-responsive")
        driver.execute_script("arguments[0].scrollLeft = arguments[0].scrollWidth;", table_container)
        time.sleep(2)
        driver.save_screenshot(os.path.join(screenshot_dir, f"{deal_id}_horizontal.png"))
        print("Horizontal scroll screenshot taken.")
        time.sleep(2)

        # deal approve button
        approve_button = driver.find_element(By.XPATH,
                                             "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div[2]/table/tbody/tr/td[14]/div/div[1]/span")
        approve_button.click()
        time.sleep(2)

        # selecting lifecycle drop down
        driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[3]/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/div[1]").click()
        time.sleep(2)

        # selecting a lifecycle
        if lifecycle == "Active":
            # active button select
            active_button = driver.find_element(By.XPATH,
                                                "/html/body/div/div[2]/div/div[1]/div/div/div/div[3]/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div[1]")
            active_button.click()

        elif lifecycle == "Ready":
            # ready button select
            ready_button = driver.find_element(By.XPATH,
                                               "/html/body/div/div[2]/div/div[1]/div/div/div/div[3]/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div[2]")
            ready_button.click()

        elif lifecycle == "Test":
            # Test button select
            test_button = driver.find_element(By.XPATH,
                                              "/html/body/div/div[2]/div/div[1]/div/div/div/div[3]/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div[3]")
            test_button.click()

        elif lifecycle == "Safe Custody":
            # Safe button select
            safecustody_button = driver.find_element(By.XPATH,
                                                     "/html/body/div/div[2]/div/div[1]/div/div/div/div[3]/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div[4]")
            safecustody_button.click()

        else:
            print("Life cycle is not matching with entered input")

        time.sleep(1)
        # if its a UAT deal
        if uat_deal == "Yes":
            driver.find_element(By.XPATH,
                                "/html/body/div/div[2]/div/div[1]/div/div/div/div[3]/div[1]/div/div/div[2]/div/div/div[2]/span/label/span[2]").click()

            time.sleep(1)
            # deal submit button
            driver.find_element(By.XPATH,
                                "/html/body/div/div[2]/div/div[1]/div/div/div/div[3]/div[1]/div/div/div[3]/div/div/button[2]").click()

        else:
            # deal submit button
            driver.find_element(By.XPATH,
                                "/html/body/div/div[2]/div/div[1]/div/div/div/div[3]/div[1]/div/div/div[3]/div/div/button[2]").click()

        # Optional: wait for page elements to load
        time.sleep(5)
        # final artefact collect eye button after approval
        # 2️⃣ Horizontal scroll screenshot
        table_container = driver.find_element(By.CSS_SELECTOR, "div.table-responsive")
        driver.execute_script("arguments[0].scrollLeft = arguments[0].scrollWidth;", table_container)
        time.sleep(2)
        driver.save_screenshot(os.path.join(screenshot_dir, f"{deal_id}_approved_horizontal.png"))
        print("Approved Horizontal scroll screenshot taken.")
        time.sleep(2)
        driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div[2]/table/tbody/tr/td[15]/img").click()
        # Optional: wait for page elements to load
        time.sleep(5)
        driver.save_screenshot(os.path.join(screenshot_dir, f"{deal_id}_approved_eye_button.png"))
        print("Approved eye button screenshot taken.")

        # break
        driver.quit()
        time.sleep(5)

        print("Please hold still automation is running")

        # -------------------- SELENIUM OPTIONS --------------------
        options = Options()
        options.add_argument("--ignore-certificate-errors")  # ignore SSL certificate errors
        options.add_argument("--incognito")  # incognito mode
        # options.add_argument("--headless")                  # uncomment if you want headless

        # Use webdriver-manager to handle driver automatically
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Maximize the window
        driver.maximize_window()

        # Open login page
        driver.get(WEB_URL)

        # self care login
        sefcare_login(username)
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

        # category state chnage
        driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div[1]/div/div[2]/div/div[2]").click()
        time.sleep(2)

        # action type select
        driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div/div[1]").click()
        time.sleep(2)

        # state chnage
        driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div/div").click()
        time.sleep(2)

        # new status
        driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div[4]/div/div/div[1]").click()
        time.sleep(2)

        # selecting test
        driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div[4]/div[1]/div[2]/div/div[2]").click()
        time.sleep(3)

        # select deal
        driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div[5]/span/div/div/span").click()
        time.sleep(3)

        # sercah fileter for deal
        driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[3]/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div[1]/div/div/span/button/div").click()
        time.sleep(2)

        # insertimng deal id
        search_box = driver.find_element(By.XPATH,
                                         "/html/body/div/div[2]/div/div[1]/div/div/div/div[3]/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div[1]/input")

        time.sleep(3)
        # Clear and type deal name
        search_box.clear()
        time.sleep(1)
        search_box.send_keys(deal_id)

        # Add a space and backspace to trigger change event
        search_box.send_keys(" ")
        time.sleep(1)
        search_box.send_keys(Keys.BACKSPACE)

        # Optional: wait for results to refresh
        time.sleep(3)

        # selecting particular deal
        driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[3]/div[1]/div/div/div[2]/div/div/div[2]/table/tbody/tr/td[8]/input").click()
        time.sleep(3)

        # select reasomn
        driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div[6]/div/div/div[1]").click()
        time.sleep(2)

        # normal suspensuion
        driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div[6]/div/div[2]/div/div[1]").click()
        time.sleep(2)

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
        time.sleep(2)

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
        time.sleep(80)

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

        # 1️⃣ Vertical scroll screenshot
        element = driver.find_element(By.CSS_SELECTOR, "div.text-truncate")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(2)
        driver.save_screenshot(os.path.join(screenshot_dir, f"{batch_id}_vertical.png"))
        print("Vertical scroll screenshot taken.")

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

        #refresh
        driver.refresh()
        time.sleep(3)

        #dashboard
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div[1]/div[1]/div[2]/ul/li[1]/a/span/a").click()
        time.sleep(3)

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

            # update service state filter
            driver.find_element(By.XPATH,
                                "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div/div[7]/div/div[1]/div/div/div[2]/div/div[1]/div[3]/div/div[2]/div/div[116]").click()
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



        logging.info("=== Automation Script Stopped ===")

    finally:
        time.sleep(5)
        driver.quit()