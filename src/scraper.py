from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=ChromeService(
    ChromeDriverManager().install()))
driver.get("https://leetcode.com/submissions/#/1")
driver.implicitly_wait(10)
title = driver.title
print(title)
driver.quit()
