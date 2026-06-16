import os
import shutil
import paramiko
import logging
from selenium import webdriver
from selenium.common import TimeoutException
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

artefacts_folder = "m2m_selfcare_whitelisting_sms_voice_artifacts"

# Safe remove of previous folder or file
if os.path.exists(artefacts_folder):
    if os.path.isfile(artefacts_folder):
        os.remove(artefacts_folder)
        print(f"✅ Removed file: {artefacts_folder}")
    else:
        shutil.rmtree(artefacts_folder)
        print(f"✅ Removed folder: {artefacts_folder}")

def get_user_inputs():
    """Display a simple Tkinter window to collect user inputs."""
    user_data = {}

    def submit():
        if not msisdn_no.get() or not username.get():
            messagebox.showerror("Error", "Please fill all fields.")
            return

        # ✅ Store values before destroying the window
        user_data["msisdn_no"] = msisdn_no.get().strip()
        user_data["username"] = username.get().strip()

        root.destroy()  # now it's safe to close

    root = tk.Tk()
    root.title("M2M Selfcare Whitelisting SMS Voice Automation Input")
    root.geometry("400x300")
    root.resizable(False, False)

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
    return user_data["msisdn_no"], user_data["username"]

def whitelist_voice_outgoing():

    wait = WebDriverWait(driver, 15)

    # --- Step 2: Generate random numbers ---
    numbers = [
        random.randint(1000000000, 9999999999),
        random.randint(1000000000, 9999999999),
        random.randint(1000000000, 9999999999),
        random.randint(1000000000, 9999999999)
    ]
    print("Generated Outgoing Voice Numbers:", numbers)

    # --- Step 3: Outgoing Number Fields with IDs ---
    outgoing_fields = [
        ("callListO", numbers[0]),
        ("callListOse", numbers[1]),
        ("callListOth", numbers[2]),
        ("callListOfor", numbers[3])
    ]

    # --- Step 5: Iterate through each input field ---
    for idx, (field_id, num) in enumerate(outgoing_fields):
        field = wait.until(EC.presence_of_element_located((By.ID, field_id)))

        if idx == 0:
            # 🟢 First number — direct entry
            field.send_keys(num)
        else:
            # 🟠 Subsequent numbers — click edit icon before typing
            edit_icon = field.find_element(By.XPATH,
                "following-sibling::span//img[contains(@src,'VIL-Edit.svg')]"
            )
            edit_icon.click()
            time.sleep(1)
            field = wait.until(EC.element_to_be_clickable((By.ID, field_id)))
            field.clear()
            field.send_keys(num)

        # ✅ Click tick icon
        tick_icon = field.find_element(By.XPATH,
            "following-sibling::span//*[name()='svg' or contains(@src,'check-circle-fill')]"
        )
        tick_icon.click()
        time.sleep(1)

        # ✅ Click 'Yes' button on confirmation popup
        confirm_button = wait.until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, "button.btn.btn-app-primary.btn-micro.border-0"
        )))
        confirm_button.click()
        time.sleep(3)

        # 📸 Take screenshot after each confirmation
        driver.save_screenshot(os.path.join(
            screenshot_dir, f"{msisdn_no}_outgoing_{idx + 1}.png"
        ))

    print("✅ Whitelisting process completed successfully for Outgoing numbers.")

def whitelist_sms_outgoing():

    wait = WebDriverWait(driver, 15)

    # --- Step 2: Generate random numbers ---
    numbers = [
        random.randint(1000000000, 9999999999),
        random.randint(1000000000, 9999999999),
        random.randint(1000000000, 9999999999),
        random.randint(1000000000, 9999999999)
    ]
    print("Generated Outgoing Voice Numbers:", numbers)

    # --- Step 3: Outgoing Number Fields with IDs ---
    outgoing_fields = [
        ("callListO", numbers[0]),
        ("callListOse", numbers[1]),
        ("callListOth", numbers[2]),
        ("callListOfor", numbers[3])
    ]

    # --- Step 5: Iterate through each input field ---
    for idx, (field_id, num) in enumerate(outgoing_fields):
        field = wait.until(EC.presence_of_element_located((By.ID, field_id)))

        if idx == 0:
            # 🟢 First number — direct entry
            field.send_keys(num)
        else:
            # 🟠 Subsequent numbers — click edit icon before typing
            edit_icon = field.find_element(By.XPATH,
                "following-sibling::span//img[contains(@src,'VIL-Edit.svg')]"
            )
            edit_icon.click()
            time.sleep(1)
            field = wait.until(EC.element_to_be_clickable((By.ID, field_id)))
            field.clear()
            field.send_keys(num)

        # ✅ Click tick icon
        tick_icon = field.find_element(By.XPATH,
            "following-sibling::span//*[name()='svg' or contains(@src,'check-circle-fill')]"
        )
        tick_icon.click()
        time.sleep(1)

        # ✅ Click 'Yes' button on confirmation popup
        confirm_button = wait.until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, "button.btn.btn-app-primary.btn-micro.border-0"
        )))
        confirm_button.click()
        time.sleep(3)

        # 📸 Take screenshot after each confirmation
        driver.save_screenshot(os.path.join(
            screenshot_dir, f"{msisdn_no}_outgoing_sms_{idx + 1}.png"
        ))

    print("✅ Whitelisting process completed successfully for Outgoing numbers.")

