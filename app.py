import psycopg2
import psycopg2.extras

from contextlib import closing
from flask import Flask, render_template, request, redirect, url_for, flash

from psycopg2 import sql
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import Form, BooleanField, StringField, PasswordField, IntegerField, validators, SelectField

from db_functions import FunctionsDB

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a36021ba723815fd92c4913d4978d2698ee53e48680281bc2f7afae1e068b5cc82e4bfa91bcc0a70'

db = FunctionsDB()


class UserForm(Form):
    name = StringField('Name', [validators.Length(min=4, max=50)])
    email = StringField('Email', [validators.Length(min=4, max=50)])

class GroupForm(Form):
    title = StringField('Title')
    group_description = StringField('Description')

class TaskForm(Form):
    title = StringField('Title')
    task_description = StringField('Description')
    created_by_id = SelectField('Created by', coerce=int)
    assigned_to_id = SelectField('Assigned to', coerce=int)

def connectToDB():
    connection_string = 'dbname=postgres user=marinasvistunova password=1997 host=localhost port=8000'
    try:
        return psycopg2.connect(connectionString)
    except:
        print("Problems with connection")

@app.route('/', methods=['GET', 'POST'])
def groups_list():
    form = GroupForm(request.form)
    groups = db.getGroups()

    if request.method == 'POST':
        result = db.addGroup(request.form['title'], request.form['group_description'])
        if result:
            flash('Вы зарегестрированы', 'success')
        else:
            flash('Ошибка создания группы', 'error')

    return render_template('groups_list.html', form=form, groups=groups)

@app.route('/delete_group/<int:id>')
def delete_group(id):
    form = GroupForm(request.form)
    db.deleteGroup(id)
    return redirect(url_for('groups_list'))

@app.route('/tasks_list/<int:id_group>/<complete>', methods=['GET', 'POST'])
def tasks_list(id_group, complete):
    all_users = db.getUsers()
    users_list = [(i['id_user'], i['email']) for i in all_users]
    form = TaskForm()
    form.assigned_to_id.choices = users_list
    form.created_by_id.choices = users_list

    if request.method == 'POST':
        task = {
            'title': request.form['title'],
            'task_description': request.form['task_description']
        }
        for user in all_users:
            if user['email'] == request.form['created_by_id']:
                task['created_by_id'] = user['id_user']
            if user['email'] == request.form['assigned_to_id']:
                task['assigned_to_id'] = user['id_user']
        task['id_group'] = id_group
        result = db.addTask(task)

    all_tasks = db.getTasks(id_group)
    tasks = []
    for task in all_tasks:
        if str(task['complete']) == complete:
            print('666')
            if task['task_description'] == None:
                task['task_description'] = ''
            tasks += [task]
    return render_template('tasks_list.html', form=form, tasks=tasks, users=users_list, id_group=id_group)

@app.route('/delete_task/<int:id_group>/<int:id>')
def delete_task(id_group, id):
    db.deleteTask(id)
    return redirect(url_for('tasks_list', id_group=id_group, complete=False))

@app.route('/complete_task/<int:id_group>/<int:id>')
def complete_task(id_group, id):
    db.changeTask({ 'id': id, 'complete': True})
    return redirect(url_for('tasks_list', id_group=id_group, complete=False))

@app.route('/edit_task/<int:id_group>/<int:id>', methods=['GET', 'POST'])
def edit_task(id_group, id):
    all_users = db.getUsers()
    users_list = [(i['id_user'], i['email']) for i in all_users]
    form = TaskForm()
    form.assigned_to_id.choices = users_list
    form.created_by_id.choices = users_list

    tasks = db.getTasks(id_group)
    for task in tasks:
        if task['id_task'] == id:
            res = task
            print(task)

    if request.method == 'POST':
        task = {
            'id': id,
            'title': request.form['title'],
            'task_description': request.form['task_description']
        }
        for user in all_users:
            if user['email'] == request.form['created_by_id']:
                task['created_by_id'] = user['id_user']
            if user['email'] == request.form['assigned_to_id']:
                task['assigned_to_id'] = user['id_user']
        task['id_group'] = id_group
        result = db.changeTask(task)
        return redirect(url_for('tasks_list', id_group=id_group, complete=False))
        

    return render_template('edit_task.html', form=form, res=res, users=users_list, id_group=id_group)

@app.route('/edit_group/<int:id>', methods=['GET', 'POST'])
def edit_group(id):
    form = GroupForm(request.form)
    groups = db.getGroups()
    group = {}
    print(groups)
    for key, value in groups.items():
        if key == id:
            group = value
            group['id'] = key

    if request.method == 'POST':
        values = {}
        values['id'] = group['id']
        for key, value in request.form.items():
            values[key] = value
        result = db.editGroup(values)
        return redirect(url_for('groups_list'))

    return render_template('edit_group.html', form=form, res=group)

if __name__ == "__main__":
    app.run(debug=True)
