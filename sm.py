from PIL import Image, ImageTk
from contextlib import contextmanager
from random import randint
from datetime import timedelta
from brainyquote import pybrainyquote
from decimal import Decimal
from bs4 import BeautifulSoup
from PySide2.QtWebEngineWidgets import (QWebEngineView as QWebView,QWebEnginePage as QWebPage, QWebEngineSettings as QWebSettings)
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFormLayout,QCalendarWidget, QPushButton)
from PySide2.QtGui import (QPalette, QIcon, QFont, QImage, QPixmap)
from PySide2.QtCore import (QSize, Qt, QTimer)


import sys
import os
import cv2
import fitbit
import random
import threading
import traceback
import requests
import json
import datetime
import time
import locale
import pymysql
import urllib.request
import feedparser
import string
import random
import urllib
import speech_recognition as sr
import imageUpload as imup
import MSFaceAPI as msface


LOCALE_LOCK = threading.Lock()

@contextmanager
def setlocale(name):
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL,name)
        finally:
            locale.setlocale(locale.LC_ALL,saved)

icon_lookup = {
    'clear-day': "assets/sun.jpg",  # clear sky day
    'wind': "assets/Wind.jpg",   #wind
    'cloudy': "assets/Cloud.jpg",  # cloudy day
    'partly-cloudy-day': "assets/PartlySunny.jpg",  # partly cloudy day
    'rain': "assets/Rain.jpg",  # rain day
    'snow': "assets/Snow.png",  # snow day
    'snow-thin': "assets/Snow.jpg",  # sleet day
    'fog': "assets/Haze.jpg",  # fog day
    'clear-night': "assets/Moon.jpg",  # clear sky night
    'partly-cloudy-night': "assets/PartlyMoon.jpg",  # scattered clouds night
    'thunderstorm': "assets/Storm.jpg",  # thunderstorm
    'tornado': "assets/Tornado.jpg",    # tornado
    'hail': "assets/Hail.jpg"  # hail
}
today = datetime.datetime.strftime(datetime.datetime.now(),"%d-%m-%Y")
rec_speech=''
dynamic_frame_w = 600
dynamic_frame_h = 400
current_uid=''
current_emotion=''
current_ufname=''
current_face_emotion=''
window_width=540
window_height=980
window_x=400
window_y=150
ip='<IP ADDRESS>'
ui_locale=''
timeFormat = 12
dateFormat="%b %d, %Y"
weather_api_key = '9d6aba24afe4fb8707068b6e3b41b8da'
aqi_api_key = 'b1a2e6dde44fdb61e9b17237848396d57e3b0e10'
weatherLanguage='en'
weatherUnit='us'
latitude=None
longitude=None
xlarge_text = 48
large_text = 28
medium_text = 18
small_text = 10
font1 = QFont('Helvetica', small_text)
font2 = QFont('Helvetica', medium_text)
font3 = QFont('Helvetica', large_text)
CONSUMER_KEY=''
CONSUMER_SECRET=''
ACCESS_TOKEN=''
REFRESH_TOKEN=''

base_path = 'C:\\Users\\ADMIN\\SM'
dataset_path = os.path.join(base_path,'dataset')
tmp_path = os.path.join(base_path,'tmp')
cloudinary_dataset = 'https://res.cloudinary.com/djdmnzbgx/image/upload/v1550554338/SmartMirror/dataset/'
cloudinary_tmp = 'https://res.cloudinary.com/djdmnzbgx/image/upload/v1550554338/SmartMirror/tmp/'
conn = pymysql.connect("sql12.freesqldatabase.com","sql12283680","upl4JHebEf","sql12283680",3306)
cursor = conn.cursor()

