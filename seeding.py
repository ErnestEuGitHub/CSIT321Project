from flask import render_template, session, request, flash, session, jsonify, url_for, redirect
from database import dbConnect
from sqlalchemy import text
from general import *

def seeding(projID, tourID, stageID):
    #fornavbar
    navtype = 'dashboard'
    tournamentName = retrieveDashboardNavName(tourID)

    #stageformat 1 is Single Elim, 2 is Double Elim, 3 is Single RR, 4 is Double RR
    with dbConnect.engine.connect() as conn:
        query = "SELECT numberOfParticipants, numberOfGroups, stageFormatID FROM stages WHERE stageID = :stageID"
        inputs = {'stageID': stageID}
        result = conn.execute(text(query), inputs)
        rows = result.fetchall()

        numberOfParticipants = rows[0][0]
        numberOfGroups = rows[0][1]
        stageForm = rows[0][2]

        query = "SELECT participantID, participantName FROM participants WHERE tourID = :tourID"
        inputs = {'tourID': tourID}
        result = conn.execute(text(query), inputs)
        rows = result.fetchall()

        participantID = [row._asdict() for row in rows]
        participantName = [row._asdict() for row in rows]

        if stageForm == 1 or stageForm == 2:
            return render_template('seedingSingleElim.html', participantID=participantID, participantName=participantName, numberOfParticipants=numberOfParticipants, numberOfGroups=numberOfGroups, navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID)
        else:
            return render_template('seeding.html', participantID=participantID, participantName=participantName, numberOfParticipants=numberOfParticipants, numberOfGroups=numberOfGroups, navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID)