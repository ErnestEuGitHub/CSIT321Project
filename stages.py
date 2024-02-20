from flask import render_template, session, request, flash, session, jsonify, url_for, redirect
from database import dbConnect
from sqlalchemy import text
from datetime import datetime
from general import *

class Stage:

    #configureStage
    def configureStage(projID, tourID, stageID):

        navtype = 'dashboard'
        tournamentName = retrieveDashboardNavName(tourID)
        moderatorPermissionList = gettingModeratorPermissions(tourID)
        isOwner = verifyOwner(tourID)

        if request.method == "POST":
            print(tourID)
            print(stageID)
            stageName = request.form.get("stageName")
            stageSequence = request.form.get("stageSequence")
            stageFormatID = request.form.get("stageFormat")
            stageStatusID = 1
            numberOfParticipants = request.form.get("numberOfParticipants")
            numberOfGroups = request.form.get("numberOfGroups")
            matchFormatID = request.form.get("matchFormat")
            maxGames = request.form.get("maximumNumberOfGames")
            
            tfMatch = request.form.get("34match")

            winPts = request.form.get("winPoints")
            drawPts = request.form.get("drawPoints")
            lossPts = request.form.get("lossPoints")
            tieBreakers = request.form.getlist("tieBreakerSelect")

            if not maxGames:
                maxGames = matchFormatID
            
            try:
                with dbConnect.engine.connect() as conn:
                    
                    print("configureStage ran! 2")
                    stageQuery = """
                        UPDATE stages SET stageName = :stageName, stageSequence = :stageSequence, stageFormatID = :stageFormatID, 
                        stageStatusID = :stageStatusID, numberOfParticipants = :numberOfParticipants, numberOfGroups = :numberOfGroups, 
                        matchFormatID = :matchFormatID, maxGames = :maxGames WHERE stageID = :stageID
                        """
                    stageInputs = {'stageName': stageName, 'stageSequence': stageSequence, 'stageFormatID': stageFormatID, 
                              'stageStatusID': stageStatusID, 'numberOfParticipants': numberOfParticipants, 'numberOfGroups': numberOfGroups, 
                              'matchFormatID': matchFormatID, 'maxGames': maxGames, 'stageID': stageID}
                    conn.execute(text(stageQuery), stageInputs)

                    if int(stageFormatID) == 1 or int(stageFormatID) == 2:
                        print("stageFormatID is" + stageFormatID)
                        elimFormatQuery = "UPDATE elimFormat SET tfMatch = :tfMatch WHERE stageID = :stageID"
                        elimInputs = {'tfMatch': tfMatch, 'stageID': stageID}
                        conn.execute(text(elimFormatQuery), elimInputs)

                    elif int(stageFormatID) == 3 or int(stageFormatID) == 4:
                        print("stageFormatID is "+ stageFormatID)
                        roundFormatQuery = "UPDATE roundFormat SET winPts = :winPts, drawPts = :drawPts, lossPts = :lossPts WHERE stageID = :stageID"
                        roundInputs = {'winPts': winPts, 'drawPts': drawPts, 'lossPts': lossPts, 'stageID': stageID}
                        conn.execute(text(roundFormatQuery), roundInputs)
                        
                        roundRobinIDQuery = "SELECT roundRobinID FROM roundFormat WHERE stageID = :stageID"
                        roundRobinIDInputs = {'stageID': stageID}
                        result = conn.execute(text(roundRobinIDQuery), roundRobinIDInputs)
                        roundRobinIDrows = result.fetchall()
                        roundRobinIDlist = [row._asdict() for row in roundRobinIDrows]
                        roundRobinID = roundRobinIDlist[0]['roundRobinID']

                        delTieBreakersQuery = "DELETE FROM tieBreaker WHERE roundRobinID = :roundRobinID"
                        delTbInputs = {'roundRobinID': roundRobinID}
                        conn.execute(text(delTieBreakersQuery), delTbInputs)

                        for i in range(len(tieBreakers)):
                            sequence = i + 1
                            tieBreakerQuery = "INSERT INTO tieBreaker (tbTypeID, sequence, roundRobinID) VALUES (:tbTypeID, :sequence, :roundRobinID)"
                            tiebreakerInput = {'tbTypeID': tieBreakers[i], 'sequence': sequence, 'roundRobinID': roundRobinID}
                            createTiebreakers = conn.execute(text(tieBreakerQuery), tiebreakerInput)
                    else:
                        print("stageFormatID is invalid!")
                
                    flash('Stage Configured!', 'success')
                    # return render_template('structure.html', navtype=navtype, tournamentName=tournamentName, tourID=tourID)
                    return redirect(url_for("loadstructure", navtype=navtype, tournamentName=tournamentName, projID = projID, tourID=tourID
                                       , moderatorPermissionList=moderatorPermissionList, isOwner = isOwner))
            except Exception as e:
                flash('Oops, an error has occured.', 'error')
                print(f"Error details: {e}")
            return render_template('configureStage.html', navtype=navtype, tournamentName=tournamentName, projID=projID, tourID=tourID
                                       , moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
        else:
            tournamentName = retrieveDashboardNavName(tourID)
            navtype = 'dashboard'
            
            try:
                with dbConnect.engine.connect() as conn:
                    
                    stageQuery = "SELECT * FROM stages WHERE stageID = :stageID"
                    stageInputs = {'stageID': stageID}
                    result = conn.execute(text(stageQuery), stageInputs)
                    stageRows = result.fetchall()
                    stage = [row._asdict() for row in stageRows]
                    print(stageRows)
                    print(stage)

                    stageName = stage[0]['stageName']
                    stageSequence = stage[0]['stageSequence']
                    stageFormatID = stage[0]['stageFormatID']
                    numberOfParticipants = stage[0]['numberOfParticipants']
                    numberOfGroups = stage[0]['numberOfGroups']
                    matchFormatID = stage[0]['matchFormatID']
                    maxGames = stage[0]['maxGames']

                    if int(stageFormatID) == 1 or int(stageFormatID) == 2:
                        elimQuery = "SELECT tfMatch FROM elimFormat WHERE stageID = :stageID"
                        elimInputs = {'stageID': stageID}
                        result = conn.execute(text(elimQuery), elimInputs)
                        elimRows = result.fetchall()
                        elim = [row._asdict() for row in elimRows]
                        print(elim)

                        tfMatch = elim[0]["tfMatch"]

                        return render_template('configureStage.html', navtype=navtype, tournamentName=tournamentName, projID = projID, tourID=tourID, stageID=stageID,
                                       stageName = stageName, stageSequence = stageSequence, stageFormatID = stageFormatID, numberOfParticipants = numberOfParticipants,
                                       numberOfGroups = numberOfGroups, matchFormatID = matchFormatID, maxGames = maxGames, tfMatch = tfMatch
                                       , moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)

                    elif int(stageFormatID) == 3 or int(stageFormatID) == 4:
                        roundQuery = "SELECT winPts, drawPts, lossPts, roundRobinID FROM roundFormat WHERE stageID = :stageID"
                        roundInputs = {'stageID': stageID}
                        result = conn.execute(text(roundQuery), roundInputs)
                        roundRows = result.fetchall()
                        round = [row._asdict() for row in roundRows]
                        print(round)
                        
                        winPts = round[0]["winPts"]
                        drawPts = round[0]["drawPts"]
                        lossPts = round[0]["lossPts"]
                        roundRobinID = round[0]["roundRobinID"]

                        tbQuery = "SELECT * FROM tieBreaker WHERE roundRobinID = :roundRobinID"
                        tbInputs = {'roundRobinID': roundRobinID}
                        result = conn.execute(text(tbQuery), tbInputs)
                        tbRows = result.fetchall()
                        tieBreakers = [row._asdict() for row in tbRows]
                        
                        return render_template('configureStage.html', navtype=navtype, tournamentName=tournamentName, projID=projID, tourID=tourID, stageID=stageID,
                                       stageName = stageName, stageSequence = stageSequence, stageFormatID = stageFormatID, numberOfParticipants = numberOfParticipants,
                                       numberOfGroups = numberOfGroups, matchFormatID = matchFormatID, maxGames = maxGames, winPts = winPts, drawPts = drawPts, lossPts = lossPts, tieBreakers = tieBreakers
                                       , moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
                    else:
                        print("Cannot get any information on stageFormat")


                return render_template('configureStage.html', navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)   
                    
            except Exception as e:
                flash('Oops, an error has occured.', 'error')
                print(f"Error details: {e}")
            return render_template('configureStage.html', navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
            
        
    def deleteStage(projID, tourID, stageID):

        navtype = 'dashboard'
        tournamentName = retrieveDashboardNavName(tourID)
        moderatorPermissionList = gettingModeratorPermissions(tourID)
        isOwner = verifyOwner(tourID)

        print(stageID)

        if request.method == "POST":
            
            print("Delete Triggered!")
            try:
                with dbConnect.engine.connect() as conn:

                    delStageQuery = "UPDATE stages SET stageStatusID = 4 WHERE stageID = :stageID"
                    delStageInputs = {'stageID': stageID}
                    conn.execute(text(delStageQuery), delStageInputs)

            except Exception as e:
                flash('Oops, an error has occured.', 'error')
                print(f"Error details: {e}")
            return redirect(url_for("loadstructure", navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner))
        else:
            return redirect(url_for("loadstructure", navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner))
