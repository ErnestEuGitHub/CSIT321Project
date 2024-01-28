from flask import render_template, session, request, flash, session, jsonify, url_for, redirect
from database import dbConnect
from sqlalchemy import text
from datetime import datetime
from general import *

class Match:

    def loadMatch(projID, tourID, stageID):
        navtype = 'dashboard'
        tournamentName = retrieveDashboardNavName(tourID)
    
        try:
            with dbConnect.engine.connect() as conn:

                stageQuery = "SELECT * FROM stages WHERE stageID = :stageID"
                stageInputs = {'stageID': stageID}
                result = conn.execute(text(stageQuery), stageInputs)
                stageRows = result.fetchall()
                stage = [row._asdict() for row in stageRows]

                stageName = stage[0]['stageName']
                stageSequence = stage[0]['stageSequence']
                stageFormatID = stage[0]['stageFormatID']
                numberOfParticipants = stage[0]['numberOfParticipants']
                numberOfGroups = stage[0]['numberOfGroups']
                matchFormatID = stage[0]['matchFormatID']
                maxGames = stage[0]['maxGames']

            return render_template('stageMatch.html', navtype=navtype, tournamentName=tournamentName, projID=projID, tourID=tourID, stageID=stageID,
                                    stageName = stageName, stageSequence = stageSequence, stageFormatID = stageFormatID, numberOfParticipants = numberOfParticipants,
                                    numberOfGroups = numberOfGroups, matchFormatID = matchFormatID, maxGames = maxGames)
        
                                    
        except Exception as e:
            flash('Oops, an error has occured.', 'error')
            print(f"Error details: {e}")
            return render_template('stageMatch.html', navtype=navtype, tournamentName=tournamentName, projID=projID, tourID=tourID, stageID = stageID)
    
    def configureMatch():
        return
    
    def deleteMatch():
        return
    
