# -*- coding: utf-8 -*-
import re
import pandas as pd
import time
import utils
from utils import GroupSettingPost, PostContent, Action
from time import sleep
from random import randrange
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

CHROME_DRIVER = "E:\MyStudy\Python\FBScraper\ChromeProfiles\chromedriver.exe"
from constants import (
    FB_XPATH_ARTICLE,
    FB_XPATH_APPROVE,
    FB_XPATH_DECLINE,
    FB_XPATH_POSTER
)

class FacebookScraper:
    def __init__(self,uid,password):
        self.uid = uid
        self.password = password
        options = webdriver.ChromeOptions()
        options.add_argument(r'--user-data-dir=E:\\MyStudy\\Python\\FBScraper\\ChromeProfiles\\'+ fr'{self.uid}')
        # options.add_argument(r'--profile-directory=12')

        #keep chrome tab open
        options.add_experimental_option("detach", True)

        service_obj = Service(CHROME_DRIVER)
        self.driver = webdriver.Chrome(service=service_obj, options=options)

        if self.check_login():
            print("Already loggin!")
        else:
            self.login()

    def check_login(self):
        self.driver.get("https://www.facebook.com")
        if 'Facebook – log in or sign up' in self.driver.title:
            return False
        else:
            return True
    
    def login(self):
        try:
            uid_input = self.driver.find_element(By.XPATH, '//*[@id="email"]')
            uid_input.send_keys(self.uid)
            sleep(1)
            password_input = self.driver.find_element(By.XPATH, '//*[@id="pass"]')
            password_input.send_keys(self.password)
            sleep(1)
            password_input.send_keys(Keys.ENTER)
            sleep(3)
        except Exception:
            print('Some exception occurred while trying to find username or password field')

    def open_url(self,url):
        self.driver.get(url)
        sleep(2)
        
    def scroll(self,loop):
        for i in range(loop):
            self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
            sleep(randrange(2,5))
    def __del__(self):
        self.driver.close()
    
    def scan_posts(self, group_setting: GroupSettingPost):
        posts = []
        seen = set()
        approve_keywords =  "(" + ")|(".join(group_setting.approve.have_keywords) + ")"
        decline_keywords =  "(" + ")|(".join(group_setting.decline.have_keywords) + ")"
        
        articles = self.driver.find_elements(By.XPATH, FB_XPATH_ARTICLE)
        
        for article in articles:
            try:
                text_content = article.get_property('textContent')
                fbpost = PostContent(article, text_content)
                
                #Get poster name
                if(len(article.find_elements(By.XPATH, FB_XPATH_POSTER)) > 0):
                    fbpost.poster = article.find_element(By.XPATH, FB_XPATH_POSTER).get_property('textContent')
                else:
                    continue
                #share link
                if(len(article.find_elements(By.XPATH,".//div[@class='rdsw9yci']")) > 0):
                    share_link = article.find_element(By.XPATH,".//div[@class='rdsw9yci']").get_property('innerText')
                    fbpost.text_content = share_link
                    if group_setting.decline.reshare:
                        fbpost.action = Action.DECLINE
                        fbpost.keycheck = 'reshare'
                #text+background
                elif(len(article.find_elements(By.XPATH,".//div[@class='hael596l alzwoclg t5n4vrf6 om3e55n1 mfclru0v']")) > 0):
                    backgroud_text = article.find_element(By.XPATH,".//div[@class='hael596l alzwoclg t5n4vrf6 om3e55n1 mfclru0v']").get_property('innerText')
                    fbpost.text_content = backgroud_text
                    check_approve = re.search(approve_keywords, backgroud_text,re.IGNORECASE)
                    if check_approve:
                        fbpost.action = Action.APPROVE
                        fbpost.keycheck = check_approve.group()
                        
                    check_decline = re.search(decline_keywords, backgroud_text,re.IGNORECASE)
                    if check_decline:
                        fbpost.action = Action.DECLINE
                        fbpost.keycheck = check_decline.group()
                # text large font
                elif(len(article.find_elements(By.XPATH,".//div[@class='r227ecj6 gt60zsk1 srn514ro rl78xhln']")) > 0) :
                    large_font = article.find_element(By.XPATH,".//div[@class='r227ecj6 gt60zsk1 srn514ro rl78xhln']").get_property('innerText')
                    fbpost.text_content = large_font
                    check_approve = re.search(approve_keywords, large_font,re.IGNORECASE)
                    if check_approve:
                        fbpost.action = Action.APPROVE
                        fbpost.keycheck = check_approve.group()
                        
                    check_decline = re.search(decline_keywords, large_font,re.IGNORECASE)
                    if check_decline:
                        fbpost.action = Action.DECLINE
                        fbpost.keycheck = check_decline.group()
                #text+ 2images+ font bold
                elif(len(article.find_elements(By.XPATH,".//div[@class='t60zsk1 ez8dtbzv r227ecj6 d2hqwtrz']")) > 0):
                    bold_font = article.find_element(By.XPATH,".//div[@class='t60zsk1 ez8dtbzv r227ecj6 d2hqwtrz']").get_property('innerText')
                    fbpost.text_content = bold_font
                    check_approve = re.search(approve_keywords, bold_font,re.IGNORECASE)
                    if check_approve:
                        fbpost.action = Action.APPROVE
                        fbpost.keycheck = check_approve.group()
                        
                    check_decline = re.search(decline_keywords, bold_font,re.IGNORECASE)
                    if check_decline:
                        fbpost.action = Action.DECLINE
                        fbpost.keycheck = check_decline.group()
                # mục đích : bypass NoSuchElementException
                # kiểm tra trước tìm element nhằm tránh bị exception khi find_element
                elif(len(article.find_elements(By.XPATH,".//div[@data-ad-comet-preview='message']")) > 0) :
                    contents = article.find_element(By.XPATH,".//div[@data-ad-comet-preview='message']").get_property('innerText')
                    fbpost.text_content = contents
                    check_approve = re.search(approve_keywords, contents,re.IGNORECASE)
                    if check_approve:
                        fbpost.action = Action.APPROVE
                        fbpost.keycheck = check_approve.group()
                        
                    check_decline = re.search(decline_keywords, contents,re.IGNORECASE)
                    if check_decline:
                        fbpost.action = Action.DECLINE
                        fbpost.keycheck = check_decline.group()
                else:
                    print("KO Thay")
                    fbpost.keycheck = "ignore"
                
                # check duplicate
                if fbpost.poster is not None:
                    if fbpost.poster not in seen:
                        seen.add(fbpost.poster)
                    else:
                        fbpost.action = Action.DECLINE
                        fbpost.keycheck = 'duplicate'
                # approve now
                print("-----------------------------------------------")
                print("Poster: ", fbpost.poster)
                print("keycheck: ", fbpost.keycheck)
                print("Action: ", fbpost.action)
                print("Content: ", fbpost.text_content)
                if fbpost.action is Action.APPROVE:
                    btn_approve = article.find_element(By.XPATH,FB_XPATH_APPROVE)
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", btn_approve)
                    self.driver.execute_script("arguments[0].click()", btn_approve)
                    sleep(randrange(1,5))
                elif fbpost.action is Action.DECLINE:
                    btn_decline = article.find_element(By.XPATH,FB_XPATH_DECLINE)
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", btn_decline)
                    self.driver.execute_script("arguments[0].click()", btn_decline)
                    sleep(randrange(1,5))
                        
                posts.append(fbpost)
            except Exception as e:
                print("lỗi là: ",e)

        # # check duplicate
        # seen = set()
        # for post in posts:
        #     if post.poster not in seen:
        #         seen.add(post.poster)
        #     else:
        #         post.action = Action.DECLINE
        #         fbpost.keycheck = 'duplicate'
        # approve now
        # for post in posts:
        #     print("-----------------------------------------------")
        #     print("Poster: ", post.poster)
        #     print("Action: ", post.action)
        #     print("Content: ", post.text_content)
        #     try:
        #         if post.action is Action.APPROVE:
        #             print("Action là ", post.action, post.text_content)
        #             btn_approve = post.webelement.find_element(By.XPATH,FB_XPATH_APPROVE)
        #             self.driver.execute_script("arguments[0].scrollIntoView(true);", btn_approve)
        #             self.driver.execute_script("arguments[0].click()", btn_approve)
        #             sleep(randrange(1,5))
        #         elif post.action is Action.DECLINE:
        #             print("Action là ", post.action, post.text_content)
        #             btn_decline = post.webelement.find_element(By.XPATH,FB_XPATH_DECLINE)
        #             self.driver.execute_script("arguments[0].scrollIntoView(true);", btn_decline)
        #             self.driver.execute_script("arguments[0].click()", btn_decline)
        #             sleep(randrange(1,5))
        #     except Exception as e:
        #         print("Approve status: ",e)
        #Update logs
        logs = []
        for post in posts:
            logcontent = utils.LogExport(post.poster, post.text_content, post.keycheck, post.action)
            logs.append(logcontent)
        
        utils.update_logfile(logs, group_setting.types)
        return posts
                    
    def approve_pending_posts(self,group_setting: GroupSettingPost):
        # Get all content posts
        articles = self.driver.find_elements(By.XPATH,"//div[@role='article']")
        normal_posts = []
        share_links = []
        large_fonts = []
        backgroud_texts = []
        bold_fonts = []
        post_image_approved = []
        post_texts_approved = []
        post_contents_approved = []
        anonimous_posts = []
        approve_keywords =  "(" + ")|(".join(group_setting.approve.have_keywords) + ")"
        num = 0
        remain = 0
        posters = []


        for article in articles:
            try:
                #get poster name
                if(len(article.find_elements(By.XPATH,".//a[@role='link']")) > 0):
                    poster = article.find_element(By.XPATH,".//a[@role='link']").get_property('innerText')
                    posters.append(poster)
                #share link
                if(len(article.find_elements(By.XPATH,".//div[@class='rdsw9yci']")) > 0):
                    share_link = article.find_element(By.XPATH,".//div[@class='rdsw9yci']").get_property('innerText')
                    share_links.append(share_link)
                #text+background
                elif(len(article.find_elements(By.XPATH,".//div[@class='hael596l alzwoclg t5n4vrf6 om3e55n1 mfclru0v']")) > 0):
                    backgroud_text = article.find_element(By.XPATH,".//div[@class='hael596l alzwoclg t5n4vrf6 om3e55n1 mfclru0v']").get_property('innerText')
                    backgroud_texts.append(backgroud_text)
                    
                    if re.search(approve_keywords, backgroud_text,re.IGNORECASE):
                        button = article.find_element(By.XPATH,".//input[@type='checkbox']")
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        self.driver.execute_script("arguments[0].click()", button)
                        sleep(randrange(1,5))
        
                        post_image_approved.append(backgroud_text)
                # text large font
                elif(len(article.find_elements(By.XPATH,".//div[@class='r227ecj6 gt60zsk1 srn514ro rl78xhln']")) > 0) :
                    large_font = article.find_element(By.XPATH,".//div[@class='r227ecj6 gt60zsk1 srn514ro rl78xhln']").get_property('innerText')
                    large_fonts.append(large_font)
                    
                    if re.search(approve_keywords, large_font,re.IGNORECASE):
                        button = article.find_element(By.XPATH,".//input[@type='checkbox']")
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        self.driver.execute_script("arguments[0].click()", button)
                        sleep(randrange(1,5))
        
                        post_texts_approved.append(large_font)
                        
                #text+ 2images+ font bold
                elif(len(article.find_elements(By.XPATH,".//div[@class='t60zsk1 ez8dtbzv r227ecj6 d2hqwtrz']")) > 0):
                    bold_font = article.find_element(By.XPATH,".//div[@class='t60zsk1 ez8dtbzv r227ecj6 d2hqwtrz']").get_property('innerText')
                    bold_fonts.append(bold_font)
                # mục đích : bypass NoSuchElementException
                # kiểm tra trước tìm element nhằm tránh bị exception khi find_element
                elif(len(article.find_elements(By.XPATH,".//div[@data-ad-comet-preview='message']")) > 0) :
                    num += 1
                    contents = article.find_element(By.XPATH,".//div[@data-ad-comet-preview='message']").get_property('innerText')
                    normal_posts.append(contents)
                    result = re.search(approve_keywords, contents,re.IGNORECASE)
                    if result :
                        button = article.find_element(By.XPATH,".//input[@type='checkbox']")
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        self.driver.execute_script("arguments[0].click()", button)
                        sleep(randrange(1,5))
        
                        post_contents_approved.append(contents)
                else:
                    remain += 1
                    print("KO Thay")
                    anonimous_posts.append(article.get_property('innerText'))
            except Exception as e:
                print("lỗi là: ",e)
        print("Tổng bài post:",len(articles))
        print("posters: ", len(posters))
        print("num: ", num)
        print("ramin: ", remain)
        print("share_links: ", len(share_links))
        print("backgroud_texts: ", len(backgroud_texts))
        print("large_fonts: ", len(large_fonts))
        print("normal_posts: ", len(normal_posts))

