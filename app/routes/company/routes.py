from flask import Blueprint, request, render_template, session, redirect, send_from_directory
import os
import time
from ...config import *
from ...db_functions import *
from mysql.connector import *
import locale

company = Blueprint('company', __name__, template_folder='templates')
company.config['UPLOAD_FOLDER'] = os.path.join(company.root_path, '../../uploads/')
os.makedirs(company.config['UPLOAD_FOLDER'], exist_ok=True)

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

    except Exception as e:
        print(f'Backend Error: {e}')

    except Error as e:
        print(f'DB Error: {e}')

    finally:

        locale.setlocale ( locale.LC_ALL, 'pt_BR.UTF-8' )

        for vacancy in inactiveVacancies:
            salary = float(vacancy['salary'])
            vacancy['salary'] = locale.currency(salary, grouping=True)

        locale.setlocale ( locale.LC_ALL, 'pt_BR.UTF-8' )

        for vacancy in activeVacancies:
            salary = float(vacancy['salary'])
            vacancy['salary'] = locale.currency(salary, grouping=True)

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
        vacancySalary = request.form['salary']

        if not vacancyTitle or not vacancyDescription or not vacancyArrangement or not vacancyType or not vacancyLocation or not companyID or not vacancySalary:
            return render_template('new-vacancy.html', errormsg='All fields are obrigatory!')
        
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
        vacancySalary = request.form['salary']

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
    
    except Error as e:
        print(f'DB Error: {e}')

    except Exception as e:
        print(f'Back-End Error: {e}')

    finally:
        DB.stop(connection, cursor)

    return send_from_directory(company.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@company.route('/delete/<int:id>')
def delete_file(id):
    try:

        connection, cursor = DB.connect()
        cursor.execute('''SELECT fileName FROM apply WHERE applyID = %s''', (id,))
        filename = cursor.fetchone()
        
        file_path = os.path.join(company.config['UPLOAD_FOLDER'], filename)
        os.remove(file_path)

        
        cursor.execute("DELETE FROM apply WHERE fileName = %s", (filename,))
        connection.commit()

        return redirect('/')
    
    except Error as e:
        return f"DB Error: {e}"
    
    except Exception as erro:
        return f"Back-end Error: {e}"
    
    finally:
        
        DB.stop(connection, cursor)

@company.route('/vacancy-docs/<int:id>')
def vacancy_docs (id):

    try:

        connection, cursor = DB.connect()
        cursor.execute('SELECT * FROM apply')
        files = cursor.fetchall()
    
        return render_template('vacancy-applies.html',files=files)
    
    except Error as e:
        return f"DB Error: {e}"  
    except Exception as e:  
        return f"Back-end Error: {e}"
    finally:
        
        DB.stop(connection, cursor)
