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

# Read the CAF.csv file
df = pd.read_csv('CAF.csv')
sample_file = "m2m_selfcare_sms_whitelist_sample.csv"
artefacts_folder = "m2m_selfcare_bulk_whitelisting_sms_artifacts"

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
new_df['sms_outgoing_1'] = '5490040071'
new_df['sms_outgoing_2'] = '9495787799'
new_df['sms_outgoing_3'] = '5490040025'
new_df['sms_outgoing_4'] = '5490040014'
new_df['sms_incoming_1'] = '5490040071'
new_df['sms_incoming_2'] = '9495787799'
new_df['sms_incoming_3'] = '5490040025'
new_df['sms_incoming_4'] = '5490040014'

# Write to Addon_activation.csv
new_df.to_csv(f'{sample_file}', index=False)

print("✅ Sample file created successfully:", sample_file)

def get_user_inputs():
    """Display a simple Tkinter window to collect user inputs."""
    user_data = {}

    def submit():
        if not eCode.get() or not username.get():
            messagebox.showerror("Error", "Please fill all fields.")
            return

        # ✅ Store values before destroying the window
        user_data["eCode"] = eCode.get().strip()
        user_data["username"] = username.get().strip()

        root.destroy()  # now it's safe to close

    root = tk.Tk()
    root.title("M2M Selfcare Bulk Whitelisting Voice Automation Input")
    root.geometry("500x400")
    root.resizable(False, False)

    tk.Label(root, text="Enter Ecode:").pack(pady=5)
    eCode = tk.Entry(root, width=40)
    eCode.pack()

    tk.Label(root, text="Enter Username for Selfcare:").pack(pady=5)
    username = tk.Entry(root, width=40)
    username.pack()

    tk.Button(root, text="Submit", command=submit, bg="#4CAF50", fg="white", width=15).pack(pady=15)
    root.mainloop()

    # ✅ Return collected values
    return user_data["eCode"], user_data["username"]

def whitelist_error_check():

    wait = WebDriverWait(driver, 10)

    # --- Outgoing first field (edit + error capture) ---
    outgoing_field = wait.until(EC.element_to_be_clickable((By.ID, "callListO")))
    edit_icon_out = outgoing_field.find_element(
        By.XPATH, "following-sibling::span//img[contains(@src,'VIL-Edit.svg')]"
    )
    edit_icon_out.click()
    time.sleep(1)
    outgoing_field.clear()
    outgoing_field.send_keys("123456789012")  # 12-digit invalid
    tick_out = outgoing_field.find_element(
        By.XPATH, "following-sibling::span//*[name()='svg' or contains(@src,'check-circle-fill')]"
    )
    tick_out.click()
    time.sleep(2)
    # --- Handle Yes/No popup ---
    confirm_yes = wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR, "button.btn.btn-app-primary.btn-micro.border-0"
    )))
    confirm_yes.click()
    time.sleep(2)
    driver.save_screenshot(os.path.join(screenshot_dir, f"{number}_outgoing_error.png"))
    time.sleep(2)

    #selecting no popup
    driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div/div[12]/div/div/div/div[5]/div/div/div/div[3]/div/button[1]").click()
    time.sleep(2)

    # --- Incoming first field (edit + error capture) ---
    incoming_field = wait.until(EC.element_to_be_clickable((By.ID, "callListT")))
    edit_icon_in = incoming_field.find_element(
        By.XPATH, "following-sibling::span//img[contains(@src,'VIL-Edit.svg')]"
    )
    edit_icon_in.click()
    time.sleep(1)
    incoming_field.clear()
    incoming_field.send_keys("123456789012")  # 12-digit invalid
    tick_in = incoming_field.find_element(
        By.XPATH, "following-sibling::span//*[name()='svg' or contains(@src,'check-circle-fill')]"
    )
    tick_in.click()
    time.sleep(2)
    # --- Handle Yes/No popup ---
    confirm_yes = wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR, "button.btn.btn-app-primary.btn-micro.border-0"
    )))
    confirm_yes.click()
    time.sleep(2)
    driver.save_screenshot(os.path.join(screenshot_dir, f"{number}_incoming_error.png"))
    time.sleep(2)

    # selecting no popup
    driver.find_element(By.XPATH,
                        "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div/div[12]/div/div/div/div[5]/div/div/div/div[3]/div/button[1]").click()
    time.sleep(2)

    print("📸 Error validation screenshots captured for Outgoing and Incoming.")

