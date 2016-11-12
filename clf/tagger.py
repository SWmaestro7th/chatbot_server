from konlpy.tag import Mecab
from konlpy.tag import Twitter

mecab = Mecab()
def parse_sentence(sentence):
    #twitter = Twitter()
    if type(sentence) is not unicode:
        t = sentence.decode('utf-8')
    else:
        t = sentence
    p = mecab.pos(t)
    result = [x[0] + '\t' + x[1] for x in p]
    return ' '.join(result)
