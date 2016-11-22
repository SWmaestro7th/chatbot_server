#-*- coding:utf-8 -*-
#!flask/bin/python
from flask import Flask
from flask import request
from flask_socketio import SocketIO
from flask_socketio import send, emit
import wikiroid
import json

"""
Initialize Flask, socketio, and wikiroid instance
"""
app = Flask(__name__)
socketio = SocketIO(app)
handler = wikiroid.Handler()

"""
Root address routes to simple message"
"""
@app.route('/')
def index():
    return "Server running"

"""
Receive query message from socketio and reply answer
"""
@socketio.on('query')
def handle_message(json):
    if json.has_key('question'):
        print('receive message: ' + str(json))
        emit('get', json)
        try:
            question = json['question']
            print question
            if type(question) is not unicode:
                question = question.decode('utf-8')
            print type(question)
            print question
            handler.reply(question, emit)
        except Exception as e:
            print "--------------------------------"
            print e
            print "--------------------------------"
    else:
        name = json['name']
        if type(name) is not unicode:
            name= name.decode('utf-8')
        emit('info', handler.getCategoryInfo(name))

"""
Add new category in wikiroid
"""
@socketio.on('new')
def handle_message(json):
    print('receive message: ' + str(json))
    emit('get', json)

    name = json['name']
    if type(name) is not unicode:
        name = name.decode('utf-8')
    print type(name)
    print name
    #raw_input(1)

    desc = json['desc']
    if type(desc) is not unicode:
        name = name.decode('utf-8')
    print type(desc)
    print desc
    #raw_input(2)

    corpus = json['corpus']
    for idx in range(len(corpus)):
        if type(corpus[idx]) is not unicode:
            corpus[idx] = corpus[idx].decode('utf-8')
    print type(corpus)
    print str(corpus)
    #raw_input(3)

    reprDict = json['reprDict']
    for k in reprDict.keys():
        for idx in range(len(reprDict[k])):
            if type(reprDict[k][idx]) is not unicode:
                reprDict[k][idx] = reprDict[k][idx].decode('utf-8')
    print type(reprDict)
    print str(reprDict)
    #raw_input(4)

    findFunc = json['findFunc']
    if type(findFunc) is not unicode:
        findFunc = findFunc.decode('utf-8')
    print type(findFunc)
    print findFunc
    #raw_input(5)

    distMethod = json['distMethod']
    for k in distMethod.keys():
        if type(distMethod[k]) is not unicode:
            distMethod[k] = distMethod[k].decode('utf-8')
    print type(distMethod)
    print str(distMethod)
    #raw_input(6)

    if handler.addCategory(name, desc, corpus, reprDict, findFunc, distMethod) and handler.build():
        emit('new_result', 'Succeed')
        emit('new_category', {"name":name, "desc":desc, "corpus":[corpus[0], corpus[1]]})
    else:
        emit('new_result', 'Failed')

"""
Return Category informations
"""
@app.route('/list', methods=['GET']) # MUST CHANGE TO POST
def getCategoryList():
    tmp = handler.getCategoryList()
    """
    for idx in range(len(tmp)):
        if type(tmp[idx]['name']) is unicode:
            tmp[idx]['name'] = tmp[idx]['name'].encode('utf-8')
        if type(tmp[idx]['desc']) is unicode:
            tmp[idx]['desc'] = tmp[idx]['desc'].encode('utf-8')
        if type(tmp[idx]['corpus'][0]) is unicode:
            tmp[idx]['corpus'][0] = tmp[idx]['corpus'][0].encode('utf-8')
        if type(tmp[idx]['corpus'][1]) is unicode:
            tmp[idx]['corpus'][1] = tmp[idx]['corpus'][1].encode('utf-8')
    """
    return str(tmp)

"""
Return Category informations
"""
@socketio.on('ask_list')
def handle_message():
    emit('list', handler.getCategoryList())

"""
Return Category informations
"""
@socketio.on('remove')
def handle_message(json):
    if json.has_key('name'):
        print('receive message: ' + str(json))
        name = json['name']
        if type(name) is not unicode:
            name = name.decode('utf-8')
        print type(name)
        print name
        try:
            handler.removeCategory(name)
            emit('remove_result', 'Succeed')
        except:
            emit('remove_result', 'Failed')


if __name__ =='__main__':
    socketio.run(app, host='0.0.0.0', port=10102)
