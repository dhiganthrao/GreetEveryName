import tweepy
import time

CONSUMER_KEY = '7NId71jMVK1ZLQ5pPp3wIK6YL'
CONSUMER_SECRET = '7FsNm7Q7hz0LuAbs1AsIpaWlibVxur9suInSKbuu9Ilbu88DDr'
ACCESS_KEY = '1244214884683755521-fnMyyltyVhp5Sp0EH0waIRUKodj3rT'
ACCESS_SECRET = 'uXAuA098t9zxPCYwaodmfrymvBqXZFcLFSAwUb5pmjNOw'


auth=tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api=tweepy.API(auth)

f=open("names.txt","r")
name = f.readline()
while name:
    api.update_status("Hello {}! Nice to meet you.".format(name.strip()))
    name=f.readline()
    time.sleep(50)
f.close()




