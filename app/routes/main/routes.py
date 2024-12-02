from flask import Flask, Blueprint, render_template, request, redirect, session, send_from_directory
from ...db_functions import DB
from mysql.connector import *
import time
import os
import locale

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

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

        if vacancies:
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
        return render_template('upload.html', vacancyID=id)
    
    if request.method == 'POST':
        print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
        def allowed_file(filename):
            ALLOWED_EXTENSIONS = {'pdf'}
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        if 'pdf' not in request.files:
            print('No file part')
            return redirect(f'/upload/{id}')
        
        file = request.files['pdf']
        
        if file.filename == '':
            msg = 'Nenhum arquivo enviado!'
            return render_template('upload.html', msg=msg)
        
        if not os.access(app.config['UPLOAD_FOLDER'], os.W_OK):
            print("Directory is not writable")

        try:

            timestamp = int(time.time())
            
            if allowed_file(file.filename):
                fileName = f'{timestamp}_{file.filename}'
            else:
                print('Invalid filename')
                return redirect(f'/upload/{id}')
            print(os.path.join(app.config['UPLOAD_FOLDER'], fileName))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], fileName))

            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']

            connection, cursor = DB.connect()
            cursor.execute("INSERT INTO apply (name, email, phone, fileName, vacancyID) VALUES (%s, %s, %s, %s, %s)", (name, email, phone, fileName, id))
            
            connection.commit()

            DB.stop(connection, cursor)
            
            return redirect('/')

        except Exception as e:
            print(f'Back-End Error: {e}')
        
            return render_template('upload.html', msg='Erro de Back-End')

        except Error as e:
            print(f'DB Error: {e}')

            return render_template('upload.html', msg='Erro de Database')


        finally: 
            return redirect('/')
