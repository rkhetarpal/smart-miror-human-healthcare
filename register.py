import sys
import os
import cv2

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette, QIcon, QFont,QImage,QPixmap
from PyQt5.QtCore import QSize, Qt,QTimer

import locale
import threading
import time
import requests
import json
import traceback
import feedparser
import pymysql

from PIL import Image, ImageTk
from contextlib import contextmanager

import imageUpload as imup
import MSFaceAPI as msface

LOCALE_LOCK = threading.Lock()

window_width =800
window_height = 500
window_x = 400
window_y = 150
ip = '<IP>'
ui_locale = '' # e.g. 'fr_FR' fro French, '' as default
time_format = "hh:mm:ss" # 12 or 24
date_format = "dd-MM-YYYY" # check python doc for strftime() for options
large_text_size = 28
medium_text_size = 18
small_text_size = 10

base_path ='C:\\Users\\ADMIN\\SM'
dataset_path = os.path.join(base_path,'dataset')
tmp_path = os.path.join(base_path,'tmp')
cloudinary_dataset = 'https://res.cloudinary.com/djdmnzbgx/image/upload/v1550554338/SmartMirror/dataset/'
cloudinary_tmp = 'https://res.cloudinary.com/djdmnzbgx/image/upload/v1550554338/SmartMirror/tmp/'

user={
    'uname':'',
    'fname':'',
    'lname':'',
    'email':'',
    'gender':'',
    'dob':'',
    'personid':'',
    'CONSUMER_KEY':'',
    'CONSUMER_SECRET':'',
    'ACCESS_TOKEN':'',
    'REFRESH_TOKEN':''

}

event={
    'userid':'',
    'username':'',
    'title':'',
    'date':'',
    'time':'',

}

medicine={
    'userid':'',
    'username':'',
    'name':'',
    'date':'',
    'time':'',

    }
doc={
    'userid':'',
    'username':'',
    'docname':'',
    'reason':'',
    'date':'',
    'time':'',
    }
conn = pymysql.connect("sql12.freesqldatabase.com","sql12283680","upl4JHebEf","sql12283680",3306)

TABLE_NAME='users'
cursor = conn.cursor()

def query(comm,params):
    cursor.execute(comm,params)
    conn.commit()
    return cursor    

new_user_added = False
new_event_added = False
new_med_added= False
new_docapp_added = False

