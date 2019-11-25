
import json
import subprocess
from flask import Flask, request
from tools import *

app = Flask(__name__)


with open('config_tests.json', 'r') as f:
    config = json.load(f)


conn = pymysql.connect(
    host=config['HOST'],
    user=config['USER'],
    password=config['PASS'],
    database='banana'
)

def cria_db(filename = 'database/script_create.sql'):
    global config
    with open(filename, 'rb') as f:
        subprocess.run(
            [
                config['MYSQL'], 
                '-u', config['USER'], 
                '-p' + config['PASS'], 
                '-h', config['HOST']
            ], 
            stdin=f
        )

cria_db()

@app.route('/tarefa', methods=['POST'])
def add_task():
    print(1)
    info = {}
    info['description'] = request.values.get('description')
    info['difficulty'] = request.values.get('difficulty')
    
    print(cria_tarefa(conn, info))
    return ""


@app.route('/tarefa', methods=['GET'])
def lista_todos_tasks():
    print(2)
    print(lista_tarefas(conn))
    return ""
    

@app.route('/tarefa/<id_task>', methods=['DELETE'])
def deleta_task(id_task):
    print(3)
    print(remove_tarefa(conn, id_task))
    return ""


@app.route('/tarefa/<id_task>', methods=['POST'])
def atualiza_task(id_task):
    print(4)
    info = {}
    info['description'] = request.values.get('description')
    info['difficulty'] = request.values.get('difficulty')
    return muda_info_tarefa(conn, id_task, info)



# Healthcheck
@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return ""


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")