def whitelist_voice_incoming():

    wait = WebDriverWait(driver, 15)

    # --- Step 2: Generate random numbers ---
    numbers = [random.randint(1000000000, 9999999999) for _ in range(4)]
    print("Generated Incoming Voice Numbers:", numbers)

    # --- Step 3: Incoming field IDs ---
    incoming_fields = [
        ("callListT", numbers[0]),
        ("callListTse", numbers[1]),
        ("callListTth", numbers[2]),
        ("callListTfor", numbers[3])
    ]

    # --- Step 5: All fields need edit-click before typing ---
    for idx, (field_id, num) in enumerate(incoming_fields):
        field = wait.until(EC.presence_of_element_located((By.ID, field_id)))

        # 🟠 Always click Edit first
        edit_icon = field.find_element(By.XPATH,
            "following-sibling::span//img[contains(@src,'VIL-Edit.svg')]"
        )
        edit_icon.click()
        time.sleep(1)

        # 🟢 Make field editable & enter number
        field = wait.until(EC.element_to_be_clickable((By.ID, field_id)))
        field.clear()
        field.send_keys(num)

        # ✅ Click tick icon
        tick_icon = field.find_element(By.XPATH,
            "following-sibling::span//*[name()='svg' or contains(@src,'check-circle-fill')]"
        )
        tick_icon.click()
        time.sleep(1)

        # ✅ Confirm 'Yes' on popup
        confirm_button = wait.until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, "button.btn.btn-app-primary.btn-micro.border-0"
        )))
        confirm_button.click()
        time.sleep(3)

        # 📸 Screenshot
        driver.save_screenshot(os.path.join(
            screenshot_dir, f"{msisdn_no}_incoming_{idx + 1}.png"
        ))

    print("✅ Whitelisting process completed successfully for Incoming numbers.")

def whitelist_sms_incoming():

    wait = WebDriverWait(driver, 15)

    # --- Step 2: Generate random numbers ---
    numbers = [random.randint(1000000000, 9999999999) for _ in range(4)]
    print("Generated Incoming Voice Numbers:", numbers)

    # --- Step 3: Incoming field IDs ---
    incoming_fields = [
        ("callListT", numbers[0]),
        ("callListTse", numbers[1]),
        ("callListTth", numbers[2]),
        ("callListTfor", numbers[3])
    ]

    # --- Step 5: All fields need edit-click before typing ---
    for idx, (field_id, num) in enumerate(incoming_fields):
        field = wait.until(EC.presence_of_element_located((By.ID, field_id)))

        # 🟠 Always click Edit first
        edit_icon = field.find_element(By.XPATH,
            "following-sibling::span//img[contains(@src,'VIL-Edit.svg')]"
        )
        edit_icon.click()
        time.sleep(1)

        # 🟢 Make field editable & enter number
        field = wait.until(EC.element_to_be_clickable((By.ID, field_id)))
        field.clear()
        field.send_keys(num)

        # ✅ Click tick icon
        tick_icon = field.find_element(By.XPATH,
            "following-sibling::span//*[name()='svg' or contains(@src,'check-circle-fill')]"
        )
        tick_icon.click()
        time.sleep(1)

        # ✅ Confirm 'Yes' on popup
        confirm_button = wait.until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, "button.btn.btn-app-primary.btn-micro.border-0"
        )))
        confirm_button.click()
        time.sleep(3)

        # 📸 Screenshot
        driver.save_screenshot(os.path.join(
            screenshot_dir, f"{msisdn_no}_incoming_sms_{idx + 1}.png"
        ))

    print("✅ Whitelisting process completed successfully for Incoming numbers.")

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
    driver.save_screenshot(os.path.join(screenshot_dir, "outgoing_error.png"))
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
    driver.save_screenshot(os.path.join(screenshot_dir, "incoming_error.png"))
    time.sleep(2)

    # selecting no popup
    driver.find_element(By.XPATH,
                        "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div/div[12]/div/div/div/div[5]/div/div/div/div[3]/div/button[1]").click()
    time.sleep(2)

    print("📸 Error validation screenshots captured for Outgoing and Incoming.")

def whitelist_error_check2():

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
    driver.save_screenshot(os.path.join(screenshot_dir, "outgoing_sms_error.png"))
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
    driver.save_screenshot(os.path.join(screenshot_dir, "incoming_sms_error.png"))
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
    msisdn_no, username = get_user_inputs()

    # ui admin login creds
    USERNAME = f"{username}"
    PASSWORD = "Admin@123"

    # Create folder for storing screenshots
    screenshot_dir = f"{artefacts_folder}"
    os.makedirs(screenshot_dir, exist_ok=True)

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

        # Optional: wait for page elements to load
        time.sleep(5)

        # global serach
        driver.find_element(By.XPATH,
                            "/html/body/div/div[1]/div[4]/div[1]/input").send_keys(msisdn_no)
        time.sleep(5)

        # selecting msisdn number
        driver.find_element(By.XPATH,
                            "/html/body/div/div[1]/div[4]/div[1]/div[3]/div/div[2]/div").click()
        time.sleep(5)

        #whitelisting page
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/ul/li[9]/button").click()
        time.sleep(4)

        # --- Step 1: Select Voice tab ---
        driver.find_element(By.XPATH,
                            "//input[contains(@value,'VOICE') or contains(@id,'voice')]"
                            ).click()
        time.sleep(2)

        #call function for voice outgoing
        whitelist_voice_outgoing()

        # call function for voice incomin
        whitelist_voice_incoming()

        #error check
        whitelist_error_check()

        #deleting the entries
        cleanup_whitelist_simple()

        #selecting sms tab
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div/div[12]/div/div/div/div[1]/li/div[2]/input").click()
        time.sleep(2)

        #call function sms outgoing
        whitelist_sms_outgoing()

        #call function sms incoming
        whitelist_sms_incoming()

        # error check
        whitelist_error_check2()

        # deleting the entries
        cleanup_whitelist_simple()


    finally:
        time.sleep(5)
        driver.quit()