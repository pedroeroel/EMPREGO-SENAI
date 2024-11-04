from flask import Blueprint, render_template, session, redirect, request
from ..config import *
from ..db_functions import *
from mysql.connector import *

admin = Blueprint('admin', __name__, template_folder='templates')

@admin.route('/admin')
def admin_menu():

    if session.get('adm') != True:
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

    except:
        print('error')

    finally:
        DB.stop(connection, cursor)
    
    return render_template('admin.html', active_companies=active_companies, inactive_companies=inactive_companies)

@admin.route('/new-company', methods=['GET', 'POST'])
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
    
@admin.route('/edit-company/<int:id>', methods=['GET', 'POST'])
def edit_company (id):

    if session.get('adm') != True:
        return redirect('/login')

    elif request.method == 'GET':

        try:
            connection, cursor = DB.connect()

            cursor.execute(f'SELECT * FROM company WHERE ID_Company = {id} ;')
            company = cursor.fetchone()

        except Exception as e:
            print(f'Back-End Error: {e}')
    
        except Error as e:
            print(f"DB Error: {e}")
    
        finally:

            DB.stop(connection, cursor)
    
        return render_template('edit-company.html', company=company, id=id)

    elif request.method == 'POST':
        
        companyName = request.form['name']
        companyEmail = request.form['email']
        companyCNPJ = request.form['cnpj']
        companyPhoneNumber = request.form['phone']
        companyPassword = request.form['password']

        if not companyName or not companyEmail or not companyCNPJ or not companyPhoneNumber or not companyPassword:
            return render_template('edit-company.html', errormsg='Todos os campos são obrigatórios!')
        
        try:
            connection, cursor = DB.connect()

            SQLstatement = '''
            UPDATE company
            SET name_Company = %s,
            cnpj = %s,
            phone = %s,
            email = %s,
            password = %s
            WHERE ID_Company = %s;'''

            cursor.execute(SQLstatement, (companyName, companyCNPJ, companyPhoneNumber, companyEmail, companyPassword, id))
            connection.commit()

        except Exception as e:
            print(f'Error: {e}')
    
        finally:
            DB.stop(connection, cursor)
        
        return redirect('/admin')


@admin.route('/switch-company-status/<int:id>')
def switch_company_status (id):
    
    if session.get('adm') != True:
        return redirect('/login')

    try:
        connection, cursor = DB.connect()
        cursor.execute('''SELECT * FROM company WHERE ID_Company = %s ;''', (id,))
        
        company = cursor.fetchone()

        if company['status'] == 'active':

            cursor.execute('''UPDATE company
                        SET status = 'inactive' 
                        WHERE ID_Company = %s ;''', (id,))
            
            cursor.execute('''UPDATE vacancy
                SET status = 'inactive' 
                WHERE ID_Company = %s ;''', (id,))

        elif company['status'] == 'inactive':
            
            cursor.execute('''UPDATE company
                SET status = 'active' 
                WHERE ID_Company = %s ;''', (id,))

    except Exception as e:
        print(f'Back-End Error: {e}')

    except Error as e:
        print(f"DB Error: {e}")
        
    finally:
        connection.commit()
        DB.stop(connection, cursor)
    
    return redirect('/admin')


@admin.route('/delete-company/<int:id>')
def delete_company (id):
    
    if session.get('adm') != True:
        return redirect('/login')

    try:
        connection, cursor = DB.connect()

        cursor.execute('''DELETE FROM vacancy WHERE ID_Company = %s ;''', (id,))        
        cursor.execute('''DELETE FROM company WHERE ID_Company = %s ;''', (id,))

    except Exception as e:
        print(f'Back-End Error: {e}')

    except Error as e:
        print(f"DB Error: {e}")
        
    finally:
        connection.commit()
        DB.stop(connection, cursor)
    
    return redirect('/admin')