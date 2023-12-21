from flask import Flask
from landing import *
from login import *
from register import *
from createTour import *
from getformat import *
from tournamentDashboard import *
from tournamentParticipant import *

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

@app.route('/tournamentOverviewPageDetails', methods=["POST", "GET"])
def loadTournamentOverviewDetails():
    return render_template('tournamentOverviewPageDetails.html')

@app.route('/tournamentOverviewPageRules', methods=["POST", "GET"])
def loadTournamentOverviewRules():
    return render_template('tournamentOverviewPageRules.html')

@app.route('/tournamentDashboard', methods=["POST", "GET"])
def loadTournamentDashboard():
    page = tournamentDashboard()
    return page

@app.route('/tournamentParticipant', methods=["POST", "GET"])
def loadTournamentParticipant():
    page = tournamentParticipant()
    return page



if __name__ == "__main__":    
    app.run(debug=True)