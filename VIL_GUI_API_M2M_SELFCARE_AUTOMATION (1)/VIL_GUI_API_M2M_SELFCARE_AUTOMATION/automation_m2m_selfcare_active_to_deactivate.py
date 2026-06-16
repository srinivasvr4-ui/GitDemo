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

artefacts_folder = "m2m_selfcare_active_to_deactive_artifacts"

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
    root.title("M2M Selfcare Active to Deactivate Automation Input")
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

if __name__ == "__main__":

    # ✅ Get user input via GUI
    msisdn_no, username = get_user_inputs()

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

        # Optional: wait for page elements to load
        time.sleep(3)

        # global serach
        driver.find_element(By.XPATH,
                            "/html/body/div/div[1]/div[4]/div[1]/input").send_keys(msisdn_no)
        time.sleep(5)

        # selecting msisdn number
        driver.find_element(By.XPATH,
                            "/html/body/div/div[1]/div[4]/div[1]/div[3]/div/div[2]/div").click()
        time.sleep(5)

        #scrolling window
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")

        # Wait for the edit icon in start of page and click it
        edit_icon = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//img[contains(@src, 'VIL-Edit.svg') or contains(@class, 'editIcon')]"
            ))
        )
        edit_icon.click()
        time.sleep(3)

        #selecting New status
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[3]/div[1]/div/div/div[2]/div/div[1]/div[2]/div/div/div[1]").click()
        time.sleep(2)

        #selecting deactivate
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[3]/div[1]/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div/div[2]").click()
        time.sleep(2)

        #selecting assignee
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[3]/div[1]/div/div/div[2]/div/div[1]/div[4]/div/div[1]/div[1]").click()
        time.sleep(2)

        #selecting email
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[3]/div[1]/div/div/div[2]/div/div[1]/div[4]/div[1]/div[2]/div/div").click()
        time.sleep(2)

        #selecting reason
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[3]/div[1]/div/div/div[2]/div/div[1]/div[6]/div/div/div[1]").click()
        time.sleep(2)

        #selecting normal suspension
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[3]/div[1]/div/div/div[2]/div/div[1]/div[6]/div/div[2]/div/div").click()
        time.sleep(2)

        #submit button
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div[2]/div/div[3]/div[1]/div/div/div[3]/div/div/button[2]").click()
        time.sleep(10)

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

        #admin login
        admin_login()

        #approvals page
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div[1]/div[1]/div[3]/ul/li[15]/a").click()
        time.sleep(3)

        #inserting msisdn in filter
        driver.find_element(By.ID, "filed_serviceId").send_keys(msisdn_no)
        time.sleep(2)

        #search button
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[1]/div/div[2]/div/div[2]/button[1]").click()
        time.sleep(3)

        #approve button
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[2]/div/div[2]/table/tbody/tr/td[15]/div/div[1]/span").click()
        time.sleep(3)

        #adding text as test
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[3]/div[1]/div/div/div[2]/div/div/div/span/div/textarea").send_keys("test")
        time.sleep(2)

        #submit button
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/div/div/div/div[3]/div[1]/div/div/div[3]/div/div/button[2]").click()
        time.sleep(10)

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

        # Create folder for storing screenshots
        screenshot_dir = "m2m_selfcare_active_to_deactive_artifacts"
        os.makedirs(screenshot_dir, exist_ok=True)

        # global serach
        driver.find_element(By.XPATH,
                            "/html/body/div/div[1]/div[4]/div[1]/input").send_keys(msisdn_no)
        time.sleep(5)

        #global serach snap
        driver.save_screenshot(os.path.join(screenshot_dir, f"{msisdn_no}_global_search.png"))

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

        # scrolling window
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
        driver.save_screenshot(os.path.join(screenshot_dir, f"{msisdn_no}_final_vertical.png"))
        print("Vertical scroll screenshot taken.")

        logging.info("=== Automation Script Completed ===")



    finally:
        time.sleep(5)
        driver.quit()