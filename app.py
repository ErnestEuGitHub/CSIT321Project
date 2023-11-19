from flask import Flask
from landing import *
from login import *
from register import *
from createTour import *
from getformat import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

@app.route('/')
def loadLanding():
    page = landing()
    return page
    
@app.route('/login', methods=["POST", "GET"])
def loadLogin():
    page = login()
    return page

@app.route('/register', methods=["POST", "GET"])
def loadregister():
    page = register()
    return page

@app.route('/createTour', methods=["POST", "GET"])
def loadCreateTour():
    page = createTour()
    return page

@app.route('/get_formats', methods=['POST'])
def getformatspy():
    formats = getformat()
    return formats

if __name__ == "__main__":
    
    app.run(debug=True)