class SignUpForm(QFrame):
    def __init__(self, parent, *args, **kwargs):
        super(SignUpForm, self).__init__()
        self.initUI()
        self.verified = False


    def initUI(self):

        self.top = QFrame()
        self.bottom = QFrame()
        #self.top.setFrameShape(QFrame.StyledPanel)
        self.top.setObjectName("gframe")
        self.bottom.setObjectName("gframe")
        #self.bottom.setFrameShape(QFrame.StyledPanel)
        self.vbox = QVBoxLayout()
        self.uname = ''
        self.unameLbl = QLabel('User Name')
        self.fnameLbl = QLabel('First Name')
        self.lnameLbl = QLabel('Last Name')
        self.emailLbl = QLabel('Email')
        self.genderLbl = QLabel('Gender')
        self.dobLbl = QLabel('DOB')
        self.fitbitkeyLbl = QLabel('CONSUMER_KEY')
        self.fitbitsecretLbl = QLabel('CONSUMER_SECRET')
        self.fitbitaccessLbl = QLabel('ACCESS_TOKEN')
        self.fitbitrefreshLbl = QLabel('REFRESH_TOKEN')
        
        self.unameEdt = QLineEdit()
        self.fnameEdt = QLineEdit()
        self.lnameEdt = QLineEdit()
        self.genderEdt = QComboBox()
        self.dobEdt = QDateEdit()
        self.dobEdt.setDisplayFormat('dd/MM/yyyy')
        self.emailEdt = QLineEdit()
        self.dobEdt.setCalendarPopup(True)
        self.genderEdt.addItems(["Male", "Female","Other"])
        self.fitbitkeyEdt = QLineEdit()
        self.fitbitsecretEdt = QLineEdit()
        self.fitbitaccessEdt = QLineEdit()
        self.fitbitrefreshEdt = QLineEdit()
        
        self.unameEdt.textChanged.connect(self.__handleTextChanged)
        self.fnameEdt.textChanged.connect(self.__handleTextChanged)
        self.lnameEdt.textChanged.connect(self.__handleTextChanged)
        self.dobEdt.dateChanged.connect(self.__handleTextChanged)
        self.emailEdt.textChanged.connect(self.__handleTextChanged)
        self.genderEdt.currentIndexChanged.connect(self.__handleTextChanged)
        self.fitbitkeyEdt.textChanged.connect(self.__handleTextChanged)
        self.fitbitsecretEdt.textChanged.connect(self.__handleTextChanged)
        self.fitbitaccessEdt.textChanged.connect(self.__handleTextChanged)
        self.fitbitrefreshEdt.textChanged.connect(self.__handleTextChanged)
        
        self.fbox=QFormLayout()
        self.fbox.setContentsMargins(100, 20, 100, 20)
        self.fbox.setSpacing(10)
        self.fbox.addRow(self.unameLbl,self.unameEdt)
        self.fbox.addRow(self.fnameLbl,self.fnameEdt)
        self.fbox.addRow(self.lnameLbl,self.lnameEdt)
        self.fbox.addRow(self.dobLbl,self.dobEdt)
        self.fbox.addRow(self.emailLbl,self.emailEdt)
        self.fbox.addRow(self.genderLbl,self.genderEdt)
        self.fbox.addRow(self.fitbitkeyLbl,self.fitbitkeyEdt)
        self.fbox.addRow(self.fitbitsecretLbl,self.fitbitsecretEdt)
        self.fbox.addRow(self.fitbitaccessLbl,self.fitbitaccessEdt)
        self.fbox.addRow(self.fitbitrefreshLbl,self.fitbitrefreshEdt)
        
        font1 = QFont('Helvetica', small_text_size)
        self.messageLbl = QLabel('')
        self.messageLbl.setFont(font1)
        self.verifyButton = QPushButton('Verify Data', self)
        self.verifyButton.clicked.connect(self.verifyData)
        self.createButton = QPushButton('Create User', self)
        self.createButton.clicked.connect(self.createUser)
        
        self.vbox1 = QVBoxLayout()
        self.hbox1 = QHBoxLayout() 
        self.hbox = QHBoxLayout()
        
        self.hbox.setAlignment(Qt.AlignCenter)
        self.hbox1.setAlignment(Qt.AlignCenter)
        self.vbox1.setAlignment(Qt.AlignCenter)
        
        
        self.hbox.addWidget(self.messageLbl)
        self.hbox1.addStretch(2)
        self.hbox1.addWidget(self.verifyButton)
        self.hbox1.addStretch(1)
        self.hbox1.addWidget(self.createButton)
        self.hbox1.addStretch(2)
        #self.hbox1.addWidget(self.nextButton)
        self.vbox1.addLayout(self.hbox)
        self.vbox1.addLayout(self.hbox1)
        self.hbox1.setSpacing(10)
        #self.vbox1.setContentsMargins(250, 10, 250, 20)

        self.topvBox = QVBoxLayout()
        self.topvBox.setAlignment(Qt.AlignCenter)
        self.topvBox.addLayout(self.fbox)
        self.top.setLayout(self.topvBox)
        self.bottom.setLayout(self.vbox1)
        
        self.splitter1 = QSplitter(Qt.Vertical)
        self.splitter1.addWidget(self.top)
        self.splitter1.addWidget(self.bottom)
        self.splitter1.setSizes([550,150])

        self.vbox.addWidget(self.splitter1)
        self.setLayout(self.vbox)



    def __handleTextChanged(self, text):
        self.verified = False

    def verifyData(self):
        self.verified=False
        global new_user_added
        new_user_added = False
        if (not self.unameEdt.text()) or (not self.fnameEdt.text()) or (not self.lnameEdt.text()) or (not self.emailEdt.text()):
            self.messageLbl.setText('Error: One or more required fields empty! verification failed')
            return
        user['uname']=str(self.unameEdt.text())
        user['fname']=str(self.fnameEdt.text())
        user['lname']=str(self.lnameEdt.text())
        user['email']=str(self.emailEdt.text())
        user['CONSUMER_KEY']=str(self.fitbitkeyEdt.text())
        user['CONSUMER_SECRET']=str(self.fitbitsecretEdt.text())
        user['ACCESS_TOKEN']=str(self.fitbitaccessEdt.text())
        user['REFRESH_TOKEN']=str(self.fitbitrefreshEdt.text())
        #print (user['email'])
        user['dob']=str(self.dobEdt.date().toString('dd-MM-yyyy'))
        user['gender']=str(self.genderEdt.currentText())
        
        sql_command = """SELECT * FROM user WHERE uname = '%s' """ % (user['uname'])
        cursor.execute(sql_command)
        
        if cursor.fetchone():
            self.messageLbl.setText('Error: Username already exist! try something new')
            print ('Username already exist')
            print ('Verification failed')
        else:
            self.messageLbl.setText('Success: Verification Successful!')
            print ('verification successful')
            self.verified = True


    def createUser(self):
        if self.verified == True:
            user['personid'] = msface.create_person(user['uname'],user['fname']+' '+ user['lname'])
            
            if not user['personid']:
                self.messageLbl.setText('Error: Error while creating person! try again')
                return

            self.messageLbl.setText('Success: User created: %s!' % user['uname'])    
            print ("User created ... " + user['uname'])
            print ("PersonID = " + user['personid'])
            
            format_str = """INSERT INTO user (uname,fname,lname,dob,email,gender,personid,CONSUMER_KEY,CONSUMER_SECRET,ACCESS_TOKEN,REFRESH_TOKEN) 
                     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"""
            params = (user['uname'], user['fname'], user['lname'],user['dob'],user['email'],user['gender'],user['personid'],user['CONSUMER_KEY'],user['CONSUMER_SECRET'],user['ACCESS_TOKEN'],user['REFRESH_TOKEN'])         
            cursor.execute(format_str,params)
            self.messageLbl.setText('Success: User added to database sucessfully! Generate Face Dataset now')
            
            print ("User added to database sucessfully!")
            conn.commit()
            global new_user_added
            new_user_added = True
            
        else:
            self.messageLbl.setText('Warning: Verification not done! first verify')
            print ("Verification not done! first verify")
