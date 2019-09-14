# -*- coding: utf-8 -*-
from datetime import datetime
import _thread
import time, requests, json, sqlite3, math
from flask import Flask, render_template, request
import RPi.GPIO as GPIO
from owm import *
from sendEmail import *
from app import *
from dweet_test import *

threshold = 20
noWaterDays = 0 # số ngày chưa tưới cây
soilMoisture = 0
pump = 14

#khai báo các chân kết nối SPI
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
CLK = 18
DOUT = 23
DIN = 24
CS = 25

GPIO.setup(CLK,  GPIO.OUT)
GPIO.setup(DOUT, GPIO.IN)
GPIO.setup(DIN,  GPIO.OUT)
GPIO.setup(CS,   GPIO.OUT)
GPIO.setup(pump, GPIO.OUT)

def readADC(num, clk, dout, din, cs):
    if((num > 7) or (num < 0)):
        return -1

    GPIO.output(cs, 1) # dừng bất kì quá trình ADC trước đó nếu có
    GPIO.output(clk, 0)
    GPIO.output(cs, 0)# chọn slave để bắt đầu ADC

    command = num
    command |= 0x18 #thêm '11' vào đầu giá trị
    command <<= 3

    for i in range(5):
        if(command & 0x80):
            GPIO.output(din, 1)
        else:
            GPIO.output(din, 0)
        command <<= 1
        GPIO.output(clk, 1)
        GPIO.output(clk, 0)

    out = 0
    for i  in range(12):
        GPIO.output(clk, 1)
        GPIO.output(clk, 0)
        out <<= 1
        out |= GPIO.input(dout)

    GPIO.output(cs, 1) #kết thúc đọc ADC
    out >>= 1
    out = (out/1023.0)*100
    out = math.ceil(out)
    return out

def setUpWaterTime():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    watertime = 0
    content = cursor.execute("SELECT unix_time  FROM Schedule")

    for item in content.fetchall():
        watertime = item[0]

    watertime = datetime.fromtimestamp(watertime)
    conn.close()
    return watertime

def isRain(weather_dict):
    if "rain" or "thunderstorm" in weather_dict["main"].lower():
        return True
    else:
        return False

def saveSoilMoisture(_soilMoisture):
        #reading_time = time.time()
        #reading_time = datetime.datetime.fromtimestamp(reading_time).strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    t = datetime.now()
    cursor.execute('INSERT INTO readings(SoilMoisture,Datetime) VALUES(?,?)', (_soilMoisture,t.strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()
    print('Insert into Readings column successfully')

def saveCurrentWeather(a_list):  #bắt đầu lưu vào bảng Weather trong dattabase.db
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    t = datetime.now()
    command = 'INSERT INTO main(Temperature, Humidity, Status, Description, WindSpeed, Cloud, Datetime) VALUES(?,?,?,?,?,?,?)'
    cursor.execute(command, (a_list["temperature"],a_list["humidity"],a_list["main"],a_list["description"],a_list["windSpeed"],a_list["cloud"],t.strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

def watering(SM, weather_list):
    GPIO.output(pump, GPIO.HIGH) # thực hiện tưới cây
    print ("start pumping water")
    time.sleep(2)
    print ("stop pumping water")
    GPIO.output(pump, GPIO.LOW)

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    water_time = datetime.now()
    unix_t = time.time()
    command1 = 'UPDATE Schedule SET datetime = ?, unix_time = ? WHERE id = 1 '
    cursor.execute(command1, ( water_time,unix_t))
    conn.commit()

    command2 = 'INSERT INTO History( watered, SoilMoisture, Description, datetime) VALUES(?,?,?,?)'
    print("Table Schedule has datetime column updated to %s" %(datetime.fromtimestamp(unix_t).strftime('%Y-%m-%d %H:%M:%S')))
    cursor.execute(command2, ("Already", SM, weather_list["description"], water_time.strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()
    print("Save water time successfully")

def dweet():
    print("I'm here")
    while True:
        SM = readADC(soilMoisture, CLK, DOUT, DIN, CS)
        current = currentWeather()
        forecast = forecastWeather()
        cpu_t = cpu_temp()
        water_time = setUpWaterTime()
        water_time = water_time.strftime("%H:%M %d-%m")
    
        sendToDweet(water_time, SM,cpu_t, current, forecast)
        time.sleep(3)

def main():
    hour = -1
    min = -1
    while True:
        now = time.localtime()
        if(now.tm_hour == 22 or now.tm_hour == 17) and (now.tm_hour != hour):
            current_SM = readADC(soilMoisture, CLK, DOUT, DIN, CS) #lấy giá trị độ ẩm đất hiện tại
            weather_list = currentWeather()
            right_now = datetime.now()
            water_time = setUpWaterTime()
            noWaterHours = (right_now.day*24 + right_now.hour) -( water_time.day*24 + water_time.hour)
            print("Soil moisture: ",current_SM)
            print("water time: ", water_time)
            print("Your garden has not been watered for", noWaterHours , "hours")

            if (current_SM < threshold and noWaterHours >= 24 and noWaterHours < 72):
                if isRain(weather_list):
                    print("It's", weather_list["description"] ,". no need to water right now")
                else:
                    watering(current_SM, weather_list)
                    sendMail("WaterPy", "Your plant has been watered.")
            elif noWaterHours >= 72:
                print("It's over 3 days without water. Watering...")
                watering(current_SM, weather_list)
                sendMail("WaterPy", "Your plant has been watered.")
            elif (current_SM < threshold and noWaterHours < 24):
                print("Soil moisture is %.1f, under threshold but your garden has been just  watered %d hours ago" % (current_SM,noWaterHours))
            elif current_SM > threshold:
                print("Soil moisture is %.1f, above threshold" %current_SM)
            hour = now.tm_hour
        elif (now.tm_min%30==0 and now.tm_min != min):
            current_SM = readADC(soilMoisture, CLK, DOUT, DIN, CS)
            weather_list = currentWeather()
            saveCurrentWeather(weather_list)
            saveSoilMoisture(current_SM)
            print("weather info and soil moisture values has been inserted into database")
            min = now.tm_min
        time.sleep(1)
        

if __name__ == "__main__":
    _thread.start_new_thread(main,())
    _thread.start_new_thread(app_run,())
    _thread.start_new_thread(dweet,())
    while 1: 
        pass
  
