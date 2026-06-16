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
import random

# -------------------- CONFIGURATION --------------------
INNER_HOST = "172.26.55.149"
INNER_USER = "stsuser"
INNER_PASS = "Vilsts#user"

OUTER_HOST = "10.0.10.206"
OUTER_USER = "vilnewuser"
OUTER_PASS = "V!lNew#useR"

LOG_FILE = "automation_m2m_selfcare_enterprise_creation_log.txt"
artefacts_folder = "m2m_selfcare_enterprise_artifacts"
URL = "https://172.26.55.149:8898/workflow-adaptor/enterprise/create"

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

def keycloak_login():

    # ui admin login creds
    USERNAME = "Admin"
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

def get_user_inputs():
    """Display a simple Tkinter window to collect user inputs."""
    user_data = {}

    def submit():
        if not corporate_Name.get() or not cust_Unique_Code.get() or not eCode.get() or not circle_id.get():
            messagebox.showerror("Error", "Please fill all fields.")
            return

        # ✅ Store values before destroying the window
        user_data["corporate_Name"] = corporate_Name.get().strip()
        user_data["cust_Unique_Code"] = cust_Unique_Code.get().strip()
        user_data["eCode"] = eCode.get().strip()
        user_data["circle_id"] = circle_id.get().strip()

        root.destroy()  # now it's safe to close

    root = tk.Tk()
    root.title("M2M Self care Enterprise Automation Input")
    root.geometry("400x300")
    root.resizable(False, False)

    # Labels and entries
    tk.Label(root, text="Enter Corporate Name:").pack(pady=5)
    corporate_Name = tk.Entry(root, width=40)
    corporate_Name.pack()

    tk.Label(root, text="Enter Customer Unique Code Name:").pack(pady=5)
    cust_Unique_Code = tk.Entry(root, width=40)
    cust_Unique_Code.pack()

    tk.Label(root, text="Enter Ecode:").pack(pady=5)
    eCode = tk.Entry(root, width=40)
    eCode.pack()

    tk.Label(root, text="Enter Circle Id:").pack(pady=5)
    circle_id = tk.Entry(root, width=40)
    circle_id.pack()

    tk.Button(root, text="Submit", command=submit, bg="#4CAF50", fg="white", width=15).pack(pady=15)
    root.mainloop()

    # ✅ Return collected values
    return user_data["corporate_Name"], user_data["cust_Unique_Code"], user_data["eCode"], user_data["circle_id"]

# -------------------- TWO-LEVEL SSH FUNCTION --------------------
def execute_curl_on_server(corporateName, custUniqueCode, eCode, requestId):
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
        curl_command = f"""curl -i -H "Accept: application/json" -H "Content-Type:application/json" -X POST --data '{{ 
"account": {{
    "accountType": "1194",
    "annTurnover": "0",
    "area": "IMTQ Manesar",
    "billingAvg": "0",
    "blockNo": "Plot No 12",
    "city": "25345151",
    "corporateName": "{corporateName}",
    "custUniqueCode": "{custUniqueCode}",
    "eCode": "{eCode}",
    "gstCustType": "1000",
    "gstNumber": "33AHIPJ2451M1QB",
    "gstState": "2",
    "gstType": "991",
    "industryType": "25001279",
    "landmark": "BLR31264AI",
    "corporateParentGrp": "Mumbai",
    "noOfEmp": "0",
    "panNumber": "BKJwJ3572D",
    "pincode": 122050,
    "state": "2",
    "rentalSlabApplicable": ""
}},
"lac": {{
    "addressType": "LAC Address Type",
    "area": "Thane city",
    "asContactNumber": "9495543518",
    "asDesignation": "Manager",
    "asEmailID": "newBC020@6dtech.co.in",
    "asName": "TESTINGG",
    "asPrivilege": "All",
    "billCycle": "BC-3",
    "blockNumber": "402",
    "circle": 1,
    "circleAccountManager": "Neethu",
    "city": "16",
    "corporateName": "{corporateName}",
    "costCenter": "MUM31264-MUM",
    "country": "India",
    "creditLimitType": "P",
    "creditSegment": "Nursery",
    "customerClass": "Large Customer",
    "customerSubType": "PPP",
    "customerType": "S",
    "dealers": [{{"dealerId":164874282,"dealerName":"VODAFONE EB SKYLINE"}}],
    "deliveryMode": "Post",
    "documentsSeen": "Y",
    "eCode": "{eCode}",
    "firstName": "BCNEW",
    "gstCustomerType": "1000",
    "gstRegistrationNumber": "33AHIPJ2451M1ZA",
    "gstRegistrationType": "991",
    "hybridCUGService": "",
    "isiSafe": "Y",
    "isSharing": "None",
    "isSummaryBill": "Y",
    "isTaxExemptionApplicable": "N",
    "lacType": "M2M",
    "landmark": "Near Fortune Indra Villaewdei",
    "largeCustomerNameID": "{corporateName}",
    "lastName": "LTD",
    "nameType": "VEL NT",
    "overwriteCorporateCUG": "N",
    "pincode": 122001,
    "serviceCommitments": "free text",
    "sharingPromo": "India",
    "simProductVariant": "UICC",
    "systemType": "CMP"
}},
"operation": "ENTERPRISE_ONBOARDING",
"requestId": "{requestId}",
"requestTimeStamp": "2022-11-06 11:00:39",
"source": "ViBh"
}}' {URL} -k"""

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

    except Exception as e:
        logging.error(f"SSH Execution failed: {e}")

    finally:
        if inner_client:
            inner_client.close()
        outer_client.close()

