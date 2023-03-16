"""
Project     : Webscraper for Remine App
Description : This script is takes an string input, the address of a real estate property.
              Read-in information from the Remine Site, and save this information onto a csv file.
              Will also perform search for the address in the CSV file to avoid duplicate read-ins
"""
import time
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Read in Property Address from user
property_address = input('Enter Property Address: ')

# Open Credential File and Read-in Information
with open('config.json', 'r') as f:
    config = json.load(f)
login_url = config['login_url']
username = config['username']
password = config['password']

# Open Login page
driver = webdriver.Chrome()
driver.get(login_url)

# Wait for Page Load, Find Input fields
wait = WebDriverWait(driver, 20)
username_field = wait.until(
    EC.visibility_of_element_located((By.NAME, "loginId")))
password_field = wait.until(
    EC.visibility_of_element_located((By.NAME, "password")))
login_btn = wait.until(
    EC.visibility_of_element_located((By.ID, "btn-login")))

# Send Credentials and Login
username_field.send_keys(username)
password_field.send_keys(password)
login_btn.click()

# Navigate to Remine
product_button = wait.until(
    EC.visibility_of_element_located((By.CLASS_NAME, "dropbtn")))
product_button.click()
remine_link = driver.find_element(by=By.LINK_TEXT, value='Remine')
remine_link.click()
driver.switch_to.window(driver.window_handles[1])
driver.close()
driver.switch_to.window(driver.window_handles[0])

# Navigate to Search Bar and Enter Property Address
driver.get(config['remine_search'])
search_field = wait.until(EC.visibility_of_element_located(
    (By.ID, "remine-smarter-search")))
search_field.send_keys(property_address)
search_field.click()
property_btn = wait.until(EC.visibility_of_element_located(
    (By.CSS_SELECTOR, 'button[data-re-id="Core-Rediscover-Search-Result-Item-Button-0-Addresses"]')))
property_btn.click()


# Convert page into soup object for HTML parsing
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')

h1_tag = soup.find('h1')
print(h1_tag)

# Close the driver instance
end = input('To close page, type "END": ')
if end == 'END':
    driver.quit()
