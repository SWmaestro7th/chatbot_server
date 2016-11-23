# -*- coding: utf-8 -*-
import requests
import json
import re
from scrapy.selector import HtmlXPathSelector
import datetime as dt
import sys
import operator

class PeopleCrawler(object):
    def make_intro_sen(self, res, def_str='이름 정보가 없습니다.\n'):
        try:
            return "이름: {0}\n".format(res['m_name'].encode('utf-8'))
        except:
            return def_str

    def make_birth_sen(self, res, def_str='생년월일 정보가 없습니다.\n'):
        try:
            return "생년월일: {0}년 {1}월 {2}일\n".format(res['birth_year'].encode('utf-8'), res['birth_mm'].encode('utf-8'), res['birth_dd'].encode('utf-8'))
        except:
            return def_str

    def make_birth_place_sen(self, res, def_str='출생지 정보가 없습니다.\n'):
        try:
            return "출생지: {0}\n".format(res['birth_place'].encode('utf-8'))
        except:
            return def_str

    def make_career_sen(self, res, def_str='경력사항 정보가 없습니다.\n'):
        try:
            if len(res['career_info']) == 0:
                return ''
            career_list = ['경력사항']
            for each in res['career_info']:
                career_list.append('  {0}~{1}\t{2}'.format(each['start_date'].encode('utf-8'), each['end_date'].encode('utf-8'), each['contents'].encode('utf-8')))
            return '\n'.join(career_list)
        except:
            return def_str

    def make_debuts_sen(self, res, def_str='데뷔 정보가 없습니다.\n'):
        try:
            if len(res['debuts_info']) == 0: return ''
            debuts_list = ['데뷔사항']
            for each in res['debuts_info']:
                debuts_list.append('  {0}년 {1}'.format(each['debuts_year'].encode('utf-8'), each['debuts_work'].encode('utf-8')))
            return '\n'.join(debuts_list)
        except:
            return def_str

    def make_job_sen(self, res, def_str='직업 정보가 없습니다.\n'):
        try:
            if len(res['job_info']) == 0:
                return ''
            job_list = ['직업정보']
            for each in res['job_info']:
                job_list.append('  {0}'.format(each['job_name'].encode('utf-8')))
            return '\n'.join(job_list)
        except:
            return def_str

    def make_management_sen(self, res, def_str='소속사 정보가 없습니다.\n'):
        try:
            if len(res['management_info']) == 0:
                return ''
            management_list = ['소속사정보']
            for each in res['management_info']:
                management_list.append('  {0}'.format(each['management_list'].encode('utf-8')))
            return '\n'.join(management_list)
        except:
            return def_str

    def make_prize_sen(self, res, def_str='수상경력 정보가 없습니다.\n'):
        try:
            if len(res['prize_info']) == 0:
                return ''
            prize_list = ['수상경력 정보']
            for each in res['prize_info']:
                prize_list.append('  {0}\t{1}'.format(each['prize_year'].encode('utf-8'), each['prize_contents'].encode('utf-8')))
            return '\n'.join(prize_list)
        except:
            return def_str

    def make_school_sen(self, res, def_str='학력 정보가 없습니다.\n'):
        try:
            if len(res['school']) == 0:
                return ''
            prize_list = ['학력 정보']
            for each in res['school']:
                enter_year = int(each['enter_year']) or ''
                gradu_year = int(each['gradu_year']) or ''
                prize_list.append('  {0}~{1}\t{2} {3}'.format(enter_year, gradu_year, each['school_name'].encode('utf-8'), each['major'].encode('utf-8')))
            return '\n'.join(prize_list)
        except:
            return def_str

    def make_height_sen(self, res, def_str='키 정보가 없습니다.\n'):
        try:
            return "신장: {0}\n".format(res['height'].encode('utf-8'))
        except:
            return def_str

    def make_weight_sen(self, res, def_str='체중 정보가 없습니다.\n'):
        try:
            return "체중: {0}\n".format(res['weight'].encode('utf-8'))
        except:
            return def_str

    def make_all_sen(self, res):
        all_str = []
        all_str.append(self.make_intro_sen(res,''))
        all_str.append(self.make_birth_sen(res,''))
        all_str.append(self.make_birth_place_sen(res,''))
        all_str.append(self.make_career_sen(res,''))
        all_str.append(self.make_debuts_sen(res,''))
        all_str.append(self.make_job_sen(res,''))
        all_str.append(self.make_management_sen(res,''))
        all_str.append(self.make_prize_sen(res,''))
        all_str.append(self.make_school_sen(res,''))
        all_str.append(self.make_height_sen(res,''))
        all_str.append(self.make_weight_sen(res,''))

        return '\n'.join(all_str)


    def getAnswer(self, full_text, params):
        parsed_dict = {}
        for k in params:
            parsed_dict[k] = [x[0] for x in params[k] if x[1] > 0.2]

        if parsed_dict.has_key('who'):
            who_str = ' '.join(parsed_dict['who'])
        else:
            who_str = ''
        if parsed_dict.has_key('detail'):
            detail_str = ''.join(parsed_dict['detail'])
        else:
            detail_str = ''
        u = 'http://people.search.naver.com/search.naver?sm=sbx_hty&where=nexearch&ie=utf8&query=' + who_str + '&x=0&y=0'
        d = requests.get(u).text
        try:
            tot_res = json.loads(d.split('"result":')[1].split(' } } ,')[0])
            if tot_res['total'] <= 0:
                raise Exception(u'해당하는 인물을 찾지 못했습니다. 좀 더 정확하게 말씀해주세요.')
            res = tot_res['itemList'][0]
        except:
            searched = False
            for each in parsed_dict['who']:
                who_str = each
                u = 'http://people.search.naver.com/search.naver?sm=sbx_hty&where=nexearch&ie=utf8&query=' + who_str + '&x=0&y=0'
                d = requests.get(u).text
                try:
                    tot_res = json.loads(d.split('"result":')[1].split(' } } ,')[0])
                    if tot_res['total'] <= 0:
                        continue
                    res = tot_res['itemList'][0]
                    searched = True
                    break
                except:
                    continue
            if not searched:
                for idx in range(0, len(parsed_dict['who']), 2):
                    who_str = parsed_dict['who'][idx] + (parsed_dict['who'][idx+1] if idx+1 < len(parsed_dict['who']) else u'')
                    u = 'http://people.search.naver.com/search.naver?sm=sbx_hty&where=nexearch&ie=utf8&query=' + who_str + '&x=0&y=0'
                    d = requests.get(u).text
                    try:
                        tot_res = json.loads(d.split('"result":')[1].split(' } } ,')[0])
                        if tot_res['total'] <= 0:
                            continue
                        res = tot_res['itemList'][0]
                        searched = True
                        break
                    except:
                        continue
                if not searched:
                    return u'해당하는 인물을 찾지 못했습니다. 좀 더 정확하게 말씀해주세요.'

        if any([x.decode('utf-8') in detail_str for x in ['프로필', '정보']]):
            tmp = self.make_all_sen(res)
            if type(tmp) is not unicode:
                tmp = tmp.decode('utf-8')
            return tmp

        res_list = []
        if any([x.decode('utf-8') in detail_str for x in ['생일', '생년', '생년월일', '출생', '몇 년 생', '몇년생']]):
            res_list.append(self.make_birth_sen(res))

        if any([x.decode('utf-8') in detail_str for x in ['출생', '출생지']]):
            res_list.append(self.make_birth_place_sen(res))

        if any([x.decode('utf-8') in detail_str for x in ['커리어', '경력']]):
            res_list.append(self.make_career_sen(res))

        if any([x.decode('utf-8') in detail_str for x in ['데뷔', '경력']]):
            res_list.append(self.make_debuts_sen(res))

        if any([x.decode('utf-8') in detail_str for x in ['직업', '경력']]):
            res_list.append(self.make_job_sen(res))

        if any([x.decode('utf-8') in detail_str for x in ['직업', '경력']]):
            res_list.append(self.make_job_sen(res))

        if any([x.decode('utf-8') in detail_str for x in ['소속사', '소속', '경력']]):
            res_list.append(self.make_management_sen(res))

        if any([x.decode('utf-8') in detail_str for x in ['상', '수상', '경력']]):
            res_list.append(self.make_prize_sen(res))

        if any([x.decode('utf-8') in detail_str for x in ['학교', '초등학교', '중학교', '고등학교', '대학교', '학력']]):
            res_list.append(self.make_school_sen(res))

        if any([x.decode('utf-8') in detail_str for x in ['키', '신장']]):
            res_list.append(self.make_height_sen(res))

        if any([x.decode('utf-8') in detail_str for x in ['체중', '몸무게']]):
            res_list.append(self.make_weight_sen(res))

        if len(res_list) == 0:
            tmp = self.make_all_sen(res)
            if type(tmp) is not unicode:
                tmp = tmp.decode('utf-8')
        else:
            tmp = '\n'.join(res_list)
            if type(tmp) is not unicode:
                tmp = tmp.decode('utf-8')
        return tmp

def getAnswer(full_text, params):
    cr = PeopleCrawler()
    return cr.getAnswer(full_text, params)
