from math import inf
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
from .pageHandlers import getNextProblemsPage, prepProblemPage, problemPageHandler
from utils.Utils import dateTimeToStr, getCurrentTime
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions


def problemScraper(driver, existingProblems=set(), problemsToScrape=100, startPage=1):
    probsLinksList = {}
    probsDict = {}
    CURRENT_TIME = getCurrentTime()
    config = configparser.ConfigParser()
    pageCore = None
    try:
        pageCore = prepProblemPage(driver, startPage)
    except Exception as e:
        raise (e)

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
            raise "Already in DB, skipping"
        isPremium = True if len(titleElement.find_elements(
            By.TAG_NAME, value="svg")) > 0 else False
        temp = cols[1].find_element(By.TAG_NAME, value="a")
        num, title = [_.strip() for _ in temp.text.split(".")]
        print(title)
        link = temp.get_attribute("href")
        try:
            tags = [e.text for e in cols[1].find_elements(
                By.TAG_NAME, value="span")]
        except:
            tags = "None"
        acceptance = cols[3].text
        difficulty = cols[4].text
        if isPremium:
            # Either cant or dont need to look at problem page to gather tags
            probsDict.update(
                {title: {
                    "number": int(num),
                    "link": link,
                    "tags": tags,
                    "difficulty": difficulty,
                    "acceptance": acceptance,
                    "update-time": CURRENT_TIME,
                }})
        else:
            probsDict.update(
                {title: {
                    "number": int(num),
                    "link": link,
                    "difficulty": difficulty,
                    "acceptance": acceptance,
                    "update-time": CURRENT_TIME,
                }})
            probsLinksList.update({link: title})
        return

    def handleProblemLinks():
        for link in probsLinksList:
            title = probsLinksList[link]
            try:
                probData = problemPageHandler(driver, title, link)
                print("here")
                probsDict.update({title: probData})
                print("Added problem: ", title)
                print("Problem data: ", probsDict[title])
            except Exception as e:
                print("Error in handleProblemLinks: ")
                print(e)
                print("Suspect link: ", link)
                continue

    def getProblemLinks(problemsToScrape, pageCore):
        print("Getting problem links")
        # The Grid contains the problems list, as well as the nav bar and pager)
        pageCoreElements = pageCore.find_elements(By.XPATH, value="*")
        problemsBody = pageCoreElements[1]
        problemsFooter = pageCoreElements[2]
        footerComponents = problemsFooter.find_elements(By.XPATH, value="*")
        navBar = footerComponents[1]
        problemsList = problemsBody.find_element(
            By.CSS_SELECTOR, value="div[role='rowgroup']")
        check = problemsList.find_element(
            By.CSS_SELECTOR, value="div[role='rowgroup'] >div:last-child >div:nth-child(2)")
        problemRows = problemsList.find_elements(
            By.CSS_SELECTOR, value="div[role='row'] >div:nth-child(2)")
        for p in problemRows:
            try:
                if p.find_elements(By.TAG_NAME, value="svg") != []:
                    print("Premium problem, skipping", p.text)
                    continue
                titleElement = p.find_element(By.TAG_NAME, value="a")
                link = titleElement.get_attribute("href")
                if link in existingProblems:
                    print("Already in DB, skipping, ", titleElement.text, link)
                    continue
                print(titleElement.text)
                probsLinksList.update(
                    {link: titleElement.text.split(".")[1].strip()})
                problemsToScrape -= 1
                if problemsToScrape == 0:
                    break
            except Exception as e:
                print("Error with problem row: ", p.text)
                print(e)
                continue
        nextBtn = navBar.find_elements(By.TAG_NAME, value="button")[-1]
        if problemsToScrape == 0 or nextBtn.get_attribute("disabled") == "true":
            print("No more pages to scrape")
            return
        pageCore = getNextProblemsPage(driver, nextBtn, check.text)
        getProblemLinks(problemsToScrape, pageCore)

    getProblemLinks(problemsToScrape, pageCore)
    print("Problem links scraped, now scraping problem pages")
    print(probsLinksList)
    handleProblemLinks()
    driver.quit()
    print("Scraping complete")
    return probsDict
