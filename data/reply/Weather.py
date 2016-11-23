# -*- coding: utf-8 -*-
import operator
from gensim.models import word2vec
from konlpy.tag import Twitter
from konlpy.tag import Mecab
from konlpy.tag import Hannanum
import numpy as np
import pandas as pd
import mtranslate
import parsedatetime
import time
import json, urllib2, requests, datetime
from datetime import timedelta,date
from sklearn.externals import joblib


class WeatherClass:
    def __init__(self):
        self.region = ''
        self.temp = 0.0
        self.humi = 0
        self.pres = 0.0
        self.wind_speed = 0.0
        self.clouds = 0
        self.lat = 0.0
        self.lng = 0.0

    def getUrlForGeoCoord(self, region_name):
        api_key = "AIzaSyAvwmpQfZtYtN0HkbM7IDiLJRcWzIs9QPI"
        url_front = "https://maps.googleapis.com/maps/api/geocode/json?address="
        url_end = "&key=" + api_key + "&sensor=true&language=ko"
        url = url_front + region_name + url_end
        # print url
        return url

    def requestAndGetJson(self, url):
        d = requests.get(url).text
        json_list = json.loads(d)

        return json_list

    def getKoreanRegionName(self):
        api_key = "AIzaSyAvwmpQfZtYtN0HkbM7IDiLJRcWzIs9QPI"
        url_front = "https://maps.googleapis.com/maps/api/geocode/json?latlng="
        url_end = "&sensor=true&language=ko"
        url = url_front + str(self.lat) + "," + str(self.lng) + url_end

        json_list = self.requestAndGetJson(url)

        print json_list['results'][0]['formatted_address']

    def getRegionCode(self):
        url = "http://www.kma.go.kr/DFSROOT/POINT/DATA/top.json.txt"
        json_list = self.requestAndGetJson(url)
        # print (json_list)
        return json_list

    def getGeoCoord(self, region_name):
        url = self.getUrlForGeoCoord(region_name)
        # rint url
        json_list = self.requestAndGetJson(url)
        self.lat = json_list['results'][0]['geometry']['location']['lat']
        self.lng = json_list['results'][0]['geometry']['location']['lng']

    def getWeatherInfo(self, region_name='서울'):
        # print('region')
        # print(region_name)

        self.getGeoCoord(region_name)

        api_key = "90e8bc7aa09ae068ee424b2518d72ebe"
        url = "http://api.openweathermap.org/data/2.5/weather?lat=" + str(self.lat) + "&lon=" + str(
            self.lng) + "&APPID=" + api_key

        # print(url)
        json_list = self.requestAndGetJson(url)

        # print json_list

        self.region = json_list['name']
        self.temp = json_list['main']['temp']
        self.humi = json_list['main']['humidity']
        self.pres = json_list['main']['pressure']
        self.wind_speed = json_list['wind']['speed']
        self.clouds = json_list['clouds']['all']

    def showWeatherInfo(self):
        st = []
        st.append("지역 : " + str(self.region))
        st.append("\n기온 : " + str(self.temp - 273.15))
        st.append("\n습도 : " + str(self.humi))
        st.append("기압 : " + str(self.pres) + " hpa")
        st.append("풍속 : " + str(self.wind_speed) + " m/s")
        st.append("강수 확률 : " + str(self.clouds) + " %")
        return '\n'.join(st)
        # print(u"lat : " + str(self.lat))
        # print(u"lng : " + str(self.lng))

