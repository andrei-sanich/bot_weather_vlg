from flask import Flask
from flask import request
from flask_sslify import SSLify
import requests
import datetime
import pytz
import re
import config


app = Flask(__name__)
sslify = SSLify(app)

URL = 'https://api.telegram.org/bot577120284:{}/'.format(config.TOKEN)


def get_forecasts(apikey):
    url = 'http://api.openweathermap.org/'
    mode = 'json'
    lang = 'ru'
    url_full = '{}data/2.5/forecast?id=472757&APPID={}&mode={}&lang={}'.format(
        url,
        apikey,
        mode,
        lang
        )
    r = requests.get(url_full).json()
    forecasts = r['list'][:2]
    return forecasts


def convert_temp(temp_K):

    temp_C = temp_K - 273.15
    return str(round(temp_C))


def text_start():

    text = ('Прогноз погоды на близжайшее время для Волгограда.\n'
           'Введите:\n'
           '/Volgograd\n')

    return text


def convert_date(date):

    utc = pytz.utc.localize(date)
    vlg_time = utc.astimezone(pytz.timezone("Europe/Samara")).strftime('%H-%M')
    return vlg_time


def make_text(forecast):

    dt = forecast['dt_txt']
    date = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
    vlg_time = convert_date(date)
    wheather_description = forecast['weather'][0]['description']
    speed_wind = forecast['wind']['speed']
    temp = convert_temp(forecast['main']['temp'])
    humidity = forecast['main']['humidity']
    text = ('Прогноз на {}:\n'
           '{}\n'
           'ск. ветра: {}\n'
           'темп-ра: {}\n'
           'влаж.: {}\n'.format(
                vlg_time,
                wheather_description,
                speed_wind,
                temp,
                humidity))
    return text


def send_message(chat_id, text='bla-bla-bla'):
    url = URL + 'sendMessage'
    answer = {'chat_id': chat_id, 'text': text}
    r = requests.post(url, json=answer)
    return r.json()


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        r = request.get_json()
        chat_id = r['message']['chat']['id']
        message = r['message']['text']

        if message == '/start':
            text = text_start()
            send_message(chat_id, text=text)

        else:
            forecasts = get_forecasts(config.APIKEY)
            for forecast in forecasts:
                send_message(chat_id, text=make_text(forecast))

    return '<h1>Bot welcomes you</h1>'
    