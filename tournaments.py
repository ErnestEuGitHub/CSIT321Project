from flask import render_template, session, request, flash, session, jsonify, url_for, redirect
from database import dbConnect
from sqlalchemy import text
from datetime import datetime
from general import *

class Tournaments:
    #Organiser Tournament Page (Page that shows all tournaments in boxes within a project)
    def tournaments(projID):
        tournamentlist = updateNavTournaments(projID)
        session["currentProj"] = projID
        
        #for navbar
        projectName = retrieveProjectNavName(projID)
        navtype = 'tournament'
        return render_template('tournament.html', tournamentlist=tournamentlist, navtype=navtype, projectName=projectName, projID=projID)
    
    #Tournament Overview Page
    def TourOverviewDetails(projID, tourID):
        with dbConnect.engine.connect() as conn:
            query = "SELECT tourName, startDate, endDate, gender, sports.sportName FROM tournaments JOIN sports ON tournaments.sportID = sports.sportID WHERE tourID = :tourID"
            inputs = {'tourID': tourID}
            result = conn.execute(text(query), inputs)
            rows = result.fetchall()

            tourName = rows[0][0]
            startDate = rows[0][1]
            endDate = rows[0][2]
            gender = rows[0][3]
            sportName = rows[0][4]
            
            #for navbar
            navtype = 'tournament'
            tournamentlist = updateNavTournaments(projID)
            # projID = session["currentProj"]
            projectName = retrieveProjectNavName(projID)
    
        return render_template('tournamentOverviewPage.html', sportName=sportName, tourName=tourName, startDate=startDate, endDate=endDate, gender=gender, navtype=navtype, tournamentlist=tournamentlist, projectName=projectName, tourID=tourID, projID=projID)
    
    #Create Tournament
    def createTour(projID):
        #for navbar
        navtype = 'tournament'
        # projID = session["currentProj"]

        if request.method == "POST":
            tourName = request.form.get("tourName")
            tourSize = request.form.get("tourSize")
            startDate = request.form.get("startDate")
            endDate = request.form.get("endDate")
            gender = request.form.get("gender")
            sport = request.form.get("sport")
            format = request.form.get("format")
            userID = session["id"]
            status = 4

            with dbConnect.engine.connect() as conn:
                query = "SELECT * FROM sports"
                result = conn.execute(text(query))
                rows = result.fetchall()

                sportsOptions = [row._asdict() for row in rows]

            if not sport:
                flash('Please select a sport!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=sport, format=format, sportlist=sportsOptions, projID=projID)
            elif not tourName:
                flash('Please fill in a tournament name!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, projID=projID)
            elif len(tourName) > 100:
                flash('Please keep tournament name less than 100 characters!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, projID=projID)
            elif not tourSize:
                flash('Please Enter a minimum participation size!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, projID=projID)
            elif int(tourSize) > 10000:
                flash('Please enter participant size from 1-10,000!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, projID=projID)
            elif int(tourSize) < 0:
                flash('Please enter participant size from 1-10,000!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, projID=projID)
            elif not format:
                flash('That is not a valid format for the sport!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, projID=projID)
            elif not endDate or not startDate:
                flash('Start or End Dates are not filled!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, projID=projID)
            elif endDate < startDate:
                flash('End Date cannot be earlier than Start Date!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, projID=projID)
            # elif len(generalInfo) > 500:
            #     flash('Please keep general info less than 500 characters!', 'error')
            #     return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, generalInfo=generalInfo, sportlist=sportsOptions)
            
            else:
                #convertion to correct types placed here after checking no empty strings
                sport = int(sport)
                tourSize = int(tourSize)
                startDate = datetime.strptime(startDate, "%Y-%m-%d")
                endDate = datetime.strptime(endDate, "%Y-%m-%d")

                try:
                    with dbConnect.engine.connect() as conn:
                        query = "SELECT * FROM sportsformats JOIN formats ON sportsformats.formatID = formats.formatID WHERE sportID = :sport AND formatName = :format"
                        inputs = {'sport': sport, 'format': format}
                        getsfID = conn.execute(text(query), inputs)
                        rows = getsfID.fetchall()
                        formatID = rows[0][2]

                        query = "INSERT INTO generalInfo SET generalInfoDesc = default;"
                        createNewGeneralInfo = conn.execute(text(query))
                        getID = createNewGeneralInfo.lastrowid
            
                        query = "INSERT INTO tournaments (tourName, tourSize, startDate, endDate, gender, projID, sportID, formatID, statusID, userID, generalInfoID) VALUES (:tourName, :tourSize, :startDate, :endDate, :gender, :projID, :sportID, :formatID, :statusID, :userID, :generalInfoID)"
                        inputs = {'tourName': tourName, 'tourSize': tourSize, 'startDate': startDate, 'endDate': endDate, 'gender':gender, 'projID':projID, 'sportID':sport, 'formatID':formatID, 'statusID':status, 'userID':userID, 'generalInfoID':getID}
                        createTournament = conn.execute(text(query), inputs)

                        #for navbar
                        tournamentlist = updateNavTournaments(projID)
                        projectName = retrieveProjectNavName(projID)

                    flash('Tournament Created!', 'success')
                    return render_template('createTour.html', sportlist=sportsOptions, tournamentlist=tournamentlist, navtype=navtype, projectName=projectName, projID=projID)
                
                except Exception as e:
                    flash('Oops, an error has occured.', 'error')
                    print(f"Error details: {e}")
                    #for navbar
                    tournamentlist = updateNavTournaments(projID)
                    projectName = retrieveProjectNavName(projID)
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, projectName=projectName, tournamentlist=tournamentlist, projID=projID)
                
        else:
            with dbConnect.engine.connect() as conn:
                query = "SELECT * FROM sports"
                result = conn.execute(text(query))
                rows = result.fetchall()

                sportsOptions = [row._asdict() for row in rows]

                #for navbar
                tournamentlist = updateNavTournaments(projID)
                projectName = retrieveProjectNavName(projID)
            return render_template('createTour.html', sportlist=sportsOptions, navtype=navtype, tournamentlist=tournamentlist, projectName=projectName, projID=projID)

    #Get Format for Create Tournaament
    def getformat():
        sportID = request.form.get('sport_id')
        
        with dbConnect.engine.connect() as conn:
            query = "SELECT formats.formatName FROM sportsformats JOIN formats ON sportsformats.formatID = formats.formatID WHERE sportID = (:sportID)"
            inputs = {'sportID': sportID}
            result = conn.execute(text(query), inputs)
            rows = result.fetchall()

            formatOptions = [row._asdict() for row in rows]

        options_html = ''.join([f'<option value="{formatOption["formatName"]}">{formatOption["formatName"]}</option>' for formatOption in formatOptions])

        return jsonify({"options": options_html})

    #Dashboard
    def dashboard(projID, tourID):
        #for navbar
        tournamentName = retrieveDashboardNavName(tourID)

        navtype = 'dashboard'
        return render_template('dashboard.html', navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID)
    
    #Structure

    def structure(projID, tourID):
        #for navbar
        tournamentName = retrieveDashboardNavName(tourID)

        navtype = 'dashboard'
        try:
            with dbConnect.engine.connect() as conn:
                    
                structureQuery = "SELECT stageName, stageSequence, stageFormatID, stageStatusID, stageID FROM stages WHERE tourID = :tourID AND stageStatusID <> 4"
                inputs = {'tourID': tourID}
                result = conn.execute(text(structureQuery), inputs)
                rows = result.fetchall()
                print(rows)
                stages = [row._asdict() for row in rows]
                print(stages)

                stageList = ''
                
                for stage in stages:
                    
                    if int(stage["stageFormatID"]) == 1:
                        stage["stageFormatID"] = "Single Elimination"
                    elif int(stage["stageFormatID"]) == 2:
                        stage["stageFormatID"] = "Double Elimination"
                    elif int(stage["stageFormatID"]) == 3:
                        stage["stageFormatID"] = "Single Round Robin"
                    elif int(stage["stageFormatID"]) == 4:
                        stage["stageFormatID"] = "Double Round Robin"
                    else:
                        print("Invalid stage format!!!")

                    stage_html = f'''
                                    <div class="card mb-3">
                                        <div class="card-body">
                                            <div class="d-flex justify-content-between" id="{stage["stageID"]}">
                                                <label>{stage["stageSequence"]}. {stage["stageName"]} - {stage["stageFormatID"]}</label>
                                                <button class="btn btn-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="true">
                                                    Edit
                                                </button>
                                                <ul class="dropdown-menu">
                                                    <li><a class="dropdown-item" href="/configureStage/{tourID}/{stage["stageID"]}">Configure</a></li>
                                                    <li><a class="dropdown-item" href="#" onclick="deleteStage({tourID}, {stage["stageID"]})">Delete</a></li>
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                '''
                    
                    stageList += stage_html
                
                    
            return render_template('structure.html', navtype=navtype, tournamentName=tournamentName, projID=projID, tourID=tourID, stageList=stageList)
        
        except Exception as e:
                flash('Oops, an error has occured.', 'error')
                print(f"Error details: {e}")
                return render_template('structure.html', navtype=navtype, tournamentName=tournamentName, projID=projID, tourID=tourID)
        
    

    #CreateStage
    @staticmethod
    def createStage(projID, tourID):
        
        #for navbar
        tournamentName = retrieveDashboardNavName(tourID)
        navtype = 'dashboard'
        
        if request.method == "POST":

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
                    
                    stageQuery = """
                        INSERT INTO stages (stageName, stageSequence, stageFormatID, stageStatusID, tourID, numberOfParticipants, numberOfGroups, matchFormatID, maxGames)
                        VALUES (:stageName, :stageSequence, :stageFormatID, :stageStatusID, :tourID, :numberOfParticipants, :numberOfGroups, :matchFormatID, :maxGames)
                        """
                    stageInputs = {'stageName': stageName, 'stageSequence': stageSequence, 'stageFormatID': stageFormatID, 'stageStatusID': stageStatusID, 'tourID': tourID, 
                                   'numberOfParticipants': numberOfParticipants, 'numberOfGroups': numberOfGroups, 'matchFormatID': matchFormatID, 'maxGames': maxGames}
                    conn.execute(text(stageQuery), stageInputs)
                    IDfetch = conn.execute(text("SELECT LAST_INSERT_ID()"))
                    stageID = IDfetch.scalar()

                    if int(stageFormatID) == 1 or int(stageFormatID) == 2:
                        print("stageFormatID is" + stageFormatID)
                        elimFormatQuery = "INSERT INTO elimFormat (tfMatch, stageID) VALUES (:tfMatch, :stageID)"
                        elimInputs = {'tfMatch': tfMatch, 'stageID': stageID}
                        conn.execute(text(elimFormatQuery), elimInputs)

                    elif int(stageFormatID) == 3 or int(stageFormatID) == 4:
                        print("stageFormatID is "+ stageFormatID)
                        roundFormatQuery = "INSERT INTO roundFormat (winPts, drawPts, lossPts, stageID) VALUES (:winPts, :drawPts, :lossPts, :stageID)"
                        roundInputs = {'winPts': winPts, 'drawPts': drawPts, 'lossPts': lossPts, 'stageID': stageID}
                        conn.execute(text(roundFormatQuery), roundInputs)
                        IDfetch = conn.execute(text("SELECT LAST_INSERT_ID()"))
                        roundRobinID = IDfetch.scalar()

                        print(tieBreakers)

                        for i in range(len(tieBreakers)):
                            sequence = i + 1
                            tieBreakerQuery = "INSERT INTO tieBreaker (tbTypeID, sequence, roundRobinID) VALUES (:tbTypeID, :sequence, :roundRobinID)"
                            tiebreakerInput = {'tbTypeID': tieBreakers[i], 'sequence': sequence, 'roundRobinID': roundRobinID}
                            createTiebreakers = conn.execute(text(tieBreakerQuery), tiebreakerInput)
                    else:
                        print("stageFormatID is invalid!")
                
                flash('Stage Created!', 'success')

                # return render_template('structure.html', navtype=navtype, tournamentName=tournamentName, tourID=tourID)
                return redirect(url_for("loadstructure", projID=projID, tourID=tourID))
                
            except Exception as e:
                flash('Oops, an error has occured.', 'error')
                print(f"Error details: {e}")
            return render_template('createStage.html', navtype=navtype, tournamentName=tournamentName, projID=projID, tourID=tourID)
        else:
            return render_template('createStage.html', navtype=navtype, tournamentName=tournamentName, projID=projID, tourID=tourID)
        
    #Settings
    def settingsGeneral(projID, tourID):
        #for navbar
        navtype = 'dashboard'
        navexpand = 'Yes'
        tournamentName = retrieveDashboardNavName(tourID)

        if request.method == "POST":
            identifier = request.form.get("formIdentifier")
            action = request.form.get('action')

            if action == 'delete':
                print('action form delete triggered!')
                return redirect(url_for('loadSuspendTour', projID=projID, tourID=tourID))
            
            else:
                print('action form delete not triggered, update form.')
                with dbConnect.engine.connect() as conn:
                    query = "SELECT * FROM sports"
                    result = conn.execute(text(query))
                    rows = result.fetchall()

                    sportsOptions = [row._asdict() for row in rows]

                # if identifier == "general":

                tourName = request.form.get("tourName")
                tourSize = request.form.get("tourSize")
                startDate = request.form.get("startDate")
                endDate = request.form.get("endDate")
                gender = request.form.get("gender")
                sport = request.form.get("sport")
                format = request.form.get("format")
                getstatus = request.form.get("status")
                status = int(getstatus)

                if not tourName:
                    flash('Please fill in a tournament name!', 'error')
                    return render_template('generalsettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, navexpand=navexpand, tournamentName=tournamentName, tourID=tourID, projID=projID)
                elif len(tourName) > 100:
                    flash('Please keep tournament name less than 100 characters!', 'error')
                    return render_template('generalsettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, navexpand=navexpand, tournamentName=tournamentName, tourID=tourID, projID=projID)
                elif not tourSize:
                    flash('Please Enter a minimum participation size!', 'error')
                    return render_template('generalsettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, navexpand=navexpand, tournamentName=tournamentName, tourID=tourID, projID=projID)
                elif int(tourSize) > 10000:
                    flash('Please enter participant size from 1-10,000!', 'error')
                    return render_template('generalsettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, navexpand=navexpand, tournamentName=tournamentName, tourID=tourID, projID=projID)
                elif int(tourSize) < 0:
                    flash('Please enter participant size from 1-10,000!', 'error')
                    return render_template('generalsettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, navexpand=navexpand, tournamentName=tournamentName, tourID=tourID, projID=projID)
                elif not format:
                    flash('That is not a valid format for the sport!', 'error')
                    return render_template('generalsettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, navexpand=navexpand, tournamentName=tournamentName, tourID=tourID, projID=projID)
                elif not endDate or not startDate:
                    flash('Start or End Dates are not filled!', 'error')
                    return render_template('generalsettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, navexpand=navexpand, tournamentName=tournamentName, tourID=tourID, projID=projID)
                elif endDate < startDate:
                    flash('End Date cannot be earlier than Start Date!', 'error')
                    return render_template('generalsettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, navexpand=navexpand, tournamentName=tournamentName, tourID=tourID, projID=projID)
                else:
            
                    try:
                        with dbConnect.engine.connect() as conn:
                            query = "SELECT * FROM sportsformats JOIN formats ON sportsformats.formatID = formats.formatID WHERE sportID = :sport AND formatName = :format"
                            inputs = {'sport': sport, 'format': format}
                            getsfID = conn.execute(text(query), inputs)
                            rows = getsfID.fetchall()
                            formatID = rows[0][2]

                            query = "UPDATE tournaments SET tourName = :tourName, tourSize = :tourSize, startDate = :startDate, endDate = :endDate, gender = :gender, sportID = :sportID, formatID = :formatID, statusID = :statusID WHERE tourID = :tourID"
                            inputs = {'tourName': tourName, 'tourSize': tourSize, 'startDate': startDate, 'endDate': endDate, 'gender':gender, 'sportID':sport, 'formatID':formatID, 'statusID':status, 'tourID':tourID}
                            updateGeneralInfo = conn.execute(text(query), inputs)
                    
                        # flash('General Information Updated!', 'success')
                    
                    except Exception as e:
                        flash('Oops, an error has occured in updating general details tab.', 'error')
                        print(f"Error details: {e}")

                # elif identifier == "details":

                generalDesc = request.form.get("generalDesc")
                rules = request.form.get("rules")
                prize = request.form.get("prize")

                try:
                    with dbConnect.engine.connect() as conn:
                        query = "SELECT generalInfoID from tournaments WHERE tourID = :tourID"
                        inputs = {'tourID':tourID}
                        getGeneralInfoID = conn.execute(text(query), inputs)
                        rows = getGeneralInfoID.fetchall()
                        generalInfoID = rows[0][0]

                        query = "UPDATE generalInfo SET generalInfoDesc = :generalDesc, rules = :rules, prize = :prize WHERE generalInfoID = :generalInfoID"
                        inputs = {'generalDesc':generalDesc, 'rules':rules, 'prize':prize, 'generalInfoID':generalInfoID}
                        updateDetails = conn.execute(text(query), inputs)
                
                    # flash('Details Updated!', 'success')
                
                except Exception as e:
                    flash('Oops, an error has occured in updating details tab.', 'error')
                    print(f"Error details: {e}")

                # elif identifier == "contact":

                contact = request.form.get("contact")
                
                try:
                    with dbConnect.engine.connect() as conn:
                        query = "UPDATE generalInfo SET contact = :contact WHERE generalInfoID = :generalInfoID"
                        inputs = {'contact':contact, 'generalInfoID':generalInfoID}
                        updateDetails = conn.execute(text(query), inputs)
                
                    # flash('Contact Updated!', 'success')
                
                except Exception as e:
                    flash('Oops, an error has occured in updating contact tab.', 'error')
                    print(f"Error details: {e}")

                flash('Tournament Details Updated!', 'success')
                return redirect(url_for('loadsettings', tourID=tourID, projID=projID))


        else:
            with dbConnect.engine.connect() as conn:
                #getting general tab information
                query = "SELECT * FROM sports"
                result = conn.execute(text(query))
                rows = result.fetchall()

                sportsOptions = [row._asdict() for row in rows]
                
                query = "SELECT tournaments.tourName, tournaments.tourSize, tournaments.startDate, tournaments.endDate, tournaments.gender, tournaments.sportID, formats.formatName, tournaments.statusID, tournaments.generalInfoID FROM tournaments JOIN formats ON tournaments.formatID = formats.formatID WHERE tournaments.tourID = :tourID"
                inputs = {'tourID': tourID}
                result = conn.execute(text(query), inputs)
                rows = result.fetchall()

                tourName = rows[0][0]
                tourSize = rows[0][1]
                startDate = rows[0][2]
                endDate = rows[0][3]
                gender = rows[0][4]
                sport = rows[0][5]
                format = rows[0][6]
                status = rows[0][7]
                generalInfoID = rows[0][8]

                if status == 5:
                    return redirect(url_for('loadSuspendTour', projID=projID, tourID=tourID))

                #getting details and contact information
                query = "SELECT * FROM generalInfo WHERE generalInfoID = :generalInfoID"
                inputs = {'generalInfoID': generalInfoID}
                result = conn.execute(text(query), inputs)
                rows = result.fetchall()

                if rows:
                    generalDesc = rows[0][1]
                    rules = rows[0][2]
                    prize = rows[0][3]
                    contact = rows[0][4]
                else: 
                    generalDesc = ""
                    rules = ""
                    prize = ""
                    contact = ""
      
            return render_template('generalsettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, navexpand=navexpand, tournamentName=tournamentName, tourID=tourID, projID=projID)
        
    #End Tournament
    def SuspendTour(projID, tourID):
        #for navbar
        navtype = 'dashboard'
        navexpand = 'Yes'
        tournamentName = retrieveDashboardNavName(tourID)

        if request.method == "POST":
            getstatus = request.form.get("status")
            status = int(getstatus)

            if status == 5:
                return redirect(url_for('loadSuspendTour', projID=projID, tourID=tourID))

            try:
                with dbConnect.engine.connect() as conn:
                    query = "UPDATE tournaments SET statusID = :statusID WHERE tourID = :tourID"
                    inputs = {'statusID':status,'tourID':tourID}
                    updateStatus = conn.execute(text(query), inputs)

                    flash('Status Updated!', 'success')
                    return redirect(url_for('loadsettings', projID=projID, tourID=tourID))
        
            except Exception as e:
                flash('Oops, an error has occured while changing status for tournament.', 'error')
                print(f"Error details: {e}")
                return render_template('suspendTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, navexpand=navexpand, tournamentName=tournamentName, tourID=tourID, projID=projID)

        else:
            try:
                with dbConnect.engine.connect() as conn:
                    query = "UPDATE tournaments SET statusID = 5 WHERE tourID = :tourID"
                    inputs = {'tourID': tourID}
                    result = conn.execute(text(query), inputs)

                    #getting general tab information
                    query = "SELECT * FROM sports"
                    result = conn.execute(text(query))
                    rows = result.fetchall()

                    sportsOptions = [row._asdict() for row in rows]
                    
                    query = "SELECT tournaments.tourName, tournaments.tourSize, tournaments.startDate, tournaments.endDate, tournaments.gender, tournaments.sportID, formats.formatName, tournaments.statusID FROM tournaments JOIN formats ON tournaments.formatID = formats.formatID WHERE tournaments.tourID = :tourID"
                    inputs = {'tourID': tourID}
                    result = conn.execute(text(query), inputs)
                    rows = result.fetchall()

                    tourName = rows[0][0]
                    tourSize = rows[0][1]
                    startDate = rows[0][2]
                    endDate = rows[0][3]
                    gender = rows[0][4]
                    sport = rows[0][5]
                    format = rows[0][6]
                    status = rows[0][7]

                    #getting details and contact information
                    query = "SELECT generalInfoID from tournaments WHERE tourID = :tourID"
                    inputs = {'tourID':tourID}
                    getGeneralInfoID = conn.execute(text(query), inputs)
                    rows = getGeneralInfoID.fetchall()
                    generalInfoID = rows[0][0]

                    query = "SELECT * FROM generalInfo WHERE generalInfoID = :generalInfoID"
                    inputs = {'generalInfoID': generalInfoID}
                    result = conn.execute(text(query), inputs)
                    rows = result.fetchall()

                    if rows:
                        generalDesc = rows[0][1]
                        rules = rows[0][2]
                        prize = rows[0][3]
                        contact = rows[0][4]
                    else: 
                        generalDesc = ""
                        rules = ""
                        prize = ""
                        contact = ""

                flash('This tournament is Suspended!', 'error')
                return render_template('suspendTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, navexpand=navexpand, tournamentName=tournamentName, tourID=tourID, projID=projID)

            except Exception as e:
                flash('Oops, an error has occured while ending tournament.', 'error')
                print(f"Error details: {e}")
                return render_template('suspendTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, navexpand=navexpand, tournamentName=tournamentName, tourID=tourID, projID=projID)
         
      
    #View Participant List
    def participant(projID, tourID):
        #for navbar
        navtype = 'dashboard'
        tournamentName = retrieveDashboardNavName(tourID)

        try:
            with dbConnect.engine.connect() as conn:            
                # Query the 'participants' table and 'players' tables
                queryOne ="""
                SELECT participants.participantID, participantEmail, participantName, GROUP_CONCAT(playerName) AS playerNames
                FROM participants LEFT JOIN players
                ON participants.participantID = players.participantID
                WHERE participants.tourID = :tourID
                GROUP BY participants.participantID, participantEmail, participantName"""
                inputOne = {'tourID': tourID}
                getparticipants = conn.execute(text(queryOne),inputOne)
                participants = getparticipants.fetchall()

                # Get the total number of participants
                total_participants = len(participants)

                # Query the 'tournaments' table
                queryThree = "SELECT tourSize FROM tournaments WHERE tourID = :tourID"
                inputThree = {'tourID': tourID}
                getTournamentSize = conn.execute(text(queryThree),inputThree)
                tournamentSize = getTournamentSize.scalar() #scalar only extract the value

                # Get the size of tournament
                tournamentSize = tournamentSize

                # Render the HTML template with the participant data and total number
                return render_template('participant.html', participants=participants, total_participants=total_participants, tournamentSize = tournamentSize, navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID)

        except Exception as e:
            # Handle exceptions (e.g., database connection error)
            print(f"Error: {e}")
            flash("An error occurred while retrieving participant data.", "error")
            return render_template('dashboard.html')  # Create an 'error.html' template for error handling 
       
    #Create Participant and Players

    def createParticipant(projID, tourID):
        #for navbar
        navtype = 'dashboard'
        tournamentName = retrieveDashboardNavName(tourID)

        if request.method == "POST":
            participantName = request.form.get("participantName")
            participantEmail = request.form.get("participantEmail")
            playerName = request.form.getlist("playerName")

            try:
                with dbConnect.engine.connect() as conn:
                    queryParticipant = "INSERT INTO participants (participantName, participantEmail, tourID) VALUES (:participantName, :participantEmail, :tourID)"
                    inputParticipant = {'participantName': participantName, 'participantEmail':participantEmail, 'tourID':tourID}
                    createNewParticipant = conn.execute(text(queryParticipant),inputParticipant)
                    
                    participantID = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()                    
                    
                    for i, playerName in enumerate(playerName, start=1):
                        queryPlayer = "INSERT INTO players (playerName, participantID) VALUES (:playerName, :participantID)"
                        inputPlayer = {'playerName': playerName, 'participantID': participantID}
                        createNewPlayer = conn.execute(text(queryPlayer), inputPlayer)
    
                    flash('Participant Created!', 'success')
                    return render_template('createParticipant.html',participantName=participantName, participantEmail=participantEmail, participantID=participantID, playerName=playerName, tourID=tourID, navtype=navtype, tournamentName=tournamentName, projID=projID)

            except Exception as e:
                flash('Oops, an error has occured haha.', 'error')
                print(f"Error details: {e}")
                
            return render_template('createParticipant.html', tourID=tourID, navtype=navtype, tournamentName=tournamentName, projID=projID) 
        else:
            return render_template('createParticipant.html', tourID=tourID, navtype=navtype, tournamentName=tournamentName, projID=projID)

    #Edit Participant
    def editParticipant(projID, tourID, participantID):
        #for navbar
        navtype = 'dashboard'
        tournamentName = retrieveDashboardNavName(tourID)

        if request.method == "POST":
            participantName = request.form.get("participantName")
            participantEmail = request.form.get("participantEmail")

            try:
                with dbConnect.engine.connect() as conn:
                    
                    queryEdit = """
                    UPDATE participants
                    SET participantName = :participantName, participantEmail = :participantEmail
                    WHERE participantID = :participantID AND tourID = :tourID
                    """
                    inputEdit = {
                        'participantName': participantName,
                        'participantEmail': participantEmail,
                        'participantID': participantID,
                        'tourID': tourID
                    }
                    updateParticipantInfo = conn.execute(text(queryEdit), inputEdit)
                    flash('Participant Information Updated!', 'success')

            
            except Exception as e:
                flash('Oops, an error has occured.', 'error')
                print(f"Error details: {e}")
                
            return render_template('editParticipant.html',participantID=participantID, participantName=participantName, participantEmail=participantEmail, navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID)
        
        else:
            with dbConnect.engine.connect() as conn:
                    queryOne = "SELECT participantName, participantEmail FROM participants WHERE tourID = :tourID AND participantID = :participantID"
                    inputs = {'tourID': tourID, 'participantID': participantID}
                    editParticipant = conn.execute(text(queryOne),inputs)
                    participants = editParticipant.fetchall()
                                        
                    participantName = participants[0][0]
                    participantEmail = participants[0][1]
                    
            return render_template('editParticipant.html',navtype=navtype, tournamentName=tournamentName, tourID=tourID, participantName=participantName, participantEmail=participantEmail, participantID=participantID, projID=projID)
        
    # Delete Participant
    def deleteParticipant(projID, tourID, participantID):       
        #for navbar
        navtype = 'dashboard'
        tournamentName = retrieveDashboardNavName(tourID) 

        if request.method == "POST":
            disabledName = request.form.get("disabledName")
            disabledEmail = request.form.get("disabledEmail")
            
            try:

                with dbConnect.engine.connect() as conn:
                    # Delete participant from the database
                    queryDelete = """
                    DELETE FROM participants
                    WHERE participantID = :participantID AND tourID = :tourID
                    """
                    inputDelete = {
                        'participantID': participantID,
                        'tourID': tourID
                    }
                    conn.execute(text(queryDelete), inputDelete)
                    flash('Participant Deleted Successfully!', 'success')
                    
                return redirect('participant.html', navtype=navtype, tournamentName=tournamentName, tourID=tourID, participantID=participantID, projID=projID)
            
            except Exception as e:
                flash('Oops, an error has occurred. Details: {}'.format(e), 'error')
                print(f"Error details: {e}")

            return redirect('participant.html')

        
        else:
            with dbConnect.engine.connect() as conn:
                    queryOne = "SELECT participantName, participantEmail FROM participants WHERE tourID = :tourID AND participantID = :participantID"
                    inputs = {'tourID': tourID, 'participantID': participantID}
                    deleteParticipant = conn.execute(text(queryOne),inputs)
                    participants = deleteParticipant.fetchall()
                                        
                    disabledName = participants[0][0]
                    disabledEmail = participants[0][1]                
            return render_template('deleteParticipant.html',disabledEmail=disabledEmail, disabledName=disabledName, navtype=navtype, tournamentName=tournamentName, tourID=tourID, participantID=participantID, projID=projID)

    #View Moderator List
    def moderator(projID, tourID):
        #for navbar
        navtype = 'dashboard'
        tournamentName = retrieveDashboardNavName(tourID)

        try:
            with dbConnect.engine.connect() as conn:            
                # Query the 'participants' table
                queryModeratorList ="""
                SELECT users.email, moderators.moderatorID
                FROM moderators JOIN users
                ON moderators.userID = users.userID
                WHERE moderators.tourID = :tourID
                GROUP BY moderators.moderatorID"""
                inputModeratorList = {'tourID': tourID}
                getmoderators = conn.execute(text(queryModeratorList),inputModeratorList)
                moderators = getmoderators.fetchall()


                # Render the HTML template with the participant data and total number
                return render_template('moderator.html',moderators=moderators, navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID)

        except Exception as e:
            # Handle exceptions (e.g., database connection error)
            print(f"Error: {e}")
            flash("An error occurred while retrieving participant data.", "error")
            return render_template('moderator.html')  # Create an 'error.html' template for error handling 

    #Placement
    def get_updated_content():
        #for navbar
        tourID = session["placementTour"]
        navtype = 'dashboard'
        tournamentName = retrieveDashboardNavName(tourID)

        # Logic to read and return updated content from seeding.html
        with open('templates\seeding.html', 'r') as file:   
            updated_content = file.read()
        return updated_content