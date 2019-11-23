import pymysql


def cria_tarefa(conn, info):
    print(info)
    with conn.cursor() as cursor:
        try:
            cursor.execute("""INSERT INTO tarefa (description, difficulty)
                           VALUES (%s, %s);""", (info["description"], info["difficulty"]))
            conn.commit()
            return 23123
        except:
            print(222)
            raise ValueError(f'Não posso inserir {info["description"]} na tabela tarefa')


def acha_tarefa(conn, info):
    with conn.cursor() as cursor:
        cursor.execute('SELECT description, difficulty FROM tarefa WHERE id_tarefa = %s', 
                      (info["id_tarefa"]))
        res = cursor.fetchone()
        if res:
            return res[0]
        else:
            return None


def lista_tarefas(conn):
    with conn.cursor() as cursor:
        cursor.execute('SELECT description from tarefa')
        res = cursor.fetchall()
        des = tuple(x[0] for x in res)
        return des


def remove_tarefa(conn, id):
    with conn.cursor() as cursor:
        cursor.execute('DELETE FROM tarefa WHERE id_tarefa=%s', (id))
        conn.commit()


def muda_info_tarefa(conn, id, info):
    with conn.cursor() as cursor:
        try:
            cursor.execute('UPDATE tarefa SET description = %s, difficulty = %s where id_tarefa = %s',
                          (info["description"], info["difficulty"], id))
            conn.commit()
            return ""
        except pymysql.err.IntegrityError as e:
            raise ValueError(f'Não posso alterar info do id {id} na tabela usuario')



