#-*- coding:utf-8 -*-
from sklearn.externals import joblib
import contextClf
import paramExtr
import util as ut
import sys
sys.path.append(ut.rp('reply/'))

"""
Main handler to run wikiroid
This class provides mapping between flask app and each component
"""
class Handler(object):
    def __init__(self, useLoad=True):
        """
        Handler constructor
        Initialize each variables used in this instance
        """
        if useLoad:
            self.load()
        else:
            self.allCorpus = {}
            self.allInfo = {}
            self.descs = []
            self.contextClf = contextClf.ContextClf(useLoad=False)
            self.paramExtr = paramExtr.ParamExtr(useLoad=False)
            self.save()

    def save(self):
        """
        Save some variables used in this instance using joblib.dump
        """
        joblib.dump(self.allCorpus, ut.rp('wikiroid/allCorpus.dat'),compress=3)
        joblib.dump(self.allInfo, ut.rp('wikiroid/allInfo.dat'),compress=3)
        joblib.dump(self.descs, ut.rp('wikiroid/descs.dat'),compress=3)

    def saveCode(self, cat, rawCode):
        """
        Save reply code in reply directory
        """
        fp = open(ut.rp('reply/' + cat + '.py'), 'w')
        if type(rawCode) is not unicode:
            code = rawCode.decode('utf-8')
        else:
            code = rawCode
        fp.write(code.encode('utf-8'))
        fp.close()

    def removeCode(self, cat):
        """
        Save reply code in reply directory
        """
        #Don't need to remove exactly
        pass

    def load(self):
        """
        Load variables from dumped files
        """
        self.allCorpus = joblib.load(ut.rp('wikiroid/allCorpus.dat'))
        self.allInfo = joblib.load(ut.rp('wikiroid/allInfo.dat'))
        self.descs = joblib.load(ut.rp('wikiroid/descs.dat'))
        self.contextClf = contextClf.ContextClf(useLoad=True)
        self.paramExtr = paramExtr.ParamExtr(useLoad=True)

    def _addCorpus(self, cat, corpus):
        """
        add new category's corpus in allcorpus
        """
        if cat not in self.allCorpus:
            self.allCorpus[cat] = []
        self.allCorpus[cat].extend(corpus)
        return True

    def _removeCorpus(self, cat):
        """
        remove category's corpus in allcorpus
        """
        self.allCorpus.pop(cat, None)
        return True

    def addCategory(self, cat, desc, quesCorpus, reprDict, findCode, distMethod):
        """
        Add new category
        """
        self.allInfo[cat] = {'name':cat, 'desc':desc, 'corpus':quesCorpus, 'reprDict':reprDict, 'findCode':findCode, 'distMethod':distMethod}
        self.descs.append({'name':cat, 'desc':desc, 'corpus':[quesCorpus[0], quesCorpus[1]]})
        self.saveCode(cat, findCode)
        self._addCorpus(cat, quesCorpus)
        self.paramExtr.build(cat, quesCorpus, reprDict, distMethod)
        self.save()
        return True

    def removeCategory(self, cat):
        """
        Remove a category
        """
        self._removeCorpus(cat)

        for idx in range(self.descs):
            if selfs.descs[idx]['name'] == cat:
                del(selfs.descs[idx])
                break
        self.allInfo.pop(cat, None)
        self.save()
        return True

    def build(self):
        """
        Build context classifier model
        """
        self.contextClf.build(self.allCorpus)
        return True

    def reply(self, ques, emitFunc):
        """
        Reply to the question
        """
        #Classify the category of the question
        predRslt = self._predContext(ques)
        #Emit context classifier's reseult
        emitFunc('classifier', predRslt)
        cat = predRslt[0][0]
        #Extract parameters in question
        params = self._extrParam(ques, cat)

        #Emit parameter Extractor's result
        emitFunc('extractor', params)
        #Import answer-making code
        exec('import ' + cat)
        exec('reload(' + cat + ')')
        getAnswer = eval(cat + '.getAnswer')
        #Make an answer and emit it
        emitFunc('reply', getAnswer(ques, params))

    def getCategoryList(self):
        return self.descs

    def getCategoryInfo(self, name):
        return self.allInfo[name]

    def _predContext(self, ques):
        """
        Predict category of the question
        """
        #return [('Weather', 10.1), ('Lotto', 5.5), ('People', 1.01)]
        return self.contextClf.predict(ques)

    def _extrParam(self, ques, cat):
        """
        Extract parameters of the question
        """
        #return {'who' : ['테스트'], 'detail' : ['테스트']}
        return self.paramExtr.extrParam(cat, ques)

if __name__ == '__main__':
    """
    This part is just Test Code
    """
    useLoad = False
    test = Handler(useLoad)
    if not useLoad:
        defDict = {}
        defList = joblib.load(ut.rp('contextClf/defList.dat'))
        for x in defList:
            if x['cat'] is not unicode:
                cat = x['cat'].decode('utf-8')
            else:
                cat = x['cat']

            if not defDict.has_key(cat):
                defDict[cat] = []

            if x['ques'] is not unicode:
                ques = x['ques'].decode('utf-8')
            else:
                ques = x['ques']
            defDict[cat].append(ques)

        print "defList Load complete"
        for k in defDict.keys():
            if k == 'People':
                peopleTestDataRaw = joblib.load(ut.rp('paramExtr/cate-people.dat'))

                peopleReprDict = {y : [] for y in list(set(sum([x['result'].keys() for x in peopleTestDataRaw], [])))}
                for each in peopleTestDataRaw:
                    for w in each['result']:
                        peopleReprDict[w].extend(each['result'][w])

                fp=open(ut.rp('reply/People.py'))
                code = []
                for line in fp:
                    code.append(line)
                fp.close()
                test.addCategory(k, 'Desc: ' + k, defDict[k], peopleReprDict, ''.join(code), {'who':'w', 'detail':'w'})
            elif k == 'Lotto':
                lottoTestDataRaw = joblib.load(ut.rp('paramExtr/cate-lotto.dat'))

                lottoReprDict = {y : [] for y in list(set(sum([x['result'].keys() for x in lottoTestDataRaw], [])))}
                for each in lottoTestDataRaw:
                    for w in each['result']:
                        lottoReprDict[w].extend(each['result'][w])

                fp=open(ut.rp('reply/Lotto.py'))
                code = []
                for line in fp:
                    code.append(line)
                fp.close()

                test.addCategory(k, 'Desc: ' + k, defDict[k], lottoReprDict, ''.join(code), {'when':'w'})
            elif k == 'Weather':
                weatherTestDataRaw = joblib.load(ut.rp('paramExtr/cate-weather.dat'))

                weatherReprDict = {y : [] for y in list(set(sum([x['result'].keys() for x in weatherTestDataRaw], [])))}
                for each in weatherTestDataRaw:
                    for w in each['result']:
                        weatherReprDict[w].extend(each['result'][w])

                fp = open(ut.rp('reply/Weather.py'))
                code = []
                for line in fp:
                    code.append(line)
                fp.close()
                test.addCategory(k, 'Desc: ' + k, defDict[k], weatherReprDict, ''.join(code), {'when':'w', 'where':'w', 'what':'w', 'detail':'w'})

        print "addCategory Complete"
        test.build()

    print "build complete"
    def test_print(a,b):
        print a + " : " + unicode(b)
    #test.reply("내일 서울 비오나요", test_print)
    test.reply(u"서석고등학교", test_print)
    #test.reply("어제 로또 번호", test_print)
    #test.reply("Test", test_print)
