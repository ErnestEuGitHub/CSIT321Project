from flask import render_template, session, jsonify
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

            projects = [row._asdict() for row in rows]

            session["projnav"] = projects
            return projects
        
def updateVenue(matchstart, matchend):
        with dbConnect.engine.connect() as conn:
            query = "SELECT matchID, venueID FROM matches WHERE (:matchstart >= matches.startTime AND :matchend <= matches.endTime) OR (:matchstart <= matches.startTime AND :matchend >= matches.endTime) OR (:matchstart >= matches.startTime AND :matchstart <= matches.endTime) OR (:matchend >= matches.startTime AND :matchend <= matches.endTime) UNION SELECT exEventName, venueID FROM venueExtEvent WHERE (:matchstart >= venueExtEvent.startDateTime AND :matchend <= venueExtEvent.endDateTime) OR (:matchstart <= venueExtEvent.startDateTime AND :matchend >= venueExtEvent.endDateTime) OR (:matchstart >= venueExtEvent.startDateTime AND :matchstart <= venueExtEvent.endDateTime) OR (:matchend >= venueExtEvent.startDateTime AND :matchend <= venueExtEvent.endDateTime)"
            inputs = {'matchstart': matchstart, 'matchend': matchend}
            getUnavailableVenues = conn.execute(text(query), inputs)
            unavailableVenuesfetch = getUnavailableVenues.fetchall()

            unavailableVenuesListDict = [row._asdict() for row in unavailableVenuesfetch]
            venueIDs = [row['venueID'] for row in unavailableVenuesListDict]
            venueIDs = [venueID for venueID in venueIDs if venueID is not None]
            unavailableVenueIDs = set(venueIDs)

            query = "SELECT * from venue"
            getVenues = conn.execute(text(query))
            venuelist = getVenues.fetchall()

            venuelistFiltered = [venue for venue in venuelist if venue[0] not in unavailableVenueIDs]
            venuelistFiltered_dicts = [{'venueID': venue[0], 'venueName': venue[1]} for venue in venuelistFiltered]

            return jsonify(venuelistFiltered_dicts)