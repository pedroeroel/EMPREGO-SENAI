import mysql.connector
from app.config import *

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