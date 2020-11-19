from contextlib import closing
import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
import json

class FunctionsDB():
    def __init__(self):
        self.connection_string = 'dbname=postgres user=marinasvistunova password=1997 host=localhost port=5432'
        with closing(psycopg2.connect(self.connection_string)) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(sql.SQL('DROP TABLE IF EXISTS tasks'))
                cursor.execute(sql.SQL('DROP TABLE IF EXISTS users'))
                cursor.execute(sql.SQL('DROP TABLE IF EXISTS groups'))

                cursor.execute(sql.SQL('''CREATE TABLE users(
                                            id_user SERIAL PRIMARY KEY,
                                            email TEXT NOT NULL,
                                            firstname TEXT,
                                            surname TEXT)'''))

                cursor.execute(sql.SQL('''CREATE TABLE groups(
                                            id_group SERIAL PRIMARY KEY,
                                            title TEXT NOT NULL,
                                            group_description TEXT)'''))

                cursor.execute(sql.SQL('''CREATE TABLE tasks(
                                            id_task SERIAL PRIMARY KEY,
                                            title TEXT NOT NULL,
                                            task_description TEXT,
                                            date_created DATE NOT NULL DEFAULT CURRENT_DATE,
                                            created_by_id SERIAL NOT NULL REFERENCES users(id_user) ON DELETE CASCADE,
                                            group_id SERIAL NOT NULL REFERENCES groups(id_group) ON DELETE CASCADE,
                                            assigned_to_id SERIAL NOT NULL REFERENCES users(id_user) ON DELETE CASCADE,
                                            complete BOOLEAN NOT NULL DEFAULT FALSE)'''))
                
                cursor.execute(sql.SQL("INSERT INTO users (email) VALUES ('first_user@gmail.com')"))
                cursor.execute(sql.SQL("INSERT INTO users (email) VALUES ('second_user@gmail.com')"))
                cursor.execute(sql.SQL("INSERT INTO users (email) VALUES ('third_user@gmail.com')"))
                
                cursor.execute(sql.SQL("INSERT INTO groups (title) VALUES ('К 17.11.2020 по программированию')"))
                cursor.execute(sql.SQL("INSERT INTO groups (title) VALUES ('К 24.11.2020 по программированию')"))
                
                cursor.execute(sql.SQL("INSERT INTO TASKS (title, created_by_id, group_id, assigned_to_id) VALUES ('Лабораторная работа №6. Login', 1, 1, 1)"))
                cursor.execute(sql.SQL("INSERT INTO TASKS (title, created_by_id, group_id, assigned_to_id) VALUES ('Лабораторная работа №6. Templates', 1, 1, 2)"))
                
                cursor.execute(sql.SQL("INSERT INTO TASKS (title, created_by_id, group_id, assigned_to_id) VALUES ('Презентация. Postgresql', 1, 2, 1)"))
                cursor.execute(sql.SQL("INSERT INTO TASKS (title, created_by_id, group_id, assigned_to_id) VALUES ('Презентация. Psycopg2', 3, 2, 1)"))
                cursor.execute(sql.SQL("INSERT INTO TASKS (title, created_by_id, group_id, assigned_to_id) VALUES ('Презентация. SQL', 1, 2, 2)"))
                cursor.execute(sql.SQL("INSERT INTO TASKS (title, created_by_id, group_id, assigned_to_id) VALUES ('Презентация. Routes', 2, 2, 3)"))
                cursor.execute(sql.SQL("INSERT INTO TASKS (title, created_by_id, group_id, assigned_to_id) VALUES ('Презентация. Templates', 3, 2, 3)"))
            conn.commit()



    # USERS
    def getUsers(self):
        with closing(psycopg2.connect(self.connection_string)) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                stmt = sql.SQL('SELECT * FROM users')
                cursor.execute(stmt)
                values = [dict(record) for record in cursor]
        return values

    def addUser(self, values):
        with closing(psycopg2.connect(self.connection_string)) as conn:
            with conn.cursor() as cursor:
                insert = sql.SQL('INSERT INTO users (email, firstname, surname) VALUES {}').format(sql.SQL(',').join(map(sql.Literal, values.values())))
                cursor.execute(insert)
                cursor.commit()
        return True
    
    # GROUPS
    def getGroups(self):
        with closing(psycopg2.connect(self.connection_string)) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                stmt = sql.SQL('SELECT * FROM tasks RIGHT JOIN groups ON tasks.group_id = groups.id_group')
                cursor.execute(stmt)
                values = [dict(record) for record in cursor]
        groups = {}
        for group in values:
            try:
                if groups[group['id_group']]:
                    if group['complete']:
                        groups[group['id_group']]['complete'] += 1
                    else:
                        groups[group['id_group']]['uncomplete'] += 1
            except:
                groups[group['id_group']] = {}
                groups[group['id_group']]['title'] = group['title']
                groups[group['id_group']]['group_description'] = group['group_description'] if group['group_description'] != None else ''
                if group['id_task'] == None:
                    groups[group['id_group']]['complete'] = 0
                    groups[group['id_group']]['uncomplete'] = 0
                else:
                    if group['complete']:
                        groups[group['id_group']]['complete'] = 1
                        groups[group['id_group']]['uncomplete'] = 0
                    else:
                        groups[group['id_group']]['uncomplete'] = 1
                        groups[group['id_group']]['complete'] = 0
        values = {}
        for key in sorted(groups.keys()):
            values[key] = groups[key]
        return values

    def addGroup(self, title, group_description):
        with closing(psycopg2.connect(self.connection_string)) as conn:
            with conn.cursor() as cursor:
                insert = sql.SQL('INSERT INTO groups (title, group_description) VALUES ({})').format(sql.SQL(',').join(map(sql.Literal, [title, group_description])))
                cursor.execute(insert)
            conn.commit()
        return True
    
    def deleteGroup(self, id):
        with closing(psycopg2.connect(self.connection_string)) as conn:
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM groups WHERE id_group = %s', (id, ))
            conn.commit()
        return True
    
    def editGroup(self, value):
        with closing(psycopg2.connect(self.connection_string)) as conn:
            with conn.cursor() as cursor:
                cursor.execute('UPDATE groups SET (title, group_description) = (%s, %s) WHERE id_group=%s', (value['title'], value['group_description'], value['id']))
            conn.commit()
        return True
    
    # TASKS
    def getTasks(self, id_group):
        with closing(psycopg2.connect(self.connection_string)) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute('''SELECT 
                                    f.id_task, f.title, f.task_description, f.date_created, f.group_id, f.created_by_id, f.email AS email_creator, f.firstname AS firstname_creator, f.surname AS surname_creator, f.complete, 
                                    f.assigned_to_id, u2.email, u2.firstname, u2.surname 
                                FROM 
                                    (SELECT 
                                        t.id_task, t.title, t.task_description, t.date_created, t.group_id, t.created_by_id, t.assigned_to_id, t.complete,
                                        u.email, u.firstname, u.surname 
                                    FROM tasks t 
                                        LEFT JOIN users u 
                                        ON t.created_by_id = u.id_user
                                        WHERE t.group_id = %s) as f 
                                LEFT JOIN users u2 
                                ON f.assigned_to_id = u2.id_user
                                ORDER BY f.date_created''', (id_group, ))
                values = [dict(record) for record in cursor]
        return values
    
    def addTask(self, task):
        with closing(psycopg2.connect(self.connection_string)) as conn:
            with conn.cursor() as cursor:
                insert = sql.SQL('INSERT INTO tasks (title, task_description, created_by_id, assigned_to_id, group_id) VALUES ({})').format(sql.SQL(',').join(map(sql.Literal, task.values())))
                cursor.execute(insert)
            conn.commit()
        return True
    
    def deleteTask(self, id):
        with closing(psycopg2.connect(self.connection_string)) as conn:
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM tasks WHERE id_task = %s', (id, ))
            conn.commit()
        return True
    
    def changeTask(self, value):
        with closing(psycopg2.connect(self.connection_string)) as conn:
            with conn.cursor() as cursor:
                if len(value) == 2 and value.get('complete'):
                    complition = cursor.execute('SELECT complete FROM tasks WHERE id_task = %s', (value['id'],))
                    result = cursor.fetchone()[0]
                    if result:
                        result = False
                    else:
                        result = True
                    cursor.execute('UPDATE tasks SET complete = %s WHERE id_task = %s', (result, value['id']))
                else:
                    complition = cursor.execute('SELECT * FROM tasks WHERE id_task = %s', (value['id'],))
                    result = cursor.fetchone()[0]
                    cursor.execute('UPDATE tasks SET (title, task_description, created_by_id, assigned_to_id) = (%s, %s, %s, %s) WHERE id_task=%s', (value['title'], value['task_description'], value['created_by_id'], value['assigned_to_id'], value['id']))
            conn.commit()
        return True