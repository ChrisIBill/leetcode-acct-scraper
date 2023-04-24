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
from .pageHandlers import prepProblemPage
from utils.Utils import dateTimeToStr, getCurrentTime
from selenium.webdriver.support.wait import WebDriverWait


def problemScraper(driver, existingProblems=set(), pagesToScrape=inf, startPage=1):
    probsLinksList = []
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
            return
        isPremium = True if len(titleElement.find_elements(
            By.TAG_NAME, value="svg")) > 0 else False
        temp = cols[1].find_element(By.TAG_NAME, value="a")
        num, title = [_.strip() for _ in temp.text.split(".")]
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
                {title: {
                    "number": int(num),
                    "link": link,
                    "tags": tags,
                    "difficulty": difficulty,
                    "acceptance": acceptance,
                    "update-time": CURRENT_TIME,
                }})
        else:
            print("Not all tags visible: ", title)
            print(tags)
            probsDict.update(
                {title: {
                    "number": int(num),
                    "link": link,
                    "difficulty": difficulty,
                    "acceptance": acceptance,
                    "update-time": CURRENT_TIME,
                }})
            probsLinksList.append(link)
        return

    def handleProblemLinks():
        for link in probsLinksList:
            driver.get(link)
            TopicsTab = WebDriverWait(driver, 3).until(lambda d: d.find_elements(
                By.XPATH, value="//*[text()='Related Topics']"))[0]
            title = driver.title.split(" - ")[0]
            print(title)
            clickable = TopicsTab.find_element(
                By.XPATH, value="./..")
            expandableTab = clickable.find_element(By.XPATH, value="./..")
            clickable.click()
            topics = WebDriverWait(expandableTab, 3).until(lambda d: d.find_elements(
                By.CSS_SELECTOR, value="div.overflow-hidden"))
            topics = [_.text for _ in topics]
            probsDict[title]["tags"] = topics

    def getProblemLinks(pagesToScrape):
        print("Getting problem links")
        # The Grid contains the problems list, as well as the nav bar and pager)
        pageCoreElements = pageCore.find_elements(By.XPATH, value="*")
        problemsBody = pageCoreElements[1]
        problemsFooter = pageCoreElements[2]
        footerComponents = problemsFooter.find_elements(By.XPATH, value="*")
        navBar = footerComponents[1]

        problemsList = problemsBody.find_element(
            By.XPATH, value="./div/div/div[@role]")

        for p in problemsList.find_elements(By.XPATH, value="*"):
            try:
                handleProblemElement(p)
            except Exception as e:
                print("Error in handleProblemElement: ", e)
                print("Suspect problem element: ", p.text)
        nextBtn = navBar.find_elements(By.TAG_NAME, value="button")[-1]
        pagesToScrape -= 1
        if pagesToScrape == 0 or nextBtn.get_attribute("disabled") == "true":
            return
        nextBtn.click()
        getProblemLinks(pagesToScrape)

    getProblemLinks(pagesToScrape)
    print("Problem links scraped, now scraping problem pages")
    print(probsDict)
    handleProblemLinks()
    driver.quit()
    print("Scraping complete")
    return probsDict
