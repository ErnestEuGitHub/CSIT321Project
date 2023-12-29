from flask import Flask
from general import *
from stages import *
from user import *
from tournaments import *
from projects import *
from tournamentParticipant import *

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
    page = User.login()
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
    page = User.register()
    return page

@app.route('/home')
def loadhome():
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    page = Projects.home()
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
                page = Tournaments.tournaments(projID)
                return page
            
            else:
                return render_template('notfound.html')

@app.route('/createTour', methods=["POST", "GET"])
def loadCreateTour():
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    page = Tournaments.createTour()
    return page

@app.route('/createProj', methods=["POST", "GET"])
def loadCreateProj():
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    page = Projects.createProj()
    return page

@app.route('/get_formats', methods=['POST'])
def getformatspy():
    formats = Tournaments.getformat()
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
                page = Tournaments.TourOverviewDetails(tourID)
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
                page = Tournaments.dashboard(tourID)
                return page
            
            else:
                return render_template('notfound.html')

@app.route('/placement/<tourID>', methods=["POST", "GET"])
def placement(tourID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    
    #fornavbar
    session["placementTour"] = tourID
    navtype = 'dashboard'
    tournamentName = retrieveDashboardNavName(tourID)

    return render_template('placement.html', navtype=navtype, tournamentName=tournamentName, tourID=tourID)

@app.route('/update_content', methods=['POST'])
def update_content():
    updated_content = Tournaments.get_updated_content()
    return jsonify({'content': updated_content})

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
                page = Tournaments.settings(tourID)
                return page
            
            else:
                return render_template('notfound.html')

@app.route('/structure/<tourID>', methods=["POST", "GET"])
def loadstructure(tourID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from tournaments WHERE userID = :userID AND tourID = :tourID"
            inputs = {'userID': session["id"], 'tourID': tourID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = Tournaments.structure(tourID)
                return page
            
            else:
                return render_template('notfound.html')
            
@app.route('/createStage/<tourID>', methods=["POST", "GET"])
def loadcreatestage(tourID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from tournaments WHERE userID = :userID AND tourID = :tourID"
            inputs = {'userID': session["id"], 'tourID': tourID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = Tournaments.createStage(tourID)
                return page
            
            else:
                return render_template('notfound.html')

@app.route('/configureStage/<tourID>/<stageID>', methods=["POST", "GET"])
def loadconfigurestage(tourID, stageID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from tournaments WHERE userID = :userID AND tourID = :tourID"
            inputs = {'userID': session["id"], 'tourID': tourID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = Stage.configureStage(tourID, stageID)
                return page
            
            else:
                return render_template('notfound.html')

@app.route('/deleteStage/<tourID>/<stageID>', methods=["POST", "GET"])
def loaddeletestage(tourID, stageID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from tournaments WHERE userID = :userID AND tourID = :tourID"
            inputs = {'userID': session["id"], 'tourID': tourID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = Stage.deleteStage(tourID, stageID)
                return page
            
            else:
                return render_template('notfound.html')
  
@app.route('/tournamentParticipant/<tourID>', methods=["POST", "GET"])
def loadTournamentParticipant(tourID):
    page = tournamentParticipant(tourID)
    return page

@app.route('/createParticipant/<tourID>', methods=["POST", "GET"])
def loadCreateParticipant(tourID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from tournaments WHERE userID = :userID AND tourID = :tourID"
            inputs = {'userID': session["id"], 'tourID': tourID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = Tournaments.createParticipant(tourID)
                return page
            
            else:
                return render_template('notfound.html')
            
@app.errorhandler(404)
def loadnotfound(error):
    return render_template('notfound.html', error=error)

if __name__ == "__main__":
    
    app.run(debug=True)