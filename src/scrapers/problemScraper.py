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


def problemsScrapper(existingProblems):
    probsLinksList = []
    probsDict = {}
    config = configparser.ConfigParser()
    driver = webdriver.Chrome(service=ChromeService(
        ChromeDriverManager().install()))
    driver.get("https://leetcode.com/problemset/all/")
    time.sleep(3)

    def prepSite(settingsElement, elemsPerPageElement, navBarElement):
        settingsBtn = settingsElement.find_element(By.TAG_NAME, value="button")
        elemsPerPageBtn = elemsPerPageElement.find_element(
            By.TAG_NAME, value="button")
        settingsBtn.click()
        time.sleep(1)
        settingsMenu = settingsElement.find_elements(By.XPATH, value="*")[-1]
        print(settingsMenu.text)
        topicTagsBox = settingsMenu.find_element(
            By.XPATH, value="*")
        topicCheckBox = topicTagsBox.find_element(By.XPATH, value="*")
        topicCheckBox.click()
        time.sleep(1)
        # Swapping to 100 elements per page
        elemsPerPageBtn.click()
        time.sleep(1)
        elemsPerPageList = elemsPerPageElement.find_element(
            By.TAG_NAME, value="ul")
        elemsListItems = elemsPerPageList.find_elements(
            By.TAG_NAME, value="li")
        elemsListItems[-1].click()
        time.sleep(1)
        lastBtn = navBarElement.find_elements(By.TAG_NAME, value="button")[-2]
        lastBtn.click()
        time.sleep(3)
        return True

    def handleProblemElement(problemElement):
        # Check if link is in DB, if so skip
        # Else if all tags are present, add to dict
        # Else add link to list of links to be scraped and add title, difficulty, and acceptance to dict
        cols = problemElement.find_elements(By.XPATH, value="*")
        if len(cols) != 6:
            print("Weird Problem Element length, skipping", len(cols))
            return
        titleElement = cols[1]
        link = titleElement.find_element(By.TAG_NAME, value="a").get_attribute(
            "href")
        if link in existingProblems:
            print("Already in DB, skipping, ", titleElement.text, link)
            return
        isPremium = True if len(titleElement.find_elements(
            By.TAG_NAME, value="svg")) > 0 else False
        temp = cols[1].find_element(By.TAG_NAME, value="a")
        num, title = temp.text.split(".")
        link = temp.get_attribute("href")
        try:
            tags = [e.text for e in cols[1].find_elements(
                By.TAG_NAME, value="span")]
        except:
            tags = "None"
        acceptance = cols[3].text
        difficulty = cols[4].text
        if len(tags) < 4 or isPremium:
            if isPremium:
                print("Premium Problem: ", title)
            else:
                print("All tags visible: ", title)
                print(tags)
            probsDict.update(
                {link: [num, title, tags, acceptance, difficulty]})
        else:
            print("Not all tags visible: ", title)
            print(tags)
            probsDict.update(
                {link: [num, title, tags, acceptance, difficulty]})
            probsLinksList.append(link)
        return

    def handleProblemLinks():
        for link in probsLinksList:
            driver.get(link)
            time.sleep(2)
            TopicsTab = driver.find_elements(
                By.XPATH, value="//*[text()='Related Topics']")[0]
            clickable = TopicsTab.find_element(
                By.XPATH, value="./..")
            expandableTab = clickable.find_element(By.XPATH, value="./..")
            clickable.click()
            time.sleep(1)
            topics = expandableTab.find_elements(By.XPATH, value="*")[1:]
            probsDict[link][2] = [n.text for n in topics]

    def getProblemLinks(sitePrepped=False):
        print("Getting problem links")
        problemsGridElements = driver.find_element(
            By.CSS_SELECTOR, value=".grid .col-span-4").find_elements(
                By.XPATH, value="*")[-1].find_elements(By.XPATH, value="*")
        problemsHeader = problemsGridElements[0]
        problemsBody = problemsGridElements[1]
        problemsFooter = problemsGridElements[2]
        # Handling Problems List Header
        headerChild = problemsHeader.find_element(
            By.XPATH, value="*").find_element(By.XPATH, value="*")
        # headerComponents = headerChild.find_element(By.XPATH, value="*")
        headerList = headerChild.find_elements(By.XPATH, value="*")
        listsBtn = headerList[0].find_element(By.TAG_NAME, value="button")
        difficultyBtn = headerList[1].find_element(
            By.TAG_NAME, value="button")
        statusBtn = headerList[2].find_element(By.TAG_NAME, value="button")
        tagsBtn = headerList[3].find_element(By.TAG_NAME, value="button")
        searchBar = headerList[4].find_element(By.XPATH, value="*")

        footerComponents = problemsFooter.find_elements(By.XPATH, value="*")
        navBar = footerComponents[1]

        if not sitePrepped:
            settingsElement = headerList[5]
            elemsPerPageElement = problemsFooter.find_element(
                By.XPATH, value="*")
            prepSite(settingsElement, elemsPerPageElement, navBar)
            sitePrepped = True

        problemsBodyComponents = problemsBody.find_element(
            By.XPATH, value="*").find_element(By.XPATH, value="*").find_elements(
            By.XPATH, value="*")
        problemsList = problemsBodyComponents[1]

        for p in problemsList.find_elements(By.XPATH, value="*"):
            try:
                handleProblemElement(p)
            except Exception as e:
                print("Error in handleProblemElement: ", e)
                print("Suspect problem element: ", p.text)
        prevBtn = navBar.find_elements(By.TAG_NAME, value="button")[0]
        if prevBtn.get_attribute("disabled") == "true":
            return
        prevBtn.click()
        getProblemLinks(sitePrepped=True)

    getProblemLinks()
    handleProblemLinks()
    driver.quit()
    return probsDict
