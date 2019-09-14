import dweepy
import time
from datetime import datetime
from cpu_temp import *
from MCP3008 import *
thing_name = "waterPy-HoangQuocHung-DATN2018"


def sendToDweet(water_time, SM, cpu_t, current_dict, forecast_dict):
    rightnow = datetime.fromtimestamp(time.time()).strftime("%H:%M %d-%m")
    dweet_1 = {"last_watering": water_time, "current_temp": current_dict["temperature"], "current_humidity": current_dict["humidity"], "description": current_dict["description"], "soil_moistue": SM,"cpu_temp": cpu_t, "cloud": current_dict["cloud"], "rightnow": rightnow}
    dweet_2 = {"temp+3h": forecast_dict[0]["temperature"],"humidity+3h":forecast_dict[0]["humidity"],"description+3h":forecast_dict[0]["description"],"rain+3h":forecast_dict[0]["rain"],"windSpeed+3h":forecast_dict[0]["windSpeed"],"windDeg+3h": forecast_dict[0]["windDeg"]}
    dweet_1.update(dweet_2)
    dweepy.dweet_for(thing_name, dweet_1)
    
    
if __name__ == "__main__":
    while True:
        SM = readadc(soilMoisture, CLK, DOUT, DIN, CS)
        current = currentWeather()
        forecast = forecastWeather()
        cpu_t = cpu_temp()
        water_time = setUpWaterTime()
        water_time = water_time.strftime("%H:%M %d-%m")

        sendToDweet(water_time, SM,cpu_t, current, forecast)
        time.sleep(1)



