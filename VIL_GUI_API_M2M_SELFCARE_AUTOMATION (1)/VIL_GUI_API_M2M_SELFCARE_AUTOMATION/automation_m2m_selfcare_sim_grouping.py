import os
import shutil
import uuid
import pandas as pd
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

# Read the CAF.csv file
df = pd.read_csv('CAF.csv')
sample_file = "SimGroupSamplefile.csv"
artefacts_folder = "m2m_selfcare_sim_grouping_artifacts"

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

# Create a new dataframe with required columns
new_df = pd.DataFrame()
new_df['msisdn'] = df['msisdn']
new_df['comment'] = 'simgroup'

# Write to Addon_activation.csv
new_df.to_csv(f'{sample_file}', index=False)

print("✅ Sample file created successfully:", sample_file)

# Write CSV normally
new_df.to_csv(sample_file, index=False)

# Now remove the last newline
with open(sample_file, "rb") as f:
    data = f.read()

# Remove newline at the end ONLY if present
while data.endswith(b"\n") or data.endswith(b"\r"):
    data = data[:-1]

# Write back clean file
with open(sample_file, "wb") as f:
    f.write(data)

print("✅ Cleaned file (no trailing newline):", sample_file)


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
    root.title("M2M Selfcare Sim Grouping Automation Input")
    root.geometry("400x300")
    root.resizable(False, False)

    # Labels and entries
    tk.Label(root, text="Enter Username for Selfcare:").pack(pady=5)
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

        #my account
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div[1]/div[1]/div[2]/ul/li[2]/a/span/a").click()
        time.sleep(4)

        #sim groups
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[2]/div/ul/li[11]/button").click()
        time.sleep(2)

        #create button
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[18]/div/div[1]/div[1]/div/div[1]/div[1]/div[2]/div/button[1]").click()
        time.sleep(3)

        # generating caf number
        simgrp = f"sim_grouping_{uuid.uuid4().hex[:6]}"

        print(f"SIM Group NUMBER: {simgrp}")

        #enter grp name
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[18]/div/div[1]/div[2]/div[1]/div/div/div[2]/div/div/div[1]/span/div/input").send_keys(simgrp)
        time.sleep(2)

        #selecting state
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[18]/div/div[1]/div[2]/div[1]/div/div/div[2]/div/div/div[2]/span/div/div/div[1]").click()
        time.sleep(2)

        #selecting maharashttra
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[18]/div/div[1]/div[2]/div[1]/div/div/div[2]/div/div/div[2]/span/div/div[2]/div/div[10]").click()
        time.sleep(2)

        #city
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[18]/div/div[1]/div[2]/div[1]/div/div/div[2]/div/div/div[3]/span/div/div/div[1]").click()
        time.sleep(2)

        #mumbai
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[18]/div/div[1]/div[2]/div[1]/div/div/div[2]/div/div/div[3]/span/div/div[2]/div/div[1]").click()
        time.sleep(2)

        #thane
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[18]/div/div[1]/div[2]/div[1]/div/div/div[2]/div/div/div[4]/span/div/textarea").send_keys("Thane")
        time.sleep(2)

        #url
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[18]/div/div[1]/div[2]/div[1]/div/div/div[2]/div/div/div[5]/span/div/input").send_keys("http://com-pod-1:3080/order-service/orders/p2a-sms")
        time.sleep(2)

        #submit
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[18]/div/div[1]/div[2]/div[1]/div/div/div[3]/div/div/button[2]").click()
        time.sleep(5)

        # Create folder for storing screenshots
        screenshot_dir = f"{artefacts_folder}"
        os.makedirs(screenshot_dir, exist_ok=True)

        # taking the artefacts
        driver.save_screenshot(os.path.join(screenshot_dir, f"{simgrp}_after_submit.png"))
        print("Screen shot has been taken after submitting sim group")

        #update button
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[18]/div/div[1]/div[1]/div/div[1]/div[1]/div[2]/div/button[2]").click()
        time.sleep(3)

        #basic deatils operation
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[18]/div/div[1]/div[6]/div/div/div[2]/div/div[2]/div/div/div/span/div[1]/div/div[1]").click()
        time.sleep(2)

        #add/modify
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[18]/div/div[1]/div[6]/div/div/div[2]/div/div[2]/div/div/div/span/div[1]/div[2]/div/div[1]").click()
        time.sleep(2)

        #sim groups
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[18]/div/div[1]/div[6]/div/div/div[2]/div/div[2]/div/div/div[2]/span/div/div/div[1]").click()
        time.sleep(2)

        #input sim groups
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[18]/div/div[1]/div[6]/div/div/div[2]/div/div[2]/div/div/div[2]/span/div/div[1]/div[1]/div[2]/div/input").send_keys(simgrp)
        time.sleep(2)

        #selecting particular sim group
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[18]/div/div[1]/div[6]/div/div/div[2]/div/div[2]/div/div/div[2]/span/div/div[2]/div/div").click()
        time.sleep(2)

        #file upload
        file_input = driver.find_element(By.XPATH, "//input[@type='file']")
        file_input.send_keys(
            fr"C:\Users\naveen.basavaraj\PycharmProjects\VIL_GUI_API_M2M_SELFCARE_AUTOMATION\{sample_file}")
        time.sleep(4)

        #submit button
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[18]/div/div[1]/div[6]/div/div/div[3]/div/div/button[2]").click()
        time.sleep(5)

        # taking the artefacts
        driver.save_screenshot(os.path.join(screenshot_dir, f"{simgrp}_after_sims.png"))
        print("Screen shot has been taken after adding sims")

        driver.refresh()
        time.sleep(5)

        # bulk menu
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div[1]/div[1]/div[2]/ul/li[8]/a/span/a").click()
        time.sleep(2)

        # bulk transactions select
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div[1]/div[1]/div[2]/ul/li[8]/ul/li[2]/div/a").click()
        time.sleep(4)

        # batching extract
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
        print("Vertical scroll bulk page screenshot taken.")

        driver.refresh()
        time.sleep(5)

        # my account
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div[1]/div[1]/div[2]/ul/li[2]/a/span/a").click()
        time.sleep(4)

        # sim groups
        driver.find_element(By.XPATH,
                            "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[2]/div/ul/li[11]/button").click()
        time.sleep(2)

        #eye button
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[18]/div/div[1]/div[1]/div/div[2]/table/tbody/tr/td[10]/div/img").click()
        time.sleep(3)

        # taking the artefacts
        driver.save_screenshot(os.path.join(screenshot_dir, f"{simgrp}_eye_view.png"))
        print("Screen shot has been taken in eye view")


    finally:
        time.sleep(5)
        driver.quit()