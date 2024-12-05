from flask import Blueprint, request, render_template, session, redirect, send_from_directory, current_app
import os
import time
from ...config import *
from ...db_functions import *
from mysql.connector import *
import locale

company = Blueprint('company', __name__, template_folder='templates')

@company.route('/company')
def company_menu ():

    if not session:
        return redirect('/login')
    if session.get('adm') == True:
        return redirect('/admin')

    company = session['companyInfo']

    try:

        connection, cursor = DB.connect()
        cursor.execute("SELECT * FROM vacancy WHERE companyID = %s AND status = 'active' ORDER BY vacancyID DESC", (company['companyID'],))
        activeVacancies = cursor.fetchall()

        cursor.execute("SELECT * FROM vacancy WHERE companyID = %s AND status = 'inactive' ORDER BY vacancyID DESC", (company['companyID'],))
        inactiveVacancies = cursor.fetchall()

        locale.setlocale(locale.LC_ALL, 'pt-BR.UTF-8')

        for vacancy in activeVacancies:
            salary = float(vacancy['salary'])
            salary = locale.currency(salary, grouping=True)
            vacancy['salary'] = salary

        for vacancy in inactiveVacancies:
            salary = float(vacancy['salary'])
            salary = locale.currency(salary, grouping=True)
            vacancy['salary'] = salary

    except Exception as e:
        print(f'Backend Error: {e}')

    except Error as e:
        print(f'DB Error: {e}')

    finally:       

        DB.stop(connection, cursor)

    return render_template('company.html', company=company, activeVacancies=activeVacancies, inactiveVacancies=inactiveVacancies)


@company.route('/new-vacancy', methods=['GET', 'POST'])
def new_vancancy ():

    if session.get('adm') == True:
        return redirect('/login')

    elif request.method == 'GET':
        return render_template('new-vacancy.html')

    elif request.method == 'POST':
        
        company = session['companyInfo']
        companyID = company['companyID']
        vacancyTitle = request.form['title']
        vacancyDescription = request.form['description']
        vacancyArrangement = request.form['arrangement']
        vacancyType = request.form['type']
        vacancyLocation = request.form['location']
        vacancySalary = DB.clearInput('currency', (request.form['salary']))

        if not vacancyTitle or not vacancyDescription or not vacancyArrangement or not vacancyType or not vacancyLocation or not companyID or not vacancySalary:
            return render_template('new-vacancy.html', errormsg='Todos os campos são obrigatórios!')
        
        try:
            connection, cursor = DB.connect()

            SQLstatement = '''
            INSERT INTO vacancy VALUES
            (null, %s, %s, %s, %s, %s, %s, %s, 'active') ;'''

            cursor.execute(SQLstatement, (vacancyTitle, vacancyDescription, vacancyArrangement, vacancyType, vacancyLocation, vacancySalary, companyID))
            connection.commit()

        except Exception as e:
            print(f'Error: {e}')
    
        finally:
            DB.stop(connection, cursor)
        
        return redirect('/company')

# VACANCY EDITING ROUTE

@company.route('/edit-vacancy/<int:id>', methods=['GET', 'POST'])
def edit_vacancy (id):

    if session.get('adm') == True:
        return redirect('/adm')

    elif request.method == 'GET':

        try:
            connection, cursor = DB.connect()

            cursor.execute(f'SELECT * FROM vacancy WHERE vacancyID = {id} ;')
            vacancy = cursor.fetchone()

            company = session['companyInfo']

            if company['companyID'] != vacancy['companyID']:
                return redirect('/company')

        except Exception as e:
            print(f'Back-End Error: {e}')
    
        except Error as e:
            print(f"DB Error: {e}")
    
        finally:

            DB.stop(connection, cursor)
    
        return render_template('edit-vacancy.html', vacancy=vacancy, id=id)

    elif request.method == 'POST':

        vacancyTitle = request.form['title']
        vacancyDescription = request.form['description']
        vacancyArrangement = request.form['arrangement']
        vacancyType = request.form['type']
        vacancyLocation = request.form['location']
        vacancySalary = DB.clearInput('currency', (request.form['salary']))

        if not vacancyTitle or not vacancyDescription or not vacancyArrangement or not vacancyType or not vacancyLocation or not vacancySalary:
            return render_template('edit-vacancy.html', errormsg='All fields are obrigatory!')
        
        try:
            connection, cursor = DB.connect()

            SQLstatement = '''
            UPDATE vacancy
            SET title = %s,
            description = %s,
            arrangement = %s,
            type = %s,
            location = %s,
            salary = %s
            WHERE vacancyID = %s;'''

            cursor.execute(SQLstatement, (vacancyTitle, vacancyDescription, vacancyArrangement, vacancyType, vacancyLocation, vacancySalary, id))
            connection.commit()

        except Exception as e:
            print(f'Error: {e}')
    
        finally:
            DB.stop(connection, cursor)
        
        return redirect('/company')

# VACANCY STATUS SWITCHING ROUTE

@company.route('/switch-vacancy-status/<int:id>')
def switch_vacancy_status (id):
    
    if session.get('adm') == True:
        return redirect('/admin')
    
    elif not session['companyInfo']:
        return redirect('/login')

    try:


        connection, cursor = DB.connect()
        cursor.execute('''SELECT * FROM vacancy WHERE vacancyID = %s ;''', (id,))
        vacancy = cursor.fetchone()
        
        company = session['companyInfo']

        if vacancy['companyID'] != company['companyID']:
            return redirect('/company')

        elif vacancy['status'] == 'active':

            cursor.execute('''UPDATE vacancy
                SET status = 'inactive' 
                WHERE vacancyID = %s ;''', (id,))

        elif vacancy['status'] == 'inactive':
            
            cursor.execute('''UPDATE vacancy
                SET status = 'active' 
                WHERE vacancyID = %s ;''', (id,))

    except Exception as e:
        print(f'Back-End Error: {e}')

    except Error as e:
        print(f"DB Error: {e}")
        
    finally:
        connection.commit()
        DB.stop(connection, cursor)

    return redirect('/company')

