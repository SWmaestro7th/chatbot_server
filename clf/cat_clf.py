#-*- coding: utf-8 -*-
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.externals import joblib
import json
import csv
import tagger
import logging
import numpy as np
from sklearn.grid_search import GridSearchCV
from sklearn.svm import LinearSVC
import os
logging.basicConfig(level=logging.DEBUG)

class CategoryClassifier(object):
    def __init__(self, load_at_boot = True):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        if not self.dir_path.endswith('/'):
            self.dir_path += '/'
        self.dir_path += 'data/'
        self.PARSED_FILENAME = self.dir_path + 'all_types_mecab_with_info.csv'
        self.LOAD_AT_BOOT = load_at_boot
        if self.LOAD_AT_BOOT:
            self.load()
        else:
            self.types = ["헤어스타일", "항공", "날씨", "방송", "교통", "동영상", "지도", "공공 데이터", "인물", "음식", "음악", "쇼핑", "영화 예매", "스포츠 경기", "환율", "주식", "로또 당첨 번호", "급식", "알바", "게임", "노래방", "놀이동산", "백과사전", "지식인", "블로그", "상담답변", "미분류" ]

            self.use_types = ["스포츠 경기", "날씨", "급식", "노래방", "놀이동산", "로또 당첨 번호", "인물"]
            self.q_list = None
            self.a_list = None
            self.s_list = None
            self.vectorizer = None
            self.x_list = None
            self.clf_model = None
            self._init_list()
            self._vectorize()
            self._learn_with_linear_svc()
            self.save()

        logging.debug('CategoryClassifier __init__ complete')


    def _truncate_list(self, cnt_dict, q_list, a_list, s_list):
        decoded_types = [x.decode('utf-8') for x in self.types]
        decoded_use_types = [x.decode('utf-8') for x in self.use_types]
        use_types_idx = [decoded_types.index(i)+1 for i in decoded_use_types]
        min_type_cnt = min([cnt_dict[x] for x in use_types_idx])
        new_cnt_dict = {x:0 for x in use_types_idx}
        trun_q_list = []
        trun_a_list = []
        trun_s_list = []
        idx = 0
        total_cnt = min_type_cnt * len(use_types_idx)
        logging.debug('total_cnt : ' + str(total_cnt))
        while total_cnt > 0:
            if s_list[idx] in use_types_idx:
                if new_cnt_dict[s_list[idx]] < min_type_cnt:
                    new_cnt_dict[s_list[idx]] += 1
                    trun_q_list.append(q_list[idx])
                    trun_a_list.append(a_list[idx])
                    trun_s_list.append(s_list[idx])
                    total_cnt -= 1
            idx += 1

        return trun_q_list, trun_a_list, trun_s_list

    def _load_file(self, cate_num=None):
        ifp = open(self.PARSED_FILENAME, 'r')
        csv_reader = csv.reader(ifp)
        row_cnt = 0
        cnt_dict = {i+1:0 for i in xrange(len(self.types))}
        q_list = []
        a_list = []
        s_list = []
        for line in csv_reader:
            if row_cnt % 100000 == 0:
                logging.debug('init_list proceeding... : ' + str(row_cnt))
            s = int(line[2])
            if cate_num == None or s == cate_num:
                q_list.append(line[0])
                a_list.append(line[1])
                s_list.append(s)
                cnt_dict[s] += 1
            row_cnt += 1

        for key in cnt_dict:
            if cnt_dict[key] > 0:
                logging.debug(self.types[key-1] + " : " + str(cnt_dict[key]))
        return cnt_dict, q_list, a_list, s_list

    def _init_list(self):
        cnt_dict,q_list,a_list,s_list = self._load_file()
        trun_q_list, trun_a_list, trun_s_list = self._truncate_list(cnt_dict, q_list, a_list, s_list)
        self.q_list = trun_q_list
        self.a_list = trun_a_list
        self.s_list = trun_s_list

    def _vectorize(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1,2))
        self.x_list = self.vectorizer.fit_transform(self.q_list)

    def _learn_with_linear_svc(self):
        svc_param = {'C':np.logspace(-2, 0, 20)}
        gs_svc = GridSearchCV(LinearSVC(),svc_param,cv=5,n_jobs=12)
        gs_svc.fit(self.x_list, self.s_list)
        logging.debug(gs_svc.best_params_)
        logging.debug('score : ' + str(gs_svc.best_score_))
        self.clf_model = LinearSVC(C=gs_svc.best_params_['C'])
        self.clf_model.fit(self.x_list, self.s_list)
        logging.debug('model initialized')

    def save(self):
        logging.debug(self.dir_path+'CategoryClassifier save started')
        joblib.dump(self.types,self.dir_path+'jisik_types.dat',compress=3)
        joblib.dump(self.use_types,self.dir_path+'jisik_use_types.dat',compress=3)
        joblib.dump(self.vectorizer,self.dir_path+'jisik_vectorizer.dat',compress=3)
        joblib.dump(self.clf_model,self.dir_path+'jisik_classify_linear_svc.model',compress=3)
        joblib.dump(self.q_list,self.dir_path+'jisik_q_list.dat',compress=3)
        joblib.dump(self.a_list,self.dir_path+'jisik_a_list.dat',compress=3)
        joblib.dump(self.x_list,self.dir_path+'jisik_x_list.dat',compress=3)
        joblib.dump(self.s_list,self.dir_path+'jisik_s_list.dat',compress=3)
        logging.debug('CategoryClassifier save finished')

    def load(self):
        logging.debug('CategoryClassifier load started')
        self.types = joblib.load(self.dir_path+'jisik_types.dat')
        self.use_types = joblib.load(self.dir_path+'jisik_use_types.dat')
        self.vectorizer = joblib.load(self.dir_path+'jisik_vectorizer.dat')
        self.clf_model = joblib.load(self.dir_path+'jisik_classify_linear_svc.model')
        self.q_list = joblib.load(self.dir_path+'jisik_q_list.dat')
        self.a_list = joblib.load(self.dir_path+'jisik_a_list.dat')
        self.x_list = joblib.load(self.dir_path+'jisik_x_list.dat')
        self.s_list = joblib.load(self.dir_path+'jisik_s_list.dat')
        logging.debug('CategoryClassifier load finished')

    def predict(self, question):
        spaced_sentence = tagger.parse_sentence(question)
        test_x = self.vectorizer.transform([spaced_sentence])
        predict_list = self.clf_model.predict(test_x)
        logging.debug(str(predict_list))
        return self.types[predict_list[0]-1]

    def add_category(self, name, corpus=None):
        if name in self.use_types:
            #Already included
            return
        min_count = len(self.q_list)/len(self.use_types)
        self.types.append(name)
        self.use_types.append(name)
        if name in self.types:
            cnt_dict,q_list,a_list,s_list = self._load_file(self.types.index(name)+1)
            if len(q_list) > min_count:
                self.q_list.extend(q_list[:min_count])
                self.a_list.extend(a_list[:min_count])
                self.s_list.extend(s_list[:min_count])
            else:
                self.q_list.extend(q_list)
                self.a_list.extend(a_list)
                self.s_list.extend(s_list)
        else:
            s = self.use_types.index(name)
            for each in corpus[:min_count]:
                self.q_list.append(tagger.parse_sentence(each['qustion']))
                self.a_list.append(each['answer'])
                self.s_list.append(s)
        self._vectorize()
        self._learn_with_linear_svc()
        self.save()

if __name__ == "__main__":
    category_classifier = CategoryClassifier(True)
    print category_classifier.predict('오늘 부산 비오나요')
    category_classifier.add_category('인물')
    print category_classifier.predict('한예슬 생일이 언제인가요')
