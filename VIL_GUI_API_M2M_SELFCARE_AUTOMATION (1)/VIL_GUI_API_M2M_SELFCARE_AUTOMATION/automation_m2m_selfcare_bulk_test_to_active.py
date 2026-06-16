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

# Read the CAF.csv file
df = pd.read_csv('CAF.csv')
sample_file = "M2M_selfcare_state+deal.csv"
artefacts_folder = "m2m_selfcare_bulk_test_to_active_artifacts"

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

def get_user_inputs():
    """Display a simple Tkinter window to collect user inputs."""
    user_data = {}

    def submit():
        if not username.get() or not deal_id.get():
            messagebox.showerror("Error", "Please fill all fields.")
            return

        # ✅ Store values before destroying the window
        user_data["username"] = username.get().strip()
        user_data["deal_id"] = deal_id.get().strip()

        root.destroy()  # now it's safe to close

    root = tk.Tk()
    root.title("M2M Selfcare Deactivate to Active Automation Input")
    root.geometry("400x300")
    root.resizable(False, False)

    # Labels and entries
    tk.Label(root, text="Enter Username for Selfcare:").pack(pady=5)
    username = tk.Entry(root, width=40)
    username.pack()

    # Labels and entries
    tk.Label(root, text="Enter Active Deal ID:").pack(pady=5)
    deal_id = tk.Entry(root, width=40)
    deal_id.pack()

    tk.Button(root, text="Submit", command=submit, bg="#4CAF50", fg="white", width=15).pack(pady=15)
    root.mainloop()

    # ✅ Return collected values
    return user_data["username"], user_data["deal_id"]

if __name__ == "__main__":

    # ✅ Get user input via GUI
    username, deal_id = get_user_inputs()

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

    # Create folder for storing screenshots
    screenshot_dir = f"{artefacts_folder}"
    os.makedirs(screenshot_dir, exist_ok=True)

    try:
        # regression url's login & deal page
        WEB_URL = "https://172.26.55.85:8090/"
        DEAL_PAGE = "https://172.26.55.85:8090/#/deal"
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

        #loading page
        time.sleep(5)

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

        # selecting activate
        driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div[4]/div[1]/div[2]/div/div[1]").click()
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