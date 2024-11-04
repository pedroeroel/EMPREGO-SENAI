environment = 'development'

if environment == 'development':
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = 'senai'
    DB_NAME = 'emprego'

# SECRET KEY

SECRET_KEY = 'emprego'

# ADMIN ACCESS

MASTER_EMAIL = 'adm@adm'
MASTER_PASSWORD = 'adm'