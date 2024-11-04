from flask import Blueprint, render_template, session, request, redirect
from ...config import *
from ...db_functions import *
from mysql.connector import *

auth = Blueprint('auth', __name__, template_folder='templates')

@auth.route('/login', methods=['GET', 'POST'])
def login():


    if session.get('adm') == True:
        
        return redirect('/admin')
    
    elif session.get('companyInfo') == True:
        
        return redirect('/company')

    elif request.method == 'GET':
        
        return render_template('login.html')
    
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            connection, cursor = DB.connect()
            cursor.execute('''SELECT * FROM company WHERE email = %s ;''', (email,))
            company = cursor.fetchone()

        except Exception as e:
            print(f"Backend Error: {e}")
            
            DB.stop(connection, cursor)
            return redirect('/login')
        
        except Error as e:
            print(f"DB Error: {e}")
            
            DB.stop(connection, cursor)
            return redirect('/login')

        if not email or not password:
            error = 'Todos os campos precisam estar preenchidos!'
            
            DB.stop(connection, cursor)
            return render_template('login.html', errormsg=error)
    
        elif email == MASTER_EMAIL and password == MASTER_PASSWORD:
            session['adm'] = True
            
            DB.stop(connection, cursor)
            return redirect('/admin')

        elif not company:
            error = 'Esse email não está cadastrado em nosso sistema!'
            
            DB.stop(connection, cursor)
            return render_template('login.html', errormsg=error)
        
        elif password == company['password'] and company['password'] == 'inactive':
            error = 'Sua empresa está inativa!'

            DB.stop(connection, cursor)
            return render_template('login.html', errormsg=error)
        
        elif password == company['password']:
            session['email'] = email
            session['password'] = password
            session['companyInfo'] = company

            DB.stop(connection, cursor)            
            return redirect('/company')

        elif password != company['password']:
            error = 'Senha incorreta!'

            DB.stop(connection, cursor)
            return render_template('login.html', errormsg=error)   
        
@auth.route('/logout')
def logout():
    session.clear()
    return redirect('/')