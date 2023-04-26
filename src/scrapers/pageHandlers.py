import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions


def loginPageHandler(driver, username=os.environ.get("LEETCODE_USERNAME"), password=os.environ.get("LEETCODE_PASSWORD")):
    time.sleep(3)
    usernameField = driver.find_element(By.ID, value="id_login")
    passwordField = driver.find_element(By.ID, value="id_password")
    signInBtn = driver.find_element(By.ID, value="signin_btn")
    usernameField.send_keys(username)
    passwordField.send_keys(password)
    signInBtn.click()
    input("Press Enter to continue...")


def problemPageHandler(driver, title, link):
    driver.get(link)
    valid = WebDriverWait(driver, 3).until(
        expected_conditions.title_contains(title))
    if not valid:
        print("Invalid problem page, skipping")
        raise "Titles do not match"
    SubmissionSection = WebDriverWait(driver, 3).until(lambda d: d.find_element(
        By.XPATH, value="//*[text()='Accepted']/../.."))
    print("Found Submissions Section: ", SubmissionSection.text)
    AcceptedElement = SubmissionSection.find_element(
        By.XPATH, value="div.items-center >div.text-label-1").text
    SubmittedElement = SubmissionSection.find_element(
        By.XPATH, value="div.items-center >div.text-label-1").text
    topics = []
    try:
        TopicsTab = WebDriverWait(driver, 3).until(lambda d: d.find_elements(
            By.XPATH, value="//*[text()='Related Topics']"))[0]
        clickable = TopicsTab.find_element(
            By.XPATH, value="./..")
        expandableTab = clickable.find_element(By.XPATH, value="./..")
        topicsList = WebDriverWait(expandableTab, 3).until(lambda d: d.find_element(
            By.CSS_SELECTOR, value="div.overflow-hidden"))
        topics = WebDriverWait(topicsList, 3).until(
            lambda d: d.find_elements(By.TAG_NAME, value="a"))
        topics = [_.get_attribute("href").split("/")[-2] for _ in topics]
    except Exception as e:
        print("No Tags Found for: ", driver.title)
        print(e)
        topics = "None"
    title = driver.title.split(" - ")[0]
    return {
        "tags": topics,
        "number-submitted": SubmittedElement,
        "number-accepted": AcceptedElement,
    }


def submissionPageHandler(driver, id):
    # Need to check if the submission perf data is in db, if not then
    # queue it for problem perf scraping
    # either way scrape the submission perf data
    driver.get(f'https://leetcode.com/submissions/detail/{id}/')
    time.sleep(2)
    perfCallouts = driver.find_elements(By.CLASS_NAME, value="callout")
    if len(perfCallouts) > 2:
        print("Greater than 2 perf callouts, skipping submission-id: ", id)
        for n in perfCallouts:
            print(n.text)
        return None
    perfs = ["N/A", "N/A"]
    for i, p in enumerate(perfCallouts):
        nums = [s for s in p.text.split(" ") if not s.isalpha()]
        perfs[i] = nums[1]
    stats = driver.find_elements(By.ID, value="ac_output")
    stats = [" ".join(s.text.split(" ")[-2:]) for s in stats]
    title = driver.find_element(By.CSS_SELECTOR, value="h4 a.inline-wrap").text
    runtime = driver.find_element(By.ID, value="result_runtime").text
    memory = driver.find_element(By.ID, value="result_memory").text
    language = driver.find_element(By.ID, value="result_language").text
    return {
        "problem-title": title,
        "runtime": runtime,
        "memory": memory,
        "language": language,
        "runtime-percentile": perfs[0],
        "memory-percentile": perfs[1],
    }


def problemSubmissionPageHandler(driver, id):
    charts = driver.find_elements(
        By.CSS_SELECTOR, value="div.highcharts-container")
    if len(charts) != 2:
        print("Weird number of charts, skipping problem-id: ", id)
        return None
    distributions = ["N/A", "N/A"]
    for i, c in enumerate(charts):
        c.click()
        try:
            distributions[i] = chartModalHandler(driver)
        except Exception as e:
            print("Error in chartModalHandler: ", e)
            continue
    return distributions


def chartModalHandler(driver):
    distributions = []
    time.wait(2)
    chartSeries = driver.find_elements(
        By.CSS_SELECTOR, value="div.highcharts-container")
    if len(chartSeries) != 3:
        print("Weird number of chart series, skipping")
        return None
    wrapper = chartSeries[2]
    label = wrapper.find_element(By.CSS_SELECTOR, value="div.highcharts-label")
    bars = wrapper.find_elements(
        By.XPATH, value="svg g.highcharts-series-group path")
    for b in bars:
        b.move_to_element()
        time.sleep(1)
        print(label.text)
        distributions.append(label.text)
    return distributions


def prepProblemPage(driver, startPage=1, elemsPerPage=100):
    driver.get(f"https://leetcode.com/problemset/all/?page={startPage}")
    # Checking for alerts and popups
    try:
        alerts = WebDriverWait(driver, 3).until(lambda d: d.find_elements(
            By.TAG_NAME, value="section"))
        for a in alerts:
            print("Alert Detected: ", a.text)
            a.find_element(By.CSS_SELECTOR, value="button").click()
    except:
        # No alerts
        pass

    try:
        pageCore = WebDriverWait(driver, 3).until(lambda d: d.find_element(
            By.CSS_SELECTOR, value="div.grid >div:first-child >div:last-child"))
        header = pageCore.find_element(By.CSS_SELECTOR, value="div.mb-3")
        body = pageCore.find_element(By.CSS_SELECTOR, value="div.-mx-4")
        footer = pageCore.find_element(By.CSS_SELECTOR, value="div.mt-4")
        # Sorting by default by number from greatest to least
        # TODO: Many improvements can be made here
        titleColumnSorter = body.find_element(
            By.CSS_SELECTOR, value="div[role='row'] > div:nth-child(2)")
        titleColumnSorter.click()
        # Setting number of problems per page
        elemsPerPageParent = footer.find_element(
            By.CSS_SELECTOR, value="div.relative")
        if elemsPerPageParent.text.split(" / ")[0] != str(elemsPerPage):
            elemsPerPageBtn = elemsPerPageParent.find_element(
                By.CSS_SELECTOR, value="button")
            elemsPerPageBtn.click()
            elemsPerPageList = WebDriverWait(elemsPerPageParent, 3).until(lambda d: d.find_elements(
                By.CSS_SELECTOR, value="ul > li"))
            for e in elemsPerPageList:
                if e.text.split(" / ")[0] == str(elemsPerPage):
                    e.click()
                    break
            else:  # If no match found
                raise Exception("No match found for elemsPerPage")

        # Setting tags view to all
        settingsBtn = header.find_element(
            By.CSS_SELECTOR, value="button[aria-label='settings']")
        settingsBtn.click()
        settingsMenu = WebDriverWait(settingsBtn, 3).until(lambda d: d.find_element(
            By.XPATH, value="./following-sibling::div"))
        tagsToggle = settingsMenu.find_element(
            By.CSS_SELECTOR, value="div > div")
        toggleState = tagsToggle.find_element(By.TAG_NAME, value="div").get_attribute(
            'aria-checked')
        if toggleState != "true":
            tagsToggle.click()
        time.sleep(2)
        pageCore = WebDriverWait(driver, 3).until(lambda d: d.find_element(
            By.CSS_SELECTOR, value="div.grid >div:first-child >div:last-child"))
        return pageCore
    except Exception as e:
        print("Error in prepProblemPage: ", e)
        raise e


def test():
    print("Testing pageHandlers.py")
