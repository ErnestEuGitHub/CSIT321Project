from flask import Flask
from landing import *
from login import *
from register import *

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

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/tournament')
def tournament():
    return render_template('tournament.html')

if __name__ == "__main__":
    
    app.run(debug=True)