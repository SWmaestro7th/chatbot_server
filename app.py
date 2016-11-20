#-*- coding:utf-8 -*-
#!flask/bin/python
from flask import Flask
from flask import request
from flask_socketio import SocketIO
from flask_socketio import send, emit
import wikiroid

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
    print('receive message: ' + str(json))
    emit('get', json)
    try:
        handler.reply(json['question'], emit)
    except Exception as e:
        print "--------------------------------"
        print e
        print "--------------------------------"

"""
Add new category in wikiroid
"""
@app.route('/new', methods=['GET']) # MUST CHANGE TO POST
def add_new_category():
    try:
        name = request.args.get('name')
        desc = request.args.get('desc')
        corpus = request.args.get('corpus')
        reprList = request.args.get('featDict')
        findFunc = request.args.get('findFunc')
        distMethod = request.args.get('distMethod')
        if handler.addCategory(name, desc, corpus, testList, findFunc, distMethod):
            return 'Succeed'
        else:
            return 'Failed'
    except Exception as e:
        print "--------------------------------"
        print e
        print "--------------------------------"

if __name__ =='__main__':
    socketio.run(app, host='0.0.0.0', port=10101)
