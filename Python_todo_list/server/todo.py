import sqlite3
from bottle import route, run, debug, template, request, validate, static_file, error


TODO_DB = '../db/todo.db'

@route('/todo')
@route('/my_todo_list')
def todo_list():
    conn = sqlite3.connect(TODO_DB)
    c = conn.cursor()
    c.execute("SELECT id, task FROM todo WHERE status LIKE '1'")
    result = c.fetchall()
    c.close()
    output = template('template/make_table', rows=result)
    return output

@route('/new', method='GET')
def new_item():
    if request.GET.get('save', '').strip():
        new = request.GET.get('task', '').strip()
        conn = sqlite3.connect(TODO_DB)
        c = conn.cursor()
        
        c.execute("INSERT INTO todo (task,status) VALUES (?,?)", (new, 1))
        new_id = c.lastrowid
        
        conn.commit()
        c.close()
        return '<p>The new task was inserted into the database, the ID is %s</p>' % new_id
    else:
        return template('template/new_task.tpl')

@route('/edit/:no', method='GET')
@validate(no=int)
def edit_item(no):

    if request.GET.get('save', '').strip():
        edit = request.GET.get('task', '').strip()
        status = request.GET.get('status', '').strip()

        if status == 'open':
            status = 1
        else:
            status = 0

        conn = sqlite3.connect(TODO_DB)
        c = conn.cursor()
        c.execute("UPDATE todo SET task = ?, status = ? WHERE id LIKE ?", (edit, status, no))
        conn.commit()

        return '<p>The item number %s was successfully updated</p>' % no
    else:
        conn = sqlite3.connect(TODO_DB)
        c = conn.cursor()
        c.execute("SELECT task FROM todo WHERE id LIKE ?", (str(no)))
        cur_data = c.fetchone()

        return template('template/edit_task', old=cur_data, no=no)

@route('/item:item#[1-9]+#')
def show_item(item):
    conn = sqlite3.connect(TODO_DB)
    c = conn.cursor()
    c.execute("SELECT task FROM todo WHERE id LIKE ?", (item))
    result = c.fetchall()
    c.close()
    if not result:
        return 'This item number does not exist!'
    else:
        return 'Task: %s' % result[0]

@route('/json:json#[1-9]+#')
def show_json(json):
    conn = sqlite3.connect(TODO_DB)
    c = conn.cursor()
    c.execute("SELECT task FROM todo WHERE id LIKE ?", (json))
    result = c.fetchall()
    c.close()

    if not result:
        return {'task':'This item number does not exist!'}
    else:
        return {'Task': result[0]}
    
#we should be able to do CRUD on that resource(via get,post,put,delete)
@route('/todo/api/todo',method='POST')#creates a todo
@route('/todo/api/todo',method='GET')#gets all todos
@route('/todo/api/todo',method='DELETE')#deletes all todos
@route('/todo/api/todo',method='PUT')#modify several todos
@route('/todo/api/todo/id',method="GET")#returns the todo,or an error if doesn't exists
@route('/todo/api/todo/id',method='PUT')#modify the todo
@route('/todo/api/todo/id',method='DELETE')#delete the todo

@route('/help')
def help():
    return static_file('help.html', mimetype='text/html', root='html')

@error(403)
def mistake403(code):
    return 'The parameter you passed has the wrong format!'

@error(404)
def mistake404(code):
    return 'Sorry, this page does not exist!'

@error(500)
def mistake500(code):
    return 'Sorry,the server is fixing'

debug(True)
run(server='paste', reloader=True)
