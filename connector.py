from flask import Flask, request
import requests
import sys, os

app = Flask(__name__)
env = os.environ.get('SERVER')

@app.route('/tarefa', methods=['POST'])
def add_task():
    to_add = {"description" : request.values.get('description'), "difficulty" : request.values.get('difficulty')}
    requests.post(str(env) + "/tarefa", data = to_add)
    txt = requests.get(str(env)+'/tarefa').text
    print(txt)

    return txt


@app.route('/tarefa', methods=['GET'])
def list_task():
    txt = requests.get(str(env)+'/tarefa').text
    return txt


@app.route('/tarefa/<id_task>', methods=['DELETE'])
def delete_task(id_task):
     requests.delete(str(env) + "/tarefa/" +id_task)
     txt = requests.get(str(env)+'/tarefa').text

     return txt

@app.route('/tarefa/<id_task>', methods=['POST'])
def update_task(id_task):
    to_add = {"description" : request.values.get('description'), "difficulty" : request.values.get('difficulty')}
    requests.post(str(env) + "/tarefa/"+id_task, data = to_add)
    txt = requests.get(str(env)+'/tarefa').text
    print(txt)

    return txt

#export SERVER="http://localhost:5000"; python connector.py


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)