# -------------------- TWO-LEVEL SSH FUNCTION --------------------
def execute_mysql_on_server(profile_id):
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
            f"mysql -ustsuser -pStsuser@123 -h127.0.0.1 -P6137 CMP_CORE_MIG -A -e \""
            f"SELECT ID FROM M2M_ENTITY_MASTER WHERE PROFILE_ID={profile_id};\""
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

        # Remove empty lines
        strip1 = [line.strip() for line in output1.splitlines() if line.strip()]

        # If there's at least one result (excluding header)
        if len(strip1) > 1:
            entity_id = strip1[1]  # first value after the header
            print("Entity ID:", entity_id)
            logging.info(f"Extracted Entity ID: {entity_id}")
        else:
            entity_id = None
            logging.warning("No ID value returned from MySQL query.")

        return entity_id

    except Exception as e:
        logging.error(f"SSH Execution failed: {e}")

    finally:
        if inner_client:
            inner_client.close()
        outer_client.close()

def generate_user_details():
    username = f"selfcareauto{random.randint(1000,9999)}"
    first_name = f"Selfcare{random.randint(1000,9999)}"
    last_name = f"Auto{random.randint(1000,9999)}"
    email_id = f"auto{random.randint(1000,9999)}@gmail.com"
    return username, first_name, last_name, email_id


