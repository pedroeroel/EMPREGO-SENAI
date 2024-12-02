from app.app import create_app
from app.config import *

app = create_app()


if environment == 'development':
    if __name__ == '__main__':
        app.run(debug=True)