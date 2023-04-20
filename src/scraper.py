import pandas as pd
import numpy as np
import time
import configparser
import validators
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from dbHandler import appendSubmissionToCSV, getDataframeFromSubmissions, readDictFromCSV, readSubmissionsFromCSV, readSubmissionsFromDB, writeProblemsToDB, writeSubmissionsToCSV, writeSubmissionsToDB


# executor_url = driver.command_executor._url
# session_id = driver.session_id


# def attach_to_session(executor_url, session_id):
#     original_execute = WebDriver.execute

#     def new_command_execute(self, command, params=None):
#         if command == "newSession":
#             # Mock the response
#             return {'success': 0, 'value': None, 'sessionId': session_id}
#         else:
#             return original_execute(self, command, params)
#     # Patch the function before creating the driver object
#     WebDriver.execute = new_command_execute
#     driver = webdriver.Remote(
#         command_executor=executor_url, desired_capabilities={})
#     driver.session_id = session_id
#     # Replace the patched function with original function
#     WebDriver.execute = original_execute
#     return driver


# driver = attach_to_session(executor_url, session_id)


## SCRAPER##
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
    ## LOGIN##

    def login():
        usernameBox = driver.find_element(By.ID, value="id_login")
        passwordBox = driver.find_element(By.ID, value="id_password")
        submit_button = driver.find_element(By.ID, value="signin_btn")
        usernameBox.send_keys(config['LeetCode Info']['Username'])
        passwordBox.send_keys(config['LeetCode Info']['Password'])
        submit_button.click()
        input("Press Enter to continue...")
    # Building list of links to submission performance pages

    def getSubmissionsLinks():
        print("Getting submissions links")
        submissionsBox = driver.find_element(
            By.ID, value="submission-list-app")
        submissionsTable = submissionsBox.find_element(
            By.TAG_NAME, value="table")
        submissions = submissionsTable.find_elements(By.TAG_NAME, value="tr")
        for s in submissions:
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
        getSubmissionsLinks()

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
    return submissionsDict


## Driver Code##
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
        overGrid = driver.find_element(
            By.CSS_SELECTOR, value=".grid .col-span-4")
        problemsGrid = overGrid.find_elements(By.XPATH, value="*")[-1]
        problemsGridElements = problemsGrid.find_elements(By.XPATH, value="*")
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

        transitive = problemsBody.find_element(By.XPATH, value="*")
        transitive = transitive.find_element(By.XPATH, value="*")
        problemsBodyComponents = transitive.find_elements(
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
        # link = p.find_element(By.XPATH, value="*").get_attribute("href")
        # if link in existingProblems:
        #     print("Already in DB, skipping, ", link)
        #     continue
        # if not validators.url(link):
        #     print("Not a valid URL, skipping, ", link)
        #     continue
        # print("Adding to list: ", link)
        # probsLinksList.append(link)
        # probsDict[link] = []
        # Handling Problems List Footer

        # prevBtn = navBar.find_eleme
        # # Preparing Site for Efficient Scrape
        # prepSite(settingsElement, elemsPerPageBtn)
        # # Setting Show Topic Tags to On
        # settingsBtn.click()
        # time.sleep(1)
        # settingsMenu = headerList[5].find_elements(
        #     By.XPATH, value="*")[-1]
        # print(settingsMenu.text)
        # topicTagsBox = settingsMenu.find_element(
        #     By.XPATH, value="*")
        # topicCheckBox = topicTagsBox.find_element(By.XPATH, value="*")
        # topicCheckBox.click()
        # # Setting elements per page to 100

    getProblemLinks()
    handleProblemLinks()
    writeProblemsToDB(pd.DataFrame.from_dict(probsDict, orient="index").rename(
        columns={0: "Number", 1: "Title", 2: "Tags", 3: "Acceptance", 4: "Difficulty"}))

    driver.quit()


def loadDataFromDB():
    submissionsDict = readSubmissionsFromCSV()
    for d in submissionsDict:
        print(d)
        print("Link objects")
        for l in submissionsDict[d]:
            print(l)
        if len(submissionsDict[d]) != 5:
            print("Weird length, skipping")
            continue
    return submissionsDict


# Collecting performance data from submission performance pages


def getLoggedInAcctSubmissions():
    subsLinksList = []
    # submissionsDict = loadDataFromDB()
    # submissionsDict = readSubmissionsFromDB()
    submissionsDict = {}
    visitedLinks = set(submissionsDict.keys())
    print(subsLinksList)
    print(submissionsDict)
    for link in submissionsDict:
        visitedLinks.add(link)
    print(visitedLinks)
    submissionsDict = acctScraper(visitedLinks)
    print("New Submissions: ", submissionsDict)
    # appendSubmissionToCSV(submissionsDict)
    writeSubmissionsToDB(submissionsDict)

    # loadDataFromDB()
    # getSubmissionsLinks()
    # getPerformanceData()
    # writeSubmissionsToCSV(submissionsDict)


def moveFileToDB():
    submDF = getDataframeFromSubmissions()
    submDF['RuntimeRank'] = submDF['RuntimeRank'].fillna("None")
    submDF['MemoryRank'] = submDF['MemoryRank'].fillna("None")

    writeSubmissionsToDB(submDF)


problemsScrapper(set())
# getLoggedInAcctSubmissions()
# moveFileToDB()
