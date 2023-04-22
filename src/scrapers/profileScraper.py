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

from src.scrapers.scraper import submissionPageScraper


def profileScraper(username, existingSubmissions=set()):
    ## INIT##
    subsIDSet = set()
    subsDict = {}
    driver = webdriver.Chrome(service=ChromeService(
        ChromeDriverManager().install()))
    driver.get(f'https://leetcode.com/{username}/')
    DUMMY_USERNAME = os.environ.get('LEETCODE_USERNAME')
    DUMMY_PASSWORD = os.environ.get('LEETCODE_PASSWORD')
    time.sleep(3)

    def login():
        usernameBox = driver.find_element(By.ID, value="id_login")
        passwordBox = driver.find_element(By.ID, value="id_password")
        submit_button = driver.find_element(By.ID, value="signin_btn")
        usernameBox.send_keys(DUMMY_USERNAME)
        passwordBox.send_keys(DUMMY_PASSWORD)
        submit_button.click()
        input("Press Enter to continue...")

    def getSubmissionsListElement():
        # This is some goooooood code
        return driver.find_elements(
            By.CSS_SELECTOR, value="#__next div div div div div.mt-4 div.bg-layer-1 div div.flex-col a")

    # Check if we need to login
    signInButton = driver.find_elements(By.ID, value="navbar_sign_in_button")
    if (len(signInButton) > 0):
        signInButton[0].click()
        time.sleep(3)
        login()
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
        perf, stats = submissionPageScraper(driver, s)
        subsDict[s].update({
            "runtime": stats[0],
            "memory": stats[1],
            "runtime-percentile": perf[0],
            "memory-percentile": perf[1],
        })
    for s in subsDict:
        print(s, subsDict[s])
    driver.quit()
    return subsDict, subsIDSet
