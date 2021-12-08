""" This is the main module where the website is rendered and most of the main funcationality that isnt data processing is done
Imports:
    from covid_data_handler:
        parse_csv_data see above module for more info
        process_covid_csv_data see above module for more info
        covid_API_requests see above module for more info
        schedule_covid_updates see above module for more info
    
    from covid_news_handling:
        schedule_news_updates see above module for more info
        update_news see above module for more info
        
    from Flask (an imported module hosting websites):
        Flask used to help with hosting and editing website
        render_template used to render the premade template 
        request used to request values from the url
    
    from test_covid_data_handler:
        test_covid_API_request used to test a function
        test_schedule_covid_updates used to test a function
        
    from test_news_data_handling:
        test_news_API_request used to test a function
        test_update_news used to test a function
        test_schedule_news_updates used to a test a function
    
    miscellaneous:
        time used to convert time for scheduling
        covid_news_handing imported 5to use variables from that module that cant be passed via a function
        covid_data_handling imported to use variables fromt that module that cant be passed via a function

Functions:
    test_web_update()
    test_parse_cv_data()
    test_process_covid_csv_data()
    config_read() -> dict
    make_logger(name)
    web_update(updatename:str,webtime:str,repeat:bool,covid:bool,news:bool)
    queue_delete(cancelupdate:str)
    delay_time(webtime:str) -> int
    updates_variations(updatename:str,schedtime:int,covid:bool,news:bool)
    delete_updates(updatename:str,deletetype:str)
    deleted_articles_filter()
    def delete_news_articles(delete_news:str)
    main()
    news_delete()
    
"""
from covid_data_handler import parse_csv_data,process_covid_csv_data,schedule_covid_updates , update_covid
from covid_news_handling import schedule_news_updates , update_news
from flask import Flask , render_template , request
from test_covid_data_handler import test_covid_API_request, test_schedule_covid_updates
from test_news_data_handling import test_news_API_request , test_update_news , test_schedule_news_update
import  time , covid_news_handling,covid_data_handler ,json,logging 

def test_parse_cv_data():
    """used to test parsce cv data function"""
    data = parse_csv_data('nation_2021-10-28.csv')
    assert len(data) == 639

def test_process_covid_csv_data():
    """used to test process covid csv data function"""
    last7days_cases , current_hospital_cases , total_deaths = process_covid_csv_data ( parse_csv_data ('nation_2021-10-28.csv') )
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544

def config_read() -> dict:
    """opens config file"""
    with open("config.json","r") as jsonfile:
        config = json.load(jsonfile)
        return config