def cleanup_whitelist_simple():
    wait = WebDriverWait(driver, 10)

    outgoing_ids = ["callListO", "callListOse", "callListOth", "callListOfor"]
    incoming_ids = ["callListT", "callListTse", "callListTth", "callListTfor"]

    def clear_section(input_ids, section_name):
        print(f"\n➡️ Clearing {section_name}")
        while True:
            filled = None
            for _id in input_ids:
                try:
                    el = driver.find_element(By.ID, _id)
                    val = (el.get_attribute("value") or "").strip()
                    if val:
                        filled = (el, val)
                        break
                except Exception:
                    continue

            if not filled:
                print(f"  ✅ All entries cleared for {section_name}")
                break

            el, val = filled
            print(f"  ▶ Deleting value: {val}")

            # Locate and click delete button — flexible path to cover your HTML pattern
            try:
                delete_btn = el.find_element(
                    By.XPATH, "./following::img[contains(@src,'VIL_Delete.svg')][1]"
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", delete_btn)
                time.sleep(0.3)
                delete_btn.click()
                print("    🖱️ Clicked delete icon")
            except Exception as e:
                print(f"    ⚠️ Delete icon not found: {e}")
                continue

            # Click Yes in confirmation
            try:
                yes_btn = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[normalize-space()='Yes' or normalize-space()='yes']")
                    )
                )
                yes_btn.click()
                print("    ✅ Confirmed delete (Yes clicked)")
            except Exception:
                print("    ⚠️ 'Yes' button not found, skipping")

            # Wait for input to clear
            for _ in range(10):
                try:
                    if not (el.get_attribute("value") or "").strip():
                        print(f"    ✓ Cleared {val}")
                        break
                except Exception:
                    break
                time.sleep(0.3)
            else:
                print(f"    ✖ Timed out waiting for {val} to clear")

            time.sleep(0.4)

    # Outgoing first
    clear_section(outgoing_ids, "Outgoing Numbers")

    # Then Incoming
    clear_section(incoming_ids, "Incoming Numbers")

    print("\n🎯 Cleanup completed cleanly.")

if __name__ == "__main__":

    # ✅ Get user input via GUI
    eCode, username = get_user_inputs()

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

        # bulk menu
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div[1]/div[1]/div[2]/ul/li[8]/a/span/a").click()
        time.sleep(2)

        #whitelisting menu
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div[1]/div[1]/div[2]/ul/li[8]/ul/li[3]/div/a").click()
        time.sleep(3)

        #file upload
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div[1]/div[1]/div[2]/div/button").click()
        time.sleep(3)

        #inseting ecode
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div/div[1]/div/div/div[1]/div[2]/div/input").send_keys(eCode)
        time.sleep(5)

        #selecting ecode
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div").click()
        time.sleep(2)

        #action type
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div/div[2]/div/div/div[1]").click()
        time.sleep(2)

        #selecting sms
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div/div[2]/div/div[2]/div/div[1]").click()
        time.sleep(2)

        # uploading file
        file_input = driver.find_element(By.XPATH, "//input[@type='file']")
        file_input.send_keys(
            fr"C:\Users\naveen.basavaraj\PycharmProjects\VIL_GUI_API_M2M_SELFCARE_AUTOMATION\{sample_file}")
        time.sleep(3)

        # next page
        driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[2]/div/button[2]").click()
        time.sleep(3)

        # submit button
        driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div[2]/div/button[3]").click()
        time.sleep(10)

        #adding filters to get values
        #ecode entry
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[1]/div/div[2]/div/div[1]/div[1]/div/div/div[1]/div[2]/div/input").send_keys(eCode)
        time.sleep(5)

        #selecting particular ecode
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[1]/div/div[2]/div/div[1]/div[1]/div/div[2]/div/div").click()
        time.sleep(2)

        #action type
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[1]/div/div[2]/div/div[1]/div[2]/div/div[1]/div[1]").click()
        time.sleep(2)

        #selecting sms
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[1]/div/div[2]/div/div[1]/div[2]/div/div[2]/div/div[1]").click()
        time.sleep(2)

        #search
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[1]/div/div[2]/div/div[2]/button[1]").click()
        time.sleep(3)

        # locate the status cell (5th column in the row)
        status_element = driver.find_element(
            By.XPATH,
            "(//tr[contains(@class, 'row_entire_selection')])[1]/td[5]/div"
        )

        status_text = status_element.text.strip()

        # check if status == "Success"
        if status_text.lower() == "file process completed":
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
        driver.save_screenshot(os.path.join(screenshot_dir, f"{eCode}_vertical.png"))
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

            # whitelisting page
            driver.find_element(By.XPATH,
                                "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/ul/li[9]/button").click()
            time.sleep(4)

            # selecting sms tab
            driver.find_element(By.XPATH,
                                "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div/div[12]/div/div/div/div[1]/li/div[2]/input").click()
            time.sleep(2)

            # Scroll to the "Whitelisting" section
            wait = WebDriverWait(driver, 30)
            whitelist_tab = wait.until(EC.visibility_of_element_located((By.ID, "voice-sms-whitelisting")))
            driver.execute_script("arguments[0].scrollIntoView(true);", whitelist_tab)
            time.sleep(2)

            #taking snap of the all upload voice msisdn
            driver.save_screenshot(os.path.join(screenshot_dir, f"{number}_vertical.png"))

            # error check
            whitelist_error_check()

            # deleting the entries
            cleanup_whitelist_simple()

            driver.refresh()
            time.sleep(5)


    finally:
        time.sleep(5)
        driver.quit()