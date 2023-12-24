from flask import render_template, session
from database import dbConnect
from sqlalchemy import text

def landing():
        with dbConnect.engine.connect() as conn:
                result = conn.execute(text("Select * from testtable"))
                rows = result.fetchall()

                descriptions = [row._asdict() for row in rows]
                return render_template('index.html', desc=descriptions)

def retrieveDashboardNavName(tourID):
        with dbConnect.engine.connect() as conn:
                query = "SELECT * FROM tournaments WHERE tourID = :tourID"
                inputs = {'tourID': tourID}
                getTour = conn.execute(text(query), inputs)
                rows = getTour.fetchall()

                tournamentName = rows[0][1]
                return tournamentName

def retrieveProjectNavName(projID):
        with dbConnect.engine.connect() as conn:
                query = "SELECT * FROM projects WHERE projID = :projID"
                inputs = {'projID': projID}
                getTour = conn.execute(text(query), inputs)
                rows = getTour.fetchall()

                projectName = rows[0][1]
                return projectName
        
def updateNavTournaments(projID):
        with dbConnect.engine.connect() as conn:
            query = "SELECT * FROM tournaments WHERE projID = :projID AND userID = :userID;"
            inputs = {'projID': projID, 'userID': session["id"]}
            getTour = conn.execute(text(query), inputs)
            rows = getTour.fetchall()

            tournamentlist = [row._asdict() for row in rows]

            session["tournav"] = tournamentlist
            return tournamentlist
        
def updateNavProjects():
        with dbConnect.engine.connect() as conn:
            query = "SELECT * FROM projects WHERE userID = :userID;"
            inputs = {'userID': session["id"]}
            getprojs = conn.execute(text(query), inputs)
            rows = getprojs.fetchall()

            projects = [row._asdict() for row in rows]

            session["projnav"] = projects
            return projects