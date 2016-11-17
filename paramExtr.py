#-*- coding=utf-8 -*-
from sklearn.externals import joblib
import util as ut
import gensim, logging
import Cython

remove_list = ["JKS", "JKC", "JKG", "JKO", "JKB", "JKV", "JKQ", "JC", "JX", "EP", "EF", "EC", "ETN","ETM", "XPN", "XSN", "XSV", "XSA", "XR", "SF", "SE", "SS", "SP", "SO", "SW"]

class ParamExtr(object):
    def __init__(self, useLoad = True):
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
        if useLoad:
            self.load()
        else:
            self.allW2VM = None
            self.indvW2VM = {}
            self.feat = {}
            self.distMethods = {}
            self.save()

    def save(self):
        if self.indvW2VM != None:
            joblib.dump(self.indvW2VM, ut.rp("paramExtr/indvW2V.model"))
        if self.feat != None:
            joblib.dump(self.feat, ut.rp("paramExtr/feat.dat"))
        if self.allW2VM != None:
            joblib.dump(self.allW2VM, ut.rp("paramExtr/allW2V.model"))
        if self.distMethods != None:
            joblib.dump(self.distMethods, ut.rp("paramExtr/distMethods.dat"))

    def load(self):
        self.indvW2VM = joblib.load(ut.rp("paramExtr/indvW2V.model"))
        self.feat = joblib.load(ut.rp("paramExtr/feat.dat"))
        self.distMethods = joblib.load(ut.rp("paramExtr/distMethods.dat"))
        try:
            self.allW2VM = joblib.load(ut.rp("paramExtr/allW2V.model"))
        except:
            self.allW2VM = None

    def buildAllW2VM(self, allCorpus):
        sentences = []
        for v in allCorpus.values():
            sentences.extend([ut.replNum(x).split(' ') for x in v])
        self.allW2VM = gensim.models.Word2Vec(sentences, min_count=1, size=5000, workers=12)
        self.save()

    def buildIndvW2VM(self, cat, corpus):
        sentences = [ut.replNum(x).split(' ') for x in corpus]
        self.indvW2VM[cat] = gensim.models.Word2Vec(sentences, min_count=1, size=5000, workers=12)
        self.save()

    def build(self, cat, corpus, testList, distMethod):
        self.distMethods[cat] = distMethod
        if distMethod == 'W2V':
            self.buildIndvW2VM(cat, corpus)
            self.learnFeat(cat, testList)
        else:
            #다른 방식
            pass

    def learnFeat(self, cat, testData):
        if not self.feat.has_key(cat):
            self.feat[cat] = {}

        newFeats = list(set(sum([x['result'].keys() for x in testData], [])))
        for each in newFeats:
            if not self.feat[cat].has_key(each):
                self.feat[cat][each] = []

        for each in testData:
            for k in each['result'].keys():
                self.feat[cat][k].extend(each['result'][k])
        self.save()

    def extrFeatW2V(self, model, feats, ques):
        parsedQues = ut.parseSentence(ques)
        if model == None:
            return "W2VM Not Found"
        res = []
        for word in parsedQues.split(' '):
            d = {'word' : word.split('\t')[0], 'prob' : {}}
            replWord = ut.replNum(word)
            if replWord in model.vocab:
                for k in feats.keys():
                    l = []
                    for w in feats[k]:
                        replFeat = ut.replNum(w).decode('utf-8')
                        if replFeat in model.vocab:
                            val = model.similarity(replFeat, replWord)
                            print replFeat + ' : ' + str(val)
                            l.append(val)
                    #l = [model.similarity(x, replWord) for x in feats[k]]
                    d['prob'][k] = sum(l) / len(l)
                res.append(d)
        return res

    def extrFeat(self, cat, ques):
        if self.distMethods[cat] == 'W2V':
            if self.indvW2VM.has_key(cat):
                model = self.indvW2VM[cat]
            else:
                model = self.allW2VM
            return self.extrFeatW2V(model, self.feat[cat], ques)
        else:
            return "Not Defined"


if __name__ == "__main__":
    test = paramExtr(False)
    print 'test'
