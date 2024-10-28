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

    connection, cursor = DB.connect()

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
            cursor.execute('''SELECT * FROM company WHERE email = %s ;''', (email,))
            company = cursor.fetchone()

        except Exception as e:
            print(f"Backend Error: {e}")
            return redirect('/login')
        
        except Error as e:
            print(f"DB Error: {e}")
            return redirect('/login')

        if not email or not password:
            error = 'Todos os campos precisam estar preenchidos!'
            return render_template('login.html', errormsg=error)
    
        elif email == MASTER_EMAIL and password == MASTER_PASSWORD:
            session['adm'] = True
            return redirect('/admin')

        elif not company:
            error = 'Esse email não está cadastrado em nosso sistema!'
            return render_template('login.html', errormsg=error)
        
        elif password == company[5] and company[6] == 'inactive':
            error = 'Sua empresa está inativa!'
            return render_template('login.html', errormsg=error)
        
        elif password == company[5]:
            session['email'] = email
            session['password'] = password
            session['companyInfo'] = company
            
            return redirect('/company')

        elif password != company[5]:
            error = 'Senha incorreta!'
            return render_template('login.html', errormsg=error)        

# ADMIN PAGE

@app.route('/admin')
def admin():

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

# LOGOUT ROUTE

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# COMPANY REGISTERING ROUTE

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

# COMPANY EDITING ROUTE

@app.route('/edit-company/<int:id>', methods=['GET', 'POST'])
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

# COMPANY STATUS SWITCH ROUTE

@app.route('/switch-company-status/<int:id>')
def switch_company_status (id):
    
    if session.get('adm') != True:
        return redirect('/login')

    try:
        connection, cursor = DB.connect()
        cursor.execute('''SELECT * FROM company WHERE ID_Company = %s ;''', (id,))
        
        company = cursor.fetchone()

        if company[6] == 'active':

            cursor.execute('''UPDATE company
                        SET status = 'inactive' 
                        WHERE ID_Company = %s ;''', (id,))
            
            cursor.execute('''UPDATE vacancy
                SET status = 'inactive' 
                WHERE ID_Company = %s ;''', (id,))

        elif company[6] == 'inactive':
            
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

# COMPANY DELETION ROUTE

@app.route('/delete-company/<int:id>')
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

# COMPANY MENU ROUTE

@app.route('/company')
def company ():

    if not session:
        return redirect('/login')
    if session.get('adm') == True:
        return redirect('/admin')

    company = session['companyInfo']

    try:

        connection, cursor = DB.connect()
        cursor.execute("SELECT * FROM vacancy WHERE ID_Company = %s AND status = 'active' ORDER BY ID_Vacancy DESC", (company[0],))
        activeVacancies = cursor.fetchall()

        cursor.execute("SELECT * FROM vacancy WHERE ID_Company = %s AND status = 'inactive' ORDER BY ID_Vacancy DESC", (company[0],))
        inactiveVacancies = cursor.fetchall()

    except Exception as e:
        print(f'Backend Error: {e}')

    except Error as e:
        print(f'DB Error: {e}')

    finally:
        DB.stop(connection, cursor)
    
    return render_template('company.html', company=company, activeVacancies=activeVacancies, inactiveVacancies=inactiveVacancies)

# VACANCY REGISTERING ROUTE

@app.route('/new-vacancy', methods=['GET', 'POST'])
def new_vancancy ():

    if session.get('adm') == True:
        return redirect('/login')

    elif request.method == 'GET':
        return render_template('new-vacancy.html')

    elif request.method == 'POST':
        
        company = session['companyInfo']
        companyID = company[0]
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

#VACANCY EDITING ROUTE

@app.route('/edit-vacancy/<int:id>', methods=['GET', 'POST'])
def edit_vacancy (id):

    if session.get('adm') == True:
        return redirect('/adm')

    elif request.method == 'GET':

        try:
            connection, cursor = DB.connect()

            cursor.execute(f'SELECT * FROM vacancy WHERE ID_Vacancy = {id} ;')
            vacancy = cursor.fetchone()

            company = session['companyInfo']

            if company[0] != vacancy[7]:
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

if environment == 'development':
    if __name__ == '__main__':
        app.run(debug=True)