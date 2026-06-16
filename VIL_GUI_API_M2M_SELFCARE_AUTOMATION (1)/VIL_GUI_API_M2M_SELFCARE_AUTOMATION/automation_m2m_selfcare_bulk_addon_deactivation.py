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
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json

sample_file = "M2M_selfcare_addon_deactivation.csv"
artefacts_folder = "m2m_selfcare_bulk_addon_deactivation_artifacts"

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

def get_user_inputs():
    """Display a simple Tkinter window to collect user inputs."""
    user_data = {}

    def submit():
        if not username.get():
            messagebox.showerror("Error", "Please fill all fields.")
            return

        # ✅ Store values before destroying the window
        user_data["username"] = username.get().strip()

        root.destroy()  # now it's safe to close

    root = tk.Tk()
    root.title("M2M SELFCARE BULK Addon Automation Input")
    root.geometry("400x300")
    root.resizable(False, False)

    # Labels and entries
    tk.Label(root, text="Enter username for selfcare:").pack(pady=5)
    username = tk.Entry(root, width=40)
    username.pack()

    tk.Button(root, text="Submit", command=submit, bg="#4CAF50", fg="white", width=15).pack(pady=15)
    root.mainloop()

    # ✅ Return collected values
    return user_data["username"]

if __name__ == "__main__":

    # ✅ Get user input via GUI
    username = get_user_inputs()

    # ui admin login creds
    USERNAME = f"{username}"
    PASSWORD = "Admin@123"

    # --- Enable Chrome Performance Logs ---
    caps = DesiredCapabilities.CHROME.copy()
    caps["goog:loggingPrefs"] = {"performance": "ALL"}

    # -------------------- SELENIUM OPTIONS --------------------
    options = Options()
    options.add_argument("--ignore-certificate-errors")  # ignore SSL certificate errors
    options.add_argument("--incognito")  # incognito mode
    # options.add_argument("--headless")                  # uncomment if you want headless

    # ✅ Merge capabilities with options (Selenium 4+ syntax)
    for key, value in caps.items():
        options.set_capability(key, value)

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

        # Optional: wait for page elements to load
        time.sleep(3)

        # Path to your CSV file
        csv_file = "M2M_selfcare_addon_activation.csv"

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

            # selecting msisdn number
            driver.find_element(By.XPATH,
                                "/html/body/div/div[1]/div[4]/div[1]/div[3]/div/div[2]/div").click()
            time.sleep(5)

            # ✅ Enable network logging (only once)
            driver.execute_cdp_cmd("Network.enable", {})

            # addon page
            driver.find_element(By.XPATH,
                                "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/ul/li[2]/button").click()
            time.sleep(4)

            # ✅ Get Chrome performance logs
            logs = driver.get_log("performance")

            # --- STEP: Search for fetchSubscription API ---
            for entry in logs:
                try:
                    log = json.loads(entry["message"])["message"]
                    if (
                            log["method"] == "Network.responseReceived"
                            and "response" in log["params"]
                            and "fetchSubscription" in log["params"]["response"]["url"]
                    ):
                        request_id = log["params"]["requestId"]
                        print(f"📡 Found fetchSubscription requestId: {request_id}")

                        # ✅ Get actual response body
                        response = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})

                        # ✅ Parse and save JSON
                        data = json.loads(response["body"])
                        output_file = f"subscription_{number}.json"
                        with open(output_file, "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=4)
                        print(f"✅ Saved JSON response for {number} → {output_file}")

                        # ---------------- PLAN FILTERING LOGIC ----------------
                        plan_to_find = "CMP_Data Add On_50MB"  # hardcoded plan name
                        first_match = None

                        # Check if 'data' exists and is a list
                        if isinstance(data.get("data"), list):
                            for record in data["data"]:
                                if record.get("planName") == plan_to_find:
                                    first_match = record
                                    break  # stop at first match

                        if first_match:
                            print(f"✅ Found first occurrence of plan '{plan_to_find}'")
                            print(f"Subscription ID: {first_match['subscriptionId']}")
                            print(f"Service ID: {first_match['serviceId']}")
                            print(f"Activation Date: {first_match['activationDate']}")

                            # --- Save result into CSV for deactivation ---
                            result_row = {
                                "msisdn": number,
                                "subscriptionId": first_match["subscriptionId"],
                                "comment": ""
                            }

                            # Append result into Addon_deactivation.csv
                            file_exists = os.path.isfile(sample_file)
                            with open(sample_file, mode="a", newline="", encoding="utf-8") as csvfile:
                                fieldnames = ["msisdn", "subscriptionId", "comment"]
                                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                                if not file_exists:
                                    writer.writeheader()
                                writer.writerow(result_row)

                            print(f"✅ Written {number} → {first_match['subscriptionId']} to {sample_file}")

                        else:
                            print(f"⚠️ No plan found matching '{plan_to_find}' for {number}")

                        break
                except Exception as e:
                    continue
            driver.refresh()
            time.sleep(3)

        #bulk menu
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div[1]/div[1]/div[2]/ul/li[8]/a/span/a").click()
        time.sleep(2)

        #bulk transactions select
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div[1]/div[1]/div[2]/ul/li[8]/ul/li[2]/div/a").click()
        time.sleep(4)

        #file upload
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div[1]/div[1]/div[2]/button").click()
        time.sleep(3)

        #category
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div[1]/div/div/div[1]").click()
        time.sleep(2)

        #category commercial plan change
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div[1]/div/div[2]/div/div[1]").click()
        time.sleep(2)

        #action type select
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div/div[1]").click()
        time.sleep(2)

        #addon on deactivation select
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div/div[5]").click()
        time.sleep(2)

        #addon type
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div[3]/div[1]/div/div[1]").click()
        time.sleep(2)

        #open market
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div[3]/div[1]/div[2]/div/div[1]").click()
        time.sleep(2)

        #inserting addon
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div[4]/div/div/div[1]/div[2]/div/input").send_keys("CMP_Data Add On_50MB")
        time.sleep(10)

        #selecting addon
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div[4]/div/div[2]/div/div[1]").click()
        time.sleep(3)

        #uploading file

        file_input = driver.find_element(By.XPATH, "//input[@type='file']")
        file_input.send_keys(fr"C:\Users\naveen.basavaraj\PycharmProjects\VIL_GUI_API_M2M_SELFCARE_AUTOMATION\{sample_file}")
        time.sleep(3)

        #next page
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[2]/div/button[2]").click()
        time.sleep(3)

        #submit button
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[2]/div/button[3]").click()
        time.sleep(2)

        wait = WebDriverWait(driver, 30)

        # --- STEP 1: Wait for table and extract FIRST Batch ID ---
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        # Wait until at least 1 row is visible
        first_row = wait.until(EC.visibility_of_element_located((By.XPATH, "(//tbody//tr[1]/td[1]//div[@id='PopoverFocus'])[1]")))

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

        # Create folder for storing screenshots
        screenshot_dir = f"{artefacts_folder}"
        os.makedirs(screenshot_dir, exist_ok=True)

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

        # refresh
        driver.refresh()
        time.sleep(3)

        # dashboard
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

            # cancel subscription filter
            driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div/div[7]/div/div[1]/div/div/div[2]/div/div[1]/div[3]/div/div[2]/div/div[26]").click()
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

            # addon page
            element = driver.find_element(By.CSS_SELECTOR, "div.table-responsive")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'top'});", element)
            time.sleep(2)
            # addon page
            driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/ul/li[2]/button").click()
            time.sleep(3)

            # 1️⃣ Vertical scroll screenshot
            element = driver.find_element(By.CSS_SELECTOR, "div.table-responsive")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(2)
            driver.save_screenshot(os.path.join(screenshot_dir, f"{number}_addon_page_vertical.png"))
            print("Vertical scroll screenshot taken.")

            # 2️⃣ Horizontal scroll screenshot
            table_container = driver.find_element(By.CSS_SELECTOR, "div.table-responsive")
            driver.execute_script("arguments[0].scrollLeft = arguments[0].scrollWidth;", table_container)
            time.sleep(2)
            driver.save_screenshot(os.path.join(screenshot_dir, f"{number}_addon_page_horizontal.png"))
            print("Horizontal scroll screenshot taken.")
            time.sleep(2)

            driver.refresh()
            time.sleep(4)

            logging.info("=== Automation Script Completed ===")

    finally:
        time.sleep(5)
        driver.quit()