"""This module processes the covid data from the uk covid 19 API and returns it in dictonary format

Imports:
    Cov19API is the covid 19 API from the uk goverment that the data is imported from
    Covid_news_handling is a module that deals with processing news articles, it is imported so 
    that all scheduled items can be queued in the same queue
    Json imported for the config file
    logging used to write to log file
    
Functions:
    make_logger(name)
    config_read() -> dict
    parse_csv_data(csv_filename) -> str
    process_covid_csv_data(covid_csv_data) -> int
    process_covid_json_data(local_covid_data:dict,nation_covid_data:dict) -> dict
    covid_API_request(location: str,location_type:str) -> dict
    schedule_covid_updates(update_interval:int, update_name:str)
    update_covid()
"""
from uk_covid19 import Cov19API  
import covid_news_handling
import json
import logging

testcase = None

def make_logger(name):
    "creates an individual logger so the user knows which module something written in the logger comes from"
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
    with open("config.json","r") as jsonfile:
        config = json.load(jsonfile)
        return config

def parse_csv_data(csv_filename: str):
    "Opens test csv file and returns it"
    csv_covid_data = open(csv_filename,'r').readlines()
    return csv_covid_data

def process_covid_csv_data(covid_csv_data) -> int:
    """ process the covid data from the csv """
    last_7_days_cases = 0
    current_hospital_cases = (covid_csv_data[1].split(","))[5]
    for lines in range(len(covid_csv_data)):
        if (covid_csv_data[lines+1].split(",")[4]) != '':
            total_deaths = covid_csv_data[lines+1].split(",")[4]
            break
    for i in range(7):
        last_7_days_cases += int((covid_csv_data[i+3].split(",")[6]))
    return last_7_days_cases , int(current_hospital_cases), int(total_deaths)

def process_covid_json_data(local_covid_data:dict,nation_covid_data:dict) -> dict:
    """ Processes both local and national covid data and returns in a dictonary """
    logger.info("process covid json data ran")
    data = {"localCases7days":0,
                  "natCases7days":0, 
                  "cumulativeDeaths":0,
                  "hospitalCases":0
                  }
    for i in range(7):
        data["localCases7days"] += int(local_covid_data['data'][i]['newCasesByPublishDate'])
    for j in range(7):
        data["natCases7days"] += int(nation_covid_data['data'][j]['newCasesByPublishDate'])
    for k in range(len(nation_covid_data['data'])):
        if nation_covid_data['data'][k]['hospitalCases'] is not None:
            data["hospitalCases"] = int(nation_covid_data['data'][k]['hospitalCases'])
            break
    data["cumulativeDeaths"] = int(nation_covid_data['data'][1]['cumDeaths28DaysByDeathDate'])
    return data

def covid_API_request(location: str,location_type:str) -> dict:
    """ Gets both local and national covid data from the covid API in JSON format and runs 
        the process covid json data function and returns covid data """
    global covid_data
    logger.info("covid API request ran")
    area_name = ('areaName='+location)
    area_type = ('areaType='+location_type)
    local_only = [area_type, area_name]
    nat_only = ['areaType=nation','areaName='+config['values']["nationareaname"]]
    cases_and_deaths = {
        "date": "date",
        "areaName": "areaName",
        "newCasesByPublishDate": "newCasesByPublishDate",
        "hospitalCases" : "hospitalCases",
        "cumDeaths28DaysByDeathDate" : "cumDeaths28DaysByDeathDate"
        }
    api_local = Cov19API(filters=local_only, structure=cases_and_deaths)
    api_nat = Cov19API(filters=nat_only, structure=cases_and_deaths)
    data_local = api_local.get_json()
    data_nat = api_nat.get_json()
    covid_data = process_covid_json_data(data_local,data_nat)
    logger.info("covid data updated")
    return covid_data    

def schedule_covid_updates(update_interval:int, update_name:str):
    """ Schedules update that will run the covid API request function """
    logger.info(update_name+" covid API request has been scheduled")
    covid_news_handling.s.enter(update_interval,1,update_covid,())
    
def update_covid():
    "uses a test to see if it will return valid data and prevent the program from crashing"
    global covid_data
    if testcase ==  True:
        covid_API_request(config['values']['location'],"Ltla")
    else:
        logger.warning("Covid API request not working")
        covid_data = {"localCases7days":"error getting data from covid 19 API",
                      "natCases7days":0, 
                      "cumulativeDeaths":0,
                      "hospitalCases":0
                      }

config =  config_read()
    