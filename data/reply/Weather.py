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
        #req = urllib2.Request(url)
        #opener = urllib2.build_opener()
        d = requests.get(url).text
        #f = opener.open(req)
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
        st.append("기온 : " + str(self.temp - 273.15))
        st.append("습도 : " + str(self.humi))
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
            req = urllib2.Request(url)
            opener = urllib2.build_opener()
            f = opener.open(req)
            json_list = json.loads(f.read())

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

            for each in json_list['list']:
                original_dt = datetime.datetime.strptime(str(each['dt_txt']), '%Y-%m-%d %H:%M:%S')
                changed_dt = original_dt - datetime.timedelta(hours=-9)
                if str(changed_dt) > str(afterday) and str(changed_dt) < str(afterdaytomorrow):
                    print(changed_dt)
                    print(u"기온 : " + str(each['main']['temp']-273.15))
                    print(u"습도 : " + str(each['main']['humidity']))
                    print(u"기압 : " + str(each['main']['pressure']) + " hpa")
                    print(u"풍속 : " + str(each['wind']['speed']) + " m/s")
                    print(u"강수 확률 : " + str(each['clouds']['all']) + " %")
                    print(" ")



    def getDateFuture(self, day_after):
        td = timedelta(days=+day_after)
        d = datetime.date.today()
        afterday = d + td

        return afterday

