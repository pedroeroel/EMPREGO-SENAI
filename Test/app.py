from flask import Flask, render_template, request, redirect, send_from_directory
import mysql.connector
import os
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads/')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def conectar_db():
    # Estabelece conexão com o Banco de Dados
    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="senai",
        database="teste_upload"
    )
    cursor = conexao.cursor(dictionary=True)
    return conexao, cursor

def encerrar_db(cursor, conexao):
    # Fechar cursor e conexão com o BD
    cursor.close()
    conexao.close()


@app.route('/')
def index():
    try:
        conexao, cursor = conectar_db()
        comandoSQL = "SELECT * FROM arquivo"
        cursor.execute(comandoSQL)
        arquivos = cursor.fetchall()
        return render_template('index.html',arquivos=arquivos)
    except mysql.connector.Error as erro:
        return f"Erro de banco: {erro}"  
    except Exception as erro:  
        return f"Erro de código: {erro}"
    finally:
        encerrar_db(cursor, conexao)

@app.route('/upload', methods=['GET','POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')
    
    if request.method == 'POST':

        file = request.files['file']
        
        if file.filename == '':
            msg = 'Nenhum arquivo enviado!'
            return render_template('upload.html', msg=msg)
        
        try:

            timestamp = int(time.time())
            nome_arquivo = f'{timestamp}_{file.filename}'
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo))

            conexao, cursor = conectar_db()
            cursor.execute("INSERT INTO arquivo (nomearquivo) VALUES (%s)", (nome_arquivo,))
            
            conexao.commit()
            
            return redirect('/')

        except Exception as e:
            print(f'Back-End Error: {e}')
        
            return render_template('upload.html', msg='Erro de Back-End')

        except mysql.connector.Error as e:
            print(f'DB Error: {e}')

            return render_template('upload.html', msg='Erro de Database')


        finally: 

            encerrar_db(cursor, conexao)
            return redirect('/')

@app.route('/download/<string:filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/delete/<filename>')
def delete_file(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.remove(file_path)  # Exclui o arquivo

        conexao, cursor = conectar_db()
        comandoSQL = "DELETE FROM arquivo WHERE nomearquivo = %s"
        cursor.execute(comandoSQL, (filename,))
        conexao.commit()

        return redirect('/')
    except mysql.connector.Error as erro:
        return f"Erro de banco de Dados: {erro}"
    except Exception as erro:
        return f"Erro de back-end: {erro}"
    finally:
        encerrar_db(conexao, cursor)

if __name__ == '__main__':
    app.run(debug=True)