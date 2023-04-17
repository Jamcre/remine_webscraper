"""
Project     : Webscraper for Remine App

Dependencies: This program was built on Python 3.9.6, probably will not cause issues but should be noted if running on different Python version
              The 'selenium' library is required for this program to function properly
              Can be installed through terminal using pip, command is as follows: 'pip install selenium'

Description : This script is takes an string input, the address of a real estate property.
              Read-in information from the Remine Site, and save this information onto a csv file.
"""

import time, csv, json, os.path, requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def read_credentials():
    """
    Read in Credentials from config.json file.
    """
    config_file = 'config.json'
    # Error Handling Case: File not in directory
    if not os.path.isfile(config_file):
        print(f'Error: {config_file} not found')
        exit()
    # File Read-in
    with open(config_file, 'r') as file:
        config = json.load(file)
        username = config.get('username', '')
        password = config.get('password', '')
        login_url = config.get('login_url', '')
        remine_search = config.get('remine_search', '')
        # Error Handling Case: File is incomplete
        if not (username and password and login_url and remine_search):
            print('Error: config file is missing required fields')
            exit()
    # Return read values
    return username, password, login_url, remine_search

def login(username, password, login_url):
    """
    Open Login page, wait for page load, find input fields, send credentials, and login.
    """
    # Initialize driver object and go to login site
    driver = webdriver.Chrome()
    driver.get(login_url)
    # 'wait' variable, meant to give webpage time to load before accessing elements
    wait = WebDriverWait(driver, 15)
    # Locate Username, Password, and Login button fields
    username_field = wait.until(EC.visibility_of_element_located((By.NAME, "loginId")))
    password_field = wait.until(EC.visibility_of_element_located((By.NAME, "password")))
    login_btn = wait.until(EC.visibility_of_element_located((By.ID, "btn-login")))
    # Send credentials and click login button
    username_field.send_keys(username)
    password_field.send_keys(password)
    login_btn.click()
    # Return driver object after webpage login
    return driver

def navigate_to_remine(driver):
    """
    Navigates from MLS landing page to the Remine Webapp
    """
    # 'wait' variable, meant to give webpage time to load before accessing elements
    wait = WebDriverWait(driver, 15)
    # Locate submenu, click submenu button
    product_button = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "dropbtn")))
    product_button.click()
    # Locate remine link, click remine link
    remine_link = driver.find_element(by=By.LINK_TEXT, value='Remine')
    remine_link.click()
    # Close unnecessary windows
    driver.switch_to.window(driver.window_handles[1])
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    # Return driver object
    return driver

def search_property(driver, remine_search, property_address):
    """
    In Remine App, searches for property, clicks first match, opens listing webpage
    """
    # Switch to search page in Remine
    driver.get(remine_search)
    # 'wait' variable, meant to give webpage time to load before accessing elements
    wait = WebDriverWait(driver, 15)
    # Locate search bar, send property address, click search
    search_field = wait.until(EC.visibility_of_element_located((By.ID, "remine-smarter-search")))
    search_field.send_keys(property_address)
    search_field.click()
    # Locate search submenu, after inputting address
    property_btn = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[data-re-id="Core-Rediscover-Search-Result-Item-Button-0-Addresses"]')))
    property_btn.click()
    # Locates first result, clicks the first result
    first_result = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-re-id="Core-Rediscover-SelectAllProperties-FloatingToggle"]')))
    first_result.click()
    # Switch to newly opened tab
    driver.switch_to.window(driver.window_handles[1])
    # Locate see all button, click to reveal all property data
    see_all_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="RemineBodyContainer"]/div/div/div/div[3]/div[1]/div[1]/div[2]/div/div/div/div/article/section[4]/div/div[3]/button')))
    see_all_btn.click()
    # Optional time buffer to wait for page load
    time.sleep(3)
    # Return driver object
    return driver

