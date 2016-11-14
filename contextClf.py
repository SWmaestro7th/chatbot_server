#-*- coding: utf-8 -*-
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.externals import joblib
import util as ut
from sklearn.grid_search import GridSearchCV
from sklearn.svm import LinearSVC
import numpy as np
import random

class ContextClf(object):
    def __init__(self, useLoad= True):
        if useLoad:
            self.load()
        else:
            self.allCorpus = {}
            self.vectorizer = None
            self.categories = None
            self.clfModel = None

    def load(self):
        self.allCorpus = joblib.load(ut.rp('contextClf/allCorpus.dat'))
        self.vectorizer = joblib.load(ut.rp('contextClf/vectorizer.dat'))
        self.categories = joblib.load(ut.rp('contextClf/categories.dat'))
        self.clfModel = joblib.load(ut.rp('contextClf/clf.model'))
    def save(self):
        joblib.dump(self.allCorpus, ut.rp('contextClf/allCorpus.dat'),compress=3)
        joblib.dump(self.vectorizer, ut.rp('contextClf/vectorizer.dat'), compress=3)
        joblib.dump(self.categories, ut.rp('contextClf/categories.dat'), compress=3)
        joblib.dump(self.clfModel, ut.rp('contextClf/clf.model'), compress=3)

    def addCorpus(self, catName, corpus):
        if catName not in self.allCorpus:
            self.allCorpus[catName] = []
        self.allCorpus[catName].extend(corpus)
        return True

    def shflCorpus(self):
        pass

    def build(self):
        cntPerCat = min([len(x) for x in self.allCorpus.values()])
        quesList = sum([x[0:cntPerCat] for x in self.allCorpus.values()], [])
        catList = sum([[x]*cntPerCat for x in self.allCorpus.keys()], [])
        combined = list(zip(quesList, catList))
        random.shuffle(combined)
        quesList[:], catList[:] = zip(*combined)

        #print quesList[0]
        #print catList[0]
        self.categories = self.allCorpus.keys()
        self.vectorizer = TfidfVectorizer(ngram_range=(1,2))
        Xlist = self.vectorizer.fit_transform(quesList)
        Ylist = [self.categories.index(x) for x in catList]
        print 'build prepared'

        svc_param = {'C':np.logspace(-2, 0, 20)}
        gs_svc = GridSearchCV(LinearSVC(),svc_param,cv=5,n_jobs=12)
        gs_svc.fit(Xlist, Ylist)
        #logging.debug(gs_svc.best_params_)
        #logging.debug('score : ' + str(gs_svc.best_score_))
        print gs_svc.best_params_
        print 'score : ' + str(gs_svc.best_score_)
        self.clfModel = LinearSVC(C=gs_svc.best_params_['C'])
        self.clfModel.fit(Xlist, Ylist)
        self.save()

    def predict(self, ques):
        if self.vectorizer == None or self.categories == None or self.clfModel == None:
            return [('Not built yet', 100)]

        parsedQues = ut.parseSentence(ques)
        testX = self.vectorizer.transform([parsedQues])
        predList = self.clfModel.predict(testX)
        return [(self.categories[predList[0]], 100)]

if __name__ == '__main__':
    cc = ContextClf(useLoad=True)
    '''
    defDict = {}
    defList = joblib.load(ut.rp('contextClf/defList.dat'))
    for x in defList:
        if not defDict.has_key(x['cat'].decode('utf-8')):
            defDict[x['cat'].decode('utf-8')] = []
        defDict[x['cat'].decode('utf-8')].append(x['ques'].decode('utf-8'))

    for k in defDict.keys():
        print k
        print defDict[k][0]
        cc.addCorpus(k, defDict[k])
    cc.build()
    '''

    print cc.predict('오늘 날씨')[0][0]
    print cc.predict('오늘 날씨'.decode('utf-8'))[0][0]
    print cc.predict('이효리 학력')[0][0]
    print cc.predict('이효리 학력'.decode('utf-8'))[0][0]
    print cc.predict('오늘 서울 비오나요')[0][0]
    print cc.predict('오늘 서울 비오나요'.decode('utf-8'))[0][0]
    print cc.predict('이번주 로또 번호')[0][0]
    print cc.predict('이번주 로또 번호'.decode('utf-8'))[0][0]
    print cc.predict('소녀시대 다시만난세계 금영 번호좀여')[0][0]
    print cc.predict('소녀시대 다시만난세계 금영 번호좀여'.decode('utf-8'))[0][0]
