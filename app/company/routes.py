from flask import Blueprint, request, render_template, session, redirect
from ..config import *
from ..db_functions import *
from mysql.connector import *

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
        cursor.execute("SELECT * FROM vacancy WHERE ID_Company = %s AND status = 'active' ORDER BY ID_Vacancy DESC", (company['ID_Company'],))
        activeVacancies = cursor.fetchall()

        cursor.execute("SELECT * FROM vacancy WHERE ID_Company = %s AND status = 'inactive' ORDER BY ID_Vacancy DESC", (company['ID_Company'],))
        inactiveVacancies = cursor.fetchall()

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
        companyID = company['ID_Company']
        vacancyTitle = request.form['title']
        vacancyDescription = request.form['description']
        vacancyArrangement = request.form['arrangement']
        vacancyType = request.form['type']
        vacancyLocation = request.form['location']
        vacancySalary = request.form['salary']
        vacancyStatus = request.form ['status']

        if not vacancyTitle or not vacancyDescription or not vacancyArrangement or not vacancyType or not vacancyLocation or not companyID or not vacancySalary or not vacancyStatus:
            return render_template('new-vacancy.html', errormsg='All fields are obrigatory!')
        
        try:
            connection, cursor = DB.connect()

            SQLstatement = '''
            INSERT INTO vacancy VALUES
            (null, %s, %s, %s, %s, %s, %s, %s, %s) ;'''

            cursor.execute(SQLstatement, (vacancyTitle, vacancyDescription, vacancyArrangement, vacancyType, vacancyLocation, vacancySalary, companyID, vacancyStatus))
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

            cursor.execute(f'SELECT * FROM vacancy WHERE ID_Vacancy = {id} ;')
            vacancy = cursor.fetchone()

            company = session['companyInfo']

            if company['ID_Company'] != vacancy['ID_Company']:
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
            WHERE ID_Vacancy = %s;'''

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
        cursor.execute('''SELECT * FROM vacancy WHERE ID_Vacancy = %s ;''', (id,))
        vacancy = cursor.fetchone()
        
        company = session['companyInfo']

        if vacancy['ID_Company'] != company['ID_Company']:
            return redirect('/company')

        elif vacancy['status'] == 'active':

            cursor.execute('''UPDATE vacancy
                SET status = 'inactive' 
                WHERE ID_Vacancy = %s ;''', (id,))

        elif vacancy['status'] == 'inactive':
            
            cursor.execute('''UPDATE vacancy
                SET status = 'active' 
                WHERE ID_Vacancy = %s ;''', (id,))

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

        cursor.execute('''SELECT * FROM vacancy WHERE ID_Vacancy = %s ;''', (id,))

        vacancy = cursor.fetchone()
        company = session['companyInfo']

        if vacancy['ID_Company'] != company['ID_Company']:
            return redirect('/company')
            
        else:
            cursor.execute('''DELETE FROM vacancy WHERE ID_Vacancy = %s ;''', (id,))        

    except Exception as e:
        print(f'Back-End Error: {e}')

    except Error as e:
        print(f"DB Error: {e}")
        
    finally:
        connection.commit()
        DB.stop(connection, cursor)
    
    return redirect('/company')