# VACANCY DELETION ROUTE

@company.route('/delete-vacancy/<int:id>')
def delete_vacancy (id):
    
    if session.get('adm') == True:
        return redirect('/admin')

    try:
        connection, cursor = DB.connect()

        cursor.execute('''SELECT * FROM vacancy WHERE vacancyID = %s ;''', (id,))

        vacancy = cursor.fetchone()
        company = session['companyInfo']

        if vacancy['companyID'] != company['companyID']:
            return redirect('/company')
            
        else:

            cursor.execute('SELECT fileName FROM apply WHERE vacancyID = %s', (id,))
            files = cursor.fetchall()

            for file in files:
                os.remove(f"{current_app.config['UPLOAD_FOLDER']}{file['fileName']}")

            cursor.execute('''DELETE FROM vacancy WHERE vacancyID = %s ;''', (id,))        

    except Exception as e:
        print(f'Back-End Error: {e}')

    except Error as e:
        print(f"DB Error: {e}")
        
    finally:
        connection.commit()
        DB.stop(connection, cursor)
    
    return redirect('/company')

@company.route('/download/<int:id>')
def download(id):
    try:
        connection, cursor = DB.connect()
        cursor.execute('''SELECT fileName FROM apply WHERE applyID = %s''', (id,))
        filename = cursor.fetchone()

        if filename is None:
            return "File not found", 404

        filename = filename[0]  
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        if not os.path.exists(file_path):
            return "File not found on server", 404

        return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

    except mysql.connector.Error as db_error:  # Catch specific database errors
        print(f"Database Error: {db_error}")
        return f"Database Error: {db_error}", 500
    except FileNotFoundError as fnf_error:  #Catch file not found errors
        print(f"File Not Found: {fnf_error}")
        return f"File Not Found: {fnf_error}", 404
    except Exception as e:  #Catch other unexpected errors
        print(f"Unexpected Error: {e}")
        return f"An unexpected error occurred", 500
    finally:
        DB.stop(connection, cursor)


@company.route('/vacancy-docs/<int:id>')
def vacancy_docs(id):
    try:
        connection, cursor = DB.connect()
        cursor.execute('SELECT * FROM vacancy WHERE vacancyID = %s', (id,))
        vacancy = cursor.fetchone()
        cursor.execute('SELECT * FROM apply WHERE vacancyID = %s', (id,))
        files = cursor.fetchall()

    except Error as e:
        print(f"DB Error: {e}")
        return f"DB Error: {e}", 500
    except Exception as e:
        print(f"Back-end Error: {e}")
        return f"Back-end Error: {e}", 500
    finally:
        DB.stop(connection, cursor)

    return render_template('vacancy-applies.html', files=files, vacancy=vacancy)

@company.route('/download/<int:id>')
def download(id):

    if not session:
        return redirect('/login')

    try:

        connection, cursor = DB.connect()

        cursor.execute('''SELECT companyID FROM vacancy WHERE vacancyID = (SELECT vacancyID FROM apply WHERE applyID = %s);''', (id,))
        companyID = cursor.fetchone()

        company = session['companyInfo']

        if companyID['companyID'] != company['companyID']:
            redirect('/company')

        cursor.execute('''SELECT fileName FROM apply WHERE applyID = %s ;''', (id,))
        filename = cursor.fetchone()

        if not filename:
            return redirect('/') 

        filename = filename['fileName']  
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        if not os.path.exists(file_path):
            return "File not found on server", 404


        return send_from_directory(f"{os.getcwd()}/app/uploads/", filename, as_attachment=False)


    except mysql.connector.Error as db_error:  # Catch specific database errors
        print(f"Database Error: {db_error}")
        return f"Database Error: {db_error}", 500
    
    except FileNotFoundError as fnf_error:  #Catch file not found errors
        print(f"File Not Found: {fnf_error}")
        return f"File Not Found: {fnf_error}", 404
    
    except Exception as e:  #Catch other unexpected errors
        print(f"Unexpected Error: {e}")
        return redirect('/company')

    finally:
        DB.stop(connection, cursor)


@company.route('/delete-file/<int:id>')
def delete_file(id):
    try:
        connection, cursor = DB.connect()
        cursor.execute('''SELECT fileName, vacancyID FROM apply WHERE applyID = %s;''', (id,))
        fileData = cursor.fetchone()

        if not fileData:
            return "Arquivo não encontrado!", 404 # Handle case where file doesn't exist

        fileName = fileData['fileName']
        vacancyID = fileData['vacancyID']
        filePath = os.path.join(f"{os.getcwd()}/app/uploads/", fileName) #Use current_app

        if os.path.exists(filePath):
            os.remove(filePath)
            print('File removed')

        cursor.execute("DELETE FROM apply WHERE applyID = %s", (id,))
        connection.commit()
        return redirect('/vacancy-docs') # Redirect to the correct URL

    except Error as e:
        print(f"DB Error: {e}")
        return f"DB Error: {e}", 500 # HTTP error code
    except Exception as e:
        print(f"Back-end Error: {e}")
        return f"Back-end Error: {e}", 500 # HTTP error code
    finally:
        DB.stop(connection, cursor)