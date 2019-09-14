from app import *
from owm import *
from dweet_test import *
from cpu_temp import *
from sendEmail import *
from MCP3008 import *
from datetime import datetime
import _thread
import time, requests, json, sqlite3, math
from flask import Flask, render_template, request
import RPi.GPIO as GPIO
from RPLCD.gpio import CharLCD
SM = 0
threshold = 20
#khai báo các chân kết nối SPI
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

pump = 14
GPIO.setup(pump, GPIO.OUT)

class AutoIrrigationSystem(object):

    def __init__(self, soilMoisture, noWaterHours):
        self.soilMoisture = soilMoisture
        self.noWaterHours = noWaterHours

    def isRain(self, cur_weather):
        if "rain"  in cur_weather["main"].lower():
            return True
        elif "thunderstorm" in cur_weather["main"].lower():
            return True
        else:
            return False
    def expectedRain(self, for_weather):
        if "shower" in for_weather[0]["description"]:
            return for_weather[0]["description"]+" at "+for_weather[0]["dt_txt"].strftime("%Hh:%M %m-%d") 
        elif "heavy" in for_weather[0]["description"]:
            return for_weather[0]["description"]+" at "+for_weather[0]["dt_txt"].strftime("%Hh:%M %m-%d")
        elif "thunderstorm" in for_weather[0]["description"]:
            return for_weather[0]["description"]+" at "+for_weather[0]["dt_txt"].strftime("%Hh:%M %m-%d")
        elif "moderate" in for_weather[0]["description"]:
            return for_weather[0]["description"]+" at "+for_weather[0]["dt_txt"].strftime("%Hh:%M %m-%d")
        else:
            for item in for_weather:
                #print(item["description"])
                if "thunderstorm"  in item["description"]:
                    return item["description"] +" at " + item["dt_txt"].strftime("%Hh:%M %m-%d") 
                    break
                if "heavy" in item["description"]:
                    return item["description"] +" at " + item["dt_txt"].strftime("%Hh:%M %m-%d") 
                    break
                else: 
                    return ""

    def saveSoilMoisture(self):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        t = datetime.now()
        command = 'INSERT INTO readings(SoilMoisture,Datetime) VALUES(?,?)'
        cursor.execute(command, (self.soilMoisture,t.strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()
        print('Insert into Readings column successfully')

    def saveCurrentWeather(self, cur_weather):  
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        t = datetime.now()
        command = 'INSERT INTO main(Temperature,Humidity,Status,Description,WindSpeed,Cloud,Datetime) VALUES(?,?,?,?,?,?,?)'
        cursor.execute(command, (cur_weather["temperature"],cur_weather["humidity"],cur_weather["main"],cur_weather["description"],cur_weather["windSpeed"],cur_weather["cloud"],t.strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()

    def watering(self, weather_dict):
        
        GPIO.output(pump, GPIO.HIGH) # thực hiện tưới cây
        print ("start pumping water")
        time.sleep(5)
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
        cursor.execute(command2, ("Already", self.soilMoisture, weather_dict["description"], water_time.strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()
        print("Save water time successfully")

    def dweet(self):
        while True:
            sendToDweet(setUpWaterTime().strftime("%H:%M %d-%m"), self.soilMoisture,cpu_temp(), currentWeather(), forecastWeather())
            time.sleep(2)

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

def dweet():
    
    while True:
        
        soilMoisture = readadc(SM, CLK, DOUT, DIN, CS)
        current = currentWeather()
        forecast = forecastWeather()
        cpu_t = cpu_temp()
        water_time = setUpWaterTime()
        water_time = water_time.strftime("%H:%M %d-%m")

        sendToDweet(water_time, soilMoisture,cpu_t, current, forecast)
        time.sleep(1)


def main():
    try:
        lcd = CharLCD(pin_rs=11, pin_rw=13, pin_e=15, pins_data=[12, 16, 20, 21],numbering_mode=GPIO.BCM, cols=16, rows=4)
        lcd.clear()
        hour = -1
        min = -1
        while True:
            
            #lcd.write_string('Raspberry Pi')
            now = time.localtime()
            soilMoisture = readadc(SM, CLK, DOUT, DIN, CS)
            water_time = setUpWaterTime() # dang datetime
            right_now = datetime.now() # dang datetime
            lcd.cursor_pos=(0,1)
            lcd.write_string(water_time.strftime("%H:%M %d/%m"))
            lcd.cursor_pos=(1,1)
            lcd.write_string(str(soilMoisture)+ " %")
            lcd.cursor_pos=(1,7)
            lcd.write_string("weather")
            #noWaterHours = (right_now.day*24 + right_now.hour) -(water_time.day*24 + water_time.hour)
            delta = (right_now - water_time).total_seconds()
            noWaterHours = delta//3600

            waterPy = AutoIrrigationSystem(soilMoisture, noWaterHours)
            #print("I'm here")
            if(now.tm_hour == 12 or now.tm_hour == 6) and (now.tm_hour != hour):
                print("Soil moisture: ",waterPy.soilMoisture, "|", "water time: ", water_time)
                print("Your garden has not been watered for", waterPy.noWaterHours , "hours")
                current = currentWeather()
                forecast = forecastWeather()

                if (waterPy.soilMoisture < threshold and waterPy.noWaterHours >= 24 and waterPy.noWaterHours < 72):
                    if waterPy.isRain(current):
                        print("It's", current["description"] ,". No need to water right now")
                    elif waterPy.expectedRain(forecast) != "":
                        print("Expecting", waterPy.expectedRain(forecast), ". No need to water right now")
                    else:
                        waterPy.watering(current)
                        print("It's", current["description"])
                        sendMail("WaterPy", "Your plant has been watered.")
                elif waterPy.noWaterHours >= 72:
                    print(current["description"])
                    print("It's over 3 days without water. Watering...")
                    waterPy.watering(current)
                    sendMail("WaterPy", "Your plant has been watered.")
                elif ( waterPy.soilMoisture < threshold and waterPy.noWaterHours < 24):
                    print("Soil moisture is %.1f, under threshold but your garden has been just  watered %d hours ago" % (waterPy.soilMoisture,waterPy.noWaterHours))
                elif waterPy.soilMoisture > threshold:
                    print("Soil moisture is %.1f, above threshold" %waterPy.soilMoisture)
                hour = now.tm_hour
            elif (now.tm_min%30==0 and now.tm_min != min):
                soilMoisture = readadc(soilMoisture, CLK, DOUT, DIN, CS)
                current = currentWeather()
                forecast = forecastWeather()
                waterPy.saveCurrentWeather(current)
                waterPy.saveSoilMoisture()
                print("weather info and soil moisture values has been inserted into database")
                min = now.tm_min
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()
        lcd.clear()

if __name__ == "__main__":
    _thread.start_new_thread(main,())
    #_thread.start_new_thread(app_run,())
    _thread.start_new_thread(dweet,())
    while 1: 
        pass
    