class ForecastWeather:
    def __init__(self):
        pass

    def getUrlForGeoCoord(self, region_name):
            api_key = "AIzaSyAvwmpQfZtYtN0HkbM7IDiLJRcWzIs9QPI"
            url_front = "https://maps.googleapis.com/maps/api/geocode/json?address="
            url_end = "&key=" + api_key + "&sensor=true&language=ko"
            url = url_front + region_name + url_end
            return url

    def requestAndGetJson(self, url):
            d = requests.get(url).text
            json_list = json.loads(d)

            return json_list


    def getGeoCoord(self, region_name):
            url = self.getUrlForGeoCoord(region_name)

            json_list = self.requestAndGetJson(url)
            coord_list = []
            coord_list.append(json_list['results'][0]['geometry']['location']['lat'])
            coord_list.append(json_list['results'][0]['geometry']['location']['lng'])

            return coord_list

    def getWeatherInfo(self, region_name, day_after='0'):
            coord_list = self.getGeoCoord(region_name)

            api_key = "90e8bc7aa09ae068ee424b2518d72ebe"
            url = "http://api.openweathermap.org/data/2.5/forecast?lat="+ str(coord_list[0]) + "&lon=" + str(coord_list[1]) + "&APPID="+api_key

            print(url)
            json_list = self.requestAndGetJson(url)

            #print json_list

            #self.region = json_list['name']
            #self.temp = json_list['main']['temp']
            #self.humi = json_list['main']['humidity']
            #self.pres = json_list['main']['pressure']
            #self.wind_speed = json_list['wind']['speed']
            #self.clouds = json_list['clouds']['all']

            afterday = self.getDateFuture(day_after)
            afterdaytomorrow = self.getDateFuture(day_after+1)

            st = []
            for each in json_list['list']:
                original_dt = datetime.datetime.strptime(str(each['dt_txt']), '%Y-%m-%d %H:%M:%S')
                changed_dt = original_dt - datetime.timedelta(hours=-9)
                if str(changed_dt) > str(afterday) and str(changed_dt) < str(afterdaytomorrow):
                    st.append(str(changed_dt))
                    st.append("기온 : " + str(each['main']['temp']-273.15))
                    st.append("습도 : " + str(each['main']['humidity']))
                    st.append("기압 : " + str(each['main']['pressure']) + " hpa")
                    st.append("풍속 : " + str(each['wind']['speed']) + " m/s")
                    st.append("강수 확률 : " + str(each['clouds']['all']) + " %")
                    st.append(" ")

            if len(st) == 0:
                return '좀 더 정확히 입력해 주세요'
            return '\n'.join(st)



    def getDateFuture(self, day_after):
        td = timedelta(days=+day_after)
        d = datetime.date.today()
        afterday = d + td

        return afterday

def exist_key(key_string, dictionary):
    if key_string in dictionary:
        return True
    else:
        return False


def get_key_if_exist(key_string, dictionary):
    if exist_key(key_string, dictionary):
        return ' '.join(dictionary[key_string])
    else:
        return ''


def getAnswer(question, params):
    result_dict = {}
    for k in params:
        result_dict[k] = [x[0] for x in params[k] if x[1] > 0.3]

    what = ''
    who = ''
    where = ''
    when = ''
    detail = ''
    why = ''
    how = ''

    what = get_key_if_exist('what', result_dict)
    who = get_key_if_exist('who', result_dict)
    where = get_key_if_exist('where', result_dict)
    when = get_key_if_exist('when', result_dict)
    detail = get_key_if_exist('detail', result_dict)
    why = get_key_if_exist('why', result_dict)
    how = get_key_if_exist('how', result_dict)

    if where == '':
        where = '서울'

    if is_now(question):
        print '현재 날씨'
        wc = WeatherClass()
        wc.getWeatherInfo(where)
        print type(where)
        print type(wc.showWeatherInfo())
        tmp = wc.showWeatherInfo()
        if type(tmp) is not unicode:
            tmp = tmp.decode('utf-8')
        return where + u' 현재 날씨입니다.\n' + tmp
    else:
        print '날씨 예보'
        wf = ForecastWeather()
        print type(where)
        tmp = wf.getWeatherInfo(where, get_date_diff(question))
        if type(tmp) is not unicode:
            tmp = tmp.decode('utf-8')
        return where + u' 날씨 예보입니다.\n' + tmp


def is_now(when):
    try:
        en = mtranslate.translate(when, 'en', 'kr')
    except:
        print 'when : ' + when
        en = mtranslate.translate(when.encode('utf-8'), 'en', 'kr')
    print en
    cal = parsedatetime.Calendar()
    cal_str = cal.parse(en)

    now = time.localtime()
    cur_year = now.tm_year
    cur_month = now.tm_mon
    cur_date = now.tm_mday

    if cur_year == cal_str[0][0] and cur_month == cal_str[0][1] and cur_date == cal_str[0][2]:
        return True
    else:
        return False


def get_date_diff(when):
    try:
        en = mtranslate.translate(when, 'en', 'kr')
    except:
        print 'when : ' + when
        en = mtranslate.translate(when.encode('utf-8'), 'en', 'kr')
    cal = parsedatetime.Calendar()
    cal_str = cal.parse(en)

    now = time.localtime()
    cur_year = now.tm_year
    cur_month = now.tm_mon
    cur_date = now.tm_mday

    d0 = date(cal_str[0][0], cal_str[0][1], cal_str[0][2])
    d1 = date(cur_year, cur_month, cur_date)
    delta = d0 - d1
    return delta.days
