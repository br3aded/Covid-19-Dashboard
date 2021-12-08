# Covid 19 Dashboard
## Introduction:
This projects goal is to have a customisable covid 19 Dashboard. The dashboard with be hosted on a local website using flask that the user can access. On the dashboard there will be covid stats covering National and Local covid data. There will also be news articles displayed on the side related to covid 19 but can be customized. The user can also schedule updates for the covid and news where they can specifiy a time , what will be updated , if the update is repeating , the name of the update and they can also delete updates once they have been scheduled. 

## Prerequisites:
This project requires:

The flask module that will host the website and render out the template

uk covid 19 api wheren all of the covid data will be pulled from

You will need to get a news api key

## Installation
```bash
pip install flask
```
```bash
pip install uk-covid19
```
For the API key you will need to sign up to this website: https://newsapi.org/
Take the API given to you and put into the config file.
```python
"apikey": "<API key>",
```
## Getting started:
To use the project all you need to do in the command prompt is change your directory to where the project is location and run
```command
python main.py
```
This will appear
```command
 * Serving Flask app 'main' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 ```
From there all you need to do is go on you browser go to http://127.0.0.1:5000/index
From there you can scheduled updates by filling out the form at the bottom or delete news articles by clicking the X in the corner of each one.

## Testing:
Testing is ran automatically when the code is ran but you can also use pytest
Install pytest
```command
pip install -U pytest
```
the go to the directory the code is in and run 
```command
python -m pytest test_covid_data_handler.py
```
or
```command
python -m pytest test_covid_news_handing.py
```
tests for the main.py module are ran internally within that module

## Developer Documentation:
All of the modules are documented within them so you can see what each module and function does.
To change the image on the website got to templates/static/images/ and add an image called favicon in a jpg format
To change what appears on the website go to the config file
```python 
"terms":"Covid COVID-19 coronavirus",
```
If this is changed the news articles will change to stuff releveant to what is being searched
```python 
"location":"Exeter",
```
This will change the location the local covid data is coming from
```python 
"nationareaname":"England",
```
This will change the country the national covid data comes from
## Details
Author - Kelsey Holdate
Distributed under the MIT License. See LICENSE.txt for more information
INDEX.HTMl code provided by Matt Collinson