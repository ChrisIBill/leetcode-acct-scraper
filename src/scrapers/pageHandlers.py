import os
import time
from selenium.webdriver.common.by import By


def loginPageHandler(driver, username=os.environ.get("LEETCODE_USERNAME"), password=os.environ.get("LEETCODE_PASSWORD")):
    time.sleep(3)
    usernameField = driver.find_element(By.ID, value="id_login")
    passwordField = driver.find_element(By.ID, value="id_password")
    signInBtn = driver.find_element(By.ID, value="signin_btn")
    usernameField.send_keys(username)
    passwordField.send_keys(password)
    signInBtn.click()
    input("Press Enter to continue...")


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


def test():
    print("Testing pageHandlers.py")
