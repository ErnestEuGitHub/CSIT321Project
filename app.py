from flask import Flask
from landing import *
from login import *
from register import *
from createTour import *
from getformat import *
from dashboard import *
from viewTour import *
from settings import *
from home import *
from tournaments import*

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
def loadhome():
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    page = home()
    return page

@app.route('/projects/<projID>')
def loadtournaments(projID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    page = tournaments(projID)
    return page

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
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    page = TourOverviewDetails(tourID)
    return page

@app.route('/dashboard', methods=["POST", "GET"])
def loaddashboard():
    page = dashboard()
    return page

@app.route('/settings/<tourID>', methods=["POST", "GET"])
def loadsettings(tourID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from tournaments WHERE userID = :userID AND tourID = :tourID"
            inputs = {'userID': session["id"], 'tourID': tourID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = settings(tourID)
                return page
            
            else:
                return render_template('notfound.html')

@app.errorhandler(404)
def loadnotfound(error):
    return render_template('notfound.html', error=error)

if __name__ == "__main__":
    
    app.run(debug=True)