def make_logger(name):
    """creates a unqiue logger so the user knows where the logged information is coming from"""
    logger = logging.getLogger(name)
    if (logger.hasHandlers()):
        logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(module)s:%(levelname)s:%(asctime)s:%(message)s')
    file_handler = logging.FileHandler('projectlog.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

def web_update(updatename:str,webtime:str,repeat:bool,covid:bool,news:bool):
    """used to store information from a scheduled update on the website into a dictonary"""
    #stores an schedules information and then deletes the scheduled update so only information is left
    schedtime = delay_time(webtime)
    tempcov = covid_news_handling.s.enter(schedtime,1,update_covid,())
    covid_news_handling.s.cancel(tempcov)
    tempnews = covid_news_handling.s.enter(schedtime,1,update_news,())
    covid_news_handling.s.cancel(tempnews)
    temprepeat= covid_news_handling.s.enter(schedtime,1,delete_updates,(updatename,"auto",))
    covid_news_handling.s.cancel(temprepeat)
    updatedict.append({'title': updatename
                       ,'content' : ("Update at " +webtime + ",repeate update: " + str(repeat) +", Covid update: " + str(covid) +", News update:" + str(news) ) 
                       ,'webtime': webtime
                       ,'schedtime':schedtime
                       ,'repeat': repeat 
                       ,'covidup':covid
                       ,'newsup':news
                       ,'covidloc': tempcov
                       ,'newsloc': tempnews
                       ,'repeatloc': temprepeat})
    #calls the updates varation function to schedule an update
    updates_variations(updatename, schedtime, covid, news)

def test_web_update():
    """used to test if updates can be added and deleted this test actually tests all functions related updates"""
    global updatedict
    #schedules update
    web_update("update", "10:10", True, True, True)
    assert len(updatedict) == 1
    assert len(covid_news_handling.s.queue) == 3
    #deletes update
    queue_delete("update")
    assert len(updatedict) == 0
    assert len(covid_news_handling.s.queue) == 0

def queue_delete(cancelupdate:str):
    """ function that is called when an update is being deleted manualy by deleting updates from the schedule queue"""
    for update in range(len(updatedict)):
        #checks if name from updatedict is the same as name from website url that is being cancelled
        if updatedict[update]['title'] ==  cancelupdate:
            if updatedict[update]['covidup'] is True:
                for queue in range(len(covid_news_handling.s.queue)):
                    if updatedict[update]['covidloc'] == covid_news_handling.s.queue[queue]:
                        covid_news_handling.s.cancel(covid_news_handling.s.queue[queue])
                        logger.info(cancelupdate +" covids schedulled updated deleted")
                        break
            if updatedict[update]['newsup'] is True:
                for queue in range(len(covid_news_handling.s.queue)):
                    if updatedict[update]['newsloc'] == covid_news_handling.s.queue[queue]:
                        covid_news_handling.s.cancel(covid_news_handling.s.queue[queue])
                        logger.info(cancelupdate +" news schedulled updated deleted")
                        break
            for queue in range(len(covid_news_handling.s.queue)):
                if updatedict[update]['repeatloc'] == covid_news_handling.s.queue[queue]:
                    covid_news_handling.s.cancel(covid_news_handling.s.queue[queue])
                    logger.info(cancelupdate +" cancel update deleted")
                    break
            delete_updates(cancelupdate, "manual")
            break

def delay_time(webtime:str) -> int:
    """converts the time in xx:xx for to seconds """
    timesecs = (int(webtime[0:2]) * 3600) + (int(webtime[3:5]) *60)
    currenttime = (time.gmtime().tm_hour*3600) + (time.gmtime().tm_min*60)
    if timesecs >= currenttime:
        schedtime = timesecs - currenttime
    #condition for if the update is scheduled for the next day
    elif timesecs < currenttime:
        schedtime = (86400 - currenttime) + timesecs
    return schedtime

def updates_variations(updatename:str,schedtime:int,covid:bool,news:bool):
    """goes through and schedules the correct updates depending what the user inputted"""
    if covid is True and news is True:
        schedule_covid_updates(schedtime, updatename)
        schedule_news_updates(schedtime,updatename)
        covid_news_handling.s.enter(schedtime,1,delete_updates,(updatename,"auto",))
        logger.info("delete update scheduled")
    elif covid is True and news is False:
        schedule_covid_updates(schedtime, updatename)
        covid_news_handling.s.enter(schedtime,1,delete_updates,(updatename,"auto",))
        logger.info("delete update scheduled")
    elif news is True and covid is False:
        schedule_news_updates(schedtime,updatename)
        covid_news_handling.s.enter(schedtime,1,delete_updates,(updatename,"auto",))
        logger.info("delete update scheduled")
    
def delete_updates(updatename:str,deletetype:str):
    """deleletes updates from the update dictonary"""
    # if the user is maunaly deleting an update 
    if deletetype == "manual":
        for update in range(len(updatedict)):
            if updatedict[update]['title'] == updatename:
                logger.info(updatename +" has been manually deleted from update dictionary")
                del updatedict[update]
                break
        return 
    #if it is automatic delete when a scheduled update has been deleted
    for update in range(len(updatedict)):
        if updatedict[update]['title'] == updatename and updatedict[update]['repeat'] is True:
            web_update(updatedict[update]['title'],updatedict[update]['webtime'],updatedict[update]['repeat'],updatedict[update]['covidup'],updatedict[update]['newsup'])
            logger.info(updatedict[update]['title']+" has been scheduled for "+str(updatedict[update]['webtime'])+" - " + "news= "+str(updatedict[update]['newsup'])+ " ,covid= "+str(updatedict[update]['covidup']) + " ,repeat="+str(updatedict[update]['repeat']))
            del updatedict[update]
            logger.info(updatename +" has been automatically deleted from update dictionary")
            del updatedict[update]
            break
        #if an automatic update is repeated it will reschedule it 
        elif updatedict[update]['title'] == updatename: 
            logger.info(updatename +" has been automatically deleted from update dictionary")
            del updatedict[update]
            break
    
def deleted_articles_filter():
    """filters through updated articles and deletes any that have been deleted"""
    global deleted_news
    global news_articles
    if len(deleted_news) != 0:
        for index, values in enumerate(deleted_news):
            for index_2,values_2 in enumerate(news_articles):
                if deleted_news[index]['title'] == news_articles[index_2]['title']:
                    #deletes articles that have already been deleted
                    del  news_articles[index_2]['title'] 
                    break
                elif index_2 == (len(news_articles)-1):
                    #removes from the delete list if deleted article isnt present in updated news articles
                    del deleted_news[index]['title']

def delete_news_articles(delete_news:str):
    """deletes news articles that the user has interacted with to deleted"""
    global news_articles
    global deleted_news
    for i in range(len(news_articles)-1):
        if news_articles[i]['title'] == delete_news:
            deleted_news.append(news_articles[i])
            del news_articles[i]
    if len(news_articles) != 0:
        if (news_articles[len(news_articles)-1]['title'] == delete_news):
            deleted_news.append(news_articles[len(news_articles)-1])
            del news_articles[len(news_articles)-1]
    


config = config_read()
app = Flask(__name__,static_folder=("./templates/static"))
@app.route('/index') 
def main():
    """the main flask module that renders the website"""
    covid_news_handling.s.run(blocking=False)
    global news_articles
    global covid_data
    global deleted_news
    delete_news = request.args.get('notif')
    news_articles =  covid_news_handling.news_articles
    covid_data = covid_data_handler.covid_data
    covid_data_handler.testcase = test_covid_API_request()
    repeat = False
    covid = False
    news = False
    #if the user schedules an update takes variables from the url
    webtime = request.args.get('update')
    updatename = request.args.get('two')
    delete_news = request.args.get('notif')
    cancelupdate = request.args.get('update_item')
    if request.args.get('repeat') == 'repeat':
        repeat = True
    if request.args.get('covid-data') == 'covid-data':
        covid = True
    if request.args.get('news') == 'news':
        news = True
    if delete_news is not None:     
        delete_news_articles(delete_news)
    if time != "" and (news is True or covid is True):
        logger.info( updatename +" has been scheduled for "+webtime+" - " + "news= "+str(news)+ " ,covid= "+str(covid) + " ,repeat="+str(repeat))
        web_update(updatename,webtime,repeat, covid,news)
    #runs the queue delete module if user trys to delete an update
    if cancelupdate is not None:
        logger.info("cancel request for "+ cancelupdate)
        queue_delete(cancelupdate)
    #renders template for the website
    return render_template('index.html',
                           title = 'Covid Dashboard', 
                           image = 'favicon.jpg',
                           favicon = 'favicon.jpg',
                           location = 'exeter', 
                           local_7day_infections = covid_data['localCases7days'], 
                           nation_location = 'England',
                           national_7day_infections = covid_data['natCases7days'], 
                           hospital_cases = covid_data['hospitalCases'], 
                           deaths_total= covid_data['cumulativeDeaths'], 
                           news_articles = news_articles, 
                           updates = updatedict)

if __name__ == '__main__':
    covid_data_handler.testcase = test_covid_API_request()
    logger = make_logger(__name__)
    #variables used on start up
    covid_data_handler.update_covid()
    covid_news_handling.news_articles =  update_news()
    updatedict = []
    deleted_news = []    
    # run all the tests
    test_parse_cv_data()
    test_process_covid_csv_data()
    test_web_update()
    test_schedule_covid_updates()
    test_news_API_request()
    test_covid_API_request()
    test_schedule_news_update()
    test_update_news()
    app.run()
