from flask import Flask,render_template,request,url_for,flash
import requests 
from datetime import datetime
from waitress import serve
import os

app = Flask(__name__)
app.secret_key = "1234567890"

#api urls
geocoding_api = r"https://geocoding-api.open-meteo.com/v1/search"
forcast_api = r"https://api.open-meteo.com/v1/forecast"
ip_api = r"http://ip-api.com/json/"
aqi_api = r"https://air-quality-api.open-meteo.com/v1/air-quality"
#weather codes
weather_code = {
	"0": "Clear sky",
	"1": "Mainly clear",
	"2": "Partly cloudy",
	"3": "Overcast",
	"45": "Fog",
	"48": "Depositing rime fog",
	"51": "Light drizzle",
	"53": "Moderate drizzle",
	"55": "Dense drizzle",
	"56": "Light freezing drizzle",
	"57": "Dense freezing drizzle",
	"61": "Slight rain",
	"63": "Moderate rain",
	"65": "Heavy rain",
	"66": "Light freezing rain",
	"67": "Heavy freezing rain",
	"71": "Slight snowfall",
	"73": "Moderate snowfall",
	"75": "Heavy snowfall",
	"77": "Snow grains",
	"80": "Slight rain showers",
	"81": "Moderate rain showers",
	"82": "Violent rain showers",
	"85": "Slight snow showers",
	"86": "Heavy snow showers",
	"95": "Thunderstorm",
	"96": "Thunderstorm with slight hail",
	"97": "Heavy thunderstorm",
	"99": "Thunderstorm with heavy hail"
}

#background file names
backgrounds = {
	'clear_':{0,1,-1},
	'fog_' : {45,48,},
	'thunderstorm_' : {99,97,96,95},
	'rain_' : {51,53,55,56,57,61,63,65,66,67,81,82,80},
	'cloudy_' : {2,3,},
	'snowfall_' : {77,71,73,75,85,86},
}


def _getcity():
	try:
		return requests.get(ip_api).json().get('city','none')
	except Exception as e:
		return 'none'
	city = _getcity()
	if city == 'none':
		city = 'london'
	return city

def _get_geocode(city):
	geocode_param = {
		"name" : city,
		"count" : 1,
		"language" : "en",
		"format" : "json"
	}
	headers = {
		'User-Agent': 'WeatherApp/1.0'
		}

	geocode_response = requests.get(geocoding_api,params = geocode_param,headers = headers).json()
	if "results" not in geocode_response :
		return 'none'
	else :
		location = geocode_response["results"][0]
	return location


def _getweather(lat,lon):
	lat = lat,
	lon = lon,
	forecast_param ={
		"latitude" : lat,
		"longitude" : lon,
		"current" : ["temperature_2m" , "is_day", "weather_code", "apparent_temperature"],
		"daily": ["temperature_2m_max", "temperature_2m_min", "moonset", "moonrise", "sunset", "sunrise"],
		"forecast_days" : 1,
		"temperature_unit": "celsius",
		"timezone": "auto",
	}
	try:
		return requests.get(forcast_api,params= forecast_param , timeout=5).json()
	except requests.exceptions.RequestException as req_err:
		return {}


def _get_aqi(lat,lon):
	lat = lat,
	lon = lon,
	aqi_param = {
		"latitude" : lat,
		"longitude" : lon,
		"current" : ['us_aqi','uv_index'],
		"forecast_days" :1 ,
		"temperature_unit": "celsius",
		"timezone": "auto",
	}
	try:
		return requests.get(aqi_api,params = aqi_param,timeout=5).json().get('current','none')
	except requests.exceptions.RequestException as req_err:
		return {}

def time_convert(iso_time):
	try:
		real_time = datetime.fromisoformat(iso_time)
		return real_time.strftime("%I:%M %p")
	except Exception as e:
		return 'not available'

@app.route("/",methods=['GET','POST'])
def weather_app():
	if request.method == 'POST':
		city = request.form.get('city')
	else :
		city = _getcity()
	location = _get_geocode(city)

	if location == 'none':
		flash(f"Couldn't find a city named '{city}'")
		city = 'london'
		location = _get_geocode(city)
	country = location.get('country',' ')
	lon = location.get('longitude')
	lat = location.get('latitude')
	forecast_response = _getweather(lat,lon)
	aqi_response = _get_aqi(lat,lon)

	current_weather = forecast_response.get('current',{})
	daily_weather = forecast_response.get('daily',{})

	current_tmp = current_weather.get('temperature_2m','N/A')
	current_code = int(current_weather.get('weather_code',-1))
	current_condition = weather_code.get(str(current_code),'N/A')
	uv = aqi_response.get('uv_index','N/A')
	aqi = aqi_response.get('us_aqi','N/A')
	sunrise = time_convert(daily_weather.get('sunrise','N/A')[0])
	sunset = time_convert(daily_weather.get('sunset','N/A')[0])
	moonrise = time_convert(daily_weather.get('moonrise','N/A')[0])
	moonset = time_convert(daily_weather.get('moonset','N/A')[0])
	max_tmp = daily_weather.get('temperature_2m_max','N/A')[0]
	min_tmp = daily_weather.get('temperature_2m_min','N/A')[0]
	is_day = int(current_weather.get('is_day',-1))

	background_vid = r"../static/backgrounds/"
	for i in backgrounds:
		if current_code in backgrounds[i]:
			background_vid += str(i)
			break;
	if is_day:
		background_vid += 'day.png' #mp4
	else:
		background_vid += 'night.png' #mp4
	if not(current_weather or daily_weather):
		flash("Request limit reached. To ensure system stability, please try again later. We appreciate your patience.")

	return render_template("index.html",
							city = city,
							current_tmp = current_tmp,
							current_condition = current_condition,
							uv = uv,
							aqi = aqi,
							sunrise =sunrise,
							sunset = sunset,
							moonrise = moonrise,
							moonset = moonset ,
							min_tmp = min_tmp,
							max_tmp = max_tmp,
							country = country,
							background_vid = background_vid,
							)

if __name__ == "__main__" :
	port = int(os.environ.get("PORT",8080))
	serve(app,host = '0.0.0.0',port = port)