from flask import Flask, redirect, render_template, session, request
import mysql.connector
from config import *
from db_functions import *

app = Flask(__name__)
app.secret_key = SECRET_KEY

# HOME PAGE
@app.route('/')
def index():

    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not email or not password:
            error = 'Todos os campos precisam estar preenchidos!'
            return render_template('login.html', errormsg=error)
        
        if email == MASTER_EMAIL and password == MASTER_PASSWORD:
            session['adm'] = True
            return redirect('/admin')


@app.route('/admin')
def admin():
    if not session or not session['adm'] == True:
        return redirect('/login')

    try:
        connection, cursor = DB.connect()
        SQLstatement = '''
            SELECT * FROM company WHERE status = 'active' ;
            '''
        cursor.execute(SQLstatement)
        active_companies = cursor.fetchall()
        
        SQLstatement = '''
            SELECT * FROM company WHERE status = 'inactive' ;
            '''
        cursor.execute(SQLstatement)
        inactive_companies = cursor.fetchall()

        return render_template('admin.html', active_companies=active_companies, inactive_companies=inactive_companies)
    except:
        print('error')
    finally:
        DB.stop(connection, cursor)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if environment == 'development':
    if __name__ == '__main__':
        app.run(debug=True)