#medicine
class MedicinesForm(QFrame):
    def __init__(self, parent, *args, **kwargs):
        super(MedicinesForm, self).__init__()
        self.initUI()
        self.medverified = False


    def initUI(self):

        self.top = QFrame()
        self.bottom = QFrame()
        #self.top.setFrameShape(QFrame.StyledPanel)
        self.top.setObjectName("gframe")
        self.bottom.setObjectName("gframe")
        #self.bottom.setFrameShape(QFrame.StyledPanel)
        self.vbox = QVBoxLayout()
        #self.uname = ''
        self.usernameLbl = QLabel('Username')
        self.titleLbl = QLabel('Medicine Name')
        self.dateLbl = QLabel('Date')
        self.timeLbl = QLabel('Time')
        #self.genderLbl = QLabel('Gender')
        #self.dobLbl = QLabel('DOB')

        self.usernameEdt = QLineEdit()
        self.titleEdt = QLineEdit()
        self.dateEdt = QDateEdit()
        self.timeEdt = QTimeEdit()
        #self.dobEdt = QDateEdit()
        self.dateEdt.setDisplayFormat('dd/MM/yyyy')
        self.timeEdt.setDisplayFormat('hh:mm:ss')
        #self.emailEdt = QLineEdit()
        #self.dobEdt.setCalendarPopup(True)
        #self.genderEdt.addItems(["Male", "Female","Other"])
        #self.unameEdt.textChanged.connect(self.__handleTextChanged)
        self.usernameEdt.textChanged.connect(self.__handleTextChanged)
        self.titleEdt.textChanged.connect(self.__handleTextChanged)
        self.dateEdt.dateChanged.connect(self.__handleTextChanged)
        self.timeEdt.timeChanged.connect(self.__handleTextChanged)
        #self.genderEdt.currentIndexChanged.connect(self.__handleTextChanged)
        
        self.fbox=QFormLayout()
        self.fbox.setContentsMargins(100, 20, 100, 20)
        self.fbox.setSpacing(10)
        self.fbox.addRow(self.usernameLbl,self.usernameEdt)
        self.fbox.addRow(self.titleLbl,self.titleEdt)
        self.fbox.addRow(self.dateLbl,self.dateEdt)
        self.fbox.addRow(self.timeLbl,self.timeEdt)
        #self.fbox.addRow(self.emailLbl,self.emailEdt)
        #self.fbox.addRow(self.genderLbl,self.genderEdt)
        
        font1 = QFont('Helvetica', small_text_size)
        self.messageLbl = QLabel('')
        self.messageLbl.setFont(font1)
        self.verifyButton = QPushButton('Verify Data', self)
        self.verifyButton.clicked.connect(self.verifyData)
        self.createButton = QPushButton('Create Event', self)
        self.createButton.clicked.connect(self.createEvent)
        
        self.vbox1 = QVBoxLayout()
        self.hbox1 = QHBoxLayout() 
        self.hbox = QHBoxLayout()
        
        self.hbox.setAlignment(Qt.AlignCenter)
        self.hbox1.setAlignment(Qt.AlignCenter)
        self.vbox1.setAlignment(Qt.AlignCenter)
        
        
        self.hbox.addWidget(self.messageLbl)
        self.hbox1.addStretch(2)
        self.hbox1.addWidget(self.verifyButton)
        self.hbox1.addStretch(1)
        self.hbox1.addWidget(self.createButton)
        self.hbox1.addStretch(2)
        #self.hbox1.addWidget(self.nextButton)
        self.vbox1.addLayout(self.hbox)
        self.vbox1.addLayout(self.hbox1)
        self.hbox1.setSpacing(10)
        #self.vbox1.setContentsMargins(250, 10, 250, 20)

        self.topvBox = QVBoxLayout()
        self.topvBox.setAlignment(Qt.AlignCenter)
        self.topvBox.addLayout(self.fbox)
        self.top.setLayout(self.topvBox)
        self.bottom.setLayout(self.vbox1)
        
        self.splitter1 = QSplitter(Qt.Vertical)
        self.splitter1.addWidget(self.top)
        self.splitter1.addWidget(self.bottom)
        self.splitter1.setSizes([550,150])

        self.vbox.addWidget(self.splitter1)
        self.setLayout(self.vbox)



    def __handleTextChanged(self, text):
        self.medverified = False

    def verifyData(self):
        self.medverified=False
        global new_med_added
        new_med_added = False
        if (not self.usernameEdt.text()) or (not self.titleEdt.text()) :
            self.messageLbl.setText('Error: One or more required fields empty! verification failed')
            print ('One or more required fields empty ! fill them all')
            print ('Verification failed')
            return
        medicine['username']=str(self.usernameEdt.text())
        medicine['name']=str(self.titleEdt.text())
        medicine['date']=str(self.dateEdt.date().toString('dd-MM-yyyy'))
        medicine['time']=str(self.timeEdt.text())
        #print user['email']
        #user['dob']=str(self.dobEdt.date().toString('dd-MM-yyyy'))
        #user['gender']=str(self.genderEdt.currentText())
        
        sql_command = """SELECT * FROM user WHERE uname = '%s' """ % (medicine['username'])
        cursor.execute(sql_command)
        
        if (not cursor.fetchone()):
            self.messageLbl.setText('Error: The given userid does not exist! Please register yourself...')
            print ('User id does not exist')
            print ('Verification failed')
        else:
            cursor.execute(sql_command)
            row=[]
            row= cursor.fetchone()
            medicine['userid']=row[7]
            medicine['username']=row[0]
            self.messageLbl.setText('Success: Verification Successful!')
            print ('verification successful')
            self.medverified = True


    def createEvent(self):
        if self.medverified == True:

            self.messageLbl.setText('Success: Reminder added for Medicine: %s!' % medicine['name'])    
            #print ("Event created ... " + medicine['title'])
            #print ("Date and time : " + medicine['date'] + " " + medicine['time'])
            
            format_str = """INSERT IGNORE INTO medicine (username, userid, name, date, time) 
                     VALUES (%s,%s,%s,%s,%s);"""
            params = (medicine['username'],medicine['userid'], medicine['name'], medicine['date'], medicine['time'])         
            cursor.execute(format_str,params)
            self.messageLbl.setText('Success: Medicine Reminder added to database sucessfully!')
            
            print ("Medicine Reminder added to database sucessfully!")
            conn.commit()
            global new_med_added
            new_med_added = True
            
        else:
            self.messageLbl.setText('Warning: Verification not done! first verify')
            print ("Verification not done! first verify")
