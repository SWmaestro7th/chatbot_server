import os
from konlpy.tag import Mecab

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
mecab = Mecab()

if not DIR_PATH.endswith('/'):
    DIR_PATH += '/'
DIR_PATH += 'data/'

def rp(subpath):
    return DIR_PATH + subpath

def parseSentence(sentence):
    if type(sentence) is not unicode:
        t = sentence.decode('utf-8')
    else:
        t = sentence
    p = mecab.pos(t)
    result = [x[0] + '\t' + x[1] for x in p]
    return ' '.join(result)

def replNum(s):
    t = s[:]
    for ch in '0123456789':
        t = t.replace(ch, 'd')
    return t
