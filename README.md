# waterPy

## Overview
waterPy is a Raspberry Pi-based auto irrigation system. 

This is my very first application. It involves Web development, database operations and Embedded development.
Technologies used: Python, Flask, OpenWeatherMap, Analog-to-Digital conversion, SQLite, HTSQL, freeboard.io

![IMG_4361](https://user-images.githubusercontent.com/40592382/54769011-fbe9f380-4c32-11e9-913b-3795ea201c1f.jpg)


## How it works
The way waterPy works is described as the chart below (in Vietnamese):
![logic_hammain-page-001](https://user-images.githubusercontent.com/40592382/54766390-c8f13100-4c2d-11e9-8e6d-16408228e6aa.jpg)

To summarise, decision-making of waterPy is computed based on three measures:
1. The time of a day ( if it's 7 A.M or 4 P.M)
2. How long since the plants were last irrigated.
3. Is there any moderate/heavy rain or even storm in the moment and next 3 hours ?

## Hardware requirements
1. A Raspberry Pi 3 (obviously). The version of mine is 3 Model B+
2. A MCP3008, an 8-chan.nel ADC IC.
3. A 12V DC water pump motor.
4. Transistor MPSA14 and diode 1N4001, used for controlling the pump motor.
5. A soil moisture sensor.
6. A 16x02 LCD module.
7. A DC connector and a few types of resistors


![complete_sketch](https://user-images.githubusercontent.com/40592382/54767077-099d7a00-4c2f-11e9-937d-7354512f96f1.jpg)


## Software requirements 
#### SQLite
I use SQLite in order to keep track of how many days since the last time my plant was watered. SQL is also the place I put other measures in, such as: soil moisture, current temperate, current humidity, current timedate, weather (clear sky/rain/storm), description of weather (moderate rain/ heavy rain/ thunderstorm).

To install SQLite, log in the Raspi and open Terminal:
``` 
$ sudo apt-get install sqlite3
```

#### HTSQL
HTSQL (“Hyper Text Structured Query Language”) is a high-level query language for relational databases. The target audience for HTSQL is the accidental programmer – one who is not a SQL expert, yet needs a usable, comprehensive query tool for data access and reporting.

HTSQL is also a web service which takes a request via HTTP, translates it into a SQL query, executes the query against a relational database, and returns the results in a format requested by the user agent (JSON, CSV, HTML, etc.).

Use of HTSQL with open source databases (PostgreSQL, MySQL, SQLite) is royalty free under BSD-style conditions.

To install,assume that pip is installed in your Raspi, open Terminal:
``` 
$ sudo pip install HTSQL
```

#### OpenWeatherMap
OpenWeatherMap is an online service that provides weather data, including current weather data, forecasts, and historical data to the developers of web services and mobile applications. For data sources, it utilizes meteorological broadcast services, raw data from airport weather stations, raw data from radar stations, and raw data from other official weather stations. All data is processed by OpenWeatherMap in a way that it attempts to provide accurate online weather forecast data and weather maps, such as those for clouds or precipitation.

I retrieve weather information from OpenWeatherMap to as the input for the irrigation decision-making of waterPy. The data OpenWeatherMap returns is JSON type. The way to retrieve and process the data is specified later on.

#### Flask (A python microframework)
I use it to host a website showing some statistics on the system. The screenshot of my simple website as below:
![web_screen](https://user-images.githubusercontent.com/40592382/54769340-95190a00-4c33-11e9-9596-fdb9d737a21b.png)
