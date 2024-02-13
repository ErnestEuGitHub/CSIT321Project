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
    
        # if request.method == "POST":
        #     action = request.form.get('action')
        #     if action == 'venue':
                
        # else:
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
                        matchParticipant = [{'matchParticipantID': None, 'participantID': None, 'participantMatchOutcome': None, 'matchID': m["matchID"], 'matchScore': 0, 'participantName': None, 'participantEmail': None, 'tourID': None},
                                            {'matchParticipantID': None, 'participantID': None, 'participantMatchOutcome': None, 'matchID': m["matchID"], 'matchScore': 0, 'participantName': None, 'participantEmail': None, 'tourID': None}]
                
                    if len(matchParticipant) < 2:
                        matchParticipant += [{'matchParticipantID': None, 'participantID': None, 'participantMatchOutcome': None, 'matchID': m["matchID"],'matchScore': 0, 'participantName': None, 'participantEmail': None, 'tourID': None}]

                    m["matchParticipants"] = matchParticipant
                    # print("Below is matchParticipantArray")
                    # print(matchParticipant)

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
                                    stageName = stageName, stageFormatID = stageFormatID, numberOfParticipants = numberOfParticipants,
                                    numberOfGroups = numberOfGroups, matchFormatID = matchFormatID, stageMatchArray = stageMatchArray)
        
                                    
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
            
            # print("This is stage")
            # print(stage)
            # print("/n")

            matchQuery = "SELECT * FROM matches WHERE matchID = :matchID"
            matchInputs = {'matchID': matchID}
            result = conn.execute(text(matchQuery), matchInputs)
            matchRows = result.fetchall()
            match = [row._asdict() for row in matchRows]

            # print("This is match")
            # print(match)
            # print("/n")
            
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

            # print("This is matchParticipant")
            # print(matchParticipant)
            # print("/n")
            
            gameQuery = "SELECT * FROM games WHERE matchID = :matchID"
            gameInputs = {'matchID': matchID}
            result = conn.execute(text(gameQuery), gameInputs)
            gameRows = result.fetchall()
            game = [row._asdict() for row in gameRows]

            # print("This is game")
            # print(game)
            # print("/n")

            gameParticipantArray = []

            for g in game:
                gameParticipantQuery = 'SELECT * FROM gameParticipant JOIN participants ON gameParticipant.participantID = participants.participantID WHERE gameParticipant.gameID = :gameID'
                gameParticipantInputs = {'gameID': g["gameID"]}
                result = conn.execute(text(gameParticipantQuery), gameParticipantInputs)
                gameParticipantRows = result.fetchall()
                # print(matchParticipantRows)
                gameParticipant = [row._asdict() for row in gameParticipantRows]
                if not gameParticipant:
                    gameParticipant = [{'gameParticipantID': None, 'gameParticipantScore': None, 'gameID': g["gameID"], 'gameParticipantOutcome': None, 'partcipantID': None},
                                        {'gameParticipantID': None, 'gameParticipantScore': None, 'gameID': g["gameID"], 'gameParticipantOutcome': None, 'partcipantID': None}]
            
                if len(gameParticipant) < 2:
                    gameParticipant += [{'gameParticipantID': None, 'gameParticipantScore': None, 'gameID': g["gameID"], 'gameParticipantOutcome': None, 'partcipantID': None}] 
                
                gameParticipantArray.append(gameParticipant)

                # print("This is gameParticipant")
                # print(gameParticipant)
                # print("/n")

            #Venue Details
            query = "SELECT * from matches LEFT JOIN venue ON matches.venueID = venue.venueID WHERE matchID = :matchID"
            inputs = {'matchID': matchID}
            getMatchDetails = conn.execute(text(query), inputs)
            matchfetchDetails = getMatchDetails.fetchall()
            matchDetails = [row._asdict() for row in matchfetchDetails]

            matchstart = matchDetails[0]["startTime"]
            matchend = matchDetails[0]["endTime"]
            currentvenueID = matchDetails[0]["venueID"]
            currentvenueName = matchDetails[0]["venueName"]

            if matchstart is None or matchend is None:
                query = "SELECT * from venue"
                getVenues = conn.execute(text(query))
                venuelistFiltered = getVenues.fetchall()

            else:
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

        return render_template('stageMatchDetails.html', navtype=navtype, tournamentName=tournamentName, projID=projID, tourID=tourID, stageID=stageID, matchID=matchID, maxGames=maxGames, match=match, matchParticipant=matchParticipant, game=game, gameParticipantArray=gameParticipantArray, venuelistFiltered=venuelistFiltered, currentvenueID=currentvenueID, currentvenueName=currentvenueName, matchstart=matchstart, matchend=matchend)


    def updateGamesDetails():
        
        if request.method == "POST":

            data = request.get_json()
            gamesData = data.get('gamesData')
            projID = data.get('projID')
            tourID = data.get('tourID')
            stageID = data.get('stageID')
            matchID = data.get('matchID')
            # print("This is the gamesData")
            # print(gamesData)
            # print("These are the IDs")
            # print(projID, tourID, stageID)

            with dbConnect.engine.connect() as conn:
                
                for game in gamesData:
                    updateGameDetailsQuery = 'UPDATE gameParticipant SET gameParticipantScore = :gameParticipantScore, gameParticipantOutcome = :gameParticipantOutcome WHERE gameParticipantID = :gameParticipantID'
                    gameDetailsInputs = {'gameParticipantScore': game['score'], 'gameParticipantOutcome': game['result'], 'gameParticipantID': game['gameParticipantID']}
                    result = conn.execute(text(updateGameDetailsQuery), gameDetailsInputs)
                    
                    if int(game['result']) == 1:
                        updateMatchDetailsQuery = 'UPDATE matchParticipant SET matchScore = matchScore + 1 WHERE matchID = :matchID AND participantID = :participantID'
                        matchDetailsInputs = {'matchID': matchID, 'participantID': game['participantID']}
                        result = conn.execute(text(updateMatchDetailsQuery), matchDetailsInputs)
                
                stageQuery = "SELECT maxGames FROM stages WHERE stageID = :stageID"
                stageInputs = {'stageID': stageID}
                result = conn.execute(text(stageQuery), stageInputs)
                stageRows = result.fetchall()
                stage = [row._asdict() for row in stageRows]
                maxGames = int(stage[0]['maxGames'])
                print(maxGames)
                
                matchParticipantQuery = "SELECT * FROM matchParticipant WHERE matchID = :matchID"
                matchParticipantInputs = {'matchID': matchID}
                result = conn.execute(text(matchParticipantQuery), matchParticipantInputs)
                matchParticipantRows = result.fetchall()
                matchParticipant = [row._asdict() for row in matchParticipantRows]

                for mp in matchParticipant:
                    if int(mp["matchScore"]) == math.ceil(maxGames/2):
                        updateMatchResultWinnerQuery = 'UPDATE matchParticipant SET participantMatchOutcome = 1 WHERE matchParticipantID = :matchParticipantID'
                        matchResultWinnnerInputs = {'matchParticipantID': mp["matchParticipantID"]}
                        conn.execute(text(updateMatchResultWinnerQuery), matchResultWinnnerInputs)
                        IDfetch = mp["matchParticipantID"]

                        updateMatchResultLoserQuery = 'UPDATE matchParticipant SET participantMatchOutcome = 3 WHERE matchParticipantID != :matchParticipantID AND matchID = :matchID'
                        matchResultLoserInputs = {'matchParticipantID': IDfetch, 'matchID': matchID}
                        conn.execute(text(updateMatchResultLoserQuery), matchResultLoserInputs)

                        updateMatchStatusQuery = 'UPDATE matches SET matchStatus = 1 WHERE matchID = :matchID'
                        matchStatusInputs = {'matchID': matchID}
                        conn.execute(text(updateMatchStatusQuery), matchStatusInputs)

                        #Update Parent Match participants
                        #Update Game Status
                                
            return "updateGamesDetails success!"
    
    def deleteMatch():
        return
    
