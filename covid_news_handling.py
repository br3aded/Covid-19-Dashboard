"""This module processes the news from the new api and returns it in a dictonary

Imports:
    time which is used for the scheduling
    sched which is used for the scheduling
    requests which is used to request from the news API.
    json used to load the config file
    logging used to send messages to the log file
    
Functions:
    make_logger(name)
    config_read() -> dict
    news_API_request(covid_terms:str) -> dict
    update_news()
    schedule_news_updates(update_interval:int)
"""
import time
import sched
import requests
import json
import logging

#the scheduler is called here but is also used in other modules
s = sched.scheduler(time.time,time.sleep)

def make_logger(name):
    "creates an individual logger for this module so the user knows where logged information comes from"
    logger = logging.getLogger(name)
    if (logger.hasHandlers()):
        logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(module)s:%(levelname)s:%(asctime)s:%(message)s')
    file_handler = logging.FileHandler('projectlog.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
        
logger = make_logger(__name__)

def config_read() -> dict:
    "opens the config file"
    with open("config.json","r") as jsonfile:
        config = json.load(jsonfile)
        return config

def news_API_request(covid_terms:str) -> dict:
    """Using the argument covid terms this function returns a dictonary of news articles
    by using the newsapi."""
    #creates the dictonary using the news API
    logger.info("news API request ran")
    base_url = "https://newsapi.org/v2/everything?q="
    api_key = config['values']['apikey']
    complete_url = base_url + covid_terms +"&language=en&apiKey=" + api_key
    response = requests.get(complete_url)
    covid_dict = response.json()['articles']
    #iterates through each news article content to have the max descripiton length
    for x,values in enumerate(covid_dict):
        #gets rid of unnessariy data
        del covid_dict[x]['author'], covid_dict[x]['urlToImage'],covid_dict[x]['publishedAt']
        #splits content in sentances and then adds until reaches the character limit
        if len(covid_dict[x]['description']) < 259:
            covid_dict[x]['content'] = covid_dict[x]['description'] + " Read more about: "+ covid_dict[x]['url']
        else:
            descrpt = covid_dict[x]['description'].split(".")
            covid_dict[x]['content'] = ""
            for i in range(len(descrpt) -1):
                if len(covid_dict[x]['content'] + descrpt[i]) < 259:
                    covid_dict[x]['content'] += descrpt[i]
                else:
                    break
            covid_dict[x]['content'] += ". Read more about:" + covid_dict[x]['url']
        del covid_dict[x]['description']
    logger.info("news data updated")
    return covid_dict

def update_news():
    """uses the new API request function to return a dictonary of news articles"""
    news_articles = news_API_request(config['values']['terms'])
    return news_articles

def schedule_news_updates(update_interval:int,update_name:str):
    """schedules an update on the news articles """
    logger.info(update_name +" news update scheduled")
    s.enter(update_interval,1,update_news,())

config = config_read()
