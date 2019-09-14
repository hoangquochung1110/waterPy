# -*- coding: utf-8 -*-
from owm import *
from flask import Flask
import time,datetime, requests, json, sqlite3,math, calendar, threading
import smtplib
#from datetime import datetime
import RPi.GPIO as GPIO

#Khai báo biến dùng cho sqlite3
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

#Khai báo biến toàn cục
soilMoisture = 0
threshold = 20
noWaterDays = 0 # số ngày chưa tưới cây
#water_time = datetime.datetime(2018,1,1,0,0,0,0) # thời điểm tưới cây, mặc định ban đầu 2018/1/1

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587 # typically 25, 465 or 587
SMTP_USER = "arsenalforeversince2007@gmail.com"
SMTP_PASS = "Jackwilshere1"
MAIL_FROM = "Quoc Hung"
MAIL_TO = "arsenalforeversince2007@gmail.com"

#khai báo các chân kết nối SPI
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
CLK = 18
DOUT = 23
DIN = 24
CS = 25
LED = 26
GPIO.setup(CLK,  GPIO.OUT)
GPIO.setup(DOUT, GPIO.IN)
GPIO.setup(DIN,  GPIO.OUT)
GPIO.setup(CS,   GPIO.OUT)
GPIO.setup(LED, GPIO.OUT)
#Khai báo kết nối gọi API
API = "3f2f6c5a4daa43b4d377e62edb6a0a01"
city = "Thanh pho Ho Chi Minh"
base_url = "http://api.openweathermap.org/data/2.5/weather?"
complete_url = base_url + "appid=" + API + "&q=" + city + "&units=metric"


def setUpWaterTime():
    watertime = 0
    content = cursor.execute("SELECT unix_time  FROM Schedule")

    for item in content.fetchall():
        watertime = item[0]

    watertime = datetime.datetime.fromtimestamp(watertime)
    return watertime

def sendMail(subject, body):
    message = "From: "+MAIL_FROM+"\r\nTo: "+MAIL_TO+"\r\n"+\
              "Subject: "+subject+"\r\n\r\n"+body
    mailServer = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    if SMTP_USER != "":
        mailServer.login(SMTP_USER, SMTP_PASS)
    mailServer.sendmail(MAIL_FROM, MAIL_TO, message)
    mailServer.close()


def saveSoilMoisture(_soilMoisture):
	t = datetime.datetime.now()
	cursor.execute('INSERT INTO readings(SoilMoisture,Datetime) VALUES(?,?)', (_soilMoisture,t.strftime('%Y-%m-%d %H:%M:%S')))
	conn.commit()

def saveCurrentWeather(a_list):  
	t = datetime.datetime.now()
        cursor.execute('INSERT INTO Weather(Temperature, Humidity, Status, Description, Datetime) VALUES(?,?,?,?,?)', (a_list[0],a_list[1],a_list[2],a_list[3],t.strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
def watering(SM, weather_list):
    GPIO.output(LED, GPIO.HIGH) 
	print "LED on"
	time.sleep(2)
	print "LED off"
	GPIO.output(LED, GPIO.LOW)
	#global water_time
	water_time = datetime.datetime.now()  
        unix_t = time.time()
	cursor.execute('UPDATE Schedule SET datetime = ?, unix_time = ? WHERE id = 1 ', ( water_time,unix_t))
        conn.commit()
	print("Table Schedule has datetime column updated to %s" %(datetime.datetime.fromtimestamp(unix_t).strftime('%Y-%m-%d %H:%M:%S')))
	cursor.execute('INSERT INTO History( watered, SoilMoisture, Description, datetime) VALUES(?,?,?,?)', ("Already", SM, weather_list[3], water_time.strftime('%Y-%m-%d %H:%M:%S')))
	conn.commit()
        print("Save water time successfully")

def isRain(weather_list):
	if "rain" in weather_list:
	    return True
	else:
	    return False


def main():

    try:
	hour = -1
	min = -1
        while True:

		now = time.localtime()
                if(now.tm_hour == 7 or now.tm_hour == 22) and (now.tm_hour != hour):
                        current_SM = readADC(soilMoisture, CLK, DOUT, DIN, CS) #lấy giá trị độ ẩm đất hiện tại
			print("Soil moisture: %.1f " %(current_SM))
			weather_list = currentWeather()
			right_now = datetime.datetime.now()
			water_time = setUpWaterTime()
			print("water time: %s " % (str(water_time)))
			delta = right_now - water_time
			noWaterHours = delta.total_seconds()//3600
			print("Your garden has not been watered for %d hours" % (noWaterHours))

			if (current_SM < threshold and noWaterHours >= 24 and noWaterHours < 72):
			    #weather_list = currentWeather()
			    if isRain(weather_list):
				print("It's raining, no need to water")
			    else:
				watering(current_SM, weather_list)
                                sendMail("Hệ thống chăm sóc cây tự động","Vườn cây của bạn đã vừa được tưới.")

			elif noWaterHours >= 72:
			    print("Your garden has not been watered for over 3 days, so it's watered right now")
			    sendMail("Hệ thống chăm sóc cây tự động","Vườn cây của bạn đã vừa được tưới.")
			    watering(current_SM, weather_list)

			elif (current_SM < threshold and noWaterHours < 24):
			    print("Soil moisture is %.1f, under threshold but your garden has been just  watered %d hours ago" % (current_SM,noWaterHours))

			elif current_SM > threshold:
			    print("No water needed because soil moisture value is %.1f" % (current_SM))

			hour = now.tm_hour
		elif (now.tm_min%30==0 and now.tm_min != min):
			current_SM = readADC(soilMoisture, CLK, DOUT, DIN, CS)
			weather_list = currentWeather()
			saveCurrentWeather(weather_list)
			saveSoilMoisture(current_SM)
			print("weather info and soil moisture values has been inserted into database")
			min = now.tm_min
    except KeyboardInterrupt:
        GPIO.cleanup()
	conn.close()

if __name__ == '__main__':
	debug2()
