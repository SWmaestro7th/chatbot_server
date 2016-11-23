# -*- coding: utf-8 -*-
import requests
import json
import re
from scrapy.selector import HtmlXPathSelector
import datetime as dt
import sys
import operator
import random

def make_words(res_dict):
    #[u'{"bnum": 42, "gno": 510, "gdate": "2012-09-08", "nums": [12, 29, 32, 33, 39, 40]}']
    return "{0}에 추첨된 {1}회 로또 당첨번호는 {2} 이며 보너스 번호는 {3} 입니다.".format(res_dict["gdate"], res_dict["gno"], ", ".join([str(x) for x in res_dict["nums"]]), res_dict["bnum"])

def make_random_numbers():
    nums = range(1, 46)
    random.shuffle(nums)
    return nums[:6]

def getAnswer(full_text, params):
    parsed_dict = {}
    for k in params:
        parsed_dict[k] = [x[0] for x in params[k] if x[1] > 0.3]

    if type(full_text) is not unicode:
        full_text = full_text.decode('utf-8')

    if u'추천' in full_text:
        return u'저는 개인적으로 ' + ', '.join([str(x) for x in make_random_numbers()]) + u'을 추천드립니다.'
    first_date = dt.date(2007,12,8)
    first_round = 262
    today_date = dt.datetime.now().date()
    most_recent_lotto_date = today_date - dt.timedelta((today_date-first_date).days % 7)
    most_recent_round = first_round + (today_date-first_date).days / 7
    def get_round_from_date(inp_date):
        if (inp_date - first_date).days % 7 == 0:
            return first_round + (inp_date - first_date).days / 7

    pred_round = []
    if parsed_dict.has_key('when'):
        when_str = ' '.join(parsed_dict['when'])
        if type(when_str) is not unicode:
            when_str = when_str.decode('utf-8')
    else:
        when_str = u''
    all_date_re = re.compile(u'[0-9]{4} 년 [0-9]{1,2} 월 [0-9]{1,2} 일')
    date_re = re.compile(u'[0-9]{1,2} 월 [0-9]{1,2} 일')
    round_re = re.compile(u'[0-9]{3}')

    all_date_info = all_date_re.findall(when_str)
    date_info = date_re.findall(when_str)
    round_info = round_re.findall(when_str)
    #round_re = re.compile('d{3}')
    #date_re = re.compile('d{1,2} 월 d{1,2} (일)?')
    #all_date_re = re.compile('d{4} 년 d{1,2} 월 d{1,2} (일)?')
    if len(all_date_info) > 0:
        #tmp_re = re.compile('[0-9]{4} 년 [0-9]{1,2} 월 [0-9]{1,2} (일)?')
        #tmp = tmp_re.findall(full_text).split(' ')
        tmp = [x.split(' ') for x in all_date_info]
        d = [dt.date(int(x[0]),int(x[2]),int(x[4])) for x in tmp]
        pred_round.extend([get_round_from_date(x) for x in d])
    elif len(date_info) > 0:
        #tmp_re = re.compile('[0-9]{1,2} 월 [0-9]{1,2} (일)?')
        #tmp = tmp_re.findall(full_text).split(' ')
        tmp = [x.split(' ') for x in date_info]
        d = [dt.date(today_date.year(),int(x[2]),int(x[4])) for x in tmp]
        pred_round.extend([get_round_from_date(x) for x in d])
    elif len(round_info) > 0:
        #tmp_re = re.compile('[0-9]{3}')
        #pred_round.extend(tmp_re.findall(full_text))
        pred_round.extend(round_info)
    else:
        if u'번주' in full_text or u'번 주' in full_text:
            cnt = full_text.count(u'저')
            if cnt >= 1:
                cnt -= 1
            pred_round.append(most_recent_round - cnt)
        else:
            pred_round.append(most_recent_round)

    u = 'http://lotto.kaisyu.com/api?method=get&gno='
    li = []

    for r in pred_round:
        try:
            d = requests.get(u + str(r)).text
            tmp = make_words(json.loads(d))
            if type(tmp) is not unicode:
                tmp = tmp.decode('utf-8')
            li.append(tmp)
        except:
            d = requests.get(u + str(most_recent_round)).text
            tmp = make_words(json.loads(d))
            if type(tmp) is not unicode:
                tmp = tmp.decode('utf-8')
            li.append(u'미래의 로또번호는 알수 없습니다. 대신 가장 최근의 로또번호를 알려드립니다.\n' + tmp)


    tmp = '\n'.join(li)
    if type(tmp) is not unicode:
        tmp = tmp.decode('utf-8')
    return tmp