class Clock(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(Clock, self).__init__()
        self.initUI()

    def initUI(self):

        self.vbox= QVBoxLayout()
        
        self.time1 = ''
        self.timeLbl = QLabel('')
        self.timeLbl.setAlignment(Qt.AlignRight)
        self.timeLbl.setFont(font3)
        
        self.day_of_week1 = ''
        self.dayOWLbl = QLabel('')
        self.dayOWLbl.setAlignment(Qt.AlignRight)
        self.dayOWLbl.setFont(font1)
        
        self.date1 = ''
        self.dateLbl = QLabel('')
        self.dateLbl.setAlignment(Qt.AlignRight)
        self.dateLbl.setFont(font1)
        
        self.vbox.addWidget(self.timeLbl)
        self.vbox.addWidget(self.dayOWLbl)
        self.vbox.addWidget(self.dateLbl)
        self.vbox.addStretch(2)
        self.vbox.setSpacing(0)
        self.setContentsMargins(0,0,0,0)
        self.setLayout(self.vbox)
        self.show()
        self.time_update()

    def time_update(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(200)

    def tick(self):
        with setlocale(ui_locale):
            if timeFormat == 12:
                time2 = time.strftime('%I:%M %p') #hour in 12h format
            else:
                time2 = time.strftime('%H:%M') #hour in 24h format

            day_of_week2 = time.strftime('%A')
            date2 = time.strftime(dateFormat)
            # if time string has changed, update it
            if time2 != self.time1:
                self.time1 = time2
                self.timeLbl.setText(time2)
            if day_of_week2 != self.day_of_week1:
                self.day_of_week1 = day_of_week2
                self.dayOWLbl.setText(day_of_week2)
            if date2 != self.date1:
                self.date1 = date2
                self.dateLbl.setText(date2)

class Weather(QWidget):
    def __init__(self,parent,*args,**kwargs):
        super(Weather,self).__init__()
        self.initUI()

    def initUI(self):
        
        self.temperature = ''
        self.temperatureLbl = QLabel('Temperature')
        self.temperatureLbl.setFont(font3)
        
        self.forecast = ''
        self.forecastLbl = QLabel('forecast')
        self.forecastLbl.setFont(font1)
        
        self.location = ''
        self.locationLbl = QLabel('location')
        self.locationLbl.setFont(font1)

        self.currently = ''
        self.currentlyLbl = QLabel('currently')
        self.currentlyLbl.setFont(font2)
        
        self.icon = ''
        self.iconLbl = QLabel()

        self.aLbl=QLabel('AQI')
        self.aLbl.setFont(font1)
        self.aLbl.setAlignment(Qt.AlignLeft)
	
        self.aqi = ''
        self.aqiLbl = QLabel('AQI')
        self.aqiLbl.setFont(font1)
        self.aqiLbl.setAlignment(Qt.AlignLeft)

        self.aqiReaction=''
        self.aqiReactionLbl=QLabel('AQIReaction')
        self.aqiReactionLbl.setFont(font1)
		
        self.vbox= QVBoxLayout()
        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()
        self.vbox1 = QVBoxLayout()
        self.hbox.addWidget(self.temperatureLbl)
        self.hbox.addWidget(self.iconLbl)
        self.hbox.setAlignment(Qt.AlignLeft)
        self.vbox1.addWidget(self.currentlyLbl)
        self.vbox1.addWidget(self.forecastLbl)
        self.vbox1.addWidget(self.locationLbl)
        self.hbox2=QHBoxLayout()
        self.hbox2.addWidget(self.aLbl)
        self.hbox2.addWidget(self.aqiLbl)
        self.hbox2.setAlignment(Qt.AlignLeft)
        self.vbox1.addLayout(self.hbox2)
        self.vbox1.addWidget(self.aqiReactionLbl)
        self.vbox1.addStretch(1)

        self.vbox.addLayout(self.hbox)
        self.vbox.addLayout(self.vbox1)
        self.vbox.setContentsMargins(0,0,0,0)
        self.setLayout(self.vbox)
        self.get_weather()
        self.weather_update()


    def weather_update(self):
        timer = QTimer()
        timer.timeout.connect(self.get_weather)
        timer.start(60000*60)

    def get_ip(self):
        try:
            ip_url = "http://jsonip.com/"
            req = requests.get(ip_url)
            ip_json = json.loads(req.text)
            return ip_json['ip']
        except Exception as e:
            traceback.print_exc()
            return "Error: %s. Cannot get ip." % e

    def get_weather(self):
        try:
            if latitude is None and longitude is None:
                # get location
                location_req_url = " http://api.ipstack.com/%s?access_key=f74bc5e6b1917a4d3c7a375f586df136&output=json&legacy=1" % self.get_ip()
                r = requests.get(location_req_url)
                location_obj = json.loads(r.text)

                lat = location_obj['latitude']
                lon = location_obj['longitude']

                location2 = "%s, %s" % (location_obj['city'], location_obj['region_code'])

                # get weather
                weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (weather_api_key, lat,lon,weatherLanguage,weatherUnit)
                aqi_req_url = "https://api.waqi.info/feed/here/?token=%s" % (aqi_api_key)
            else:
                location2 = ""
                # get weather
                weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (weather_api_key, latitude, longitude, weatherLanguage, weatherUnit)
                aqi_req_url = "https://api.waqi.info/feed/here/?token=%s" % (aqi_api_key)
            r = requests.get(weather_req_url)
            ra=requests.get(aqi_req_url)
            weather_obj = json.loads(r.text)
            aqi_obj = json.loads(ra.text)
            degree_sign= u'\N{DEGREE SIGN}'
            f = int(weather_obj['currently']['temperature'])
            c = int(5*(f-32)/9)
            temperature2 = "%s%s" % (str(c), degree_sign)
            currently2 = weather_obj['currently']['summary']
            forecast2 = weather_obj["hourly"]["summary"]
            aqi2=aqi_obj["data"]["aqi"]

            if aqi2>=0 & aqi2<=50:
                aqiReaction2='You are good to go outside!'
            elif aqi2>=51 & aqi2<=100:
                aqiReaction2='Moderate - but you should limit outdoor exertion!'
            elif aqi2>=101 & aqi2<=150:
                aqiReaction2='Unhealthy for you, if you have respiratory diseases or if you are a child!'
            elif aqi2>=151 & aqi2<=200:
                aqiReaction2='Unhealthy to go outside right now!'
            elif aqi2>=201 & aqi2<=300:
                aqiReaction2='Very Unhealthy to go outside right now. Avoid unless it is an emergency condition!'
            elif aqi2>=301:
                aqiReaction2='Hazardous to go out right now. Avpid in all circumstances!'
            icon_id = weather_obj['currently']['icon']
            icon2 = None

            if icon_id in icon_lookup:
                icon2 = icon_lookup[icon_id]

            if icon2 is not None:
                 if icon2!=self.icon:
                     self.icon=icon2
                     try:
                         image = cv2.imread(icon2, cv2.IMREAD_COLOR);
                         image = cv2.resize(image,(50,50), interpolation = cv2.INTER_CUBIC)
                     except Exception as e:
                        print(str(e))

                     image = QImage(image, image.shape[1], image.shape[0],image.strides[0], QImage.Format_RGB888)
    
                     #pix = pil2qpixmap(image)

                     self.iconLbl.setPixmap(QPixmap.fromImage(image))
            else:
                # remove image
                self.iconLbl.setPixmap(QPixmap(''))
                a=1

            if self.currently != currently2:
                print (self.currently)
                self.currently = currently2
                self.currentlyLbl.setText(currently2)
            if self.forecast != forecast2:
                self.forecast = forecast2
                self.forecastLbl.setText(forecast2)
            if self.temperature != temperature2:
                self.temperature = temperature2
                self.temperatureLbl.setText(temperature2)
            if self.location != location2:
                if location2 == ", ":
                    self.location = "Cannot Pinpoint Location"
                    self.locationLbl.setText("Cannot Pinpoint Location")
                else:
                    self.location = location2
                    self.locationLbl.setText(location2)
            if self.aqi != aqi2:
                self.aqi = aqi2
                self.aqiLbl.setText(str(aqi2))

            if self.aqiReaction != aqiReaction2:
                self.aqiReaction = aqiReaction2
                self.aqiReactionLbl.setText(aqiReaction2)
	    
        except Exception as e:
            traceback.print_exc()
            print ("Error: %s. Cannot get weather." % e)


    @staticmethod
    def convert_kelvin_to_fahrenheit(kelvin_temp):
        return 1.8 * (kelvin_temp - 273) + 32

class ToDo(QWidget):
    def __init__(self,parent,*args,**kwargs):
        super(ToDo,self).__init__()
        self.prev_uid=-1
        self.initUI()

    def initUI(self):
        self.heading=QLabel("To - Do")
        self.heading.setAlignment(Qt.AlignLeft)
        self.heading.setFont(font2)

        self.vbox=QVBoxLayout()
        self.vbox.addWidget(self.heading)
        self.vbox.setAlignment(Qt.AlignTop)

        self.fbox=QFormLayout()
        self.fbox.setSpacing(10)
        self.fbox.setAlignment(Qt.AlignLeft)

        self.eventLbl=QLabel('')
        self.timeLbl=QLabel('')
        self.eventLbl.setFont(font1)
        self.timeLbl.setFont(font1)

        self.fbox.addRow(self.eventLbl,self.timeLbl)

        self.eventNames=[]
        self.eventTime=[]
        self.noEventLbl=QLabel('No Event Today')

        self.update_check()

        self.vbox.addLayout(self.fbox)
        self.setLayout(self.vbox)

    def update_check(self):
        self.timer=QTimer(self)
        self.timer.timeout.connect(self.update_events)
        self.timer.start(500)

    def update_events(self):
        global current_uid
        if self.prev_uid!=current_uid:
            for i in reversed(range(self.fbox.count())): 
                self.fbox.itemAt(i).widget().setParent(None)

            self.prev_uid=current_uid

            if(current_uid!=0):
                print(current_uid)
                sql_command=" SELECT * from event where userid like '%s'" % (current_uid)
                params=(current_uid)
                cursor.execute(sql_command)
                self.obj=cursor.fetchall()
                self.eventNames=[]
                self.eventTime=[]

                for i,event in enumerate(self.obj):
                    self.eventNames.append(event[2])
                    self.eventTime.append(event[4])

                for i,event in enumerate(self.eventNames):
                    eventLbl=QLabel(str(event))
                    timeLbl=QLabel(':'.join(str(self.eventTime[i]).split(':')[:2]))
                    eventLbl.setFont(font1)
                    timeLbl.setFont(font1)
                    self.fbox.addRow(eventLbl,timeLbl)

            if(current_uid==0):
                self.fbox.addRow(self.noEventLbl)

class ToDoMedicines(QWidget):
    def __init__(self,parent,*args,**kwargs):
        super(ToDoMedicines,self).__init__()
        self.prev_uid=-1
        self.initUI()

    def initUI(self):
        self.heading=QLabel("Medicine Reminders")
        self.heading.setAlignment(Qt.AlignLeft)
        self.heading.setFont(font2)

        self.vbox=QVBoxLayout()
        self.vbox.addWidget(self.heading)
        self.vbox.setAlignment(Qt.AlignTop)

        self.fbox=QFormLayout()
        self.fbox.setSpacing(10)
        self.fbox.setAlignment(Qt.AlignLeft)

        self.eventLbl=QLabel('')
        self.timeLbl=QLabel('')
        self.eventLbl.setFont(font1)
        self.timeLbl.setFont(font1)

        self.fbox.addRow(self.eventLbl,self.timeLbl)

        self.eventNames=[]
        self.eventTime=[]
        self.noEventLbl=QLabel('No Medicine Reminders Today')

        self.update_check()

        self.vbox.addLayout(self.fbox)
        self.setLayout(self.vbox)

    def update_check(self):
        self.timer=QTimer(self)
        self.timer.timeout.connect(self.update_events)
        self.timer.start(500)

    def update_events(self):
        global current_uid
        if self.prev_uid!=current_uid:
            for i in reversed(range(self.fbox.count())): 
                self.fbox.itemAt(i).widget().setParent(None)

            self.prev_uid=current_uid

            if(current_uid!=0):
                print(current_uid)
                sql_command=" SELECT * from medicine where userid like '%s'" % (current_uid)
                params=(current_uid)
                cursor.execute(sql_command)
                self.obj=cursor.fetchall()
                self.eventNames=[]
                self.eventTime=[]

                for i,event in enumerate(self.obj):
                    self.eventNames.append(event[2])
                    self.eventTime.append(event[4])

                for i,event in enumerate(self.eventNames):
                    eventLbl=QLabel(str(event))
                    timeLbl=QLabel(':'.join(str(self.eventTime[i]).split(':')[:2]))
                    eventLbl.setFont(font1)
                    timeLbl.setFont(font1)
                    self.fbox.addRow(eventLbl,timeLbl)

            if(current_uid==0):
                self.fbox.addRow(self.noEventLbl)
                
class ToDoDoctor(QWidget):
    def __init__(self,parent,*args,**kwargs):
        super(ToDoDoctor,self).__init__()
        self.prev_uid=-1
        self.initUI()

    def initUI(self):
        self.heading=QLabel("Doctor Appointments")
        self.heading.setAlignment(Qt.AlignLeft)
        self.heading.setFont(font2)

        self.vbox=QVBoxLayout()
        self.vbox.addWidget(self.heading)
        self.vbox.setAlignment(Qt.AlignTop)

        self.fbox=QFormLayout()
        self.fbox.setSpacing(10)
        self.fbox.setAlignment(Qt.AlignLeft)

        self.eventLbl=QLabel('')
        self.timeLbl=QLabel('')
        self.eventLbl.setFont(font1)
        self.timeLbl.setFont(font1)

        self.fbox.addRow(self.eventLbl,self.timeLbl)

        self.eventNames=[]
        self.eventTime=[]
        self.noEventLbl=QLabel('No Doctor Appointments Today')

        self.update_check()

        self.vbox.addLayout(self.fbox)
        self.setLayout(self.vbox)

    def update_check(self):
        self.timer=QTimer(self)
        self.timer.timeout.connect(self.update_events)
        self.timer.start(500)

    def update_events(self):
        global current_uid
        if self.prev_uid!=current_uid:
            for i in reversed(range(self.fbox.count())): 
                self.fbox.itemAt(i).widget().setParent(None)

            self.prev_uid=current_uid

            if(current_uid!=0):
                print(current_uid)
                sql_command=" SELECT * from doc where userid like '%s'" % (current_uid)
                params=(current_uid)
                cursor.execute(sql_command)
                self.obj=cursor.fetchall()
                self.eventNames=[]
                self.eventTime=[]

                for i,event in enumerate(self.obj):
                    self.eventNames.append(event[3])
                    self.eventTime.append(event[5])

                for i,event in enumerate(self.eventNames):
                    eventLbl=QLabel(str(event))
                    timeLbl=QLabel(':'.join(str(self.eventTime[i]).split(':')[:2]))
                    eventLbl.setFont(font1)
                    timeLbl.setFont(font1)
                    self.fbox.addRow(eventLbl,timeLbl)

            if(current_uid==0):
                self.fbox.addRow(self.noEventLbl)

class FitBitData(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(FitBitData, self).__init__()
        self.initUI()
    def initUI(self):
        self.headLbl=QLabel("FITBIT Data")
        self.headLbl.setFont(font1)
        self.headLbl.setAlignment(Qt.AlignRight)
        
        self.todayLbl=QLabel("TODAY")
        self.todayLbl.setFont(font1)
        
        self.waterTxtLbl=QLabel("Water Drank:")
        self.waterTxtLbl.setFont(font1)
        self.waterTxtLbl.setAlignment(Qt.AlignLeft)

        self.waterValLbl=QLabel('VALUE')
        self.waterValLbl.setFont(font1)
        self.waterValLbl.setAlignment(Qt.AlignLeft)

        self.waterUnitLbl=QLabel('ml')
        self.waterUnitLbl.setFont(font1)
        self.waterUnitLbl.setAlignment(Qt.AlignLeft)

        self.waterLeftLbl=QLabel('Need to drink')
        self.waterLeftLbl.setFont(font1)
        self.waterLeftLbl.setAlignment(Qt.AlignLeft)

        self.waterLeftAmtLbl=QLabel('VALUE')
        self.waterLeftAmtLbl.setFont(font1)
        self.waterLeftAmtLbl.setAlignment(Qt.AlignLeft)

        self.waterLeftTxtLbl=QLabel('ml more today!')
        self.waterLeftTxtLbl.setFont(font1)
        self.waterLeftTxtLbl.setAlignment(Qt.AlignLeft)
        
        self.calTxtLbl=QLabel('Calories Burnt Today:')
        self.calTxtLbl.setFont(font1)
        self.calTxtLbl.setAlignment(Qt.AlignLeft)

        self.calValLbl=QLabel('VALUE')
        self.calValLbl.setFont(font1)
        self.calValLbl.setAlignment(Qt.AlignLeft)

        self.bmiTxtLbl=QLabel("Body Mass Index:")
        self.bmiTxtLbl.setFont(font1)
        self.bmiTxtLbl.setAlignment(Qt.AlignLeft)

        self.bmiValLbl=QLabel('VALUE')
        self.bmiValLbl.setFont(font1)
        self.bmiValLbl.setAlignment(Qt.AlignLeft)

        self.bmiReacLbl=QLabel('BMI is...')
        self.bmiReacLbl.setFont(font1)
        self.bmiReacLbl.setAlignment(Qt.AlignLeft)

        self.weekLbl=QLabel("Last 3 days AVERAGE")
        self.weekLbl.setFont(font1)
        
        self.waterTxtWeekLbl=QLabel("Water Drank:")
        self.waterTxtWeekLbl.setFont(font1)
        self.waterTxtWeekLbl.setAlignment(Qt.AlignLeft)

        self.waterValWeekLbl=QLabel('VALUE')
        self.waterValWeekLbl.setFont(font1)
        self.waterValWeekLbl.setAlignment(Qt.AlignLeft)

        self.waterUnitWeekLbl=QLabel('ml')
        self.waterUnitWeekLbl.setFont(font1)
        self.waterUnitWeekLbl.setAlignment(Qt.AlignLeft)
        
        self.calTxtWeekLbl=QLabel('Calories Burnt in the last 3 days:')
        self.calTxtWeekLbl.setFont(font1)
        self.calTxtWeekLbl.setAlignment(Qt.AlignLeft)

        self.calValWeekLbl=QLabel('VALUE')
        self.calValWeekLbl.setFont(font1)
        self.calValWeekLbl.setAlignment(Qt.AlignLeft)

        fbit_client = fitbit.Fitbit(CONSUMER_KEY,CONSUMER_SECRET,access_token=ACCESS_TOKEN,refresh_token=REFRESH_TOKEN)

        today=str(datetime.datetime.now().strftime("%Y-%m-%d"))
        todayminus1=str((datetime.datetime.now()-timedelta(days=1)).strftime("%Y-%m-%d"))
        todayminus2=str((datetime.datetime.now()-timedelta(days=2)).strftime("%Y-%m-%d"))
        todayminus3=str((datetime.datetime.now()-timedelta(days=3)).strftime("%Y-%m-%d"))
        todayminus4=str((datetime.datetime.now()-timedelta(days=4)).strftime("%Y-%m-%d"))
        todayminus5=str((datetime.datetime.now()-timedelta(days=5)).strftime("%Y-%m-%d"))
        todayminus6=str((datetime.datetime.now()-timedelta(days=6)).strftime("%Y-%m-%d"))
        todayminus7=str((datetime.datetime.now()-timedelta(days=7)).strftime("%Y-%m-%d"))
        bodytoday = fbit_client.body(date=today)
        activitiestoday=fbit_client.activities(date=today)
        watertoday=(fbit_client.foods_log_water(date=today))

        bodytodayminus1 = fbit_client.body(date=todayminus1)
        activitiestodayminus1=fbit_client.activities(date=todayminus1)
        watertodayminus1=(fbit_client.foods_log_water(date=todayminus1))

        bodytodayminus2 = fbit_client.body(date=todayminus2)
        activitiestodayminus2=fbit_client.activities(date=todayminus2)
        watertodayminus2=(fbit_client.foods_log_water(date=todayminus2))

        bodytodayminus3 = fbit_client.body(date=todayminus3)
        activitiestodayminus3=fbit_client.activities(date=todayminus3)
        watertodayminus3=(fbit_client.foods_log_water(date=todayminus3))

        bodytodayminus4 = fbit_client.body(date=todayminus4)
        watertodayminus4=(fbit_client.foods_log_water(date=todayminus4))

        bodytodayminus5 = fbit_client.body(date=todayminus5)
        watertodayminus5=(fbit_client.foods_log_water(date=todayminus5))

        bodytodayminus6 = fbit_client.body(date=todayminus6)
        watertodayminus6=(fbit_client.foods_log_water(date=todayminus6))
        caltoday=activitiestoday['summary']['caloriesOut']
        caltodayminus1=activitiestodayminus1['summary']['caloriesOut']
        caltodayminus2=activitiestodayminus2['summary']['caloriesOut']
        caltodayminus3=activitiestodayminus3['summary']['caloriesOut']
        print(caltodayminus3)
        watertoday=watertoday['summary']['water']
        watertodayminus1=watertodayminus1['summary']['water']
        watertodayminus2=watertodayminus2['summary']['water']
        watertodayminus3=watertodayminus3['summary']['water']
        watertodayminus4=watertodayminus4['summary']['water']
        watertodayminus5=watertodayminus5['summary']['water']
        watertodayminus6=watertodayminus6['summary']['water']
        print(watertodayminus6)
        weeklywater=(watertodayminus1+watertodayminus2+watertodayminus3+watertodayminus4+watertodayminus5+watertodayminus6+watertoday)/7
        self.waterValWeekLbl.setText(str(weeklywater))
        weeklycal=(caltoday+caltodayminus1+caltodayminus2+caltodayminus3)/4
        self.calValWeekLbl.setText(str(weeklycal))
        
        bmi=str(bodytoday['body']['bmi'])
        bmiNote=''
        if Decimal(bmi)<Decimal(18.5):
            bmiNote='You are underweight!'
        elif Decimal(bmi)>=Decimal(18.5) and Decimal(bmi)<=Decimal(24.9):
            bmiNote='You are healthy!'
        elif Decimal(bmi)>=Decimal(25) and Decimal(bmi)<=Decimal(29.9):
            bmiNote='You are overweight!'
        elif Decimal(bmi)>=Decimal(30):
            bmiNote='You are obese!'
        self.bmiValLbl.setText(str(bmi))
        self.bmiReacLbl.setText(bmiNote)
        self.calValLbl.setText(str(activitiestoday['summary']['caloriesOut']))
        dispWater=watertoday
        dispWater=dispWater*29.574
        self.waterValLbl.setText(str("{:.2f}".format(dispWater)))
        waterLimit=1893
        if dispWater<1893:
            self.waterLeftAmtLbl.setText(str("{:.2f}".format(waterLimit-dispWater)))
        else:
            self.waterLeftAmtLbl.setText(str(0))
        self.hbox=QHBoxLayout()
        self.hbox.addWidget(self.waterTxtLbl)
        self.hbox.addWidget(self.waterValLbl)
        self.hbox.addWidget(self.waterUnitLbl)
        self.hbox.setAlignment(Qt.AlignLeft)

        self.hbox5=QHBoxLayout()
        self.hbox5.addWidget(self.waterLeftLbl)
        self.hbox5.addWidget(self.waterLeftAmtLbl)
        self.hbox5.addWidget(self.waterLeftTxtLbl)
        self.hbox5.setAlignment(Qt.AlignLeft)

        self.hbox2=QHBoxLayout()
        self.hbox2.addWidget(self.calTxtLbl)
        self.hbox2.addWidget(self.calValLbl)
        self.hbox2.setAlignment(Qt.AlignLeft)

        self.hbox4=QHBoxLayout()
        self.hbox4.addWidget(self.bmiTxtLbl)
        self.hbox4.addWidget(self.bmiValLbl)
        self.hbox4.addWidget(self.bmiReacLbl)
        self.hbox4.setAlignment(Qt.AlignLeft)

        self.hbox6=QHBoxLayout()
        self.hbox6.addWidget(self.weekLbl)
        self.hbox6.setAlignment(Qt.AlignLeft)
        
        self.hbox7=QHBoxLayout()
        self.hbox7.addWidget(self.waterTxtWeekLbl)
        self.hbox7.addWidget(self.waterValWeekLbl)
        self.hbox7.addWidget(self.waterUnitWeekLbl)
        self.hbox7.setAlignment(Qt.AlignLeft)

        self.hbox9=QHBoxLayout()
        self.hbox9.addWidget(self.calTxtWeekLbl)
        self.hbox9.addWidget(self.calValWeekLbl)
        self.hbox9.setAlignment(Qt.AlignLeft)
        
        self.hbox3=QHBoxLayout()
        self.hbox3.addWidget(self.headLbl)
        self.hbox3.setAlignment(Qt.AlignLeft)
        
        self.vbox=QVBoxLayout()
        self.vbox.addLayout(self.hbox3)
        self.vbox.addLayout(self.hbox)
        self.vbox.addLayout(self.hbox5)
        self.vbox.addLayout(self.hbox2)
        self.vbox.addLayout(self.hbox4)
        self.vbox.addLayout(self.hbox6)
        self.vbox.addLayout(self.hbox7)
        self.vbox.addLayout(self.hbox9)
        self.setLayout(self.vbox)

class Message(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(Message, self).__init__()
        self.initUI()

    def initUI(self):
        self.msgLbl=QLabel('Welcome '+current_ufname+'! Have a nice day! You are feeling '+current_face_emotion+' today!')
        self.msgLbl.setAlignment(Qt.AlignCenter)
        self.msgLbl.setFont(font1)
        self.hbox = QHBoxLayout()
        self.fname = ''
        self.hbox.addWidget(self.msgLbl)
        self.setLayout(self.hbox)
        self.update_check()


    def update_check(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_message)
        self.timer.start(500)

    def update_message(self):
        global current_ufname 
        if current_ufname!=self.fname:
            self.msgLbl.setText('Welcome '+current_ufname+'! Have a nice day! You are feeling '+current_face_emotion+' today!')

class HealthTips(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(HealthTips,self).__init__()
        self.initUI()
    def initUI(self):
        self.qlab=QLabel('HealthTips')
        self.qlab.setFont(font2)
        self.qlab.setWordWrap(True)
        self.qlab.setAlignment(Qt.AlignCenter)
        
        self.hbox=QHBoxLayout()
        self.hbox.addWidget(self.qlab)
        self.setLayout(self.hbox)

        self.tips_update()

    def tips_update(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.get_quotes)
        self.timer.start(700)
        
    def get_quotes(self):
        try:
            url = "http://www.brainyquote.com/quotes/topics/topic_fitness.html"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            quotes = []
            for quote in soup.find_all('a', {'title': 'view quote'}):
                quotes.append(quote.contents[0])
            random.shuffle(quotes)
            index=0
            index=randint(0,30)
            result = quotes[:30]
            # print res
            #print(result)
            self.qlab.setText(result[index])
            self.qlab.setFont(font1)
            self.qlab.resize(self.qlab.sizeHint())
            
            #print(data)
            #print self.data_get(self.data_fetch(url))
        except IOError:
            print('no internet')

class SpeechLabel(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(SpeechLabel, self).__init__()
        self.initUI()
    def initUI(self):
        self.intro=QLabel('What could be the cause of these common symptoms?')
        self.intro.setFont(font2)
        self.intro.setAlignment(Qt.AlignCenter)

        self.hboxRow1=QHBoxLayout()
        self.symptom1=QLabel('Abdominal Pain')
        self.cause1=QLabel('Appendicitis, Eating junk, Indigestion, Cramps, Diarrhoea')
        self.cause1.setAlignment(Qt.AlignLeft)
        self.hboxRow1.addWidget(self.symptom1)
        self.hboxRow1.addWidget(self.cause1)

        self.hboxRow2=QHBoxLayout()
        self.symptom2=QLabel('Head Ache')
        self.cause2=QLabel('Hangover, Dehydration,Heat Stroke, Migraine')
        self.cause2.setAlignment(Qt.AlignLeft)

        self.hboxRow2.addWidget(self.symptom2)
        self.hboxRow2.addWidget(self.cause2)

        self.hboxRow3=QHBoxLayout()
        self.symptom3=QLabel('Muscular Pain')
        self.cause3=QLabel('Muscle Cramp, Sprains, Fatigue, Flu')
        self.cause3.setAlignment(Qt.AlignLeft)
        self.hboxRow3.addWidget(self.symptom3)
        self.hboxRow3.addWidget(self.cause3)

        self.hboxRow4=QHBoxLayout()
        self.symptom4=QLabel('Cough')
        self.cause4=QLabel('Asthma, Allergy, TB, Sinusistis, Bronchitis')
        self.cause4.setAlignment(Qt.AlignLeft)
        self.hboxRow4.addWidget(self.symptom4)
        self.hboxRow4.addWidget(self.cause4)

        self.hboxRow5=QHBoxLayout()
        self.symptom5=QLabel('Common Cold')
        self.cause5=QLabel('Virus, Physical contact with someone who has cold')
        self.cause5.setAlignment(Qt.AlignLeft)
        self.hboxRow5.addWidget(self.symptom5)
        self.hboxRow5.addWidget(self.cause5)

        self.hboxRow6=QHBoxLayout()
        self.symptom6=QLabel('Breathlessness')
        self.cause6=QLabel('Lung condition, Heart Condition, Anxiety, Unhealthy Lifestyle')
        self.cause6.setAlignment(Qt.AlignLeft)
        self.hboxRow6.addWidget(self.symptom6)
        self.hboxRow6.addWidget(self.cause6)

        self.hboxRow7=QHBoxLayout()
        self.symptom7=QLabel('Tooth Ache')
        self.cause7=QLabel('Tooth Decay, Cracked Tooth, Gum disease, Sensitive teeth')
        self.cause7.setAlignment(Qt.AlignLeft)
        self.hboxRow7.addWidget(self.symptom7)
        self.hboxRow7.addWidget(self.cause7)

        self.hboxRow8=QHBoxLayout()
        self.symptom8=QLabel('Fever')
        self.cause8=QLabel('Infections, Drugs, Trauma or Injury, Damage to tissue cells')
        self.cause8.setAlignment(Qt.AlignLeft)
        self.hboxRow8.addWidget(self.symptom8)
        self.hboxRow8.addWidget(self.cause8)

        self.hboxRow9=QHBoxLayout()
        self.symptom9=QLabel('Fatigue')
        self.cause9=QLabel('Anaemia, Thyroid, Sleep Disorder')
        self.cause9.setAlignment(Qt.AlignLeft)
        self.hboxRow9.addWidget(self.symptom9)
        self.hboxRow9.addWidget(self.cause9)

        self.hboxRow10=QHBoxLayout()
        self.symptom10=QLabel('Blisters')
        self.cause10=QLabel('Skin being damaged from friction or heat')
        self.cause10.setAlignment(Qt.AlignLeft)
        self.hboxRow10.addWidget(self.symptom10)
        self.hboxRow10.addWidget(self.cause10)

        self.hboxRow11=QHBoxLayout()
        self.symptom11=QLabel('Acne')
        self.cause11=QLabel('Oily Skin, Hormonal Imbalance')
        self.cause11.setAlignment(Qt.AlignLeft)
        self.hboxRow11.addWidget(self.symptom11)
        self.hboxRow11.addWidget(self.cause11)

        self.hboxRow12=QHBoxLayout()
        self.symptom12=QLabel('Vomiting')
        self.cause12=QLabel('Food Poisoning, Gastritis, Ulcer')
        self.cause12.setAlignment(Qt.AlignLeft)
        self.hboxRow12.addWidget(self.symptom12)
        self.hboxRow12.addWidget(self.cause12)

        self.hboxRow13=QHBoxLayout()
        self.symptom13=QLabel('Nausea')
        self.cause13=QLabel('Motion Sickness, Intense Pain, Emotional Stress')
        self.cause13.setAlignment(Qt.AlignLeft)
        self.hboxRow13.addWidget(self.symptom13)
        self.hboxRow13.addWidget(self.cause13)

        self.hboxRow14=QHBoxLayout()
        self.symptom14=QLabel('Back Pain')
        self.cause14=QLabel('Repeated heavy lifting, Sudden awkward movement')
        self.cause14.setAlignment(Qt.AlignLeft)
        self.hboxRow14.addWidget(self.symptom14)
        self.hboxRow14.addWidget(self.cause14)

        self.hboxRow15=QHBoxLayout()
        self.symptom15=QLabel('Itching')
        self.cause15=QLabel('Toxins on the skin, Rare Forms of Skin cancer, Insect Bites')
        self.cause15.setAlignment(Qt.AlignLeft)
        self.hboxRow15.addWidget(self.symptom15)
        self.hboxRow15.addWidget(self.cause15)

        self.vbox=QVBoxLayout()
        self.vbox.addWidget(self.intro)
        self.vbox.addLayout(self.hboxRow1)
        self.vbox.addLayout(self.hboxRow2)
        self.vbox.addLayout(self.hboxRow3)
        self.vbox.addLayout(self.hboxRow4)
        self.vbox.addLayout(self.hboxRow5)
        self.vbox.addLayout(self.hboxRow6)
        self.vbox.addLayout(self.hboxRow7)
        self.vbox.addLayout(self.hboxRow8)
        self.vbox.addLayout(self.hboxRow9)
        self.vbox.addLayout(self.hboxRow10)
        self.vbox.addLayout(self.hboxRow11)
        self.vbox.addLayout(self.hboxRow12)
        self.vbox.addLayout(self.hboxRow13)
        self.vbox.addLayout(self.hboxRow14)
        self.vbox.addLayout(self.hboxRow15)
        self.setLayout(self.vbox)

class Calendar(QWidget):
    def __init__(self,parent,*args,**kwargs):
        super(Calendar,self).__init__()
        self.initUI()
    def initUI(self):
        cal=QCalendarWidget(self)
        cal.setGridVisible(True)
        cal.setFixedWidth(400)
        vbox=QVBoxLayout()
        vbox.addWidget(cal)
        self.setLayout(vbox)
class SmartMirrorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        self.resize(window_width,window_height)
        self.setWindowTitle("Healthcare Smart Mirror")
        self.show()

        pal=QPalette()
        pal.setColor(QPalette.Background,Qt.black)
        pal.setColor(QPalette.Foreground,Qt.white)
        self.setPalette(pal)

        hbox1 = QHBoxLayout()
        clock = Clock(QWidget())
        weather = Weather(QWidget())
        clock.setFixedHeight(200)
        weather.setFixedHeight(200)

        hbox1.addWidget(weather)
        hbox1.addStretch()
        hbox1.addWidget(clock)

        hbox2 = QHBoxLayout()
        fit=FitBitData(QWidget())
        fit.setFixedHeight(280)
        todo= ToDo(QWidget())
        todo.setFixedWidth(200)
        tododoc=ToDoDoctor(QWidget())
        todomed=ToDoMedicines(QWidget())
        cal = Calendar(QWidget())
        hbox2.addWidget(fit)
        hbox2.addStretch(2)
        hbox2.addWidget(todo)
        hbox2.addWidget(tododoc)
        hbox2.addWidget(todomed)
        hbox2.addWidget(cal)
        
        hbox4 = QHBoxLayout()
        speechrecog = SpeechLabel(QWidget())
        hbox4.addWidget(speechrecog)
        hbox4.addStretch(2)

        hbox5 = QHBoxLayout()
        messageBox = Message(QWidget())
        hbox5.addWidget(messageBox)

        hbox6 = QHBoxLayout()
        health = HealthTips(QWidget())
        health.setFixedHeight(150)
        hbox6.addWidget(health)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addStretch(2)
        vbox.addLayout(hbox4)
        vbox.addStretch(2)
        vbox.addLayout(hbox5)
        vbox.addLayout(hbox6)

        self.setLayout(vbox)

def start_qt():
    a=QApplication(sys.argv)
    w=SmartMirrorWindow()
    sys.exit(a.exec_())

# Record Audio
def start_speech_recording(tmp):
    print("Speech recognition started")
    global recognised_speech
    #BING_KEY = "1e53c91557a94b889f7bd32cb08d305f" 
    while True:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say something!")
            r.adjust_for_ambient_noise(source, duration = 1)
            audio = r.listen(source)
        
        try:
            recognised_speech = r.recognize_google(audio).lower()
            print("Google Voice Recognition thinks you said:" + recognised_speech)
            if "hello" in recognised_speech or "wake up" in recognised_speech or "start" in recognised_speech:
                threading.Thread(group=None,target=face_identify(1)).start()
                threading.Thread(group=None,target=start_qt()).start()
        except sr.UnknownValueError:
            print("Google Voice Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Voice Recognition service; {0}".format(e))

def id_generator(size=20, chars=string.ascii_lowercase + string.digits + string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))

def face_identify(tmp):

    global current_uid
    global current_ufname
    global current_face_emotion
    global CONSUMER_KEY
    global CONSUMER_SECRET
    global ACCESS_TOKEN
    global REFRESH_TOKEN
    
    detected_personid = ''
    cascPath = 'C:\\Users\\ADMIN\\SM\\haarcascade_frontalface_default.xml'
    faceCascade = cv2.CascadeClassifier(cascPath)
    
    ramp_frames = 10
    
    print ("Face identification started ..........")
    cam = cv2.VideoCapture(1) 
    try:
        
        while True:
            for i in range(ramp_frames):
                s, im = cam.read()   

            ret,image = cam.read()
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            #cv2.imshow('Recognizing you...', gray)
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            # Draw a rectangle around the faces
            max_area = 0
            mx = 0
            my = 0 
            mh = 0 
            mw = 0
            for (x, y, w, h) in faces:
                #cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                if w*h > max_area:
                    mx = x
                    my = y
                    mh = h
                    mw = w
                    max_area=w*h

            
            if max_area>=15000:        
                image_crop = image[my:my+mh,mx:mx+mw]
                file_name = id_generator()+'.jpg'
                file = os.path.join(tmp_path,file_name)
                cloudinary_url=cloudinary_tmp + '/' + file_name        
                cv2.imwrite(file, image_crop)
                imup.upload_image(file,file_name)
                faceid=msface.face_detect(cloudinary_url)
                faceEmotion=msface.emotion_detect(cloudinary_url)
                if faceEmotion=='happiness':
                    faceEmotion='happy'
                elif faceEmotion=='sadness':
                    faceEmotion='sad'
                elif faceEmotion=='disgust':
                    faceEmotion='disgusting'
                print ("faceId = " + str(faceid))
                print("Emotion detected = " + str(faceEmotion))
                detected_personid = msface.face_identify(faceid)
                print ("detected_personid = " + str(detected_personid))
            
            else:
                continue    
                
            if detected_personid:
                comm = "SELECT * FROM user WHERE personid = '%s'" % detected_personid
                res = cursor.execute(comm)
                res = cursor.fetchone()
                if res:
                    CONSUMER_KEY=res[8]
                    CONSUMER_SECRET=res[9]
                    ACCESS_TOKEN=res[10]
                    REFRESH_TOKEN=res[11]
                    current_uid = res[7]
                    current_ufname = res[1]
                    fname = res[1]
                    current_face_emotion=faceEmotion
                    print ("Welcome "+fname+"!"+"You are feeling "+current_face_emotion+" today!")
                    return

                else:
                    print ("person id not found in database")
            
            else:
                print ("Unknown person found")
                                   
    except Exception as e:
        print ("Errors occured !")
        print (e)   

    cam.release()
    cv2.destroyAllWindows() 

if __name__=='__main__':
    try:
        threading.Thread(group=None,target=start_speech_recording(1)).start()
        #threading.Thread(group=None,target=face_identify(1)).start()
        #threading.Thread(group=None,target=start_qt()).start
    except Exception as e:
        print(e)
        print("Can't start thread!")
    while 1:
        pass
