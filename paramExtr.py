#-*- coding=utf-8 -*-
from sklearn.externals import joblib
import util as ut
import gensim, logging
import Cython

remove_list = ["JKS", "JKC", "JKG", "JKO", "JKB", "JKV", "JKQ", "JC", "JX", "EP", "EF", "EC", "ETN","ETM", "XPN", "XSN", "XSV", "XSA", "XR", "SF", "SE", "SS", "SP", "SO", "SW"]

class ParamExtr(object):
    def __init__(self, useLoad = True):
        self.useAllW2V = False
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

    def build(self, cat, corpus, reprDict, distMethod):
        self.distMethods[cat] = distMethod
        if 'W' in distMethod.values():
            #Word2Vec
            self.buildIndvW2VM(cat, corpus)
            self.learnFeat(cat, reprDict)
        if 'E' in distMethod.values():
            #Elastic Search
            pass

    def learnFeat(self, cat, rawReprDict):
        reprDict = {}
        for k in rawReprList.keys():
            reprDict[k] = ut.parseSentence(' '.join(rawReprDict[k])).split(' ')

        if not self.feat.has_key(cat):
            self.feat[cat] = {}

        newFeats = reprDict.keys()
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
                        replFeat = ut.replNum(w)#.decode('utf-8')
                        if replFeat in model.vocab:
                            val = model.similarity(replFeat, replWord)
                            l.append(val)
                    d['prob'][k] = sum(l) / len(l)
                res.append(d)
        return res

    def extrFeat(self, cat, ques):
        if 'W' in self.distMethods[cat]:
            if self.useAllW2V:
                model = self.allW2VM
            else:
                model = self.indvW2VM[cat]
            return self.extrFeatW2V(model, self.feat[cat], ques)
        else:
            return "Not Defined"


if __name__ == "__main__":
    test = paramExtr(False)
