# Main app code
# Importing required libraries
from flask import Flask
from backend.models import db


app = None

def setup_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydb.sqlite3" #Sqlite connection
    db.init_app(app) # Flask app is connected to db
    app.app_context().push() # Direct access to other module
    app.debug = True

# Call the setup function
setup_app()

from backend.controllers import *

if __name__ == '__main__':
    app.run()