#doctor
class DoctorForm(QFrame):
    def __init__(self, parent, *args, **kwargs):
        super(DoctorForm, self).__init__()
        self.initUI()
        self.docverified = False

    def initUI(self):

        self.top = QFrame()
        self.bottom = QFrame()
        #self.top.setFrameShape(QFrame.StyledPanel)
        self.top.setObjectName("gframe")
        self.bottom.setObjectName("gframe")
        #self.bottom.setFrameShape(QFrame.StyledPanel)
        self.vbox = QVBoxLayout()
        #self.uname = ''
        self.usernameLbl = QLabel('Username')
        self.nameLbl = QLabel("Doctor's Name")
        self.titleLbl=QLabel("Reason")
        self.dateLbl = QLabel('Date')
        self.timeLbl = QLabel('Time')
        #self.genderLbl = QLabel('Gender')
        #self.dobLbl = QLabel('DOB')

        self.usernameEdt = QLineEdit()
        self.nameEdt=QLineEdit()
        self.titleEdt = QLineEdit()
        self.dateEdt = QDateEdit()
        self.timeEdt = QTimeEdit()
        #self.dobEdt = QDateEdit()
        self.dateEdt.setDisplayFormat('dd/MM/yyyy')
        self.timeEdt.setDisplayFormat('hh:mm:ss')
        #self.emailEdt = QLineEdit()
        #self.dobEdt.setCalendarPopup(True)
        #self.genderEdt.addItems(["Male", "Female","Other"])
        #self.unameEdt.textChanged.connect(self.__handleTextChanged)
        self.usernameEdt.textChanged.connect(self.__handleTextChanged)
        self.nameEdt.textChanged.connect(self.__handleTextChanged)
        self.titleEdt.textChanged.connect(self.__handleTextChanged)
        self.dateEdt.dateChanged.connect(self.__handleTextChanged)
        self.timeEdt.timeChanged.connect(self.__handleTextChanged)
        #self.genderEdt.currentIndexChanged.connect(self.__handleTextChanged)
        
        self.fbox=QFormLayout()
        self.fbox.setContentsMargins(100, 20, 100, 20)
        self.fbox.setSpacing(10)
        self.fbox.addRow(self.usernameLbl,self.usernameEdt)
        self.fbox.addRow(self.nameLbl,self.nameEdt)
        self.fbox.addRow(self.titleLbl,self.titleEdt)
        self.fbox.addRow(self.dateLbl,self.dateEdt)
        self.fbox.addRow(self.timeLbl,self.timeEdt)
        #self.fbox.addRow(self.emailLbl,self.emailEdt)
        #self.fbox.addRow(self.genderLbl,self.genderEdt)
        
        font1 = QFont('Helvetica', small_text_size)
        self.messageLbl = QLabel('')
        self.messageLbl.setFont(font1)
        self.verifyButton = QPushButton('Verify Data', self)
        self.verifyButton.clicked.connect(self.verifyData)
        self.createButton = QPushButton('Add Doctor Appointment', self)
        self.createButton.clicked.connect(self.createEvent)
        
        self.vbox1 = QVBoxLayout()
        self.hbox1 = QHBoxLayout() 
        self.hbox = QHBoxLayout()
        
        self.hbox.setAlignment(Qt.AlignCenter)
        self.hbox1.setAlignment(Qt.AlignCenter)
        self.vbox1.setAlignment(Qt.AlignCenter)
        
        
        self.hbox.addWidget(self.messageLbl)
        self.hbox1.addStretch(2)
        self.hbox1.addWidget(self.verifyButton)
        self.hbox1.addStretch(1)
        self.hbox1.addWidget(self.createButton)
        self.hbox1.addStretch(2)
        #self.hbox1.addWidget(self.nextButton)
        self.vbox1.addLayout(self.hbox)
        self.vbox1.addLayout(self.hbox1)
        self.hbox1.setSpacing(10)
        #self.vbox1.setContentsMargins(250, 10, 250, 20)

        self.topvBox = QVBoxLayout()
        self.topvBox.setAlignment(Qt.AlignCenter)
        self.topvBox.addLayout(self.fbox)
        self.top.setLayout(self.topvBox)
        self.bottom.setLayout(self.vbox1)
        
        self.splitter1 = QSplitter(Qt.Vertical)
        self.splitter1.addWidget(self.top)
        self.splitter1.addWidget(self.bottom)
        self.splitter1.setSizes([550,150])

        self.vbox.addWidget(self.splitter1)
        self.setLayout(self.vbox)


    def __handleTextChanged(self, text):
        self.docverified = False

    def verifyData(self):
        self.docverified=False
        global new_docapp_added
        new_docapp_added = False
        if (not self.usernameEdt.text()) or (not self.titleEdt.text()) or (not self.nameEdt.text()) :
            self.messageLbl.setText('Error: One or more required fields empty! verification failed')
            print ('One or more required fields empty ! fill them all')
            print ('Verification failed')
            return
        doc['username']=str(self.usernameEdt.text())
        doc['docname']=str(self.nameEdt.text())
        doc['reason']=str(self.titleEdt.text())
        doc['date']=str(self.dateEdt.date().toString('dd-MM-yyyy'))
        doc['time']=str(self.timeEdt.text())
        #print user['email']
        #user['dob']=str(self.dobEdt.date().toString('dd-MM-yyyy'))
        #user['gender']=str(self.genderEdt.currentText())
        
        sql_command = """SELECT * FROM user WHERE uname = '%s' """ % (doc['username'])
        cursor.execute(sql_command)
        
        if (not cursor.fetchone()):
            self.messageLbl.setText('Error: The given userid does not exist! Please register yourself...')
            print ('User id does not exist')
            print ('Verification failed')
        else:
            cursor.execute(sql_command)
            row=[]
            row= cursor.fetchone()
            doc['userid']=row[7]
            doc['username']=row[0]
            self.messageLbl.setText('Success: Verification Successful!')
            print ('verification successful')
            self.docverified = True


    def createEvent(self):
        if self.docverified == True:
            self.messageLbl.setText('Success: Doctor Appointment added for: %s!' % doc['reason'])    
            #print ("Event created ... " + doc['reason'])
            #print ("Date and time : " + doc['date'] + " " + doc['time'])
            
            format_str = """INSERT IGNORE INTO doc (username, userid, docname, reason, date, time) 
                     VALUES (%s,%s,%s,%s,%s,%s);"""
            params = (doc['username'],doc['userid'],doc['docname'], doc['reason'], doc['date'], doc['time'])         
            cursor.execute(format_str,params)
            self.messageLbl.setText('Success: Doctor Appointment added to database sucessfully!')
            
            print ("Doctor Appointment added to database sucessfully!")
            conn.commit()
            global new_docapp_added
            new_docapp_added = True
            
        else:
            self.messageLbl.setText('Warning: Verification not done! first verify')
            print ("Verification not done! first verify")
