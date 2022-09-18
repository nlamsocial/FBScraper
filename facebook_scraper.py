# -*- coding: utf-8 -*-
import re
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
    FB_XPATH_DECLINE
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

        approve_keywords =  "(" + ")|(".join(group_setting.approve.have_keywords) + ")"
        decline_keywords =  "(" + ")|(".join(group_setting.decline.have_keywords) + ")"
        
        articles = self.driver.find_elements(By.XPATH, FB_XPATH_ARTICLE)
        
        for article in articles:
            try:
                text_content = article.get_property('textContent')
                fbpost = PostContent(article, text_content)
    
                #share link
                if(len(article.find_elements(By.XPATH,".//div[@class='rdsw9yci']")) > 0):
                    share_link = article.find_element(By.XPATH,".//div[@class='rdsw9yci']").get_property('innerText')
                    fbpost.text_content = share_link
                    if group_setting.decline.reshare:
                        fbpost.action = Action.DECLINE
                #text+background
                elif(len(article.find_elements(By.XPATH,".//div[@class='hael596l alzwoclg t5n4vrf6 om3e55n1 mfclru0v']")) > 0):
                    backgroud_text = article.find_element(By.XPATH,".//div[@class='hael596l alzwoclg t5n4vrf6 om3e55n1 mfclru0v']").get_property('innerText')
                    fbpost.text_content = backgroud_text
                    if re.search(approve_keywords, backgroud_text,re.IGNORECASE):
                        fbpost.action = Action.APPROVE
                    if re.search(decline_keywords, backgroud_text,re.IGNORECASE):
                        fbpost.action = Action.DECLINE
                # text large font
                elif(len(article.find_elements(By.XPATH,".//div[@class='r227ecj6 gt60zsk1 srn514ro rl78xhln']")) > 0) :
                    large_font = article.find_element(By.XPATH,".//div[@class='r227ecj6 gt60zsk1 srn514ro rl78xhln']").get_property('innerText')
                    fbpost.text_content = large_font
                    if re.search(approve_keywords, large_font,re.IGNORECASE):
                        fbpost.action = Action.APPROVE
                    if re.search(decline_keywords, large_font,re.IGNORECASE):
                        fbpost.action = Action.DECLINE
                #text+ 2images+ font bold
                elif(len(article.find_elements(By.XPATH,".//div[@class='t60zsk1 ez8dtbzv r227ecj6 d2hqwtrz']")) > 0):
                    bold_font = article.find_element(By.XPATH,".//div[@class='t60zsk1 ez8dtbzv r227ecj6 d2hqwtrz']").get_property('innerText')
                    fbpost.text_content = bold_font
                    if re.search(approve_keywords, bold_font,re.IGNORECASE):
                        fbpost.action = Action.APPROVE
                    if re.search(decline_keywords, bold_font,re.IGNORECASE):
                        fbpost.action = Action.DECLINE
                # mục đích : bypass NoSuchElementException
                # kiểm tra trước tìm element nhằm tránh bị exception khi find_element
                elif(len(article.find_elements(By.XPATH,".//div[@data-ad-comet-preview='message']")) > 0) :
                    contents = article.find_element(By.XPATH,".//div[@data-ad-comet-preview='message']").get_property('innerText')
                    fbpost.text_content = contents
                    result = re.search(approve_keywords, contents,re.IGNORECASE)
                    if result :
                        fbpost.action = Action.APPROVE
                    if re.search(decline_keywords, contents,re.IGNORECASE):
                        fbpost.action = Action.DECLINE
                else:
                    print("KO Thay")
                    
                #detect duplicate poster
                seen = set()
                posters = []
                if(len(article.find_elements(By.XPATH,".//a[@class='qi72231t nu7423ey n3hqoq4p r86q59rh b3qcqh3k fq87ekyn bdao358l fsf7x5fv rse6dlih s5oniofx m8h3af8h l7ghb35v kjdc1dyq kmwttqpk srn514ro oxkhqvkx rl78xhln nch0832m cr00lzj9 rn8ck1ys s3jn8y49 icdlwmnq cxfqmxzd pbevjfx6 innypi6y']")) > 0):
                    poster = article.find_element(By.XPATH,".//a[@class='qi72231t nu7423ey n3hqoq4p r86q59rh b3qcqh3k fq87ekyn bdao358l fsf7x5fv rse6dlih s5oniofx m8h3af8h l7ghb35v kjdc1dyq kmwttqpk srn514ro oxkhqvkx rl78xhln nch0832m cr00lzj9 rn8ck1ys s3jn8y49 icdlwmnq cxfqmxzd pbevjfx6 innypi6y']").get_property('textContent')
                    if poster not in seen:
                        posters.append(poster)
                        seen.add(poster)
                    else:
                        #get duplicate name
                        print("cone")
                        fbpost.action = Action.DECLINE
                posts.append(fbpost)
            except Exception as e:
                print("lỗi là: ",e)
        
        for post in posts:
            if post.action is Action.APPROVE:
                print("Action là ", post.action, post.text_content)
                btn_approve = post.webelement.find_element(By.XPATH,FB_XPATH_APPROVE)
                self.driver.execute_script("arguments[0].scrollIntoView(true);", btn_approve)
                self.driver.execute_script("arguments[0].click()", btn_approve)
                sleep(randrange(1,5))
            elif post.action is Action.DECLINE:
                print("Action là ", post.action, post.text_content)
                btn_decline = post.webelement.find_element(By.XPATH,FB_XPATH_DECLINE)
                self.driver.execute_script("arguments[0].scrollIntoView(true);", btn_decline)
                self.driver.execute_script("arguments[0].click()", btn_decline)
                sleep(randrange(1,5))

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