# -------------------- MAIN --------------------
if __name__ == "__main__":
    logging.info("=== Automation Script Started ===")

    # Mandatory inputs
    #corporateName = input("Enter corporateName: ").strip()
    #custUniqueCode = input("Enter custUniqueCode: ").strip()
    #eCode = input("Enter eCode: ").strip()

    # ✅ Get user input via GUI
    corporateName, custUniqueCode, eCode, circle_id = get_user_inputs()

    print("Corporate Name:", corporateName)
    print("Customer Unique Name:", custUniqueCode)
    print("Ecode Name:", eCode)

    import uuid

    # Generate a unique numeric requestId (15-16 digits)
    requestId = str(uuid.uuid4().int)[:11]
    print(f"Generated unique requestId: {requestId}")
    #requestId = input("Enter requestId: ").strip()

    # ui admin login creds
    USERNAME = "cmpadmin"
    PASSWORD = "Admin@123"

    #mandatory params
    if not all([corporateName, custUniqueCode, eCode, requestId]):
        print("Error: All parameters are mandatory.")
        logging.error("All input parameters were not provided. Exiting script.")
        exit(1)

    # Execute curl via SSH
    execute_curl_on_server(corporateName, custUniqueCode, eCode, requestId)

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
        #regression url's login & order page
        WEB_URL = "https://172.26.55.85:8090/"
        TARGET_PAGE = "https://172.26.55.85:8090/#/orders"
        KEYCLOAK_URL = "https://172.26.55.63:9093/auth/admin/master/console/#/realms/6D_IN"

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
        driver.get(TARGET_PAGE)
        print(f"Opened page: {TARGET_PAGE}")

        # Optional: wait for page elements to load
        time.sleep(5)

        try:
            # Wait until at least one row is present
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.text-truncate"))
            )

            # Get all divs with the class 'text-truncate'
            all_rows = driver.find_elements(By.CSS_SELECTOR, "div.text-truncate")

            # Check if any of the rows match the eCode
            found = False
            for row in all_rows:
                row_value = row.get_attribute("title").strip()
                if row_value == eCode:
                    found = True
                    break

            if found:
                print(f"✅ eCode {eCode} is present in the orders table.")
            else:
                print(f"❌ eCode {eCode} not found in the orders table.")

        except Exception as e:
            print(f"Error while verifying eCode: {e}")

        # Get the first row's orderId
        first_row_div = driver.find_element(By.CSS_SELECTOR, "div.text-truncate")
        # Get the title/text of the first row
        orderid = first_row_div.get_attribute("title")  # or use .text
        print(f"Latest orderId found: {orderid}")

        # Apply orderId in the filter input using the exact ID
        order_id_filter_input = driver.find_element(By.ID, "filed_orderId")
        order_id_filter_input.clear()
        order_id_filter_input.send_keys(orderid)
        time.sleep(5)

        # Click the Search button
        search_button = driver.find_element(By.XPATH,
                                            "/html/body/div/div[2]/div/div[1]/div/div/div[1]/div/div/div/div[2]/div/div[2]/button[1]")
        search_button.click()

        # Wait for table to refresh
        time.sleep(3)

        # wait until the profile column is present
        wait = WebDriverWait(driver, 10)

        profileid_column_element = wait.until(
            EC.presence_of_element_located((By.XPATH, "//tr[contains(@class,'row_entire_selection')]/td[3]/div"))
        )

        # extract text
        profile_id = profileid_column_element.get_attribute("title").strip()

        print("Profile ID Value:", profile_id)

        # Create folder for storing screenshots
        screenshot_dir = "m2m_selfcare_enterprise_artifacts"
        os.makedirs(screenshot_dir, exist_ok=True)

        # 1️⃣ Vertical scroll screenshot
        element = driver.find_element(By.CSS_SELECTOR, "div.text-truncate")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(2)
        driver.save_screenshot(os.path.join(screenshot_dir, f"{orderid}_m2m_selfcare_vertical.png"))
        print("Vertical scroll screenshot taken.")

        # 2️⃣ Horizontal scroll screenshot
        table_container = driver.find_element(By.CSS_SELECTOR, "div.table-responsive")
        driver.execute_script("arguments[0].scrollLeft = arguments[0].scrollWidth;", table_container)
        time.sleep(2)
        driver.save_screenshot(os.path.join(screenshot_dir, f"{orderid}_m2m_selfcare_horizontal.png"))
        print("Horizontal scroll screenshot taken.")
        time.sleep(1)

        # Execute mysql via SSH
        entity_id = execute_mysql_on_server(profile_id)

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
        driver.get(KEYCLOAK_URL)

        # keycloak login
        keycloak_login()

        time.sleep(3)

        #selecting users
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div[3]/ul/li[2]/a").click()
        time.sleep(3)

        #creating add user
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/table/thead/tr[1]/th/div/div[2]/a").click()
        time.sleep(3)

        #generating unique names
        username, first_name, last_name, email_id = generate_user_details()

        print(f"Username: {username}")
        print(f"First: {first_name}")
        print(f"Last: {last_name}")
        print(f"Email ID: {email_id}")

        #username input
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/fieldset/div[3]/div/input").send_keys(username)
        time.sleep(2)

        # email id input
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/fieldset/div[4]/div/input").send_keys(email_id)
        time.sleep(2)

        # first name input
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/fieldset/div[5]/div/input").send_keys(first_name)
        time.sleep(2)

        # lastname input
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/fieldset/div[6]/div/input").send_keys(last_name)
        time.sleep(2)

        #user disabling
        #driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/fieldset/div[7]/div/span/div/label/span[1]/span[1]").click()
        #time.sleep(2)

        #saving the deatils
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/div/div[1]/button[1]").click()
        time.sleep(3)

        driver.save_screenshot(os.path.join(screenshot_dir, f"{orderid}_m2m_selfcare_details.png"))
        time.sleep(1)

        #attributes page
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div/ul/li[2]/a").click()
        time.sleep(3)

        #1st key pair
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/table/tbody/tr/td[1]/input").send_keys("circle")
        time.sleep(1)

        #1st value pair
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/table/tbody/tr/td[2]/input").send_keys(circle_id)
        time.sleep(1)

        #add button
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/table/tbody/tr/td[3]").click()
        time.sleep(2)

        #2nd key pair
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/table/tbody/tr[2]/td[1]/input").send_keys("entityId")
        time.sleep(1)

        #2nd value pair
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/table/tbody/tr[2]/td[2]/input").send_keys("100")
        time.sleep(1)

        #add button
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/table/tbody/tr[2]/td[3]").click()
        time.sleep(2)

        #3rd key pair
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/table/tbody/tr[3]/td[1]/input").send_keys("entityType")
        time.sleep(1)

        #3rd value pair
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/table/tbody/tr[3]/td[2]/input").send_keys("2")
        time.sleep(1)

        #add button
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/table/tbody/tr[3]/td[3]").click()
        time.sleep(2)

        #4th key pair
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/table/tbody/tr[4]/td[1]/input").send_keys("channel")
        time.sleep(1)

        #4th value pair
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/table/tbody/tr[4]/td[2]/input").send_keys("ums")
        time.sleep(1)

        #add button
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/table/tbody/tr[4]/td[3]").click()
        time.sleep(2)

        #5th key pair
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/table/tbody/tr[5]/td[1]/input").send_keys("entity")
        time.sleep(1)

        #5th value pair
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/table/tbody/tr[5]/td[2]/input").send_keys(entity_id)
        time.sleep(1)

        #add button
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/table/tbody/tr[5]/td[3]").click()
        time.sleep(2)

        #save attributes page
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/div/div/button[1]").click()
        time.sleep(3)

        driver.save_screenshot(os.path.join(screenshot_dir, f"{orderid}_m2m_selfcare_attributes.png"))
        time.sleep(1)

        #credentials page
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div/ul/li[3]/a").click()
        time.sleep(3)

        #password
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/fieldset[3]/div[1]/div/div/input").send_keys("Admin@123")
        time.sleep(1)

        #password confirmation
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/fieldset[3]/div[2]/div/div/input").send_keys("Admin@123")
        time.sleep(1)

        #disabling temproary
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/fieldset[3]/div[3]/div/span/div/label/span[1]/span[1]").click()
        time.sleep(2)

        #set password
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/fieldset[3]/div[4]/div/button").click()
        time.sleep(3)

        #confirming the password
        wait = WebDriverWait(driver, 10)

        set_password_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(text())='Set password']"))
        )

        set_password_btn.click()
        time.sleep(3)

        #saving the creds
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/fieldset[2]/table/tbody/tr/td[6]/div").click()
        time.sleep(3)

        driver.save_screenshot(os.path.join(screenshot_dir, f"{orderid}_m2m_selfcare_credentials_saved.png"))
        time.sleep(1)

        #role mappings
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div/ul/li[4]/a").click()
        time.sleep(3)

        #deafult roles move ment
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/div[1]/div/div/div[1]/select/option[8]").click()
        time.sleep(2)

        #add selected role
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/div[1]/div/div/div[1]/button").click()
        time.sleep(2)

        #selexcting client roles
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/div[2]/div[1]/div/a/span[1]").click()
        time.sleep(3)

        #selecting VIL CMP
        driver.find_element(By.XPATH, "/html/body/div[5]/ul/li[20]/div").click()
        time.sleep(3)

        #selecting eneterprise
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/div[2]/div[2]/div/div[1]/select/option[30]").click()
        time.sleep(2)

        #add button
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/form/div[2]/div[2]/div/div[1]/button").click()
        time.sleep(2)

        driver.save_screenshot(os.path.join(screenshot_dir, f"{orderid}_m2m_selfcare_role_mappings.png"))
        time.sleep(1)

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

        # selfcare login
        sefcare_login(username)
        time.sleep(3)

        driver.save_screenshot(os.path.join(screenshot_dir, f"{orderid}_m2m_selfcare_dashboard_page.png"))

    finally:
        logging.info("=== Automation Script Completed ===")
        time.sleep(5)
        driver.quit()