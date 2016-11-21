import os
from konlpy.tag import Mecab

"""
Initial global variables
"""
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
if not DIR_PATH.endswith('/'):
    DIR_PATH += '/'
DIR_PATH += 'data/'

mecab = Mecab()

def rp(subpath):
    """
    Make subpath to full path
    """
    return DIR_PATH + subpath

def parseSentence(sentence):
    """
    Parse sentence using mecab and add some tag
    NOTE : tab is used to separator. so if sentence has tab at first,
    This can be a cause of errors
    """
    if type(sentence) is not unicode:
        t = sentence.decode('utf-8')
    else:
        t = sentence
    p = mecab.pos(t)
    result = [x[0] + '\t' + x[1] for x in p]
    return ' '.join(result)

def replNum(s):
    """
    """
    t = s[:]
    for ch in '0123456789':
        t = t.replace(ch, 'd')
    return t
