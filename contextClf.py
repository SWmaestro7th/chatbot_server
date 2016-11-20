#-*- coding: utf-8 -*-
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.externals import joblib
import util as ut
from sklearn.grid_search import GridSearchCV
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
import numpy as np
import random
import operator

"""
Context classifier class
This class provides building classifier model from corpus and predicting using
classifier model
"""
class ContextClf(object):
    def __init__(self, useLoad= True):
        """
        Context classifier constructor
        Initialize each variables used in this instance
        """
        if useLoad:
            self.load()
        else:
            self.vectorizer = None
            self.categories = None
            self.clfModel = None
            self.save()

    def load(self):
        """
        Load variables from dumped files
        """
        try:
            self.vectorizer = joblib.load(ut.rp('contextClf/vectorizer.dat'))
            self.categories = joblib.load(ut.rp('contextClf/categories.dat'))
            self.clfModel = joblib.load(ut.rp('contextClf/clf.model'))
        except:
            self.vectorizer = None
            self.categories = None
            self.clfModel = None

    def save(self):
        """
        Save some variables used in this instance using joblib.dump
        """
        if self.vectorizer != None:
            joblib.dump(self.vectorizer, ut.rp('contextClf/vectorizer.dat'), compress=3)
        if self.categories != None:
            joblib.dump(self.categories, ut.rp('contextClf/categories.dat'), compress=3)
        if self.clfModel != None:
            joblib.dump(self.clfModel, ut.rp('contextClf/clf.model'), compress=3)

    def shflCorpus(self):
        """
        Shuffle Corpus to make better classifier model
        NOTE : This function is not implemented yet
        """
        pass

    def build(self, allCorpus):
        """
        Build classifier model from corpus
        """
        #Make question and category list to use at sklearn
        #NOTE: each category's corpus has different amount of corpus, so we equalize each category's corpus
        cntPerCat = min(map(len, allCorpus.values()))
        quesList = sum([x[0:cntPerCat] for x in allCorpus.values()], [])
        catList = sum([[x]*cntPerCat for x in allCorpus.keys()], [])
        #shuffle question and category list to build better model
        combined = list(zip(quesList, catList))
        random.shuffle(combined)
        quesList[:], catList[:] = zip(*combined)

        self.categories = allCorpus.keys()
        #We use TfidVectorizer and bigram
        self.vectorizer = TfidfVectorizer(ngram_range=(1,2))
        Xlist = self.vectorizer.fit_transform(map(ut.replNum, quesList))
        Ylist = [self.categories.index(x) for x in catList]
        print 'build prepared'

        #Search best model
        svc_param = {'C':np.logspace(-2, 0, 20)}
        gs_svc = GridSearchCV(LinearSVC(),svc_param,cv=5,n_jobs=12)
        gs_svc.fit(Xlist, Ylist)
        #logging.debug(gs_svc.best_params_)
        #logging.debug('score : ' + str(gs_svc.best_score_))
        print gs_svc.best_params_
        print 'score : ' + str(gs_svc.best_score_)
        svm = LinearSVC(C=gs_svc.best_params_['C'])
        self.clfModel = CalibratedClassifierCV(base_estimator=svm)

        #Build model
        self.clfModel.fit(Xlist, Ylist)
        #save model
        self.save()

    def predict(self, ques):
        """
        Predict category of the question
        """
        if self.vectorizer == None or self.categories == None or self.clfModel == None:
            return [('Not built yet', 100)]

        parsedQues = ut.parseSentence(ques)
        testX = self.vectorizer.transform([ut.replNum(parsedQues)])
        predList = self.clfModel.predict_proba(testX)
        res = [(self.categories[x], predList[0][x]) for x in range(len(self.categories))]
        sortedRes = sorted(res, key=operator.itemgetter(1), reverse=True)
        return sortedRes

if __name__ == '__main__':
    """
    This part is just test code
    """
    cc = ContextClf(useLoad=True)
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
