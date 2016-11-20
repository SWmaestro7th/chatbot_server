#-*- coding=utf-8 -*-
from sklearn.externals import joblib
import util as ut
import gensim, logging
import Cython

"""
This Tags are less important than the others.
But this list is not used yet
"""
remove_list = ["JKS", "JKC", "JKG", "JKO", "JKB", "JKV", "JKQ", "JC", "JX", "EP", "EF", "EC", "ETN","ETM", "XPN", "XSN", "XSV", "XSA", "XR", "SF", "SE", "SS", "SP", "SO", "SW"]

"""
Parameter extractor class
This class provides function which extracts feature-related words from question
"""
class ParamExtr(object):
    def __init__(self, useLoad = True):
        """
        Parameter extractor constructor
        Initialize each variables used in this instance
        """
        #useAllW2V defines word2vec model whether indvW2V or allW2V
        self.useAllW2V = False
        #Show progress of word2vec
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
        """
        Save some variables used in this instance using joblib.dump
        """
        if self.indvW2VM != None:
            joblib.dump(self.indvW2VM, ut.rp("paramExtr/indvW2V.model"))
        if self.feat != None:
            joblib.dump(self.feat, ut.rp("paramExtr/feat.dat"))
        if self.allW2VM != None:
            joblib.dump(self.allW2VM, ut.rp("paramExtr/allW2V.model"))
        if self.distMethods != None:
            joblib.dump(self.distMethods, ut.rp("paramExtr/distMethods.dat"))

    def load(self):
        """
        Load variables from dumped files
        """
        self.indvW2VM = joblib.load(ut.rp("paramExtr/indvW2V.model"))
        self.feat = joblib.load(ut.rp("paramExtr/feat.dat"))
        self.distMethods = joblib.load(ut.rp("paramExtr/distMethods.dat"))
        try:
            self.allW2VM = joblib.load(ut.rp("paramExtr/allW2V.model"))
        except:
            self.allW2VM = None

    def _buildAllW2VM(self, allCorpus):
        """
        Build word2vec model using all corpus
        NOTE : indvW2V makes each category's model but allW2V is shared among categories, so It doesn't have to rebuild often.
        """
        sentences = []
        for v in allCorpus.values():
            sentences.extend([ut.replNum(x).split(' ') for x in v])
        self.allW2VM = gensim.models.Word2Vec(sentences, min_count=1, size=500, workers=12)
        self.save()

    def _buildIndvW2VM(self, cat, corpus):
        """
        Build the category's word2vec model using corpus
        """
        sentences = [ut.replNum(x).split(' ') for x in corpus]
        self.indvW2VM[cat] = gensim.models.Word2Vec(sentences, min_count=1, size=5000, workers=12)
        self.save()

    def build(self, cat, corpus, reprDict, distMethod):
        """
        Build parameter extractor model.
        NOTE: distMethod can be W(word2vec) or E(elasticsearch)
        """
        self.distMethods[cat] = distMethod
        if 'W' in distMethod.values():
            #Word2Vec
            self._buildIndvW2VM(cat, corpus)
            self._learnFeat(cat, reprDict)
        if 'E' in distMethod.values():
            #Elastic Search
            pass

    def _learnFeat(self, cat, rawReprDict):
        """
        Learn reprentative words of each feature
        """
        reprDict = {}
        for k in rawReprDict.keys():
            reprDict[k] = ut.parseSentence(' '.join(rawReprDict[k])).split(' ')

        if not self.feat.has_key(cat):
            self.feat[cat] = {}

        for each in reprDict.keys():
            if not self.feat[cat].has_key(each):
                self.feat[cat][each] = []
            self.feat[cat][each].extend(reprDict[each])

        self.save()

    def _extrFeatW2V(self, model, feats, ques):
        """
        extract parameters using word2vec model
        """
        parsedQues = ut.parseSentence(ques)
        if model == None:
            raise Exception("W2VM Not Found")
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
        """
        Extract
        """
        if 'W' in self.distMethods[cat]:
            if self.useAllW2V:
                model = self.allW2VM
            else:
                model = self.indvW2VM[cat]
            return self._extrFeatW2V(model, self.feat[cat], ques)
        else:
            raise Exception("Not Defined")#This Code will be removed if elasticsearch is implemented


if __name__ == "__main__":
    test = paramExtr(False)
