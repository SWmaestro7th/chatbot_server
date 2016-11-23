# -*- coding: utf-8 -*-
import requests
import json
import re
from scrapy.selector import HtmlXPathSelector
import datetime as dt
import sys
import operator

def make_words(res_dict):
    #[u'{"bnum": 42, "gno": 510, "gdate": "2012-09-08", "nums": [12, 29, 32, 33, 39, 40]}']
    return "{0}에 추첨된 {1}회 로또 당첨번호는 {2} 이며 보너스 번호는 {3} 입니다.".format(res_dict["gdate"], res_dict["gno"], ", ".join([str(x) for x in res_dict["nums"]]), res_dict["bnum"])

def getAnswer(full_text, params):
    parsed_dict = {}
    for k in params:
        parsed_dict[k] = [x[0] for x in params[k] if x[1] > 0.3]

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
        pred_round.append(most_recent_round)

    u = 'http://lotto.kaisyu.com/api?method=get&gno='
    li = []

    for r in pred_round:
        try:
            d = requests.get(u + str(r)).text
            li.append(json.loads(d))
        except:
            try:
                d = requests.get(u + str(r-1)).text
                li.append(json.loads(d))
            except:
                return u'잘못된 날짜가 들어있는 것 같습니다!'
    tmp = '\n'.join([make_words(x) for x in li])
    if tmp is not unicode:
        tmp = tmp.decode('utf-8')
    return tmp
