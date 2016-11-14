#!flask/bin/python
from flask import Flask
from flask import request
from flask_socketio import SocketIO
from flask_socketio import send, emit
import wikiroid

handler = wikiroid.Handler()
app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return "Server running"

@socketio.on('query')
def handle_message(json):
    print('receive message: ' + str(json))
    handler.reply(json['question'], emit)

@app.route('/new', methods=['GET']) # MUST CHANGE TO POST
def add_new_category():
    name = request.args.get('name')
    corpus = request.args.get('corpus')
    testList = request.args.get('testList')
    findFunc = request.args.get('findFunc')
    distMethod = request.args.get('distMethod')
    if handler.addCategory(name, corpus, testList, findFunc, distMethod):
        return 'Succeed'
    else:
        return 'Failed'

if __name__ =='__main__':
    app.run(host='0.0.0.0', port=8888)
