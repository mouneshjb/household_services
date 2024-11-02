# Main app code
# Importing required libraries
from flask import Flask

app = None

def setup_app():
    app = Flask(__name__)
    #Sqlite connection
    app.app_context().push() # Direct access to other module
    app.debug = True

# Call the setup function
setup_app()

from backend.controllers import *

if __name__ == '__main__':
    app.run()