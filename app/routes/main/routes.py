from flask import Blueprint, render_template
from ...db_functions import DB
from mysql.connector import Error

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/')
def index():

    try:

        connection, cursor = DB.connect()

        cursor.execute('''
            SELECT v.*, c.name_Company as company FROM vacancy v JOIN company c ON v.ID_Company = c.ID_Company WHERE v.status = 'active';''')    
        vacancies = cursor.fetchall()

    except Error as e:
        print(f'DB Error: {e}')

    except Exception as e:
        print(f'Back-End Error: {e}')

    finally:

        DB.stop(connection, cursor)

    return render_template('index.html', vacancies=vacancies)