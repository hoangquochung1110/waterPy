from flask import Flask, render_template, request
from project import *
from owm import *
import time
from datetime import datetime
import sqlite3
from MCP3008 import *
def getWaterTime():
    conn = sqlite3.connect('database.db')
    content = conn.execute("SELECT unix_time  FROM Schedule")
    ds = content.fetchall()
    for item in ds:
        watertime = item[0]
    watertime = datetime.fromtimestamp(watertime).strftime("%H:%M %d-%m")
    return watertime


app = Flask(__name__)
@app.route('/')
def index():
    current_time = datetime.fromtimestamp(time.time()).strftime("%H:%M %d-%m")
    weather_dict = currentWeather()
    forecast_dict = forecastWeather()
    SM = 0
    water_time = getWaterTime()
    SM = readadc(SM,18,23,24,25)
    templateData = {'Current_time': current_time,'Temperature': weather_dict["temperature"], 'Humidity': weather_dict["humidity"],'Status':weather_dict["main"], 'Description':weather_dict["description"],'Soil_moisture': SM,'Water_time': water_time}
    templateData.update({"next_3hours": forecast_dict[0]["description"]})
    return render_template('index.html', **templateData)

@app.route('/next')
def next():
    return "Next 3 hours"

def app_run():
    app.run(host = '0.0.0.0', debug = False)
    time.sleep(1)
if __name__ == "__main__":
    app_run()