weather_data_list = [
    {'question':"오늘비오나요", 'result':{ 'when':["오늘"], 'what':["비"]}},
    {'question':"오늘 날씨 어때요??", 'result':{'when':["오늘"], 'what':['날씨']}},
    {'question':"오늘서울시도봉구날씨는어떤가요?", 'result':{'when':['오늘'], 'what':['날씨'], 'where':['서울시','도봉구']}},
    {'question':'이번주토요일에비올확률은?', 'result':{'when':['이번주','토요일'], 'what':['비'], 'detail':['확률']}},
    {'question':'금요일날씨알려주세요', 'result':{'when':['금요일'], 'what':['날씨']}},
    {'question':'오늘오후에비오나요?궁굼해오', 'result':{'when':['오늘','오후'], 'what':['비']}},
    {'question':'오늘오후경기도광명시에비올확률은', 'result':{'when':['오늘','오후'], 'what':['비'], 'where':['경기도','광명시'], 'detail':['확률']}},
    {'question':'5월5일경주날씨특히강수확률', 'result':{'when':['5월','5일'], 'what':['날씨'], 'where':['경주']}},
    {'question':'내일비오나요??', 'result':{'when':['내일'], 'what':['비']}},
    {'question':'오늘 저녁 7시 서울에 비올 확률은?', 'result':{'when':['오늘', '저녁', '7시'], 'what':['비'], 'where':['서울'], 'detail':['확률']}},
    {'question':'오늘비가몇시부터제대로오죠?', 'result':{'when':['오늘'], 'what':['비']}},
    {'question':'요즘의중국날씨어때요~?', 'result':{'when':['요즘'], 'what':['날씨'], 'where':['중국']}},
    {'question':'오늘비몇시에와요??', 'result':{'when':['몇시'], 'what':['비']}},
    {'question':'오늘서울의 비올확률은?', 'result':{'when':['오늘'], 'what':['비'], 'where':['서울'], 'detail':['확률']}},
    {'question':'비오냐고요오늘', 'result':{'when':['오늘'], 'what':['비']}},
    {'question':'오늘평택날씨', 'result':{'when':['오늘'], 'what':['날씨'], 'where':['평택']}},
    {'question':'오늘서울강남지역비오나염', 'result':{'when':['오늘'], 'what':['비'], 'where':['서울','강남']}},
    {'question':'내일의 날씨는', 'result':{'when':['내일'], 'what':['날씨']}},
    {'question':'5월4일 날씨좀요', 'result':{'when':['5월','4일'], 'what':['날씨']}},
    {'question':'오늘비얼마나와요', 'result':{'when':['오늘'], 'what':['비']}},
    {'question':'대답을제대로해야지 이따일곱시에비오냐구요', 'result':{'when':['일곱시'], 'what':['비']}},
    {'question':'내일 아침9시 서울에 비올확률은?', 'result':{'when':['내일','아침9시'], 'what':['비'], 'where':['서울'], 'detail':['확률']}},
    {'question':'내일서울날씨요?', 'result':{'when':['내일'], 'what':['날씨'], 'where':['서울']}},
    {'question':'광명 날씨물어봤는데요--내일이요 근데이상한걸보냈잖아요', 'result':{'when':['내일'], 'what':['날씨'], 'where':['광명']}},
    {'question':'오늘비는언제그칠까요~~', 'result':{'when':['오늘'], 'what':['비'], 'detail':['그칠']}},
    {'question':'오늘 5시 비올 확률은?', 'result':{'when':['오늘','5시'], 'what':['비'], 'detail':['확률']}},
    {'question':'북경요새날씨좀알려주세요', 'result':{'when':['요새'], 'what':['날씨'], 'where':['북경']}},
    {'question':'내일비오나요?', 'result':{'when':['내일'], 'what':['비']}},
    {'question':'서울비올확률이어떻게되나요???', 'result':{'what':['비'], 'where':['서울'], 'detail':['확률']}},
    {'question':'오늘 비 내리나요??', 'result':{'when':['오늘'],'what':['비']}},
    {'question':'내일 강화도에 비올확률은??', 'result':{'when':['내일'], 'what':['비'], 'where':['강화도'], 'detail':['확률']}},
    {'question':'강원도강릉날씨좀알려주세요자세하게', 'result':{'what':['날씨'], 'where':['강원도','강릉']}},
    {'question':'경기도파주비와요', 'result':{'what':['비'], 'where':['경기도','파주']}},
    {'question':'이번주 날씨는?', 'result':{'when':['이번주'], 'what':['날씨']}},
    {'question':'오늘비올확률은??', 'result':{'when':['오늘'], 'what':['비'], 'detail':['확률']}},
    {'question':'내일경주에비올확률은?', 'result':{'when':['내일'], 'what':['비'], 'where':['경주'], 'detail':['확률']}},
    {'question':'오늘저녁7시쯤 서울에비올확률은?', 'result':{'when':['오늘','저녁','7시'], 'what':['비'], 'where':['서울'], 'detail':['확률']}},
    {'question':'내일날씨알려주세요', 'result':{'when':['내일'], 'what':['날씨']}},
    {'question':'주말에 비오나요', 'result':{'when':['주말'], 'what':['비']}},
    {'question':'오늘 비 와요', 'result':{'when':['오늘'], 'what':['비']}},
    {'question':'금요일 날씨좀알려주세요', 'result':{'when':['금요일'], 'what':['날씨']}},
    {'question':'오늘저녁 서울에 비올 확률은?', 'result':{'when':['오늘','저녁'], 'what':['비'], 'where':['서울'], 'detail':['확률']}},
    {'question':'이번주말금토일날씨는??', 'result':{'when':['이번','주말'], 'what':['날씨']}},
    {'question':'5월5일날씨?', 'result':{'when':['5월','5일'], 'what':['날씨']}},
    {'question':'수목금요일제주도날씨알려주세요', 'result':{'when':['수','목','금요일'], 'what':['날씨'], 'where':['제주도']}},
    {'question':'내일 서울에 비오나요', 'result':{'when':['내일'], 'what':['비'], 'where':['서울']}},
    {'question':'내일서울양천구날씨가어떻게되나요?', 'result':{'when':['내일'], 'what':['날씨'], 'where':['서울','양천구']}},
    {'question':'15일의 대략적인날씨는~?', 'result':{'when':['15일'], 'what':['날씨']}},
    {'question':'내일비올확률은?', 'result':{'when':['내일'], 'what':['비'], 'detail':['확률']}},
    {'question':'내일서울날씨는어떤가요?아침부터저녁까지', 'result':{'when':['내일'], 'what':['날씨'], 'where':['서울']}},
    {'question':'현재 서울 마포지역 기상일보 확인부탁드려요', 'result':{'when':['현재'], 'what':['일보'], 'where':['서울','마포']}},
    {'question':'지금 일산에 비가오나요?', 'result':{'when':['지금'], 'what':['비'], 'where':['일산']}},
    {'question':'오늘서울지역날씨는?', 'result':{'when':['오늘'], 'what':['날씨'], 'where':['서울']}},
    {'question':'비언제그쳐요?', 'result':{'what':['비'], 'detail':['언제','그쳐']}},
    {'question':'중부지방에내일도비가오나요??', 'result':{'when':['내일'],'what':['비'],'where':['중부','지방']}},
    {'question':'요번주 금요일날 비가 내릴 확률은??', 'result':{'when':['금요일'], 'what':['비'], 'detail':['확률']}},
    {'question':'대전인데 내일 비오나요??', 'result':{'when':['내일'], 'what':['비'], 'where':['대전']}},
    {'question':'내일의날씨는??', 'result':{'when':['내일'], 'what':['날씨']}},
    {'question':'이번주날씨좀알려주세요', 'result':{'when':['이번주'], 'what':['날씨']}},
    {'question':'오늘 저녁 7시 서울에 비올 확률은?', 'result':{'when':['오늘','저녁','7시'], 'what':['비'], 'where':['서울'], 'detail':['확률']}},
    {'question':'내일날씨어때요?', 'result':{'when':['내일'], 'what':['날씨']}},
    {'question':'내일날씨', 'result':{'when':['내일'], 'what':['날씨']}},
    {'question':'내일강릉에 비가오나요?', 'result':{'when':['내일'], 'what':['비'], 'where':['강릉']}},
    {'question':'내일날씨는 어떤가요?', 'result':{'when':['내일'], 'what':['날씨']}},
    {'question':'5월2일날씨는??', 'result':{'when':['5월','2일'], 'where':['날씨']}},
    {'question':'오월 이일 서울 비올확률은?', 'result':{'when':['오월','이일'], 'what':['비'], 'where':['서울'], 'detail':['확률']}},
    {'question':'오늘의날씨', 'result':{'when':['오늘'], 'what':['날씨']}},
    {'question':'이번주금요일경기도안양시 날씨좀알려주세요', 'result':{'when':['금요일'], 'what':['날씨'], 'where':['경기도','안양시']}},
    {'question':'오늘의 날씨 부탁해요', 'result':{'when':['오늘'], 'what':['날씨']}},
    {'question':'충남천안아산의오늘의날씨는!?', 'result':{'when':['오늘'], 'what':['날씨'], 'where':['충남','천안','아산']}},
    {'question':'오늘하루비올확률은?', 'result':{'when':['오늘'], 'what':['비'], 'detail':['확률']}},
    {'question':'오늘춘천쪽일기예보가어떤지??', 'result':{'when':['오늘'], 'what':['예보'], 'where':['춘천']}},
    {'question':'중국의 지금 기온은??', 'result':{'when':['지금'], 'what':['기온'], 'where':['중국']}},
    {'question':'오늘오전에서울에비올확률은??', 'result':{'when':['오늘','오전'], 'what':['비'], 'where':['서울'], 'detail':['확률']}},
    {'question':'오늘서울에눈이올확률은??', 'result':{'when':['오늘'], 'what':['눈'], 'where':['서울'], 'detail':['확률']}},
    {'question':'오늘저녁7시 서울에 비올 확률은?', 'result':{'when':['오늘','저녁','7시'], 'what':['비'], 'where':['서울'], 'detail':['확률']}},
    {'question':'12일에 서울에 비올확률은', 'result':{'when':['12일'], 'what':['비'], 'where':['서울'], 'detail':['확률']}},
    {'question':'오늘추워요?', 'result':{'when':['오늘'], 'what':['추워']}},
    {'question':'5월5일경주지역날씨', 'result':{'when':['5월','5일'], 'what':['날씨'], 'where':['경주']}},
    {'question':'5월5일날씨는?', 'result':{'when':['5월','5일'], 'what':['날씨']}},
    {'question':'오늘비와여?', 'result':{'when':['오늘'], 'what':['비']}},
    {'question':'오늘밤10시에비올확률점', 'result':{'when':['오늘','밤','10시'], 'what':['비'], 'detail':['확률']}},
    {'question':'5월5일 경주지역비올확률', 'result':{'when':['5월','5일'], 'what':['비'], 'where':['경주'], 'detail':['확률']}},
    {'question':'금요일경주날씨', 'result':{'when':['금요일'], 'what':['날씨'], 'where':['경주']}},
    {'question':'오늘 6시 서울에 비올 확률은?', 'result':{'when':['6시'], 'what':['비'], 'where':['서울'], 'detail':['확률']}},
    {'question':'5월5일날비가올확률은?', 'result':{'when':['5월','5일'], 'what':['비'], 'detail':['확률']}},
    {'question':'5월4일 따뜻한가요?', 'result':{'when':['5월','4일'], 'what':['따뜻']}},
    {'question':'5월4일안목날씨는', 'result':{'when':['5월','4일'], 'what':['날씨'], 'where':['안목']}},
    {'question':'내일날씨좀알려주세용!!', 'result':{'when':['내일'], 'what':['날씨']}},
    {'question':'5월5일 천안 날씨알고싶어요', 'result':{'when':['5월','5일'], 'what':['날씨'], 'where':['천안']}},
    {'question':'서울에비올확률은?', 'result':{'what':['비'], 'where':['서울'], 'detail':['확률']}},
    {'question':'이번주주말서울날씨알려주세요', 'result':{'when':['주말'], 'what':['날씨'], 'where':['서울']}},
    {'question':'이번주말에 비오나요?', 'result':{'when':['주말'], 'what':['비']}},
    {'question':'5.3.서울날씨 알려주세요', 'result':{'when':['5.3'], 'what':['날씨'], 'where':['서울']}},
    {'question':'내일서울경기날씨', 'result':{'when':['내일'], 'what':['날씨'], 'where':['서울','경기']}},
    {'question':'3일과4일의날씨는?', 'result':{'when':['3일'], 'what':['날씨']}},
    {'question':'5월3일 날씨는?', 'result':{'when':['5월','3일'], 'what':['날씨']}},
    {'question':'내일서울에비가오나요?', 'result':{'when':['내일'], 'what':['비'], 'where':['서울']}},
    {'question':'오늘 저녁7시 서울에 비올확률은?', 'result':{'when':['7시'], 'what':['비'], 'where':['서울'], 'what':['확률']}},
    {'question':'저녁7시 서울의 온도는?', 'result':{'when':['7시'], 'what':['온도'], 'where':['서울']}},
    {'question':'5월4일 신천날씨정보', 'result':{'when':['5월','4일'], 'what':['날씨'], 'where':['신천']}},
    {'question':'오늘저녁에비와요??', 'result':{'when':['저녁'], 'what':['비']}}
]

