import pyowm
from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps


class MyWeather(object):
    def __init__(self, api_key, translator, country='Romania', city='Bucharest'):
        self.country = country
        self.city = city
        self.owm = pyowm.OWM(api_key)
        self.mgr = self.owm.weather_manager()
        self.translator = translator

    def get_weather(self):
        weather = self.mgr.weather_at_place(self.city)
        data = weather.weather
        return data

    def compose_weather_status(self, city=None):
        if city is not None:
            self.city = city
        weather = self.get_weather()
        return f'In {self.translator.translate(self.city).replace(".", "")} avem {self.translator.translate(weather.detailed_status)}, iar temperatura ' \
               f'este {int(weather.temperature("celsius")["temp"])} ℃.'
