# -*- coding: utf-8 -*-
import yaml
from yaml import Loader, SafeLoader
from enum import Enum

class Action(Enum):
    NONE = 0
    APPROVE = 1
    DECLINE = 2
    BLOCK = 3
    
class PostContent():
    def __init__(self, webelement, text_content, action = Action.NONE):
        self.webelement = webelement
        self.text_content = text_content
        self.action = action
        
class ApproveConfigPost():
    def __init__(self,have_keywords):
        self.have_keywords = have_keywords
        
class DeclineConfig():
    def __init__(self,livestream, reshare, have_keywords):
        self.livestream = livestream
        self.reshare = reshare
        self.have_keywords = have_keywords
        
class GroupSettingPost():
    def __init__(self, url, member_approve, number_of_posts, 
                 approve: ApproveConfigPost, decline: DeclineConfig):
        self.url = url
        self.member_approve = member_approve
        self.number_of_posts = number_of_posts
        self.approve = approve
        self.decline = decline
        
class Profiles: 
    def __init__(self, uid, pw): 
        self.uid = uid
        self.pw = pw
        
def get_profiles():
    profiles = []
    with open('profiles.txt') as temp_file:
      nicks = [line.rstrip('\n') for line in temp_file]
      for nick in nicks:
          detail = nick.split("|")
          profiles.append(Profiles(detail[0],detail[1]))
    return profiles

def is_duplicate(anylist):
    if type(anylist) != 'list':
        return("Error. Passed parameter is Not a list")
    if len(anylist) != len(set(anylist)):
        return True
    else:
        return False

def get_config():
    with open('config.yaml', 'r', encoding='utf-8') as f:
        data = yaml.load(f, Loader=SafeLoader)
        
    group_settings = []
    for group_setting in data['groupmanagement']:
        url = group_setting['url']
        member_approve = group_setting['member_approve']
        number_of_posts = group_setting['number_of_posts']
        approve = ApproveConfigPost(group_setting['approve_if']['have_keywords'])
        decline = DeclineConfig(group_setting['decline_if']['livestream'],
                                group_setting['decline_if']['reshare'], 
                                group_setting['decline_if']['have_keywords'])
        
        group_settings.append(GroupSettingPost(url, member_approve, number_of_posts, approve, decline))

    
    return group_settings