class EventsForm(QFrame):
    def __init__(self, parent, *args, **kwargs):
        super(EventsForm, self).__init__()
        self.initUI()
        self.verified = False


    def initUI(self):

        self.top = QFrame()
        self.bottom = QFrame()
        #self.top.setFrameShape(QFrame.StyledPanel)
        self.top.setObjectName("gframe")
        self.bottom.setObjectName("gframe")
        #self.bottom.setFrameShape(QFrame.StyledPanel)
        self.vbox = QVBoxLayout()
        #self.uname = ''
        self.usernameLbl = QLabel('Username')
        self.titleLbl = QLabel('Event Title')
        self.dateLbl = QLabel('Event Date')
        self.timeLbl = QLabel('Event Time')
        #self.genderLbl = QLabel('Gender')
        #self.dobLbl = QLabel('DOB')

        self.usernameEdt = QLineEdit()
        self.titleEdt = QLineEdit()
        self.dateEdt = QDateEdit()
        self.timeEdt = QTimeEdit()
        #self.dobEdt = QDateEdit()
        self.dateEdt.setDisplayFormat('dd/MM/yyyy')
        self.timeEdt.setDisplayFormat('hh:mm:ss')
        #self.emailEdt = QLineEdit()
        #self.dobEdt.setCalendarPopup(True)
        #self.genderEdt.addItems(["Male", "Female","Other"])
        #self.unameEdt.textChanged.connect(self.__handleTextChanged)
        self.usernameEdt.textChanged.connect(self.__handleTextChanged)
        self.titleEdt.textChanged.connect(self.__handleTextChanged)
        self.dateEdt.dateChanged.connect(self.__handleTextChanged)
        self.timeEdt.timeChanged.connect(self.__handleTextChanged)
        #self.genderEdt.currentIndexChanged.connect(self.__handleTextChanged)
        
        self.fbox=QFormLayout()
        self.fbox.setContentsMargins(100, 20, 100, 20)
        self.fbox.setSpacing(10)
        self.fbox.addRow(self.usernameLbl,self.usernameEdt)
        self.fbox.addRow(self.titleLbl,self.titleEdt)
        self.fbox.addRow(self.dateLbl,self.dateEdt)
        self.fbox.addRow(self.timeLbl,self.timeEdt)
        #self.fbox.addRow(self.emailLbl,self.emailEdt)
        #self.fbox.addRow(self.genderLbl,self.genderEdt)
        
        font1 = QFont('Helvetica', small_text_size)
        self.messageLbl = QLabel('')
        self.messageLbl.setFont(font1)
        self.verifyButton = QPushButton('Verify Data', self)
        self.verifyButton.clicked.connect(self.verifyData)
        self.createButton = QPushButton('Create Event', self)
        self.createButton.clicked.connect(self.createEvent)
        
        self.vbox1 = QVBoxLayout()
        self.hbox1 = QHBoxLayout() 
        self.hbox = QHBoxLayout()
        
        self.hbox.setAlignment(Qt.AlignCenter)
        self.hbox1.setAlignment(Qt.AlignCenter)
        self.vbox1.setAlignment(Qt.AlignCenter)
        
        
        self.hbox.addWidget(self.messageLbl)
        self.hbox1.addStretch(2)
        self.hbox1.addWidget(self.verifyButton)
        self.hbox1.addStretch(1)
        self.hbox1.addWidget(self.createButton)
        self.hbox1.addStretch(2)
        #self.hbox1.addWidget(self.nextButton)
        self.vbox1.addLayout(self.hbox)
        self.vbox1.addLayout(self.hbox1)
        self.hbox1.setSpacing(10)
        #self.vbox1.setContentsMargins(250, 10, 250, 20)

        self.topvBox = QVBoxLayout()
        self.topvBox.setAlignment(Qt.AlignCenter)
        self.topvBox.addLayout(self.fbox)
        self.top.setLayout(self.topvBox)
        self.bottom.setLayout(self.vbox1)
        
        self.splitter1 = QSplitter(Qt.Vertical)
        self.splitter1.addWidget(self.top)
        self.splitter1.addWidget(self.bottom)
        self.splitter1.setSizes([550,150])

        self.vbox.addWidget(self.splitter1)
        self.setLayout(self.vbox)



    def __handleTextChanged(self, text):
        self.verified = False

    def verifyData(self):
        self.verified=False
        global new_event_added
        new_event_added = False
        if (not self.usernameEdt.text()) or (not self.titleEdt.text()) :
            self.messageLbl.setText('Error: One or more required fields empty! verification failed')
            print ('One or more required fields empty ! fill them all')
            print ('Verification failed')
            return
        event['username']=str(self.usernameEdt.text())
        event['title']=str(self.titleEdt.text())
        event['date']=str(self.dateEdt.date().toString('dd-MM-yyyy'))
        event['time']=str(self.timeEdt.text())
        #print user['email']
        #user['dob']=str(self.dobEdt.date().toString('dd-MM-yyyy'))
        #user['gender']=str(self.genderEdt.currentText())
        
        sql_command = """SELECT * FROM user WHERE uname = '%s' """ % (event['username'])
        cursor.execute(sql_command)
        
        if (not cursor.fetchone()):
            self.messageLbl.setText('Error: The given userid does not exist! Please register yourself...')
            print ('User id does not exist')
            print ('Verification failed')
        else:
            cursor.execute(sql_command)
            row=[]
            row= cursor.fetchone()
            event['userid']=row[7]
            event['username']=row[0]
            self.messageLbl.setText('Success: Verification Successful!')
            print ('verification successful')
            self.verified = True


    def createEvent(self):
        if self.verified == True:

            self.messageLbl.setText('Success: Event created: %s!' % event['title'])    
            #print ("Event created ... " + event['title'])
            #print ("Date and time : " + event['date'] + " " + event['time'])
            
            format_str = """INSERT IGNORE INTO event (username, userid, title, date, time) 
                     VALUES (%s,%s,%s,%s,%s);"""
            params = (event['username'],event['userid'], event['title'], event['date'], event['time'])         
            cursor.execute(format_str,params)
            self.messageLbl.setText('Success: Event added to database sucessfully!')
            
            print ("Event added to database sucessfully!")
            conn.commit()
            global new_event_added
            new_event_added = True
            
        else:
            self.messageLbl.setText('Warning: Verification not done! first verify')
            print ("Verification not done! first verify")

