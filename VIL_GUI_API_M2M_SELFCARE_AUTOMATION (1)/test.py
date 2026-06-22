from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Open browser
driver = webdriver.Chrome()
driver.maximize_window()

driver.get("https://uitest.iotsmartcentral.myvi.in:8090")

driver.find_element(By.XPATH, "//input[@id='username']").send_keys("cmpadmin")

driver.find_element(By.XPATH, "//input[@id='password']").send_keys("Admin@123")

driver.find_element(By.XPATH, "//button[@type='sign in']").click()

#driver.find.element()

# Wait for page load
time.sleep(3)

# Validate login success message
message = driver.find_element(By.ID, "flash").text
print("Message:", message)
print("Message click:", message)
print("Message flash:", message)
driver.quit()