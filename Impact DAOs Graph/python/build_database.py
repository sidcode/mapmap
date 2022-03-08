import glob
from datetime import datetime
import json
import pandas as pd
import sys
import tweepy

from config import json_datapath, timestamp_fmt
from credentials import consumer_key, consumer_secret


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)



def get_clean_handle(x):
    try:
        x = x.replace(' ','')
        if '/' in x:
            x = x.split('/')[-1]
        if x[0] == '@':
            x = x[1:]
        return x
    except:
        print(f"Invalid or missing handle `{x}`")
        return None

def get_user_data(handle):
    try:
        u = api.get_user(screen_name=handle)
        print(f"Data obtained for user `{handle}`")
        return u._json
    except:
        print(f"Unable to find handle for https://twitter.com/{handle}")
        return None

def add_project_to_database(project_name, handle):
    
    d = datetime.today()
    timestamp = datetime.strftime(d, timestamp_fmt)

    clean_handle = get_clean_handle(handle)
    if clean_handle is None:
        return None

    user_data = get_user_data(clean_handle)
    if user_data is None:
        return None
    
    uid = user_data['id']

    with open(json_datapath, 'r+') as json_file:
        try:
            data = json.load(json_file)
        except:
            data = []
        if data:
            if uid in [dao['UID'] for dao in data]:
                print(f"Twitter `{handle}` already in the database.")
                return None
        
        friend_ids = api.get_friend_ids(user_id=uid)
        follower_ids = [] # api.get_follower_ids(user_id=uid)            
        data.append({
            'UID': uid, 
            'Project Name': project_name, 
            'Twitter': clean_handle, 
            'Updated': timestamp,
            'Meta Data': user_data, 
            'Friend IDs': friend_ids, 
            'Follower IDs': follower_ids
        })

        json_file.seek(0)
        json.dump(data, json_file, indent=4)
    
    print("Database updated:", project_name, handle)


def main():

    try:
        csv_path = sys.argv[1]                   
        csv = pd.read_csv(csv_path)
        csv.dropna(inplace=True)
        list_of_projects = list(zip(csv['Project Name'], csv['Twitter Handle']))
    
    except:
        print("Please enter a csv file with columns Project Name and Twitter Handle\n")
        return None

    for p in list_of_projects:
        add_project_to_database(*p)


if __name__ == "__main__":
    main()