# -*- coding: utf-8 -*-
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
CHROME_DRIVER = "E:\MyStudy\Python\FBScraper\FBScraper\ChromeProfiles\chromedriver.exe"

options = webdriver.ChromeOptions()
options.add_argument(r'--user-data-dir=E:\MyStudy\Python\FBScraper\FBScraper\ChromeProfiles\1212313')
# options.add_argument(r'--profile-directory=12')

#keep chrome tab open
options.add_experimental_option("detach", True)

service_obj = Service(CHROME_DRIVER)
driver = webdriver.Chrome(service=service_obj, options=options)
driver.get("https://twitter.com")
