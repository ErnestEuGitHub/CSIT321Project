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
                # print ("TournamentName: ",tournamentName)
                return tournamentName

def retrieveProjectNavName(projID):
        with dbConnect.engine.connect() as conn:
                query = "SELECT * FROM projects WHERE projID = :projID"
                inputs = {'projID': projID}
                getTour = conn.execute(text(query), inputs)
                rows = getTour.fetchall()

                projectName = rows[0][1]
                
                # print ("ProjectName: ",projectName)
                return projectName
        
        
def updateNavParticipants(participantID):
        with dbConnect.engine.connect() as conn:
            query = "SELECT * FROM participants WHERE participantID = :participantID AND userID = :userID;"
            inputs = {'participantID': participantID, 'userID': session["id"]}
            getParticipants = conn.execute(text(query), inputs)
            rows = getParticipants.fetchall()

            participantlist = [row._asdict() for row in rows]

            session["partnav"] = participantlist
            return participantlist
        
def updateNavTournaments(projID):
        with dbConnect.engine.connect() as conn:
            query = "SELECT * FROM tournaments WHERE projID = :projID AND userID = :userID AND (statusID IS NULL OR statusID != 5);"
            inputs = {'projID': projID, 'userID': session["id"]}
            getTour = conn.execute(text(query), inputs)
            rows = getTour.fetchall()

            tournamentlist = [row._asdict() for row in rows]

            session["tournav"] = tournamentlist
            return tournamentlist
        
def updateNavProjects():
        with dbConnect.engine.connect() as conn:
            query = "SELECT * FROM projects WHERE userID = :userID AND (statusID IS NULL OR statusID != 5);"
            inputs = {'userID': session["id"]}
            getprojs = conn.execute(text(query), inputs)
            rows = getprojs.fetchall()  
        #     print("rows: ",rows)  
            
            projects = [row._asdict() for row in rows]         
        #     print("projects: ",projects)  

            session["projnav"] = projects
            
            return projects
    
def gettingModeratorPermissions(tourID):
        with dbConnect.engine.connect() as conn:
                queryRetrieveModerator = """
                SELECT permissions.permissionName
                FROM moderators 
                LEFT JOIN moderatorPermissions ON moderators.moderatorID = moderatorPermissions.moderatorID 
                LEFT JOIN permissions ON moderatorPermissions.permissionID = permissions.permissionID
                WHERE moderators.tourID = :tourID AND moderators.userID = :userID"""
                inputRetrieveModerator = {'tourID': tourID, 'userID': session["id"]}
                # print("inputRetrieveModerator: ",inputRetrieveModerator)  
                retrieveModerator = conn.execute(text(queryRetrieveModerator),inputRetrieveModerator)
                permissions = retrieveModerator.fetchall()                
                # print("Permissions: ",permissions)  
                  
                moderatorPermissionList = [row[0] for row in permissions if row[0] is not None] # Assuming permissionList is the second column
                # print("Permission List: ", moderatorPermissionList)
            
                return moderatorPermissionList
        
def updateNavProjectsModerators():
        with dbConnect.engine.connect() as conn:
            query = """SELECT * FROM projects 
            LEFT JOIN tournaments on projects.projID == tournaments.projID
            LEFT JOIN moderators on tournaments.tourID == moderators.tourID
            WHERE moderators.userID = :userID AND (statusID IS NULL OR statusID != 5);"""
            inputs = {'userID': session["id"]}
            getprojs = conn.execute(text(query), inputs)
            rowModerator = getprojs.fetchall() 
        #     print("rowModerator: ",rowModerator)  
            
            moderatorProjects = [row._asdict() for row in rowModerator]   
        #     print("rowModerator: ",rowModerator)  

            session["projnav"] = moderatorProjects
            
            return moderatorProjects
        
def updateNavTournamentsModerator(projID):
        with dbConnect.engine.connect() as conn:
            query = """SELECT * FROM tournaments 
            WHERE projID = :projID AND userID = :userID 
            AND (statusID IS NULL OR statusID != 5);"""
            inputs = {'projID': projID, 'userID': session["id"]}
            getTour = conn.execute(text(query), inputs)
            rows = getTour.fetchall()

            tournamentlist = [row._asdict() for row in rows]

            session["tournav"] = tournamentlist
            return tournamentlist

    