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
from createProj import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

@app.route('/')
def loadLanding():
    if "id" in session:
        return redirect(url_for('loadhome'))
    page = landing()
    return page
    
@app.route('/login', methods=["POST", "GET"])
def loadLogin():
    if "id" in session:
        return redirect(url_for('loadhome'))
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
        return redirect(url_for('loadhome'))
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
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from projects WHERE userID = :userID AND projID = :projID"
            inputs = {'userID': session["id"], 'projID': projID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = tournaments(projID)
                return page
            
            else:
                return render_template('notfound.html')

@app.route('/createTour', methods=["POST", "GET"])
def loadCreateTour():
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    page = createTour()
    return page

@app.route('/createProj', methods=["POST", "GET"])
def loadCreateProj():
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    page = createProj()
    return page

@app.route('/get_formats', methods=['POST'])
def getformatspy():
    formats = getformat()
    return formats

@app.route('/tournamentOverviewPage/<tourID>')
def loadTourOverviewWithID(tourID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from tournaments WHERE userID = :userID AND tourID = :tourID"
            inputs = {'userID': session["id"], 'tourID': tourID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = TourOverviewDetails(tourID)
                return page
            
            else:
                return render_template('notfound.html')

@app.route('/dashboard/<tourID>', methods=["POST", "GET"])
def loaddashboard(tourID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from tournaments WHERE userID = :userID AND tourID = :tourID"
            inputs = {'userID': session["id"], 'tourID': tourID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = dashboard(tourID)
                return page
            
            else:
                return render_template('notfound.html')

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