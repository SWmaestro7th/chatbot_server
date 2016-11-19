#-*- coding:utf-8 -*-
from sklearn.externals import joblib
import contextClf
import paramExtr
import util as ut
import sys
sys.path.append(ut.rp('reply/'))

class Handler(object):
    def __init__(self, useLoad=True):
        if useLoad:
            self.load()
        else:
            self.allCorpus = {}
            self.contextClf = contextClf.ContextClf(useLoad=False)
            self.paramExtr = paramExtr.ParamExtr(useLoad=False)
            self.save()

    def save(self):
        joblib.dump(self.allCorpus, ut.rp('wikiroid/allCorpus.dat'),compress=3)

    def saveCode(self, cat, code):
        fp = open(ut.rp('reply/' + cat + '.py'), 'w')
        fp.write(code)
        fp.close()

    def load(self):
        self.allCorpus = joblib.load(ut.rp('wikiroid/allCorpus.dat'))
        self.contextClf = contextClf.ContextClf(useLoad=True)
        self.paramExtr = paramExtr.ParamExtr(useLoad=True)

    def _addCorpus(self, cat, corpus):
        if cat not in self.allCorpus:
            self.allCorpus[cat] = []
        self.allCorpus[cat].extend(corpus)
        return True

    def addCategory(self, cat, quesCorpus, testList, findCode, distMethod):
        self.saveCode(cat, findCode)
        self._addCorpus(cat, quesCorpus)
        self.paramExtr.build(cat, quesCorpus, testList, distMethod)
        self.save()
        return True

    def build(self):
        self.contextClf.build(self.allCorpus)

    def reply(self, ques, emitFunc):
        predRslt = self._predContext(ques)
        emitFunc('classifier', predRslt)
        cat = predRslt[0][0]
        params = self._extrParam(ques, cat)

        emitFunc('extractor', params)
        exec('import ' + cat)
        exec('reload(' + cat + ')')
        getAnswer = eval(cat + '.getAnswer')
        emitFunc('reply', getAnswer(ques, params))

    def _predContext(self, ques):
        #return [('Weather', 10.1), ('Lotto', 5.5), ('People', 1.01)]
        return self.contextClf.predict(ques)

    def _extrParam(self, ques, cat):
        #return {'who' : ['테스트'], 'detail' : ['테스트']}
        return self.paramExtr.extrFeat(cat, ques)

if __name__ == '__main__':
    useLoad = True
    test = Handler(useLoad)
    if not useLoad:
        defDict = {}
        defList = joblib.load(ut.rp('contextClf/defList.dat'))
        peopleTestDataRaw = joblib.load(ut.rp('paramExtr/cate-people.dat'))
        lottoTestDataRaw = joblib.load(ut.rp('paramExtr/cate-lotto.dat'))
        for x in defList:
            if not defDict.has_key(x['cat'].decode('utf-8')):
                defDict[x['cat'].decode('utf-8')] = []
            defDict[x['cat'].decode('utf-8')].append(x['ques'].decode('utf-8'))

        print "defList Load complete"
        for k in defDict.keys():
            if k == 'People':
                fp=open(ut.rp('wikiroid/people_crawler.py'))
                code = []
                for line in fp:
                    code.append(line)
                fp.close()

                test.addCategory(k, defDict[k], peopleTestDataRaw, ''.join(code), 'W2V')
            elif k == 'Lotto':
                fp=open(ut.rp('wikiroid/lotto_crawler.py'))
                code = []
                for line in fp:
                    code.append(line)
                fp.close()

                test.addCategory(k, defDict[k], lottoTestDataRaw, ''.join(code), 'W2V')
            elif k == 'AAA':
                code ="\
def getAnswer(a, b):\n\
    return '1'\n\
"
                testData = []
                test.addCategory(k, defDict[k], testData, code, 'W2V')
                break
        print "addCategory Complete"
        test.build()

    print "build complete"
    def test_print(a,b):
        print a + " : " + str(b)
    test.reply("손나은 정보", test_print)
