import pandas as pd
import numpy as np
import re
import sqlite3
import tweepy
import json
from requests_oauthlib import OAuth1Session
import time
#load_ext autoreload
#%load_ext autoreload
import lib
#from notion_client import 

import pandas as pd 


def build_tweet(d,user):
    tweet=d["tweet"]
    if len(user.location)>0:            
        locstr=user.location.replace("日本","")
        locstr=locstr[:8]        
    else:
         locstr=""
            
    if d["pickup"]:     
        nname=7
        if "士" in d["search_word"]:
            if len(locstr)>0:
                locstr+="の"
            ptweet=+user.name[:13]+"@"+user.screen_name+"さん "+tweet
        elif "議" in d["condition_profile"]: 
            if len(locstr)>0:
                locstr+="在住という事になっている議員の"
            else:
                locstr="議員の"
            ptweet=locstr+user.name[:nname]+"@"+user.screen_name[:nname]+" さん "+tweet            
        else:
            ptweet="#"+d["search_word"]+" を利用中の"+locstr+user.name[:nname]+"@"+user.screen_name[:nname]+"さん "+tweet
    else:
        ptweet=tweet            
        
    m=re.search("https?://[\w/:%#\$&\?\(\)~\.=\+\-]+",ptweet)
    #l=len(m.group())
    url=""
    if m.start()>=0:
        url=ptweet[m.start():m.end()]
        
        if m.start()+22>140:
            btweet=ptweet[:min(141,m.start())]
        else:
            btweet=ptweet
    else:
        btweet=ptweet[:140]
    return btweet+url
    print("strlength",len(ptweet))
    '''
    if not m:
        print("not url")
        return ptweet[:150]
    
    if len(ptweet)<=162:
        return ptweet
    return ptweet[:150]
    '''
    #ptweet+=" "+urls



def search_profile(search_query):
    print("search_q",search_query)
    res=tweepy.Cursor(api.search_users, q =search_query,lang = 'ja').items(10)    

    return list(res)


def search(search_query):
    global Ntweet,api
    print(Ntweet,search_query)
    tweet=tweepy.Cursor(api.search, q =search_query+" -filter:retweets",  include_entities = True, tweet_mode = 'extended', lang = 'ja').items(Ntweet)    
    #tweet=api.search(search_query,count=5000)
    texts=[]
    profile=[]
   
    df=[]
    for r in tweet:        
        #print(r)
        #if "RT @" in status.text[0:4]:
        #    continue
            
        df.append(r)    
        texts.append(r.user.name+r.user.description+"  "+r.full_text)
        #df.append({"name":r.user.name,"location":r.user.location,"description":r.user.description})        

    #print(len(texts))
    return df,texts



def run_bot(df):
    global api,ST
    #df.weight[pd.isna(df.weight)]=1
    tmp=[]
    for w in tdf.weight:
        if type(w)==str:
            w=1
        tmp.append(w)
    df.weight=tmp
    
    n=df.weight    
    while True:
        d=df.iloc[np.random.choice(range(df.shape[0]),p=n/np.sum(n))]
        key=d.search_word
        print("wt",key)
  
        if d.tweettype=="tweet":
            tweets=d["tweet"]
            #print(np.random.choice(tweets,1)[0])
            try:
                api.update_status(d.tweet)
            except:
                continue
            #time.sleep(ST)
            print("tweeted")
            
        elif d.tweettype=="search":            
            try:
                tweets,texts=search(key)
            except:
                continue
            retweetWithComment(d,tweets,
                           texts=texts)    
        elif d.tweettype=="search_profile":
            try:
                users=search_profile(key)    
                print("users",len(users))
                if len(users)<=0:
                    continue
                reply(d,np.random.choice(users))            
            except Exception as e:
                print(e)

        else:
            continue
            
        #print(tweets)
        #print("aft",d)
            
        time.sleep(ST)

def insertusertable(r):
    u=r.user
    dd=[u.id,u.screen_name,u.name,search_query,u.description,r.full_text,u.location]    
    cur.execute("insert into users(id,screen_name,name,search_query,description,tweet,location) values(?,?,?,?,?,?,?)",dd)
    
