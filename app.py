#!flask/bin/python
from flask import Flask
from flask import request
from clf import cat_clf


app = Flask(__name__)
category_classfier = cat_clf.CategoryClassifier()

@app.route('/')
def index():
    return "Server running"

@app.route('/api/predict', methods=['GET'])
def get_answer():
    question = request.args.get('question')
    print question
    if question == '' or question == None:
        return 'please add question parameter'
    return category_classfier.predict(question)

if __name__ =='__main__':
    app.run(host='0.0.0.0', port=8888)
