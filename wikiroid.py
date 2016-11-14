#-*- coding:utf-8 -*-
from sklearn.externals import joblib
import contextClf
import util as ut

exec("\
def findWeather(ques, params, dist_method):\
    return '날씨가 맑을 예정입니다.'\
")
exec("\
def findPeople(ques, params, dist_method):\
    return 'People Test'\
")
exec("\
def findSports(ques, params, dist_method):\
    return 'Sports Test'\
")
exec("\
def findLotto(ques, params, dist_method):\
    return 'Lotto Test'\
")
exec("\
def findKaraoke(ques, params, dist_method):\
    return 'Karaoke Test'\
")
exec("\
def findMeal(ques, params, dist_method):\
    return 'Meal Test'\
")

class Handler(object):
    def __init__(self, useLoad=True):
        if useLoad:
            self.load()
        else:
            self.categories = []
            self.contextClf = contextClf.ContextClf(useLoad=False)
            self.paramExtr = None
            self.save()

    def save(self):
        joblib.dump(self.categories, ut.rp('wikiroid/categories.dat'),compress=3)

    def load(self):
        self.categories = joblib.load(ut.rp('wikiroid/categories.dat'))
        self.contextClf = contextClf.ContextClf(True)
        self.paramExtr = None

    def addCategory(self, name, quesCorpus, testList, findCode, distMethod):
        return True

    def reply(self, ques, emitFunc):
        predRslt = self._predContext(ques)
        emitFunc('classifier', predRslt)
        cat = predRslt[0][0]
        params = self._extrParam(ques, cat)

        emitFunc('extractor', params)
        f = eval('find' + cat)
        emitFunc('reply', f(ques, params, True))

    def _predContext(self, ques):
        #return [('Weather', 10.1), ('Lotto', 5.5), ('People', 1.01)]
        return self.contextClf.predict(ques)

    def _extrParam(self, ques, cat):
        return {'who' : ['테스트'], 'detail' : ['테스트']}

if __name__ == '__main__':
    test = Handler(useLoad=False)
