import pandas as pd
import numpy as np
import os
import time
import configparser
import validators
import configparser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from src.scrapers.pageHandlers import loginPageHandler, submissionPageHandler
# from utils.dbHandler import writeSubmissionsToDB, writeUserdataToDB


def profileScraper(username, existingSubmissions=set()):
    ## INIT##
    subsIDSet = set()
    subsDict = {}
    driver = webdriver.Chrome(service=ChromeService(
        ChromeDriverManager().install()))
    driver.get(f'https://leetcode.com/{username}/')
    time.sleep(3)

    def getSubmissionsListElement():
        # This is some goooooood code
        return driver.find_elements(
            By.CSS_SELECTOR, value="#__next div div div div div.mt-4 div.bg-layer-1 div div.flex-col a")

    # Check if we need to login
    signInButton = driver.find_elements(By.ID, value="navbar_sign_in_button")
    if (len(signInButton) > 0):
        signInButton[0].click()
        loginPageHandler(driver)
    # Get submissions
    submissionsListElement = getSubmissionsListElement()
    print(len(submissionsListElement))
    for l in submissionsListElement:
        link = l.get_attribute("href")
        parts = link.split('/')
        if not validators.url(link) or not parts[-2].isnumeric():
            print("Bad link, skipping: ", link)
            continue
        id = parts[-2]
        if id in existingSubmissions:
            print("Already in DB, skipping, ", link)
            continue
        subsIDSet.add(id)
        title = l.find_elements(By.CSS_SELECTOR, value="div span")[0].text
        subsDict.update({id: {
            "title": title,
        }})
    for s in subsDict:
        print(s)
        try:
            subsDict[s].update(submissionPageHandler(driver, s))
        except Exception as e:
            print("Error scraping submission page: ", e)
            subsIDSet.remove(s)
            del subsDict[s]
    driver.quit()
    # writeUserdataToDB(username, list(subsIDSet))
    # writeSubmissionsToDB(subsDict)
    return subsDict, subsIDSet
