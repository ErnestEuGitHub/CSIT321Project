from flask import render_template, session, request, flash, jsonify, url_for, redirect
from itertools import combinations
from database import dbConnect
from sqlalchemy import text
from general import *

def seeding(projID, tourID, stageID):

    #fornavbar
    navtype = 'dashboard'
    tournamentName = retrieveDashboardNavName(tourID)
    moderatorPermissionList = gettingModeratorPermissions(tourID)
    isOwner = verifyOwner(tourID)

    if request.method == "POST":
        data = request.get_json()
        formIdentifier = data.get('formIdentifier')
        getplacements = data.get('placements')
        placements = [item['content'] for item in getplacements]

        #Check if records in Seeding exists
        with dbConnect.engine.connect() as conn:
            query = "SELECT seedingID FROM seeding WHERE stageID = :stageID"
            inputs = {'stageID': stageID}
            result = conn.execute(text(query), inputs)
            getSeedID = result.fetchall()

        if not getSeedID:
            #If no existing records, Insert Sequence into Seeding
            seqcount = 1
            for teams in placements:
                # print ('Teams in placements:'+teams+'.')
                if teams != '':
                    with dbConnect.engine.connect() as conn:
                        query = "SELECT participantID FROM participants WHERE participantName = :participantName"
                        inputs = {'participantName': teams}
                        result = conn.execute(text(query), inputs)
                        rows = result.fetchone()
                        # print('Array from DB:', rows)
                        partID = rows[0]

                        query = "INSERT INTO seeding (participantID, placementStatusID, sequence, stageID) VALUES (:participantID, :placementStatusID, :sequence, :stageID)"
                        inputs = {'participantID': partID, 'placementStatusID': 1, 'sequence': seqcount, 'stageID': stageID}
                        result = conn.execute(text(query), inputs)
                        conn.commit()

                else:
                    with dbConnect.engine.connect() as conn:
                        query = "INSERT INTO seeding (placementStatusID, sequence, stageID) VALUES (:placementStatusID, :sequence, :stageID)"
                        inputs = {'placementStatusID': 0, 'sequence': seqcount, 'stageID': stageID}
                        result = conn.execute(text(query), inputs)
                        conn.commit()
                    
                seqcount = seqcount + 1
        
        else:
            #If seeding exists, update seeding table
            seqcount = 1
            seedcount = 0
            for teams in placements:
                # print ('Teams in placements:'+teams+'.')
                if teams != '':
                    with dbConnect.engine.connect() as conn:
                        query = "SELECT participantID FROM participants WHERE participantName = :participantName"
                        inputs = {'participantName': teams}
                        result = conn.execute(text(query), inputs)
                        rows = result.fetchone()
                        # print('Array from DB:', rows)
                        partID = rows[0]

                        query = "UPDATE seeding SET participantID = :participantID, placementStatusID = :placementStatusID, sequence = :sequence, stageID = :stageID WHERE seedingID = :seedingID"
                        inputs = {'participantID': partID, 'placementStatusID': 1, 'sequence': seqcount, 'stageID': stageID, 'seedingID': getSeedID[seedcount][0]}
                        result = conn.execute(text(query), inputs)
                        conn.commit()

                else:
                    with dbConnect.engine.connect() as conn:
                        query = "UPDATE seeding SET participantID = NULL, placementStatusID = :placementStatusID, sequence = :sequence, stageID = :stageID WHERE seedingID = :seedingID"
                        inputs = {'placementStatusID': 0, 'sequence': seqcount, 'stageID': stageID, 'seedingID': getSeedID[seedcount][0]}
                        result = conn.execute(text(query), inputs)
                        conn.commit()
                    
                seqcount = seqcount + 1
                seedcount = seedcount + 1


        if formIdentifier == 'rr':
            try:
                def chunk_list(lst, chunk_size):
                    """Split a list into sublists of a specified size."""
                    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

                with dbConnect.engine.connect() as conn:
                    #remove any existing matches from matchParticipant

                    query = "SELECT matchID FROM matches WHERE stageID = :stageID"
                    inputs = {'stageID': stageID}
                    result = conn.execute(text(query), inputs)
                    fetchmatches = result.fetchall()


                    query = "SELECT * FROM matchParticipant WHERE matchID = :matchID"
                    inputs = {'matchID': fetchmatches[0][0]}
                    result = conn.execute(text(query), inputs)
                    checkMatchPart = result.fetchall()
                    checkMatchPartArray = [row._asdict() for row in checkMatchPart]
                    
                    firstMatchPart = checkMatchPartArray[0]['participantID']

                    if firstMatchPart > 0:
                        #Split Placements List of Participantns into different group
                        query = "SELECT numberOfParticipants, numberOfGroups FROM stages WHERE stageID = :stageID"
                        inputs = {'stageID': stageID}
                        result = conn.execute(text(query), inputs)
                        rows = result.fetchall()

                        numberOfParticipants = rows[0][0]
                        numberOfGroups = rows[0][1]

                        teamsPerGrp = numberOfParticipants // numberOfGroups
                        print('teamsPerGrp array is:', teamsPerGrp)

                        placementGrpArray = chunk_list(placements, teamsPerGrp)

                        print('placement grp array is:', placementGrpArray)

                        # count = 0
                        # matchcounter = 0
                        # #Generate different combinations required for match participants and store in matchParticipants
                        # for group in placementGrpArray:
                        #     def round_robin_teams(teams):
                        #         return list(combinations(teams, 2))
                            
                        #     pairings = round_robin_teams(group)
                        #     print('parings is:', pairings)

                        #     #For each match, Insert pairings into matchParticipants
                        #     for matchpair in pairings:
                        #         # print(f"{match[0]} vs {match[1]}")
                        #         matchID = fetchmatches[matchcounter][0]

                        #         query = "SELECT participantID FROM participants WHERE participantName = :participantName"
                        #         inputs = {'participantName': matchpair[0]}
                        #         result = conn.execute(text(query), inputs)
                        #         rows = result.fetchone()

                        #         if rows is None:
                        #             firstteam = 0
                        #         else:
                        #             firstteam = rows[0]

                        #         inputs = {'participantName': matchpair[1]}
                        #         result = conn.execute(text(query), inputs)
                        #         rows = result.fetchone()

                        #         if rows is None:
                        #             secondteam = 0
                        #         else:
                        #             secondteam = rows[0]
                                
                        #         query = "SELECT * FROM matchParticipant WHERE matchID = :matchID"
                        #         inputs = {'matchID': matchID}
                        #         result = conn.execute(text(query), inputs)
                        #         getcurrentPartIDs = result.fetchall()

                        #         query = "UPDATE matchParticipant set participantID = :participantID WHERE matchParticipantID = :matchParticipantID"
                        #         inputs = {'participantID': firstteam, 'matchParticipantID': getcurrentPartIDs[0][0]}
                        #         result = conn.execute(text(query), inputs)

                        #         query = "UPDATE matchParticipant set participantID = :participantID WHERE matchParticipantID = :matchParticipantID"
                        #         inputs = {'participantID': secondteam, 'matchParticipantID': getcurrentPartIDs[1][0]}
                        #         result = conn.execute(text(query), inputs)

                        #         matchcounter = matchcounter + 1
                        flash('Seeding has previously been updated, unable to set seeding again!', 'error')
                        return jsonify({'message': 'Seeding has previously been updated!', 'category': 'success', 'redirect': url_for("loadSeeding", projID=projID, tourID=tourID, stageID=stageID)})

                    else:
                        #Split Placements List of Participantns into different group
                        query = "SELECT numberOfParticipants, numberOfGroups FROM stages WHERE stageID = :stageID"
                        inputs = {'stageID': stageID}
                        result = conn.execute(text(query), inputs)
                        rows = result.fetchall()

                        numberOfParticipants = rows[0][0]
                        numberOfGroups = rows[0][1]

                        teamsPerGrp = numberOfParticipants // numberOfGroups
                        # print('teamsPerGrp array is:', teamsPerGrp)

                        placementGrpArray = chunk_list(placements, teamsPerGrp)
                        # print('placement grp array is:', placementGrpArray)

                        placementGrpCounter = 0

                        #converting all names to IDs and insert into ranking table
                        rankingStgGrpCounter = 0
                        for grp in placementGrpArray:
                            for idx, team in enumerate(grp):
                                query = "SELECT participantID FROM participants WHERE participantName = :participantName"
                                inputs = {'participantName': team}
                                result = conn.execute(text(query), inputs)
                                fetchPartID = result.fetchone()

                                if fetchPartID:
                                    grp[idx] = fetchPartID[0]  # Replace team name with participant ID

                        for group in placementGrpArray:
                            rankingStgGrpCounter += 1
                            for team in group:
                                query = "INSERT INTO ranking (participantID, stageGroup, stageID) VALUES (:participantID, :stageGroup, :stageID)"
                                inputs = {'participantID': team, 'stageGroup': rankingStgGrpCounter, 'stageID': stageID}
                                result = conn.execute(text(query), inputs)
                                conn.commit()

                        # Update matchParticipant
                        for grp in placementGrpArray:
                            placementGrpCounter += 1
                            query = "SELECT * FROM matches WHERE stageID = :stageID AND stageGroup = :stageGroup"
                            inputs = {'stageID': stageID, 'stageGroup': placementGrpCounter}
                            result = conn.execute(text(query), inputs)
                            fetchMatchList = result.fetchall()
                            MatchList = [row._asdict() for row in fetchMatchList]

                            for match in MatchList:
                                teamsInGrpCounter = 0
                                for teams in grp:
                                    query = "UPDATE matchParticipant SET participantID = :participant WHERE matchID = :matchID AND participantID = :tempNum"
                                    inputs = {'participant': teams, 'matchID': match['matchID'], 'tempNum': (teamsInGrpCounter+1) * -1}
                                    result = conn.execute(text(query), inputs)
                                    conn.commit()

                                    query = "UPDATE matchParticipant SET participantID = :participant WHERE matchID = :matchID AND participantID = :tempNum"

                                    teamsInGrpCounter+=1


                        # count = 0
                        # #Generate different combinations required for match participants and store in matchParticipants
                        # for group in placementGrpArray:
                        #     def round_robin_teams(teams):
                        #         return list(combinations(teams, 2))
                            
                        #     pairings = round_robin_teams(group)
                        #     print('parings is:', pairings)

                        #     #For each match, Insert pairings into matchParticipants
                        #     for matchpair in pairings:
                        #         # print(f"{match[0]} vs {match[1]}")

                        #         query = "SELECT participantID FROM participants WHERE participantName = :participantName"
                        #         inputs = {'participantName': matchpair[0]}
                        #         result = conn.execute(text(query), inputs)
                        #         rows = result.fetchone()

                        #         if rows is None:
                        #             firstteam = 0
                        #         else:
                        #             firstteam = rows[0]

                        #         inputs = {'participantName': matchpair[1]}
                        #         result = conn.execute(text(query), inputs)
                        #         rows = result.fetchone()

                        #         if rows is None:
                        #             secondteam = 0
                        #         else:
                        #             secondteam = rows[0]
                                
                        #         query = "INSERT INTO matchParticipant (participantID, matchID) VALUES (:participantID, :matchID)"
                        #         inputs = {'participantID': firstteam, 'matchID':fetchmatches[count][0]}
                        #         result = conn.execute(text(query), inputs)

                        #         inputs = {'participantID': secondteam, 'matchID':fetchmatches[count][0]}
                        #         result = conn.execute(text(query), inputs)

                        #         count = count + 1

                    #Game Participant Code
                    matchesarray = [row._asdict() for row in fetchmatches]
                    # print('matchesarray: ', matchesarray)
                    
                    #for each match select gameIDs
                    for match in matchesarray:
                        query = "SELECT gameID from games WHERE matchID = :matchID"
                        inputs = {'matchID': match['matchID']}
                        result = conn.execute(text(query), inputs)
                        games = result.fetchall()

                        gamesarray = [row._asdict() for row in games]

                        print("This is gamesarray")
                        print(gamesarray)
                        print("/n")

                        for game in gamesarray: 
                            #check if gameParticipant exists
                            query = "SELECT gameParticipantID from gameParticipant WHERE gameID = :gameID"
                            inputs = {'gameID': game['gameID']}
                            result = conn.execute(text(query), inputs)
                            checkgamepart = result.fetchall()
                            checkgamepartarray = [row._asdict() for row in checkgamepart]

                            print("This is checkgamepart")
                            print(checkgamepart)
                            print("/n")
                            
                            # print('gamesarray: ', gamesarray)

                            if checkgamepart:
                                #for each gameID
                                # print('checkgamepart: ', checkgamepart)
                                
                                #select match participants where matchID
                                query = "SELECT participantID from matchParticipant WHERE matchID = :matchID"
                                inputs = {'matchID': match['matchID']}
                                result = conn.execute(text(query), inputs)
                                matchParticipants = result.fetchall()
                                # print('matchParticipants: ', matchParticipants)

                                #update 2 game participants
                                query = "UPDATE gameParticipant SET participantID = :participantID WHERE gameParticipantID = :gameParticipantID"
                                inputs = {'gameParticipantID': checkgamepart[0][0], 'participantID': matchParticipants[0][0]}
                                result = conn.execute(text(query), inputs)
                                conn.commit()

                                query = "UPDATE gameParticipant SET participantID = :participantID WHERE gameParticipantID = :gameParticipantID"
                                inputs = {'gameParticipantID': checkgamepart[1][0], 'participantID': matchParticipants[1][0]}
                                result = conn.execute(text(query), inputs)
                                conn.commit()
                            else:    
                                #for each gameID
                                # print('checkgamepart else: ', checkgamepart)
                                
                                #select match participants where matchID
                                query = "SELECT participantID from matchParticipant WHERE matchID = :matchID"
                                inputs = {'matchID': match['matchID']}
                                result = conn.execute(text(query), inputs)
                                matchParticipants = result.fetchall()

                                #create 2 game participants
                                query = "INSERT INTO gameParticipant (gameID, participantID) VALUES (:gameID, :participantID)"
                                inputs = {'gameID': game['gameID'], 'participantID': matchParticipants[0][0]}
                                result = conn.execute(text(query), inputs)
                                conn.commit()

                                query = "INSERT INTO gameParticipant (gameID, participantID) VALUES (:gameID, :participantID)"
                                inputs = {'gameID': game['gameID'], 'participantID': matchParticipants[1][0]}
                                result = conn.execute(text(query), inputs)
                                conn.commit()

                flash('Seeding Updated!', 'success')
                print('Flash msg activated')
                return jsonify({'message': 'Seeding Updated!', 'category': 'success', 'redirect': url_for("loadSeeding", projID=projID, tourID=tourID, stageID=stageID)})

            except Exception as e:
                flash('Oops, something went wrong while trying to update seeding!', 'error')
                print(f"Error details: {e}")
                return jsonify({'message': 'Error updating seeding!', 'category': 'error', 'redirect': url_for("loadSeeding", projID=projID, tourID=tourID, stageID=stageID)})
            
        elif formIdentifier == 'SE':
            try:
                with dbConnect.engine.connect() as conn:
                    #remove any existing matches from matchParticipant

                    query = "SELECT matchID FROM matches WHERE stageID = :stageID AND bracketSequence = 1"
                    inputs = {'stageID': stageID}
                    result = conn.execute(text(query), inputs)
                    fetchmatches = result.fetchall()


                    query = "SELECT * FROM matchParticipant WHERE matchID = :matchID"
                    inputs = {'matchID': fetchmatches[0][0]}
                    result = conn.execute(text(query), inputs)
                    checkMatchPart = result.fetchall()

                    if len(checkMatchPart) > 0:
                        for matches in fetchmatches:
                            matchID = matches[0]

                            query = "SELECT * FROM matchParticipant WHERE matchID = :matchID"
                            inputs = {'matchID': matchID}
                            result = conn.execute(text(query), inputs)
                            getcurrentPartIDs = result.fetchall()

                            teamsForMatch = placements[:2]
                            placements = placements[2:]
                            
                            counter = 0
                            for team in teamsForMatch:
                                query = "SELECT participantID FROM participants WHERE participantName = :participantName"
                                inputs = {'participantName': team}
                                result = conn.execute(text(query), inputs)
                                rows = result.fetchone()

                                if rows is None:
                                    participantID = 0
                                else:
                                    participantID = rows[0]

                                query = "UPDATE matchParticipant SET participantID = :participantID WHERE matchParticipantID = :matchParticipantID"
                                inputs = {'participantID': participantID, 'matchParticipantID': getcurrentPartIDs[counter][0]}
                                result = conn.execute(text(query), inputs)
                                conn.commit()

                                counter = counter + 1

                    else:
                        for matches in fetchmatches:
                            teamsForMatch = placements[:2]
                            placements = placements[2:]
                            matchID = matches[0]

                            for team in teamsForMatch:
                                query = "SELECT participantID FROM participants WHERE participantName = :participantName"
                                inputs = {'participantName': team}
                                result = conn.execute(text(query), inputs)
                                rows = result.fetchone()

                                if rows is None:
                                    participantID = 0
                                else:
                                    participantID = rows[0]

                                query = "INSERT INTO matchParticipant (participantID, matchID) VALUES (:participantID, :matchID)"
                                inputs = {'participantID': participantID, 'matchID':matchID}
                                result = conn.execute(text(query), inputs)
                                conn.commit()

                    #Game Participant Code
                    matchesarray = [row._asdict() for row in fetchmatches]
                    # print('matchesarray: ', matchesarray)
                    
                    #for each match select gameIDs
                    for match in matchesarray:
                        query = "SELECT gameID from games WHERE matchID = :matchID"
                        inputs = {'matchID': match['matchID']}
                        result = conn.execute(text(query), inputs)
                        games = result.fetchall()

                        gamesarray = [row._asdict() for row in games]

                        for game in gamesarray:
                            #check if gameParticipant exists
                            query = "SELECT gameParticipantID from gameParticipant WHERE gameID = :gameID"
                            inputs = {'gameID': game['gameID']}
                            result = conn.execute(text(query), inputs)
                            checkgamepart = result.fetchall()

                            checkgamepartarray = [row._asdict() for row in checkgamepart]
                            # print('gamesarray: ', gamesarray)

                            if checkgamepart:
                                #for each gameID
                                # print('checkgamepart: ', checkgamepart)
                                
                                #select match participants where matchID
                                query = "SELECT participantID from matchParticipant WHERE matchID = :matchID"
                                inputs = {'matchID': match['matchID']}
                                result = conn.execute(text(query), inputs)
                                matchParticipants = result.fetchall()
                                # print('matchParticipants: ', matchParticipants)

                                #update 2 game participants
                                query = "UPDATE gameParticipant SET participantID = :participantID WHERE gameParticipantID = :gameParticipantID"
                                inputs = {'gameParticipantID': checkgamepart[0][0], 'participantID': matchParticipants[0][0]}
                                result = conn.execute(text(query), inputs)
                                conn.commit()

                                query = "UPDATE gameParticipant SET participantID = :participantID WHERE gameParticipantID = :gameParticipantID"
                                inputs = {'gameParticipantID': checkgamepart[1][0], 'participantID': matchParticipants[1][0]}
                                result = conn.execute(text(query), inputs)
                                conn.commit()
                            else:    
                                #for each gameID
                                # print('checkgamepart else: ', checkgamepart)
                                
                                #select match participants where matchID
                                query = "SELECT participantID from matchParticipant WHERE matchID = :matchID"
                                inputs = {'matchID': match['matchID']}
                                result = conn.execute(text(query), inputs)
                                matchParticipants = result.fetchall()

                                #create 2 game participants
                                query = "INSERT INTO gameParticipant (gameID, participantID) VALUES (:gameID, :participantID)"
                                inputs = {'gameID': game['gameID'], 'participantID': matchParticipants[0][0]}
                                result = conn.execute(text(query), inputs)
                                conn.commit()

                                query = "INSERT INTO gameParticipant (gameID, participantID) VALUES (:gameID, :participantID)"
                                inputs = {'gameID': game['gameID'], 'participantID': matchParticipants[1][0]}
                                result = conn.execute(text(query), inputs)
                                conn.commit()
                                
                flash('Seeding Updated!', 'success')
                print('Flash msg activated')
                return jsonify({'message': 'Seeding Updated!', 'category': 'success', 'redirect': url_for("loadSeeding", projID=projID, tourID=tourID, stageID=stageID)})
            
            except Exception as e:
                flash('Oops, something went wrong while trying to update seeding!', 'error')
                print(f"Error details: {e}")
                return jsonify({'message': 'Error updating seeding!', 'category': 'error', 'redirect': url_for("loadSeeding", projID=projID, tourID=tourID, stageID=stageID)})
    else:
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

            #retrieving from Seeding Table if have
            query = "SELECT participantID FROM seeding WHERE stageID = :stageID ORDER BY sequence ASC"
            inputs = {'stageID': stageID}
            result = conn.execute(text(query), inputs)
            getSeedingPartID = result.fetchall()

            seedingTeam = []

            if len(getSeedingPartID) > 0:
                for p in getSeedingPartID:
                    query = "SELECT participantName FROM participants WHERE participantID = :participantID"
                    inputs = {'participantID': p[0]}
                    result = conn.execute(text(query), inputs)
                    getSeedingName = result.fetchone()
                
                    if getSeedingName is None:
                        seedingTeam.append('')
                    else:
                        seedingTeam.append(getSeedingName[0])

            if stageForm == 1 or stageForm == 2:
                return render_template('seedingSingleElim.html', participantID=participantID, participantName=participantName, numberOfParticipants=numberOfParticipants, numberOfGroups=numberOfGroups, navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, seedingTeam=seedingTeam, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
            elif stageForm == 3 or stageForm == 4:
                return render_template('seeding.html', participantID=participantID, participantName=participantName, numberOfParticipants=numberOfParticipants, numberOfGroups=numberOfGroups, navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, seedingTeam=seedingTeam, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)