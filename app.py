from flask import Flask, redirect, render_template, session, request
from mysql.connector import Error
from config import *
from db_functions import *

app = Flask(__name__)
app.secret_key = SECRET_KEY

# HOME PAGE

@app.route('/')
def index():

    return render_template('index.html')

# LOGIN PAGE

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

# ADMIN PAGE

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

# LOGOUT ROUTE

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# COMPANY REGISTERING PAGE
@app.route('/new-company', methods=['GET', 'POST'])
def new_company ():
    if session.get('adm') != True:
        return redirect('/login')

    elif request.method == 'GET':
        return render_template('new-company.html')
        
    elif request.method == 'POST':
        
        companyName = request.form['name']
        companyEmail = request.form['email']
        companyCNPJ = request.form['cnpj']
        companyPhoneNumber = request.form['phone']
        companyPassword = request.form['password']

        if not companyName or not companyEmail or not companyCNPJ or not companyPhoneNumber or not companyPassword:
            return render_template('new-company.html', errormsg='All fields are obrigatory!')
        
        try:
            connection, cursor = DB.connect()

            SQLstatement = '''
            INSERT INTO company VALUES
            (null, %s, %s, %s, %s, %s, 'active') ;'''

            cursor.execute(SQLstatement, (companyName, companyCNPJ, companyPhoneNumber, companyEmail, companyPassword))
            connection.commit()

        except Exception as e:
            print(f'Error: {e}')
        finally:
            DB.stop(connection, cursor)
        
        return redirect('/admin')

if environment == 'development':
    if __name__ == '__main__':
        app.run(debug=True)