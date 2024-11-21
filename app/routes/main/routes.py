from flask import Blueprint, render_template, request, redirect, session, send_from_directory
from ...db_functions import DB
from mysql.connector import *
import time
import os
import locale


main = Blueprint('main', __name__, template_folder='templates')

@main.route('/')
def index():

    try:

        connection, cursor = DB.connect()

        cursor.execute('''
            SELECT v.*, c.name as company FROM vacancy v JOIN company c ON v.companyID = c.companyID WHERE v.status = 'active';''')    
        vacancies = cursor.fetchall()

    except Error as e:
        print(f'DB Error: {e}')

    except Exception as e:
        print(f'Back-End Error: {e}')

    finally:

        locale.setlocale(locale.LC_ALL, 'pt-BR.UTF-8')

        for vacancy in vacancies:
            salary = float(vacancy['salary'])
            salary = locale.currency(salary, grouping=True)
            vacancy['salary'] = salary

        DB.stop(connection, cursor)

    return render_template('index.html', vacancies=vacancies)

@main.route('/search', methods=['GET'])
def search ():

    try:
        search = request.args.get('search')

        connection, cursor = DB.connect()

        search_term = f'%{search}%'

        cursor.execute('''
            SELECT v.*, c.name as company FROM vacancy v JOIN company c ON v.companyID = c.companyID WHERE v.status = 'active' AND v.title LIKE %s OR v.description LIKE %s OR v.location LIKE %s OR c.name LIKE %s;''' , (search_term, search_term, search_term, search_term)) 
        vacancies = cursor.fetchall()

    except Error as e:
        print(f'DB Error: {e}')

        vacancies = False

    except Exception as e:
        print(f'Back-End Error: {e}')

        vacancies = False

    finally:

        locale.setlocale(locale.LC_ALL, 'pt-BR.UTF-8')

        for vacancy in vacancies:
            salary = float(vacancy['salary'])
            salary = locale.currency(salary, grouping=True)
            vacancy['salary'] = salary

        DB.stop(connection, cursor)

        if not vacancies:
            return render_template('search.html', search=search, searchpage=True)
        else:

            return render_template('search.html', vacancies=vacancies, search=search, searchpage=True)
        
@main.route('/vacancy-details/<int:id>')
def vacancy_details (id):

    try:

        connection, cursor = DB.connect()

        cursor.execute('''
            SELECT v.*, c.name as company FROM vacancy v JOIN company c ON v.companyID = c.companyID WHERE vacancyID = %s;''', (id,))    
        vacancy = cursor.fetchone()

        locale.setlocale(locale.LC_ALL, 'pt-BR.UTF-8')

        vacancy['salary'] = locale.currency(float(vacancy['salary']), grouping=True)

        return render_template('detailed-vacancy.html', vacancy=vacancy)

    except Error as e:
        print(f'DB Error: {e}')
        
    except Exception as e:
        print(f'Back-End Error: {e}')


    finally:

        DB.stop(connection, cursor)

        if not vacancy:
            return redirect('/')

@main.route('/upload/<int:id>', methods=['GET','POST'])
def upload (id):
    if request.method == 'GET':
        return render_template('upload.html')
    
    if request.method == 'POST':

        file = request.files['file']
        
        if file.filename == '':
            msg = 'Nenhum arquivo enviado!'
            return render_template('upload.html', msg=msg)
        
        try:

            timestamp = int(time.time())
            fileName = f'{timestamp}_{file.filename}'
            file.save(os.path.join(main.config['UPLOAD_FOLDER'], fileName))

            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']

            connection, cursor = DB.connect()
            cursor.execute("INSERT INTO apply (name, email, phone, fileName, vacancyID) VALUES (%s, %s, %s, %s, %s)", (name, email, phone, fileName, id))
            
            connection.commit()
            
            return redirect('/')

        except Exception as e:
            print(f'Back-End Error: {e}')
        
            return render_template('upload.html', msg='Erro de Back-End')

        except Error as e:
            print(f'DB Error: {e}')

            return render_template('upload.html', msg='Erro de Database')


        finally: 

            DB.stop(connection, cursor)
            return redirect('/')