'''
model = word2vec.Word2Vec.load_word2vec_format('./jisik.question.word2vec.5w.100e.model',binary=True)

key_word_list_dict = {}
for each in weather_data_list:
    for fld in each.keys():
        if fld == 'question':
            continue
        if fld == 'result':
            result_dict = each[fld]

            for key in result_dict:
                if key not in key_word_list_dict:
                    key_word_list_dict[key] = set()
                for word in result_dict[key]:
                    key_word_list_dict[key].add(word)
'''


'''
# 질문에서 파라메터를 뽑아 딕셔너리로 리턴
def get_parameters(question):
    twitter = Twitter()
    hannanum = Hannanum()
    mecab = Mecab()

    noun = []

    for each in twitter.morphs(question):
        noun.append(each)
        print each

    value_dict = {'who': 0.0, 'when': 0.0, 'where': 0.0, 'what': 0.0, 'why': 0.0, 'how': 0.0, 'detail': 0.0}
    result_dict = {'who': [], 'when': [], 'where': [], 'what': [], 'why': [], 'how': [], 'detail': []}

    for word in noun:
        if word not in model:
            continue
        fld_score_dict = {}
        for fld in key_word_list_dict:
            score_list = []

            for w in key_word_list_dict[fld]:
                if w.decode('utf-8') not in model:
                    continue
                score_list.append(model.similarity(w.decode('utf-8'), word))

            fld_score_dict[fld] = np.mean(score_list)
        sorted_list = sorted(fld_score_dict.items(), key=lambda (k, v): (v, k), reverse=True)

        for sub in sorted_list:
            # print word, sub
            if value_dict.get(sub[0]) < sub[1] and sub[1] > 0.2:
                value_dict[sub[0]] = sub[1]
                # result_dict[sub[0]].append(word.encode('utf-8'))
                result_dict[sub[0]].append(word.encode('utf-8'))
                break;

    for key in result_dict.keys():
        if len(result_dict[key]) == 0:
            del result_dict[key]

    for key in result_dict.keys():
        print key
        for each in result_dict[key]:
            print each

    formatted_dict = {'result': result_dict}

    return formatted_dict
'''


# 질문을 입력하면 파라메터를 찾아 출력
'''
def print_parameter(question):
    result_list = get_parameters(question)['result']

    for key in result_list.keys():
        print key,
        for each in result_list[key]:
            print each
'''


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
    question = question.decode('utf-8')
    #result_dict = get_parameters(question)['result']
    result_dict = {}
    for each in params:
        feat = max(each['prob'].iteritems(), key=operator.itemgetter(1))[0]
        if not result_dict.has_key(feat):
            result_dict[feat] = []
        result_dict[feat].append(each['word'])

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
        return wc.showWeatherInfo()
    else:
        print '날씨 예보'
        wf = ForecastWeather()
        wf.getWeatherInfo(where, get_date_diff(question.encode('utf-8')))


def is_now(when):
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

    if cur_year == cal_str[0][0] and cur_month == cal_str[0][1] and cur_date == cal_str[0][2]:
        return True
    else:
        return False


def get_date_diff(when):
    en = mtranslate.translate(when, 'en', 'kr')
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

