import tweepy
import pandas as pd
import time
import re
import os

file = 'Data/last_seen_id.txt'
# Reading the necessary datasets
covid_hospitals = pd.read_csv("Data/ICMRTestingLabs.csv")
hospitals = pd.read_csv("Data/devfest.csv")
cities = []
cities = covid_hospitals.city.unique()
states = covid_hospitals.state.unique()

# Getting the login credentials pf the Bot
CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")
ACCESS_KEY = os.environ.get("ACCESS_KEY")
ACCESS_SECRET = os.environ.get("ACCESS_SECRET")
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)


def retrieve_last_seen_id(file_name):

    # Opens file containing the number of the
    # last Tweet the bot responded to.
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id


def store_last_seen_id(last_seen_id, file_name):

    # Stores the number of the most recent
    # Tweet responded to in a file.
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return


def find_hospitals(pincode):
    pincode[0].strip()  # Pincode is obtained from the tweet as a
    # list of a string.
    hospital_area = pd.DataFrame()
    hospital_area = hospitals[hospitals["Pincode"] == pincode[0]]
    hosp = hospital_area.reset_index()
    hosp = hosp.drop(['index'], axis=1)
    # Performing formatting on the new dataset
    # so it contains only relevant columns
    total_rows = len(hosp.axes[0])
    name = hosp['Hospital_Name']
    hosp.drop(labels=['Hospital_Name'], axis=1, inplace=True)
    hosp.insert(0, 'Hospital_Name', name)
    # Reordering columns
    # to make the address more readable
    print(total_rows)
    dict = {}
    hosp_list = []
    string = ""
    dict = hosp.to_dict()
    print(dict.keys())
    for i in range(total_rows):
        dict['Hospital_Name'][i] = dict['Hospital_Name'][i] + ', '
        # Formatting the address
        # to look better
        dict['State'][i] = dict['State'][i] + ', '
        dict['District'][i] = dict['District'][i] + ', '
        dict['Location'][i] = dict['Location'][i] + ' '
    hosp_list = []
    for i in range(total_rows):
        string = ''
        for j in dict.keys():
            string = string + dict[j][i]
            hosp_list.append(string)
    return(hosp_list, total_rows)  # Returns the list of
    # hospitals and the number of hospitals


def covid_hospitals_list(state):
    covid_list = pd.DataFrame()
    covid_list = covid_hospitals[covid_hospitals['state'] == state]
    total1 = len(covid_list.axes[0])
    covid_list = covid_list.reset_index()
    covid_list = covid_list.drop(['index'], axis=1)
    pincode = covid_list['pincode']
    lab = covid_list['lab']
    hosp_type = covid_list['type']
    state = covid_list['state']
    city = covid_list['city']
    covid_list.drop(['pincode', 'type', 'lab', 'state', 'city'],
                    axis=1, inplace=True)
    dict = {}
    dict = covid_list.to_dict()
    hosp_list = []
    for i in range(total1):
        string = ''
        for j in dict.keys():
            string = string + str(dict[j][i])
        hosp_list.append(string)
    return(hosp_list, total1)


mentions = api.mentions_timeline()
print(mentions[0].text, mentions[0].id)
store_last_seen_id(mentions[0].id, file)


def reply_to_tweets():
    print('retrieving and replying to tweets...', flush=True)
    last_seen_id = retrieve_last_seen_id(file)
    # NOTE: We need to use tweet_mode='extended' below to show
    # all full tweets (with full_text). Without it, long tweets
    # would be cut off.
    mentions = api.mentions_timeline(last_seen_id, tweet_mode='extended')
    for mention in reversed(mentions):
        if 'corona' in mention.full_text.lower() or 'covid'
        or 'covid-19' in mention.full_text.lower():
            print("COVID tweet found!")
            total_covid = 0
            for i in states:
                if i in mention.full_text:
                    hosp_list, total_covid = covid_hospitals_list(i)
                    break
            if total_covid == 0:
                # Checking if
                # any facilities are present
                api.update_status('@' + mention.user.screen_name + ' ' +
                                  'Uh oh! Unforturnately, we could not' +
                                  'find any hospitals in this state.' +
                                  'Kindly enter another state.', mention.id)
            else:
                for i in range(total_covid):
                    api.update_status('@' + mention.user.screen_name + ' ' +
                                      hosp_list[i], mention.id)
                    time.sleep(1)
        else:
            pin_code = re.findall(r' (\d{6})', mention.full_text)
            # Extracts pincode from Tweet
            print("Found Tweet!")
            if len(pin_code) != 0:
                hosp_list, total = find_hospitals(pin_code)
                if total == 0:
                    # Checks if there are any hospitals in that pincode
                    api.update_status('@' + mention.user.screen_name +
                                      ' ' +
                                      'Uh oh! Unforturnately, we could not' +
                                      'find any hospitals in this pin code.' +
                                      'Kindly enter another pincode.',
                                      mention.id)
                else:
                    for i in range(total):
                        api.update_status('@' + mention.user.screen_name +
                                          ' ' + hosp_list[i], mention.id)
                        time.sleep(1)
                    print(str(mention.id) + ' - ' + mention.full_text,
                          flush=True)
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, file)


while True:
    reply_to_tweets()
    time.sleep(1)