def inserttweet(tw):
    twt=[r.id,r.full_text,r.user.screen_name,r.user.name,r.user.description,search_query,r.created_at,r.user.location,r.retweet_count]
    cur.execute("insert into tweets(id,tweet,screen_name,name,description,search_query,created_at,location,retweet_count) values(?,?,?,?,?,?,?,?,?)",twt)

def reply(d,user):    

    tmp=build_tweet(d,user)
    #tmp=tmp[:140]
    print("message",len(tmp),tmp)
    api.update_status(tmp)

    print("replyed")
    #insertusertable(user)
    #inserttweet(tw)
    #conn.commit()    
 
    

def retweetWithComment(d,tweets,texts=[]):
    global gtest,cur
    
    search_query=d.search_word
    cnt=0
    for i in range(len(tweets)):
        k=np.random.choice(range(len(tweets)),1)[0]
        tw=tweets[k]
        
        print("minret",d.min_retweet,d["min_retweet"])
        try:
            if tw.retweet_count<=d["min_retweet"]:
                continue
        except:
            pass
        user=False
        try:
            user=res.retweeted_status.user
        except:
            user=tw.user
        print(tw.id,tw.user.screen_name)
        print(user.screen_name)
        
        urls="https://twitter.com/"+user.screen_name+"/status/"+str(tw.id)
        
        if len(user.location)>0:            
            locstr=user.location.replace("日本","")
            locstr=locstr[:12]
            locstr=locstr+"の"
        else:
            locstr=""
        
        
        try:
            insertusertable(user)
            #cur.execute("insert into users(screen_name,name,description,location) values(?,?,?,?)",dd)            
            conn.commit()            
        except:
            pass
        try:
            inserttweet(tw)
            conn.commit()  
        except:
            pass
            
        if not(pd.isna(d.condition_profile)) and not(d.condition_profile in user.description):
            continue            
            
        
        tweet=d["tweet"]
        '''
        try:
            tweet=np.random.choice(d["tweet"],1)[0]
        except:
            tweet=d["tweet"]
        '''
        ptweet=""
        if d["pickup"]:     
            nname=15
            if "士" in search_query:
                ptweet=locstr+user.name[:13]+" @"+user.screen_name[:15]+"さん "+tweet
            else:
                ptweet="#"+search_query+" を利用中の"+locstr+user.name[:nname]+" @"+user.screen_name[:nname]+"さん "+tweet
        else:
            ptweet=tweet            
        m=re.search("https?://[\w/:%#\$&\?\(\)~\.=\+\-]+",ptweet)
        #l=len(m.group())
        if m and m.start()+11>140:
            ptweet=ptweet[:m.start()]
        print(ptweet)
        print("strlength",len(ptweet))
        
        ptweet+=" "+urls        
        
        print(ptweet)
        
        try:
            if gtest:
                print(1)
            else:          
                print("bpost")
                api.update_status(ptweet)
                print("posted")
            cnt+=1
        except:
            continue
            
        return

        
gtest=False

Ntweet=50
if gtest:
    ST=1000
    Ntweet=int(50)
else:
    ST=6000
    Ntweet=int(100)


api=lib.getApiInstance()
#discord https://discord.com/invite/HpNBWw7KYt
dbname = 'fukusi.db'
conn = sqlite3.connect(dbname)
cur= conn.cursor()
#cur.execute(
#    'CREATE TABLE users(id INTEGER PRIMARY KEY AUTOINCREMENT,        
#     screen_name STRING unique)')
#tdf=pd.read_csv("/Users/satoshi/Downloads/twitter bo ede84.csv")
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# use creds to create a client to interact with the Google Drive API
scope =['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    '/Users/satoshi/Downloads/mental-aad2c-27954a09b178.json',
                                                        scope)
client = gspread.authorize(creds)

sheet=client.open("障害福祉").sheet1
tdf = sheet.get_all_records()
tdf=pd.DataFrame(tdf)

#tdf=tdf.drop_duplicates()
run_bot(tdf)
conn.close()
           