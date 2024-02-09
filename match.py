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
                        matchParticipant = [{'matchParticipantID': None, 'participantID': None, 'participantMatchOutcome': None, 'matchID': m["matchID"], 'matchScore': None, 'participantName': None, 'participantEmail': None, 'tourID': None},
                                            {'matchParticipantID': None, 'participantID': None, 'participantMatchOutcome': None, 'matchID': m["matchID"], 'matchScore': None, 'participantName': None, 'participantEmail': None, 'tourID': None}]
                
                    if len(matchParticipant) < 2:
                        matchParticipant += [{'matchParticipantID': None, 'participantID': None, 'participantMatchOutcome': None, 'matchID': m["matchID"],'matchScore': None, 'participantName': None, 'participantEmail': None, 'tourID': None}]

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

      
        with dbConnect.engine.connect() as conn:
                
                stageQuery = "SELECT * FROM stages WHERE stageID = :stageID"
                stageInputs = {'stageID': stageID}
                result = conn.execute(text(stageQuery), stageInputs)
                stageRows = result.fetchall()
                stage = [row._asdict() for row in stageRows]
                maxGames = int(stage[0]['maxGames'])
                print(maxGames)
                
                print("This is stage")
                print(stage)
                print("/n")

                matchQuery = "SELECT * FROM matches WHERE matchID = :matchID"
                matchInputs = {'matchID': matchID}
                result = conn.execute(text(matchQuery), matchInputs)
                matchRows = result.fetchall()
                match = [row._asdict() for row in matchRows]

                print("This is match")
                print(match)
                print("/n")
                
                # matchParticipantArray = []

                for m in match:
                    # print(m["matchID"])
                    matchParticipantQuery = 'SELECT * FROM matchParticipant JOIN participants ON matchParticipant.participantID = participants.participantID WHERE matchParticipant.matchID = :matchID'
                    matchParticipantInputs = {'matchID': m["matchID"]}
                    result = conn.execute(text(matchParticipantQuery), matchParticipantInputs)
                    matchParticipantRows = result.fetchall()
                    # print(matchParticipantRows)
                    matchParticipant = [row._asdict() for row in matchParticipantRows]
                    if not matchParticipant:
                        matchParticipant = [{'matchParticipantID': None, 'participantID': None, 'participantMatchOutcome': None, 'matchID': m["matchID"], 'matchScore': None, 'participantName': None, 'participantEmail': None, 'tourID': None},
                                            {'matchParticipantID': None, 'participantID': None, 'participantMatchOutcome': None, 'matchID': m["matchID"], 'matchScore': None, 'participantName': None, 'participantEmail': None, 'tourID': None}]
                
                    if len(matchParticipant) < 2:
                        matchParticipant += [{'matchParticipantID': None, 'participantID': None, 'participantMatchOutcome': None, 'matchID': m["matchID"],'matchScore': None, 'participantName': None, 'participantEmail': None, 'tourID': None}]

                print("This is matchParticipant")
                print(matchParticipant)
                print("/n")
                
                gameQuery = "SELECT * FROM games WHERE matchID = :matchID"
                gameInputs = {'matchID': matchID}
                result = conn.execute(text(gameQuery), gameInputs)
                gameRows = result.fetchall()
                game = [row._asdict() for row in gameRows]

                print("This is game")
                print(game)
                print("/n")

                gameParticipantArray = []

                for g in game:
                    gameParticipantQuery = 'SELECT * FROM gameParticipant JOIN participants ON gameParticipant.participantID = participants.participantID WHERE gameParticipant.gameID = :gameID'
                    gameParticipantInputs = {'gameID': g["gameID"]}
                    result = conn.execute(text(gameParticipantQuery), gameParticipantInputs)
                    gameParticipantRows = result.fetchall()
                    # print(matchParticipantRows)
                    gameParticipant = [row._asdict() for row in gameParticipantRows]
                    if not gameParticipant:
                        gameParticipant = [{'gameParticipantID': None, 'gameParticipantScore': None, 'gameID': g["gameID"], 'gameParticipantOutcome': None, 'partcipantID': None, 'participantName': None, 'participantEmail': None, 'tourID': None},
                                            {'gameParticipantID': None, 'gameParticipantScore': None, 'gameID': g["gameID"], 'gameParticipantOutcome': None, 'partcipantID': None, 'participantName': None, 'participantEmail': None, 'tourID': None}]
                
                    if len(gameParticipant) < 2:
                        gameParticipant += [{'gameParticipantID': None, 'gameParticipantScore': None, 'gameID': g["gameID"], 'gameParticipantOutcome': None, 'partcipantID': None, 'participantName': None, 'participantEmail': None, 'tourID': None}] 
                    
                    gameParticipantArray.append(gameParticipant)

                    print("This is gameParticipantArray")
                    print(gameParticipantArray)
                    print("/n")

        return render_template('stageMatchDetails.html', navtype=navtype, tournamentName=tournamentName, projID=projID, tourID=tourID, stageID=stageID, matchID=matchID, maxGames=maxGames, match=match, matchParticipant=matchParticipant, game=game, gameParticipant=gameParticipant)
    