class AddDetailsTab(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(AddDetailsTab, self).__init__()
        self.initUI()

    def initUI(self):
        self.hbox = QHBoxLayout()
        self.SignUpFrame = QFrame()
        self.SignUpForm = SignUpForm(self.SignUpFrame)
        self.hbox.addWidget(self.SignUpForm)
        self.vbox  = QVBoxLayout()
        self.vbox.addLayout(self.hbox)
        self.setLayout(self.vbox)

#MEDICINES
class AddMedicineTimings(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(AddMedicineTimings, self).__init__()
        self.initUI()

    def initUI(self):
        self.hbox = QHBoxLayout()
        self.CreateFrame = QFrame()
        self.MedicinesForm = MedicinesForm(self.CreateFrame)
        self.hbox.addWidget(self.MedicinesForm)
        self.vbox  = QVBoxLayout()
        self.vbox.addLayout(self.hbox)
        self.setLayout(self.vbox)
#Doc Appointments
class AddDoctorAppointments(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(AddDoctorAppointments, self).__init__()
        self.initUI()

    def initUI(self):
        self.hbox = QHBoxLayout()
        self.CreateFrame = QFrame()
        self.DoctorForm = DoctorForm(self.CreateFrame)
        self.hbox.addWidget(self.DoctorForm)
        self.vbox  = QVBoxLayout()
        self.vbox.addLayout(self.hbox)
        self.setLayout(self.vbox)

class AddEventsTab(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(AddEventsTab, self).__init__()
        self.initUI()

    def initUI(self):
        self.hbox = QHBoxLayout()
        self.CreateFrame = QFrame()
        self.EventsForm = EventsForm(self.CreateFrame)
        self.hbox.addWidget(self.EventsForm)
        self.vbox  = QVBoxLayout()
        self.vbox.addLayout(self.hbox)
        self.setLayout(self.vbox)

class GenerateDatasetTab(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(GenerateDatasetTab, self).__init__()
        self.capturing=False
        self.video_size = QSize(400, 300)
        self.snapshot_size = QSize(80, 80)
        self.store_dir= os.path.join(dataset_path,user['uname'])
        self.cascPath = 'C:\\Users\\ADMIN\\SM\\haarcascade_frontalface_default.xml'
        #loading the cascade classifiers
        self.faceCascade = cv2.CascadeClassifier(self.cascPath)
        self.snapshotCnt=0
        self.maxSnapshotCnt=8
        self.captureCompleted = False
        self.uploadCompleted = False
        self.trained = False
        self.initUI()


    def initUI(self):
        self.topleft = QFrame()        
        self.imageLabel=QLabel()
        self.imageLabel.setScaledContents(True)
        self.topleft.setObjectName('gframe')
        self.topleft.setContentsMargins(50,10,50,10)
        self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.vbox1 = QVBoxLayout()
        self.vbox1.addWidget(self.imageLabel)
        self.topleft.setLayout(self.vbox1)

        self.topright = QFrame()
        self.snpGrid = QGridLayout()
        
        self.snpGrid.setSpacing(2)
        self.snpGrid.setContentsMargins(2,2,2,2)
        
        self.topright.setLayout(self.snpGrid)
        self.hbox = QHBoxLayout()
        self.startButton = QPushButton('Start')
        self.stopButton = QPushButton('Stop')
        self.takeSnapshotButton = QPushButton('Take Snapshot')
        self.uploadDatasetButton = QPushButton('Upload Dataset')
        self.trainModelButton = QPushButton('Train Model')
        self.messageLbl = QLabel('')
        font1 = QFont('Helvetica', small_text_size)
        self.messageLbl.setFont(font1)

        self.startButton.clicked.connect(self.startCapture)
        self.stopButton.clicked.connect(self.stopCapture)
        self.takeSnapshotButton.clicked.connect(self.takeSnapshot)
        self.uploadDatasetButton.clicked.connect(self.uploadDataset)
        self.trainModelButton.clicked.connect(self.trainModel)

        self.hbox.addWidget(self.startButton)
        self.hbox.addWidget(self.stopButton)
        self.hbox.addWidget(self.takeSnapshotButton)
        self.hbox.addWidget(self.uploadDatasetButton)
        self.hbox.addWidget(self.trainModelButton)
        
        self.mhbox = QHBoxLayout()
        self.mhbox.setAlignment(Qt.AlignCenter)
        self.mhbox.addWidget(self.messageLbl)

        self.bvbox = QVBoxLayout()
        self.bvbox.addLayout(self.mhbox)
        self.bvbox.addLayout(self.hbox)
        self.bvbox.setSpacing(10)
        
        self.bottom = QFrame()
        self.bottom.setLayout(self.bvbox)
        self.bottom.setObjectName("gframe")

        self.splitter1 = QSplitter(Qt.Horizontal)
        self.splitter1.addWidget(self.topleft)
        self.splitter1.addWidget(self.topright)
        self.splitter1.setSizes([5,2])

        self.splitter2 = QSplitter(Qt.Vertical)
        self.splitter2.addWidget(self.splitter1)
        self.splitter2.addWidget(self.bottom)
        self.splitter2.setSizes([375,75])
        self.hbox1=QHBoxLayout()
        self.hbox1.addWidget(self.splitter2)
        self.setLayout(self.hbox1)
        self.initGrid()

    def initDir(self):
        self.store_dir= os.path.join(dataset_path,user['uname'])
        if os.path.isdir(self.store_dir)==False:
            try:
                original_umask = os.umask(0)
                os.makedirs(self.store_dir)
            finally:
                os.umask(original_umask)

    def initGrid(self):
        range_x=(self.maxSnapshotCnt+1)/2
        self.snpLabels =[]
        for i in range(self.maxSnapshotCnt):
            self.snpLabels.append(QLabel())
            self.snpLabels[i].setScaledContents(True)
            self.snpLabels[i].setFixedSize(self.snapshot_size)
            self.snpLabels[i].setObjectName("gframe")

        range_y =2
        pos = [(i,j) for i in range(int(range_x)) for j in range(range_y)]
        
        for p, lbl in zip(pos, self.snpLabels):
            self.snpGrid.addWidget(lbl,*p)


    def display_video_stream(self):
        #print("inside disp func...capturing frames")
        r , frame = self.capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow('Gray video frame',gray)
        #detecting faces
        faces = self.faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(40, 40),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        #drawing rectangles on faces
        for (x, y, w, h) in faces:
            #image,pt1,pt2,color,thickness
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.flip(frame, 1)
        image = QImage(frame, frame.shape[1], frame.shape[0],frame.strides[0], QImage.Format_RGB888)
        self.imageLabel.setPixmap(QPixmap.fromImage(image))
        print("leaving func")


    def startCapture(self):
        global new_user_added
        if new_user_added == True:
            self.initDir()
            self.capturing = True
            self.capture = cv2.VideoCapture(1)
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_size.width())
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_size.height())
            self.timer = QtCore.QTimer()
            print("disp func calling...")
            self.timer.timeout.connect(self.display_video_stream)
            self.timer.start()

        else:
            self.messageLbl.setText('Warning: First create new user')

    def stopCapture(self):
        #print "pressed End"
        if self.capturing == True:
            self.capturing = False
            self.capture.release()
            self.timer.stop()
            cv2.destroyAllWindows()

    def takeSnapshot(self):

        if self.capturing == False:
            self.messageLbl.setText('Warning: Start the camera')
            return

        if self.snapshotCnt == self.maxSnapshotCnt:
            self.messageLbl.setText('Warning: All snapshots taken, no need to take more now!')
            return                 
        
        if (self.capturing == True)  and (self.snapshotCnt < self.maxSnapshotCnt):
            try:
                print("Ready to take snaps...")
                r , frame = self.capture.read()
                frame = cv2.flip(frame, 1)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.faceCascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(40, 40),
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
                if len(faces)==0:
                    return
                max_area = 0
                mx = 0
                my = 0 
                mh = 0 
                mw = 0
                for (x, y, w, h) in faces:
                    if w*h > max_area:
                        mx = x
                        my = y
                        mh = h
                        mw = w
                        max_area=w*h    
                
                image_crop = frame[my:my+mh,mx:mx+mw]
                self.snapshotCnt=self.snapshotCnt+1
                self.messageLbl.setText('Process: Total snapshots captured: %d (Remaining: %d)' % (self.snapshotCnt,self.maxSnapshotCnt-self.snapshotCnt))
                file_name = 'img_%d.jpg'% (self.snapshotCnt)
                file = os.path.join(self.store_dir,file_name)
                cv2.imwrite(file, image_crop)
                self.snpLabels[self.snapshotCnt-1].setPixmap(QPixmap(file))

            except Exception as e:
                self.messageLbl.setText('Error: Snapshot capturing failed')
                print ("Snapshot capturing failed...\n Errors:")
                print (e)

        if(self.snapshotCnt == self.maxSnapshotCnt):
            self.captureCompleted=True
            self.stopCapture()


    def uploadDataset(self):
        if self.capturing == True:
            self.stopCapture()

        if self.captureCompleted == False:
            self.messageLbl.setText('Warning: Take required no of snapshot for uploading dataset!')
            return
        i=1
        personName = user['uname']
        if not personName:
            self.messageLbl.setText('Error: Username empty!')
            print ('username empty!')
            self.messageLbl.setText('Error: Upload dataset failed!')
            print ('upload dataset failed!')
            return

        for file in os.listdir(self.store_dir):
            file_path=os.path.join(self.store_dir,file)
            try:
                self.messageLbl.setText('Process: Uploading image... %d' %i)
                print ('Uploading... %d' % i)
                imup.upload_person_image(file_path,file,user['uname'])
                print ('Uploaded... %d' % i)
                self.messageLbl.setText('Success: Uploaded image... %d' %i)
                i=i+1
            except Exception as e:
                print("Error: %s" % e.message)

        if i==1:
            self.messageLbl.setText('Error: Some error while uploading to cloudnary, Please try later!')
            print ('Some error while uploading to cloudnary, Please try later!')
            return

        try:    
            cloudinary_dir= cloudinary_dataset+'/'+personName+'/'
            for i in range(1,self.maxSnapshotCnt+1):
                image_url=cloudinary_dir+'img_%d.jpg' % i
                self.messageLbl.setText('Process: Adding face... %d' %i)
                print ('Adding face... %d'%i)
                msface.add_person_face(user['personid'],image_url)
                print ('Added face... %d'%i)
                self.messageLbl.setText('Success: Added face... %d' %i)
            
            print ("Dataset Uploaded Sucessfuly!")    
            self.messageLbl.setText('Success: Dataset Uploaded Sucessfuly!')
            self.uploadCompleted = True    
        except Exception as e:
                self.messageLbl.setText('Error: Unknown Error!')
                print("Error: \n")
                print (e)

    def trainModel(self):
            self.messageLbl.setText('Process: Training Started ')
            print('Training Started...')
            msface.train()
            print('Training Completed...')
            self.messageLbl.setText('Success: Training Completed Successfully')

class MainWindow:

    def __init__(self): 
        self.qt = QTabWidget()
        self.qt.setGeometry(window_x, window_y, window_width, window_height)
        self.pal=QPalette()
        self.pal.setColor(QPalette.Background,Qt.white)
        self.pal.setColor(QPalette.Foreground,Qt.black)
        self.qt.setPalette(self.pal)
    
        self.tab1 = QWidget()
        self.DetailsTab=AddDetailsTab(self.tab1)
        self.qt.addTab(self.DetailsTab,"Create User")
    
        self.tab2 = QWidget()
        self.DatasetTab=GenerateDatasetTab(self.tab2)
        self.qt.addTab(self.DatasetTab,"Generate Face Dataset")

        self.tab4 = QWidget()
        self.EventsTab=AddEventsTab(self.tab4)
        self.qt.addTab(self.EventsTab,"Create Event")

        self.tab5 = QWidget()
        self.MedicineTab=AddMedicineTimings(self.tab5)
        self.qt.addTab(self.MedicineTab,"Add Medicine Reminders")

        self.tab6 = QWidget()
        self.DocTab=AddDoctorAppointments(self.tab6)
        self.qt.addTab(self.DocTab,'Add Doctor Appointments')

        self.qt.show()
        self.qt.setStyleSheet("#gframe {border-radius:5px;border:1px solid #a5a5a5}")

        
if __name__ == '__main__':
    a = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(a.exec_())
