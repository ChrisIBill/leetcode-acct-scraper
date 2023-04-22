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

def submissionPageScraper(driver, id):
    # Need to check if the submission perf data is in db, if not then
    # queue it for problem perf scraping
    # either way scrape the submission perf data
    driver.get(f'https://leetcode.com/submissions/detail/{id}/')
    time.sleep(2)
    perfCallouts = driver.find_elements(By.CLASS_NAME, value="callout")
    if len(perfCallouts) > 2:
        print("Greater than 2 perf callouts, skipping: ", link)
        for n in perfCallouts:
            print(n.text)
        return None
    perfs = ["N/A", "N/A"]
    for i, p in enumerate(perfCallouts):
        nums = [s for s in p.text.split(" ") if not s.isalpha()]
        perfs[i] = nums[1]
    stats = driver.find_elements(By.ID, value="ac_output")
    stats = [s.text.split(" ")[-2:] for s in stats]
    return perfs, stats


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

# Complete Scrape of all problems


# def getAllProblems():
#     # problemsDict = readProblemsFromDB()
#     problemsDict = problemsScrapper(set())
#     writeProblemsToDB(pd.DataFrame.from_dict(problemsDict, orient="index").rename(
#         columns={0: "Number", 1: "Title", 2: "Tags", 3: "Acceptance", 4: "Difficulty"}))


# def getNewProblems():
#     problemsDict = readProblemsFromDB()
#     newProblems = problemsScrapper(problemsDict.keys())
#     writeProblemsToDB(pd.DataFrame.from_dict(newProblems, orient="index").rename(
#         columns={0: "Number", 1: "Title", 2: "Tags", 3: "Acceptance", 4: "Difficulty"}))


# def getProblemPerformanceDistributions():
#     problemsDict = readProblemsFromDB()
#     for link in problemsDict:
#         # check if perf data has been scraped
#         print("BROKEN")


# def moveFileToDB():
#     submDF = getDataframeFromSubmissions()
#     submDF['RuntimeRank'] = submDF['RuntimeRank'].fillna("None")
#     submDF['MemoryRank'] = submDF['MemoryRank'].fillna("None")

#     writeSubmissionsToDB(submDF)


# problemsScrapper(set())
# getLoggedInAcctSubmissions()
# moveFileToDB()
