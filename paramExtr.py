#-*- coding=utf-8 -*-
from sklearn.externals import joblib
import util as ut
import gensim, logging
import Cython
import os
from elasticsearch import helpers
from elasticsearch import Elasticsearch

"""
This Tags are less important than the others.
But this list is not used yet
"""
remove_list = ["JKS", "JKC", "JKG", "JKO", "JKB", "JKV", "JKQ", "JC", "JX", "EP", "EF", "EC", "ETN","ETM", "XPN", "XSN", "XSV", "XSA", "XR", "SF", "SE", "SS", "SP", "SO", "SW"]

"""
Varaibles to connect with ElasticSearch Server
"""
_LOCAL_SEARCH_URL = 'http://127.0.0.1:9200'
es_client = Elasticsearch(_LOCAL_SEARCH_URL, timeout=6000)

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
        self.useAllW2V = False#True
        self.THR = 0.3
        #Show progress of word2vec
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
        if useLoad:
            self.load()
        else:
            self.allW2VM = None
            self.indvW2VM = {}
            self.reprDict = {}
            self.distMethods = {}
            self.save()

    def save(self):
        """
        Save some variables used in this instance using joblib.dump
        """
        if self.indvW2VM != None:
            joblib.dump(self.indvW2VM, ut.rp("paramExtr/indvW2V.model"))
        if self.reprDict != None:
            joblib.dump(self.reprDict, ut.rp("paramExtr/reprDict.dat"))
        if self.allW2VM != None:
            joblib.dump(self.allW2VM, ut.rp("paramExtr/allW2V.model"))
        if self.distMethods != None:
            joblib.dump(self.distMethods, ut.rp("paramExtr/distMethods.dat"))

    def load(self):
        """
        Load variables from dumped files
        """
        self.indvW2VM = joblib.load(ut.rp("paramExtr/indvW2V.model"))
        self.reprDict = joblib.load(ut.rp("paramExtr/reprDict.dat"))
        self.distMethods = joblib.load(ut.rp("paramExtr/distMethods.dat"))
        try:
            self.allW2VM = joblib.load(ut.rp("paramExtr/allW2V.model"))
        except:
            self.allW2VM = None
        for cat in self.distMethods:
            for k in self.distMethods[cat]:
                if self.distMethods[cat][k] == 'e':
                    self._buildES(cat, k, self.reprDict[cat][k])


    def _buildAllW2VM(self, allCorpus):
        """
        Build word2vec model using all corpus
        NOTE : indvW2V makes each category's model but allW2V is shared among categories, so It doesn't have to rebuild often.
        """
        sentences = []
        for v in allCorpus.values():
            sentences.extend([ut.replNum(ut.parseSentence(x)).split(' ') for x in v])
        self.allW2VM = gensim.models.Word2Vec(sentences, min_count=1, size=100, workers=12)
        self.save()

    def _buildIndvW2VM(self, cat, corpus):
        """
        Build the category's word2vec model using corpus
        """
        sentences = [ut.replNum(ut.parseSentence(x)).split(' ') for x in corpus]
        self.indvW2VM[cat] = gensim.models.Word2Vec(sentences, min_count=1, size=100, workers=12)
        self.save()

    def _buildES(self, cat, feat, reprList):
        """
        Build the category's elasticsearch model using corpus
        """
        if not self.reprDict.has_key(cat):
            self.reprDict[cat] = {}
        self.reprDict[cat][feat] = reprList
        lowerCat = cat.lower()
        os.system(ut.rp('elastic/init_entity_search.sh ') + lowerCat + ' ' + feat)
        actionList = []
        uniqReprList = list(set(reprList))
        for each in uniqReprList:
            action = {
                "_index":lowerCat,
                "_type":feat,
                "_source":{"name":each}
            }
            actionList.append(action)

        for success, info in helpers.parallel_bulk(es_client, actionList,chunk_size=200,thread_count=12):
            print success, info

        self.save()

    def build(self, cat, corpus, reprDict, distMethod):
        """
        Build parameter extractor model.
        NOTE: distMethod can be W(word2vec) or E(elasticsearch)
        """
        self.distMethods[cat] = distMethod
        if not self.useAllW2V and 'w' in distMethod.values():
            #Word2Vec
            self._buildIndvW2VM(cat, corpus)
        for k in distMethod:
            if distMethod[k] == 'w':
                self._learnParam(cat, k, reprDict[k])
            if distMethod[k] == 'e':
                #Elastic Search
                self._buildES(cat, k, reprDict[k])

    def _learnParam(self, cat, feat, rawReprList):
        """
        Learn reprentative words of each feature
        """
        reprList = ut.parseSentence(' '.join(rawReprList)).split(' ')

        if not self.reprDict.has_key(cat):
            self.reprDict[cat] = {}

        if not self.reprDict[cat].has_key(feat):
            self.reprDict[cat][feat] = []
        self.reprDict[cat][feat].extend(reprList)

        self.save()

    def _extrParamW2V(self, model, reprList, ques):
        """
        extract parameters using word2vec model
        """
        if model == None:
            raise Exception("W2VM Not Found")
        parsedQues = ut.parseSentence(ques)
        res = []
        for word in parsedQues.split(' '):
            replWord = ut.replNum(word)
            if replWord in model.vocab:
                l = []
                for w in reprList:
                    replRepr = ut.replNum(w)#.decode('utf-8')
                    if replRepr in model.vocab:
                        val = model.similarity(replRepr, replWord)
                        l.append(val)
                d = (word, sum(l) / len(l))
                if d[1] > self.THR:
                    res.append(d)
        return res

    def _extrParamES(self, cat, feat, ques):
        """
        extract parameters using elasticsearch model
        """
        lowerCat = cat.lower()
        query = ques
        d = es_client.search(
            index=lowerCat,
            doc_type=feat,
            size=10,
            body={
                'query':
                    {'multi_match' : {
                                "type": "best_fields",
                                "fields": ['','name'],
                                "query": query,
                                "operator": 'or',
                        }
                    }
            })

        res = []
        for each in  d['hits']['hits']:
            res.append((each['_source']['name'], each['_score']))
        return res

    def extrParam(self, cat, ques):
        """
        Extract Parameters from question
        """
        if 'w' in self.distMethods[cat].values():
            if self.useAllW2V:
                model = self.allW2VM
            else:
                model = self.indvW2VM[cat]
        res = {}
        for k in self.distMethods[cat]:
            if self.distMethods[cat][k] == 'w':
                res[k] = self._extrParamW2V(model, self.reprDict[cat][k], ques)
            if self.distMethods[cat][k] == 'e':
                res[k] = self._extrParamES(cat, k, ques)

        resRmTag = {}
        for k in res.keys():
            resRmTag[k] = [(x[0].split('\t')[0], x[1]) for x in res[k]]

        return resRmTag


if __name__ == "__main__":
    test = paramExtr(False)
