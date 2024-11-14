from flask import Blueprint, render_template, request, redirect, session
from ...db_functions import DB
import locale
from mysql.connector import Error

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

        locale.setlocale ( locale.LC_ALL, 'pt_BR.UTF-8' )

        for vacancy in vacancies:
            salary = float(vacancy['salary'])
            vacancy['salary'] = locale.currency(salary, grouping=True)

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

        locale.setlocale ( locale.LC_ALL, 'pt_BR.UTF-8' )

        DB.stop(connection, cursor)

        if not vacancies:
            return render_template('search.html', search=search, searchpage=True)
        else:
            for vacancy in vacancies:  
                salary = float(vacancy['salary'])
                vacancy['salary'] = locale.currency(salary, grouping=True)

            return render_template('search.html', vacancies=vacancies, search=search, searchpage=True)
        
@main.route('/vacancy-details/<int:id>')
def vacancy_details (id):

    try:


        connection, cursor = DB.connect()

        cursor.execute('''
            SELECT v.*, c.name as company FROM vacancy v JOIN company c ON v.companyID = c.companyID WHERE vacancyID = %s;''', (id,))    
        vacancy = cursor.fetchall()

    except Error as e:
        print(f'DB Error: {e}')

    except Exception as e:
        print(f'Back-End Error: {e}')

    finally:

        locale.setlocale ( locale.LC_ALL, 'pt_BR.UTF-8' )

        if not vacancy:
            return redirect('/')
        else:
            for info in vacancy:
                salary = float(info['salary'])
                info['salary'] = locale.currency(salary, grouping=True)
                vacancy = vacancy[0]

        DB.stop(connection, cursor)

    return render_template('detailed-vacancy.html', vacancy=vacancy)