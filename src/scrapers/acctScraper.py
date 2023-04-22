import pandas as pd
import numpy as np
import time
import configparser
import validators
import configparser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


def acctScraper(existingSubmissions):
    ## INIT##
    subsLinksList = []
    submissionsDict = {}
    config = configparser.ConfigParser()
    config.read('config.ini')
    print(config.sections())
    driver = webdriver.Chrome(service=ChromeService(
        ChromeDriverManager().install()))
    driver.get("https://leetcode.com/submissions/#/1")
    time.sleep(3)

    def login():
        usernameBox = driver.find_element(By.ID, value="id_login")
        passwordBox = driver.find_element(By.ID, value="id_password")
        submit_button = driver.find_element(By.ID, value="signin_btn")
        usernameBox.send_keys(config['LeetCode Info']['Username'])
        passwordBox.send_keys(config['LeetCode Info']['Password'])
        submit_button.click()
        # Need to wait for user input in case captcha fires
        input("Press Enter to continue...")

    # Building list of links to submission performance pages
    def getSubmissionsLinks():
        print("Getting submissions links")
        submissions2 = driver.find_elements(
            By.CSS_SELECTOR, value="#submission-list-app table tr")
        for s in submissions2:
            tabs = s.find_elements(By.TAG_NAME, value="td")
            if (len(tabs) != 5):
                print({"Weird Tab Length, skipping": print(tabs)})
                print(len(tabs))
                for t in tabs:
                    print(t.text)
                continue
            if tabs[2].text != "Accepted":
                print("Not Accepted, skipping")
                continue
            linkElement = tabs[2].find_element(By.TAG_NAME, value="a")
            link = linkElement.get_attribute("href")
            if (link in existingSubmissions):
                print("Already in DB, skipping, ", link)
                continue
            if not validators.url(link):
                print("Not a valid URL, skipping, ", link)
                continue
            print("Adding to list: ", link)
            subsLinksList.append(link)
            submissionsDict[link] = [
                tabs[1].text, tabs[3].text, tabs[4].text]
        pager = driver.find_element(By.CLASS_NAME, value="pager")
        next = pager.find_element(By.CLASS_NAME, value="next")
        if next.get_attribute("class") == "next disabled":
            print("Completed collecting all submissions")
            return
        nextButton = next.find_element(By.TAG_NAME, value="a")
        nextButton.click()
        time.sleep(2)
        # getSubmissionsLinks()

    def getPerformanceData():
        for link in subsLinksList:
            driver.get(link)
            time.sleep(2)
            perfCallouts = driver.find_elements(By.CLASS_NAME, value="callout")
            if len(perfCallouts) > 2:
                print("Greater than 2 perf callouts, skipping: ", link)
                for n in perfCallouts:
                    print(n.text)
                continue
            perfs = ["N/A", "N/A"]
            for i, p in enumerate(perfCallouts):
                nums = [s for s in p.text.split(" ") if not s.isalpha()]
                perfs[i] = nums[1]
            submissionsDict[link].extend(perfs)

    login()
    getSubmissionsLinks()
    getPerformanceData()
    driver.quit()
    print(submissionsDict)
    return submissionsDict


def acctScraperTest():
    acctScraper(set())
