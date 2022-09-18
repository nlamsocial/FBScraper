# -*- coding: utf-8 -*-
import argparse

from facebook_scraper import FacebookScraper
import utils
import pandas as pd
import facebook_scraper
from time import sleep


# with open('profiles.txt') as temp_file:
#   nicks = [line.rstrip('\n') for line in temp_file]
#   for nick in nicks:
#       detail = nick.split("|")
#       print(detail[1])


        
def run():
    parser = argparse.ArgumentParser(description='Facebook Scraper.')
    parser.add_argument('-la', '--listaccounts', action='store_true',help="Show list facebook accounts")
    parser.add_argument('-a', '--account', type=int,help="Select Nick FB Account")
    parser.add_argument('-l', '--login', action='store_true',help="Show list facebook profiles")
    parser.add_argument('-s', '--seeding', action='store_true',help="Show list facebook profiles")
    parser.add_argument('-gm', '--groupmanagement', action='store_true',help="Show list facebook profiles")
    parser.add_argument('-gs', '--groupscheduler', action='store_true',help="Show list facebook profiles")
    parser.add_argument('-pm', '--pagemanagement', action='store_true',help="Show list facebook profiles")
    args = parser.parse_args()
    
    
    profiles = utils.get_profiles()

    if args.account is not None:
        if args.account >= len(profiles):
            print("Account is not valied")
            exit()
    else:
        if(args.groupscheduler or args.groupmanagement or args.pagemanagement):
            print("Please choose the account index")
            exit()
    if(args.listaccounts):
        print("args.account  ",args.account)
        df = pd.DataFrame([t.__dict__ for t in profiles ])
        df.rename(columns={'uid': 'UID','pw': 'PASS'}, inplace=True)
        print(df)
    

    if(args.seeding):
        print("seeding now")
        
    if(args.groupmanagement):
        print("groupmanagement now")
        uid = profiles[args.account].uid
        password = profiles[args.account].pw
        configs = utils.get_config()
        fb = FacebookScraper(uid,password)
        
        for group_setting in configs:
            sleep(10)
            print(group_setting.url)
            fb.open_url(group_setting.url + '/pending_posts?search=&has_selection=false')
            fb.scroll(group_setting.number_of_posts)
            fb.scan_posts(group_setting)

    
    if(args.groupscheduler):
        print("groupscheduler now")

    if(args.pagemanagement):
        print("pagemanagement now")
          
if __name__ == '__main__':
  run()
