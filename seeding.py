from flask import render_template, session, request, flash, session, jsonify, url_for, redirect
from database import dbConnect
from sqlalchemy import text
from general import *

def seeding(tourID, stageID):
    #fornavbar
    session["placementTour"] = tourID
    navtype = 'dashboard'
    tournamentName = retrieveDashboardNavName(tourID)

    with dbConnect.engine.connect() as conn:
        query = "SELECT numberOfParticipants, numberOfGroups FROM stages WHERE stageID = :stageID"
        inputs = {'stageID': stageID}
        result = conn.execute(text(query), inputs)
        rows = result.fetchall()

        numberOfParticipants = rows[0][0]
        numberOfGroups = rows[0][1]

        query = "SELECT participantID, participantName FROM participants WHERE tourID = :tourID"
        inputs = {'tourID': tourID}
        result = conn.execute(text(query), inputs)
        rows = result.fetchall()

        participantID = [row._asdict() for row in rows]
        participantName = [row._asdict() for row in rows]

    return render_template('seeding.html', participantID=participantID, participantName=participantName, numberOfParticipants=numberOfParticipants, numberOfGroups=numberOfGroups, navtype=navtype, tournamentName=tournamentName, tourID=tourID)