import mysql.connector
from app.config import *
import re

class DB:

    def connect():
        
        connection = mysql.connector.connect(
        host = DB_HOST,
        user = DB_USER,
        password = DB_PASSWORD,
        database = DB_NAME
        )

        cursor = connection.cursor(dictionary=True)

        return connection, cursor
    
    def stop(connection, cursor):

        cursor.close()
        connection.close()

    def clearInput(type, input):
        if type.lower() in ["cpf", "cnpj", "phone"]:
        
            return re.sub(r"\D", "", input)
    
        elif type.lower() == "currency":

            raw = input.replace(".", "").replace("-", "").replace("/", "").replace("(", "").replace(")", "").replace(" ", "").replace("R$", "").replace(",", ".")
        
            return raw