def scrape_public_records(driver):
    """
    Scrapes the Public records section, and returns info as list
    """
    # 'wait' variable, meant to give webpage time to load before accessing elements
    wait = WebDriverWait(driver, 15)
    # Locate Public Records div, and extract info (<p> tags)
    public_records_xpath = '//*[@id="RemineBodyContainer"]/div/div/div/div[3]/div[1]/div[1]/div[2]/div/div/div/div/article/section[4]/div/div[1]/div/div/div'
    public_records_elements = wait.until(EC.visibility_of_element_located((By.XPATH, public_records_xpath)))
    public_records = public_records_elements.find_elements(By.XPATH, '//div/div/div/ul/li/p')
    public_records_text = [p.text for p in public_records]
    # Return info as list
    return public_records_text

def write_onto_csv(property_data):
    """
    Takes a list of data and writes onto provided CSV file
    """
    # Write queried property info onto CSV
    column_names = property_data[::2]
    row_values = property_data[1::2]

    # Write the data to a CSV file
    with open('property_data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(column_names)
        writer.writerow(row_values)

def datalist_to_dict(property_data_lst):
    """
    Converts Propery Data List into Dictionary with, 
    Property Field as key
    Current Property data as value
    """
    property_data_dict = {}
    # Goes through property data list, even indices are keys, odd indices are values
    for index in range(0, len(property_data_lst), 2):
        key = property_data_lst[index]
        value = property_data_lst[index + 1]
        property_data_dict[key] = value
    # Return dictionary
    return property_data_dict

def push_to_zoho_creator(property_data_dict):
    """
    Will push data to the Property Application app
    """
    # Scopes for Zoho Self Client 
    # ZohoCreator.dashboard.read, ZohoCreator.form.CREATE, ZohoCreator.meta.CREATE, ZohoCreator.meta.DELETE, ZohoCreator.meta.application.read, ZohoCreator.meta.form.read, ZohoCreator.meta.report.read, ZohoCreator.report.CREATE, ZohoCreator.report.DELETE, ZohoCreator.report.READ, ZohoCreator.report.UPDATE

    # James' Zoho API Self Client information
    client_id = '1000.WUGZWSGSXG8E3S9CS5EEFLKOTVSA8J'
    client_secret = '53347f8c1a744c03b91335068bbab812b7582111d2'

    # Auth Token, lasts 10 minutes, create one later for testing
    auth_token = '1000.b7bb695292a5182b909cada37916e56c.defe93ae106e56a406be2afa429f582a'
    # Header for POST
    headers = {'Authorization': auth_token}
    # Need Access to check if the URL below is correct
    application_url = "https://creator.zoho.com/api/v2/accounts4470/Property-Application-Form/record/add"

    response = requests.post(application_url, headers=headers, data=property_data_dict)

    # Check the response status code to see if the request was successful
    if response.status_code == 200:
        print('Data pushed to Zoho Creator successfully!')
    else:
        print('Error pushing data to Zoho Creator')

def main():
    """
    Remine scraper 
    """
    # Read in Property Address from user, clean string
    property_address = input('Enter Property Address: ')
    property_address = property_address.upper().strip()
    # Read in Credentials
    username, password, login_url, remine_search = read_credentials()
    # Log onto webpage
    driver = login(username, password, login_url)
    # Navigate to Remine
    driver = navigate_to_remine(driver)
    # Search property address on Remine
    driver = search_property(driver, remine_search, property_address)
    # Get Property data as list
    property_data_lst = scrape_public_records(driver)
     
    # Property listing info, stored as dictionary
    property_data_dict = datalist_to_dict(property_data_lst)
    print(property_data_dict)
    
    # Push to Zoho Creator
    push_to_zoho_creator(property_data_dict)

    # Write onto csv
    write_onto_csv(property_data_lst)   

    # End instance / Close Driver
    end = input("Write 'END' to Stop: ")
    if end == 'END':
        driver.quit()

    # """
    # NOTE FOR DESTINY AND/OR CAMILLE:

    # I implemented a function that converts the property data list into a dictionary with the following format:
    # property_dictionary[key] = value
    # The key would be the property data field: zipcode, floors, etc.
    # The value would be the data for the property: 11372, 2, and so on.
    
    # Example usage below:
    # property_dictionary[zipcode] = 11368

    # This dictionary would hold all info for the currently queried property, may be useful when implementing the push_to_zoho function,
    # psuedocode for previous function was provided by Ivan in the new Zoho Projects subtasks

    # Good luck! - James
    # """
    

if __name__ == '__main__':
    main()
