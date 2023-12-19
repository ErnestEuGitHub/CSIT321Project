from flask import Flask
from landing import *
from login import *
from register import *
from createTour import *
from getformat import *
from dashboard import *
from placement import *
from viewTour import *
from settings import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

@app.route('/')
def loadLanding():
    if "id" in session:
        return redirect(url_for('home'))
    page = landing()
    return page
    
@app.route('/login', methods=["POST", "GET"])
def loadLogin():
    if "id" in session:
        return redirect(url_for('home'))
    page = login()
    return page

@app.route('/logout', methods=["POST", "GET"])
def logout():
    session.pop("id", None)
    session.pop("profileID", None)
    session.pop("fname", None)
    return redirect(url_for('loadLogin'))

@app.route('/register', methods=["POST", "GET"])
def loadregister():
    if "id" in session:
        return redirect(url_for('home'))
    page = register()
    return page

@app.route('/home')
def home():
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    return render_template('home.html')

@app.route('/tournament')
def tournament():
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    return render_template('tournament.html')

@app.route('/createTour', methods=["POST", "GET"])
def loadCreateTour():
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    page = createTour()
    return page

@app.route('/get_formats', methods=['POST'])
def getformatspy():
    formats = getformat()
    return formats

@app.route('/tournamentOverviewPage', methods=["POST", "GET"])
def loadTournamentOverviewPage():
    return render_template('tournamentOverviewPage.html')

@app.route('/tournamentOverviewPage/<tourID>')
def loadTourOverviewWithID(tourID):
    page = TourOverviewDetails(tourID)
    return page

@app.route('/dashboard', methods=["POST", "GET"])
def loaddashboard():
    page = dashboard()
    return page

@app.route('/placement', methods=["POST", "GET"])
def placement():
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    return render_template('placement.html')

@app.route('/update_content', methods=['POST'])
def update_content():
    # Read updated content from a separate HTML file
    with open('seeding.html', 'r') as file:
        updated_content = file.read()
    return jsonify({'content': updated_content})

@app.route('/settings/<tourID>', methods=["POST", "GET"])
def loadsettings(tourID):
    page = settings(tourID)
    return page

if __name__ == "__main__":
    
    app.run(debug=True)