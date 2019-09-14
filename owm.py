import json
import urllib.request
from datetime import datetime


forecast = "http://api.openweathermap.org/data/2.5/forecast?lat=10.762622&lon=106.660172&appid=3f2f6c5a4daa43b4d377e62edb6a0a01&cnt=12&units=metric"
weather = "http://api.openweathermap.org/data/2.5/weather?lat=10.762622&lon=106.660172&appid=3f2f6c5a4daa43b4d377e62edb6a0a01&units=metric"

def read_json_from_internet_unicode(url1):
    DEFAULT_ENCODING = 'utf-8'   
    
    urlResponse = urllib.request.urlopen(url1)
    
    if hasattr(urlResponse.headers, 'get_content_charset'):
        encoding = urlResponse.headers.get_content_charset(DEFAULT_ENCODING)
    else:
        encoding = urlResponse.headers.getparam('charset') or DEFAULT_ENCODING
    noi_dung = json.loads(urlResponse.read().decode(encoding))

    return noi_dung



# cac thong tin can lay: temp, humidity, main, description, dt, sunrise, sunset

def currentWeather():
    content = read_json_from_internet_unicode(weather)
    if content["cod"] != 200:
        print("Cannot connect to OpenWeatherMap")
    else:
        current_dict = {"main": content["weather"][0]["main"], "description": content["weather"][0]["description"], "temperature": content["main"]["temp"], "humidity": content["main"]["humidity"],"dt": content["dt"],"sunrise":content["sys"]["sunrise"], "sunset":content["sys"]["sunset"] }
        if content["wind"].get("speed") != None: 
                current_dict.update({"windSpeed": content["wind"]["speed"]})
        else:
            current_dict.update({"windSpeed": 0})
        if content["wind"].get("deg") != None: 
            current_dict.update({"windDeg": content["wind"]["deg"]})
        else:
            current_dict.update({"windDeg": 0})
        if content["clouds"].get("all") != None:
            current_dict.update({"cloud": content["clouds"]["all"]})
        else:
            current_dict.update({"cloud": "not given"})
        return current_dict


def forecastWeather():
    content = read_json_from_internet_unicode(forecast)
    forecast_list = []
    if content["cod"] != "200":
        print(content["cod"])
        print("Cannot connect to OpenWeatherMap")
    else:
        for item in content["list"]:
            dt_text = datetime.fromtimestamp(item["dt"])
            forecast_dict = {"dt": item["dt"],"dt_txt": dt_text , "temperature": item["main"]["temp"], "humidity": item["main"]["humidity"], "main": item["weather"][0]["main"], "description": item["weather"][0]["description"]}
            if item.get("wind") != None and item["wind"].get("speed") != None: 
                forecast_dict.update({"windSpeed": item["wind"]["speed"]})
            else:
                forecast_dict.update({"windSpeed": 0})
            if item.get("wind") != None and item["wind"].get("deg") != None: 
                forecast_dict.update({"windDeg": item["wind"]["deg"]})
            else:
                forecast_dict.update({"windDeg": 0})
            if item.get("clouds") != None and item["clouds"].get("all") != None:
                forecast_dict.update({"cloud": item["clouds"]["all"]})
            else:
                forecast_dict.update({"cloud": "not given"})
            if item.get("rain") != None and item["rain"].get("3h") != None:
                forecast_dict.update({"rain": item["rain"]["3h"]})
            else:
                forecast_dict.update({"rain": 0})
            forecast_list.append(forecast_dict)
    return forecast_list

        
        
        
if __name__ == "__main__":
    
    forecast = forecastWeather()
    for i in forecast:
        print(i)
    
    
   