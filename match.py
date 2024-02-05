from flask import render_template, session, request, flash, session, jsonify, url_for, redirect
from database import dbConnect
from sqlalchemy import text
from datetime import datetime
from general import *
import math

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

                # Select all matches of the stage
                matchQuery = "SELECT * FROM matches WHERE matches.stageID = :stageID"
                matchInputs = {'stageID': stageID}
                result = conn.execute(text(matchQuery), matchInputs)
                matchRows = result.fetchall()
                match = [row._asdict() for row in matchRows]
                # print("The match list is below:")
                # print(match)

                for m in match:
                    # print(m["matchID"])
                    matchParticipantQuery = 'SELECT * FROM matchParticipant JOIN participants ON matchParticipant.participantID = participants.participantID WHERE matchParticipant.matchID = :matchID'
                    matchParticipantInputs = {'matchID': m["matchID"]}
                    result = conn.execute(text(matchParticipantQuery), matchParticipantInputs)
                    matchParticipantRows = result.fetchall()
                    # print(matchParticipantRows)
                    matchParticipant = [row._asdict() for row in matchParticipantRows]
                    if not matchParticipant:
                        matchParticipant = [{'matchParticipantID': None, 'participantID': None, 'participantMatchOutcome': None, 'matchID': m["matchID"], 'participantName': None, 'participantEmail': None, 'tourID': None},
                                            {'matchParticipantID': None, 'participantID': None, 'participantMatchOutcome': None, 'matchID': m["matchID"], 'participantName': None, 'participantEmail': None, 'tourID': None}]
                
                    if len(matchParticipant) < 2:
                        matchParticipant += [{'matchParticipantID': None, 'participantID': None, 'participantMatchOutcome': None, 'matchID': m["matchID"], 'participantName': None, 'participantEmail': None, 'tourID': None}]

                    print("Below is matchParticipantArray")
                    print(matchParticipant)
                    m["matchParticipants"] = matchParticipant

                #Separate them into different rounds
                noOfRound = int(math.log2(int(numberOfParticipants)))
                stageMatchArray = []
                for no in range(noOfRound):
                    roundMatchArray = []
                    for m in match:
                        if m["bracketSequence"] == no + 1:
                            roundMatchArray.append(m)
                    stageMatchArray.append(roundMatchArray)        
                # print("Below is stageMatchArray")
                # print(stageMatchArray)   
                
            return render_template('stageMatch.html', navtype=navtype, tournamentName=tournamentName, projID=projID, tourID=tourID, stageID=stageID,
                                    stageName = stageName, stageSequence = stageSequence, stageFormatID = stageFormatID, numberOfParticipants = numberOfParticipants,
                                    numberOfGroups = numberOfGroups, matchFormatID = matchFormatID, maxGames = maxGames, stageMatchArray = stageMatchArray)
        
                                    
        except Exception as e:
            flash('Oops, an error has occured.', 'error')
            print(f"Error details: {e}")
            return render_template('stageMatch.html', navtype=navtype, tournamentName=tournamentName, projID=projID, tourID=tourID, stageID = stageID)
    
    def loadMatchDetails(projID, tourID, stageID, matchID):
        navtype = 'dashboard'
        tournamentName = retrieveDashboardNavName(tourID)

        return render_template('stageMatchDetails.html', navtype=navtype, tournamentName=tournamentName, projID=projID, tourID=tourID, stageID=stageID, matchID = matchID)
    
    def deleteMatch():
        return
    
