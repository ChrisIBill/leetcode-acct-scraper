import pandas as pd
import numpy as np
import time
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from .pageHandlers import loginPageHandler, submissionPageHandler

def submissionsScraper(submissionsDict):
    print("Submissions Dict: ", submissionsDict)
    driver = webdriver.Chrome(service=ChromeService(
        ChromeDriverManager().install()))
    driver.get(f'https://leetcode.com/')
    time.sleep(3)
    # Check if we need to login
    signInButton = driver.find_elements(By.ID, value="navbar_sign_in_button")
    if (len(signInButton) > 0):
        signInButton[0].click()
        loginPageHandler(driver)
    
    for username in submissionsDict:
        print(username)
        print(submissionsDict[username])
        for data in submissionsDict[username]:
            id, title, slug, timestamp = data.values()
            print(id, title, slug, timestamp)
            driver.get(f'https://leetcode.com/problems/{slug}/submissions/')
            try:
                WebDriverWait(driver, 3).until(lambda d: d.find_elements(
            By.TAG_NAME, value="section"))
            except Exception as e:
                print("Error scraping submission", username, id)
                print(e)
            # submissionPageHandler(driver, id)
            # time.sleep(1)
        driver.close()