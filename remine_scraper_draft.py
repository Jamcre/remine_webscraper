"""
Project     : Webscraper for Remine App
Description : This script is takes an string input, the address of a real estate property.
              Read-in information from the Remine Site, and save this information onto a csv file.
"""

import time
import csv
import json
import os.path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Read in Credentials from config.json
config_file = 'config.json'
if not os.path.isfile(config_file):
    print(f'Error: {config_file} not found')
    exit()

with open(config_file, 'r') as f:
    config = json.load(f)
    username = config.get('username', '')
    password = config.get('password', '')
    login_url = config.get('login_url', '')
    remine_search = config.get('remine_search', '')

    if not (username and password and login_url and remine_search):
        print('Error: config file is missing required fields')
        exit()

# Read in Property Address from user
property_address = input('Enter Property Address: ')

# Open Login page
driver = webdriver.Chrome()
driver.get(login_url)

# Wait for Page Load, Find Input fields
wait = WebDriverWait(driver, 20)
username_field = wait.until(
    EC.visibility_of_element_located((By.NAME, "loginId")))
password_field = wait.until(
    EC.visibility_of_element_located((By.NAME, "password")))
login_btn = wait.until(EC.visibility_of_element_located((By.ID, "btn-login")))

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
driver.get(remine_search)
search_field = wait.until(EC.visibility_of_element_located(
    (By.ID, "remine-smarter-search")))
search_field.send_keys(property_address)
search_field.click()
property_btn = wait.until(EC.visibility_of_element_located(
    (By.CSS_SELECTOR, 'button[data-re-id="Core-Rediscover-Search-Result-Item-Button-0-Addresses"]')))
property_btn.click()

# Click on the first search result
first_result = wait.until(EC.element_to_be_clickable(
    (By.CSS_SELECTOR, 'button[data-re-id="Core-Rediscover-SelectAllProperties-FloatingToggle"]')))
first_result.click()

# Switch to the new tab or window
driver.switch_to.window(driver.window_handles[1])

# Click 'See All' button
see_all_btn = wait.until(EC.element_to_be_clickable(
    (By.XPATH, '//*[@id="RemineBodyContainer"]/div/div/div/div[3]/div[1]/div[1]/div[2]/div/div/div/div/article/section[4]/div/div[3]/button')))
see_all_btn.click()

# Click AirDNA menu info
AirDNA_btn =  wait.until(EC.element_to_be_clickable(
    (By.XPATH, '//*[@id="RemineBodyContainer"]/div/div/div/div[3]/div[1]/div[6]/div[2]/div/div/div/div/article/div[3]/div[2]/div/button')))
AirDNA_btn.click()

# Wait for page loads
time.sleep(3)

# Public records scrape
public_records_xpath = '//*[@id="RemineBodyContainer"]/div/div/div/div[3]/div[1]/div[1]/div[2]/div/div/div/div/article/section[4]/div/div[1]/div/div/div'
public_records_elements = wait.until(EC.visibility_of_element_located((By.XPATH, public_records_xpath)))
public_records = public_records_elements.find_elements(By.XPATH, '//div/div/div/ul/li/p')
public_records_text = [p.text for p in public_records]

# Write queried property info onto CSV
column_names = public_records_text[::2]
row_values = public_records_text[1::2]

# Write the data to a CSV file
with open('property_data.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(column_names)
    writer.writerow(row_values)

# Close Instance 
end = input("Write 'END' to Stop: ")
if end == 'END':
    driver.quit()
