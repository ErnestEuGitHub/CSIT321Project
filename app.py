from flask import Flask
from general import *
from stages import *
from user import *
from tournaments import *
from projects import *
from match import *

from placement import *
from seeding import *

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

@app.route('/createTour/<projID>', methods=["POST", "GET"])
def loadCreateTour(projID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    page = Tournaments.createTour(projID)
    return page

@app.route('/createProj', methods=["POST", "GET"])
def loadCreateProj():
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    page = Projects.createProj()
    return page

@app.route('/settings/<projID>', methods=["POST", "GET"])
def loadProjSettings(projID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from projects WHERE userID = :userID AND projID = :projID"
            inputs = {'userID': session["id"], 'projID': projID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = Projects.ProjSettings(projID)
                return page
            
            else:
                return render_template('notfound.html')
            
@app.route('/endProj/<projID>', methods=["POST", "GET"])
def loadSuspendProj(projID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from projects WHERE userID = :userID AND projID = :projID"
            inputs = {'userID': session["id"], 'projID': projID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = Projects.SuspendProj(projID)
                return page
            
            else:
                return render_template('notfound.html')

@app.route('/get_formats', methods=['POST'])
def getformatspy():
    formats = Tournaments.getformat()
    return formats

@app.route('/tournamentOverviewPage/<projID>/<tourID>')
def loadTourOverviewWithID(projID, tourID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from tournaments WHERE userID = :userID AND tourID = :tourID"
            inputs = {'userID': session["id"], 'tourID': tourID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                if rows[0][9] == 5:
                    return redirect(url_for('loadtournaments', projID=projID))
                else:
                    page = Tournaments.TourOverviewDetails(projID, tourID)
                    return page
            
            else:
                return render_template('notfound.html')

@app.route('/dashboard/<projID>/<tourID>', methods=["POST", "GET"])
def loaddashboard(projID, tourID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from tournaments WHERE userID = :userID AND tourID = :tourID"
            inputs = {'userID': session["id"], 'tourID': tourID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                if rows[0][9] == 5:
                    return redirect(url_for('loadtournaments', projID=projID))
                else:
                    page = Tournaments.dashboard(projID, tourID)
                    return page
            
            else:
                return render_template('notfound.html')


@app.route('/placement/<projID>/<tourID>', methods=["POST", "GET"])
def loadPlacement(projID, tourID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))

    page = placement(projID, tourID)
    return page

@app.route('/seeding/<projID>/<tourID>/<stageID>', methods=["POST", "GET"])
def loadSeeding(projID, tourID, stageID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    
    page = seeding(projID, tourID, stageID)
    return page

@app.route('/settings/general/<projID>/<tourID>', methods=["POST", "GET"])
def loadsettings(projID, tourID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from tournaments WHERE userID = :userID AND tourID = :tourID"
            inputs = {'userID': session["id"], 'tourID': tourID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = Tournaments.settingsGeneral(projID, tourID)
                return page
            
            else:
                return render_template('notfound.html')
            
@app.route('/suspendTour/<projID>/<tourID>', methods=["POST", "GET"])
def loadSuspendTour(projID, tourID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from tournaments WHERE userID = :userID AND tourID = :tourID"
            inputs = {'userID': session["id"], 'tourID': tourID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = Tournaments.SuspendTour(projID, tourID)
                return page
            
            else:
                return render_template('notfound.html')

@app.route('/structure/<projID>/<tourID>', methods=["POST", "GET"])
def loadstructure(projID, tourID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from tournaments WHERE userID = :userID AND tourID = :tourID"
            inputs = {'userID': session["id"], 'tourID': tourID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = Tournaments.structure(projID, tourID)
                return page
            
            else:
                return render_template('notfound.html')
            
@app.route('/createStage/<projID>/<tourID>', methods=["POST", "GET"])
def loadcreatestage(projID, tourID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from tournaments WHERE userID = :userID AND tourID = :tourID"
            inputs = {'userID': session["id"], 'tourID': tourID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = Tournaments.createStage(projID, tourID)
                return page
            
            else:
                return render_template('notfound.html')

@app.route('/configureStage/<projID>/<tourID>/<stageID>', methods=["POST", "GET"])
def loadconfigurestage(projID, tourID, stageID):

    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from tournaments WHERE userID = :userID AND tourID = :tourID"
            inputs = {'userID': session["id"], 'tourID': tourID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = Stage.configureStage(projID, tourID, stageID)
                return page
            else:
                return render_template('notfound.html')

@app.route('/deleteStage/<projID>/<tourID>/<stageID>', methods=["POST", "GET"])
def loaddeletestage(projID, tourID, stageID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from tournaments WHERE userID = :userID AND tourID = :tourID"
            inputs = {'userID': session["id"], 'tourID': tourID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = Stage.deleteStage(projID, tourID, stageID)
                return page
            
            else:
                return render_template('notfound.html')


@app.route('/participant/<projID>/<tourID>', methods=["POST", "GET"])
def loadParticipant(projID, tourID):
    page = Tournaments.participant(projID, tourID)
    return page

@app.route('/createParticipant/<projID>/<tourID>', methods=["POST", "GET"])
def loadCreateParticipant(projID, tourID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from tournaments WHERE tournaments.userID = :userID AND tournaments.tourID = :tourID"
            inputs = {'userID': session["id"], 'tourID': tourID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = Tournaments.createParticipant(projID, tourID)
                return page
            
            else:
                return render_template('notfound.html')
            
@app.route('/editParticipant/<projID>/<tourID>/<participantID>', methods=["POST", "GET"])
def loadEditParticipant(projID, tourID, participantID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from tournaments JOIN participants ON tournaments.tourID = participants.tourID WHERE tournaments.userID = :userID AND tournaments.tourID = :tourID AND participants.participantID = :participantID"
            inputs = {'userID': session["id"], 'tourID': tourID, 'participantID': participantID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = Tournaments.editParticipant(projID, tourID, participantID)
                return page
            else:
                return render_template('notfound.html')
            
@app.route('/deleteParticipant/<projID>/<tourID>/<participantID>', methods=["POST", "GET"])
def loadDeleteParticipant(projID, tourID, participantID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from tournaments JOIN participants ON tournaments.tourID = participants.tourID WHERE tournaments.userID = :userID AND tournaments.tourID = :tourID AND participants.participantID = :participantID"
            inputs = {'userID': session["id"], 'tourID': tourID, 'participantID': participantID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = Tournaments.deleteParticipant(projID, tourID, participantID)
                return page
            else:
                page = Tournaments.participant(projID, tourID)
                return page
            
@app.route('/deletePlayer/<projID>/<tourID>/<participantID>/<playerID>', methods=["POST", "GET"])
def loadDeletePlayer(projID, tourID, participantID, playerID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        print("loadDeletePlayer function is being accessed!")  # Add this print statement
        with dbConnect.engine.connect() as conn:
            query = """SELECT * FROM tournaments JOIN participants JOIN players 
            ON tournaments.tourID = participants.tourID AND participants.participantID = players.participantID 
            WHERE tournaments.userID = :userID AND tournaments.tourID = :tourID AND 
            participants.participantID = :participantID AND players.playerID = :playerID"""
            inputs = {'userID': session["id"], 'tourID': tourID, 'participantID': participantID, 'playerID': playerID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = Tournaments.deletePlayer(projID, tourID, participantID, playerID)
                return page
            else:
                page = Tournaments.participant(projID, tourID)
                return page
            
@app.route('/moderator/<projID>/<tourID>', methods=["POST", "GET"])
def loadModerator(projID, tourID):
    page = Tournaments.moderator(projID, tourID)
    return page

@app.route('/createModerator/<projID>/<tourID>', methods=["POST", "GET"])
def loadCreateModerator(projID, tourID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from tournaments WHERE tournaments.userID = :userID AND tournaments.tourID = :tourID"
            inputs = {'userID': session["id"], 'tourID': tourID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = Tournaments.createModerator(projID, tourID)
                return page
            
            else:
                return render_template('notfound.html')
            
@app.route('/editModerator/<projID>/<tourID>/<moderatorID>', methods=["POST", "GET"])
def loadEditModerator(projID, tourID, moderatorID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = """SELECT * from tournaments JOIN users JOIN moderators
            ON tournaments.userID = users.userID AND users.userID = moderators.userID
            WHERE tournaments.userID = :userID AND tournaments.tourID = :tourID AND moderators.moderatorID = :moderatorID"""
            inputs = {'userID': session["id"], 'tourID': tourID, 'moderatorID': moderatorID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = Tournaments.editModerator(projID, tourID, moderatorID)
                return page
            
            else:
                return render_template('notfound.html')
            
@app.route('/match/<projID>/<tourID>', methods=["POST", "GET"])
def match(projID, tourID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from tournaments WHERE userID = :userID AND tourID = :tourID"
            inputs = {'userID': session["id"], 'tourID': tourID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = Tournaments.match(projID, tourID)
                return page
            
            else:
                return render_template('notfound.html')
            
@app.route('/loadmatch/<projID>/<tourID>/<stageID>', methods=["POST", "GET"])
def loadmatch(projID, tourID, stageID):
    if "id" not in session:
        return redirect(url_for('loadLogin'))
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * from tournaments WHERE userID = :userID AND tourID = :tourID"
            inputs = {'userID': session["id"], 'tourID': tourID}
            checktour = conn.execute(text(query), inputs)
            rows = checktour.fetchall()

            if rows:
                page = Match.loadMatch(projID, tourID, stageID)
                return page
            
            else:
                return render_template('notfound.html')

@app.errorhandler(404)
def loadnotfound(error):
    return render_template('notfound.html', error=error)

if __name__ == "__main__":
    
    app.run(debug=True)