import time
import configparser
import validators
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from dbHandler import writeSubmissionsToCSV
## INIT##
config = configparser.ConfigParser()
config.read('config.ini')
print(config.sections())
driver = webdriver.Chrome(service=ChromeService(
    ChromeDriverManager().install()))
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

driver.get("https://leetcode.com/submissions/#/1")
time.sleep(3)

## LOGIN##
usernameBox = driver.find_element(By.ID, value="id_login")
passwordBox = driver.find_element(By.ID, value="id_password")
submit_button = driver.find_element(By.ID, value="signin_btn")
usernameBox.send_keys(config['LeetCode Info']['Username'])
passwordBox.send_keys(config['LeetCode Info']['Password'])
submit_button.click()
input("Press Enter to continue...")

## Driver Code##
subsLinksList = []
submissionsDict = {}
# Building list of links to submission performance pages


def getSubmissionsLinks():
    submissionsBox = driver.find_element(By.ID, value="submission-list-app")
    submissionsTable = submissionsBox.find_element(By.TAG_NAME, value="table")
    submissions = submissionsTable.find_elements(By.TAG_NAME, value="tr")
    print(len(submissions))
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
        if not validators.url(link):
            print("Not a valid URL, skipping, ", link)
            continue
        subsLinksList.append(link)
        submissionsDict[link] = [tabs[1].text, tabs[3].text, tabs[4].text]
    pager = driver.find_element(By.CLASS_NAME, value="pager")
    print(pager.text)
    next = pager.find_element(By.CLASS_NAME, value="next")
    if next.get_attribute("class") == "next disabled":
        print("Completed collecting all submissions")
        return
    nextButton = next.find_element(By.TAG_NAME, value="a")
    nextButton.click()
    time.sleep(2)
    getSubmissionsLinks()


getSubmissionsLinks()

print(subsLinksList)
print(submissionsDict)

# Collecting performance data from submission performance pages
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

writeSubmissionsToCSV(submissionsDict)
driver.implicitly_wait(1000)
driver.quit()
