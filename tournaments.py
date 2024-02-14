from flask import Flask, render_template, session, request, flash, jsonify, url_for, redirect
from database import dbConnect
from sqlalchemy import text
from datetime import datetime
from general import *
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
import math

#Google Drive API credentials
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'
PARENT_FOLDER_ID = "1Gjt43kVhn6yAmRT88w11KQSbO2IQvTNZ"
PARENT_FOLDER_ID_2 = "1UOe9hiR1xh__jy-ZbWjs4NidcBjtEfp7" ### This is part of the parent folder 2 ###

def authenticate():
    # Authentication
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

def get_drive_service():
    # Create and return a Google Drive service instance using the authenticated credentials
    creds = authenticate()
    return build('drive', 'v3', credentials=creds)

### This part slowly code in the meta data 2 and parent folder 2

def upload_to_google_drive(image, image_2, tour_name):
    try:
        drive_service = get_drive_service()

        google_drive_folder_id = PARENT_FOLDER_ID
        google_drive_folder_id_2 = PARENT_FOLDER_ID_2
        
        ### Upload the first file
        if image:
            # Prepare metadata
            file_metadata = {'name': f'{tour_name}', 'parents': [google_drive_folder_id]}
            file_bytes = image.read()
            file_like_object = BytesIO(file_bytes)
            media = MediaIoBaseUpload(file_like_object, mimetype='application/octet-stream', resumable=True)
            file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            # Get the file ID
            file_id = file.get('id')
            print(f"File 1 ID: {file_id}")

        else:
            file_id = None
            print("No file1 provided. Skipping upload.")

        # Upload the second file
        
        if image_2:
            # Prepare metadata_2
            file_metadata_2 = {'name': f'{tour_name}', 'parents': [google_drive_folder_id_2]}
            file_bytes_2 = image_2.read()
            file_like_object_2 = BytesIO(file_bytes_2)
            media_2 = MediaIoBaseUpload(file_like_object_2, mimetype='application/octet-stream', resumable=True)
            file_2 = drive_service.files().create(body=file_metadata_2, media_body=media_2, fields='id').execute()
            # Get the file_2 ID
            file_id_2 = file_2.get('id')
            print(f"File 2 ID: {file_id_2}")
        else:
            file_id_2 = None
            print("No file2 provided. Skipping upload.")
        
        return file_id, file_id_2
    
    except Exception as e:
        print(f"Error uploading to Google Drive: {e}")
        return None

app = Flask(__name__)

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
            query = "SELECT tourName, startDate, endDate, gender, sports.sportName, tourBannerID FROM tournaments JOIN sports ON tournaments.sportID = sports.sportID WHERE tourID = :tourID"
            inputs = {'tourID': tourID}
            result = conn.execute(text(query), inputs)
            rows = result.fetchall()

            tourName = rows[0][0]
            startDate = rows[0][1]
            endDate = rows[0][2]
            gender = rows[0][3]
            sportName = rows[0][4]
            tourBannerID = rows[0][5]
            
            #for navbar
            navtype = 'tournament'
            tournamentlist = updateNavTournaments(projID)
            # projID = session["currentProj"]
            projectName = retrieveProjectNavName(projID)
    
        return render_template('tournamentOverviewPage.html', sportName=sportName, tourName=tourName, startDate=startDate, endDate=endDate, gender=gender, navtype=navtype, tournamentlist=tournamentlist, projectName=projectName, tourID=tourID, projID=projID, tourBannerID=tourBannerID)
    
    @staticmethod
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
            # format = request.form.get("format")
            tourImage = request.files.get("tourImage")
            bannerImage = request.files.get("bannerImage")
            templateID = request.form.get("template")
            userID = session["id"]
            status = 4

            with dbConnect.engine.connect() as conn:
                query = "SELECT * FROM sports"
                result = conn.execute(text(query))
                rows = result.fetchall()

                sportsOptions = [row._asdict() for row in rows]

                query = "SELECT * from template WHERE userID = :userID"
                inputs = {'userID': session["id"]}
                getTemplates = conn.execute(text(query), inputs)
                fetchTemplates = getTemplates.fetchall()
                templatelist = [row._asdict() for row in fetchTemplates]

            if not sport:
                flash('Please select a sport!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=sport, sportlist=sportsOptions, projID=projID, templatelist=templatelist)
            elif not tourName:
                flash('Please fill in a tournament name!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), sportlist=sportsOptions, projID=projID, templatelist=templatelist)
            elif len(tourName) > 100:
                flash('Please keep tournament name less than 100 characters!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), sportlist=sportsOptions, projID=projID, templatelist=templatelist)
            elif not tourSize:
                flash('Please Enter a minimum participation size!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), sportlist=sportsOptions, projID=projID, templatelist=templatelist)
            elif int(tourSize) > 10000:
                flash('Please enter participant size from 1-10,000!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), sportlist=sportsOptions, projID=projID, templatelist=templatelist)
            elif int(tourSize) < 0:
                flash('Please enter participant size from 1-10,000!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), sportlist=sportsOptions, projID=projID, templatelist=templatelist)
            elif not format:
                flash('That is not a valid format for the sport!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), sportlist=sportsOptions, projID=projID, templatelist=templatelist)
            elif not endDate or not startDate:
                flash('Start or End Dates are not filled!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), sportlist=sportsOptions, projID=projID, templatelist=templatelist)
            elif endDate < startDate:
                flash('End Date cannot be earlier than Start Date!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), sportlist=sportsOptions, projID=projID, templatelist=templatelist)
            # elif len(generalInfo) > 500:
            #     flash('Please keep general info less than 500 characters!', 'error')
            #     return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, generalInfo=generalInfo, sportlist=sportsOptions)
            
            else:
                if int(templateID) > 0:
                    print('Template Detected!')
                    sport = int(sport)
                    tourSize = int(tourSize)
                    startDate = datetime.strptime(startDate, "%Y-%m-%d")
                    endDate = datetime.strptime(endDate, "%Y-%m-%d")

                    try:
                        with dbConnect.engine.connect() as conn:
                            query = "INSERT INTO generalInfo SET generalInfoDesc = default;"
                            createNewGeneralInfo = conn.execute(text(query))
                            getID = createNewGeneralInfo.lastrowid

                            query = "INSERT INTO tournaments (tourName, tourSize, startDate, endDate, gender, projID, sportID, formatID, statusID, userID, generalInfoID, tourImageID, tourBannerID) VALUES (:tourName, :tourSize, :startDate, :endDate, :gender, :projID, :sportID, 0, :statusID, :userID, :generalInfoID, :tourImageID, :tourBannerID)"
                            file_id = upload_to_google_drive(tourImage, bannerImage, tourName)
                            inputs = {'tourName': tourName, 'tourSize': tourSize, 'startDate': startDate, 'endDate': endDate, 'gender':gender, 'projID':projID, 'sportID':sport, 'statusID':status, 'userID':userID, 'generalInfoID':getID, 'tourImageID': file_id[0], 'tourBannerID': file_id[1]}
                            createTournament = conn.execute(text(query), inputs)
                            newtourID = createTournament.lastrowid

                            #get Template Tournament ID
                            query = "SELECT tourID from template WHERE templateID = :templateID"
                            inputs = {'templateID': templateID}
                            getTemplateTourID = conn.execute(text(query), inputs)
                            fetchTemplateTourID = getTemplateTourID.fetchone()
                            templateTourID = fetchTemplateTourID[0]

                            #Copy Structure Codes
                            
                            query = "SELECT * from stages WHERE tourID = :tourID"
                            inputs = {'tourID': templateTourID}
                            getStageFields = conn.execute(text(query), inputs)
                            fetchStageFields = getStageFields.fetchall()
                            stageFields = [row._asdict() for row in fetchStageFields]

                            templateStageID = stageFields[0]["stageID"]
                            stageName = stageFields[0]["stageName"]
                            stageSequence = stageFields[0]["stageSequence"]
                            stageFormatID = stageFields[0]["stageFormatID"]
                            stageStatusID = 1
                            numberOfParticipants = stageFields[0]["numberOfParticipants"]
                            numberOfGroups = stageFields[0]["numberOfGroups"]
                            matchFormatID = stageFields[0]["matchFormatID"]
                            maxGames = stageFields[0]["maxGames"]

                            stageQuery = """
                                INSERT INTO stages (stageName, stageSequence, stageFormatID, stageStatusID, tourID, numberOfParticipants, numberOfGroups, matchFormatID, maxGames)
                                VALUES (:stageName, :stageSequence, :stageFormatID, :stageStatusID, :tourID, :numberOfParticipants, :numberOfGroups, :matchFormatID, :maxGames)
                                """
                            stageInputs = {'stageName': stageName, 'stageSequence': stageSequence, 'stageFormatID': stageFormatID, 'stageStatusID': stageStatusID, 'tourID': newtourID, 
                                   'numberOfParticipants': numberOfParticipants, 'numberOfGroups': numberOfGroups, 'matchFormatID': matchFormatID, 'maxGames': maxGames}
                            conn.execute(text(stageQuery), stageInputs)
                            IDfetch = conn.execute(text("SELECT LAST_INSERT_ID()"))
                            stageID = IDfetch.scalar()
                            
                            print('Stage Created with Template!')
                            if stageFormatID == 1 or stageFormatID == 2:
                                query = "SELECT * from elimFormat WHERE stageID = :stageID"
                                inputs = {'stageID': templateStageID}
                                getElimFormat = conn.execute(text(query), inputs)
                                fetchElimFormat = getElimFormat.fetchall()
                                elimFormat = [row._asdict() for row in fetchElimFormat]

                                # elimID = elimFormat[0]["elimID"]
                                tfMatch = elimFormat[0]["tfMatch"]

                                elimFormatQuery = "INSERT INTO elimFormat (tfMatch, stageID) VALUES (:tfMatch, :stageID)"
                                elimInputs = {'tfMatch': tfMatch, 'stageID': stageID}
                                conn.execute(text(elimFormatQuery), elimInputs)

                                 # noOfMatch = numberOfParticipants - 1
                                noOfRound = int(math.log2(int(numberOfParticipants)))
                                currentMatchArray = []
                                childMatchArray = []
                                print(noOfRound)

                                for currentRoundNo in range(int(noOfRound)):
                                    print(currentRoundNo)
                                    noOfRoundMatch = int(int(numberOfParticipants) / (math.pow(2, currentRoundNo + 1)))
                                    print(noOfRoundMatch)
                                    for m in range(noOfRoundMatch):
                                        matchCreateQuery = """INSERT INTO matches (stageID, bracketSequence, matchStatus) 
                                        VALUES (:stageID, :bracketSequence, matchStatus)
                                        """
                                        matchCreateInputs = {'stageID': stageID,'bracketSequence': currentRoundNo + 1, 'matchStatus': 0}
                                        conn.execute(text(matchCreateQuery), matchCreateInputs)
                                        IDfetch = conn.execute(text("SELECT LAST_INSERT_ID()"))
                                        matchID = IDfetch.scalar()
                                        currentMatchArray.append(matchID)
                                        print(currentMatchArray)

                                        for n in range(2):
                                            matchParticipantCreateQuery = """INSERT INTO matchParticipant (matchID) 
                                            VALUES (:matchID)
                                            """
                                            matchParticipantCreateInputs = {'matchID': matchID}
                                            conn.execute(text(matchParticipantCreateQuery), matchParticipantCreateInputs)
                                        
                                        for n in range(int(maxGames)):
                                            gameCreateQuery = """INSERT INTO games (matchID, gameNo) 
                                            VALUES (:matchID, :gameNo)
                                            """
                                            matchCreateInputs = {'matchID': matchID,'gameNo': n+1}
                                            conn.execute(text(gameCreateQuery), matchCreateInputs)
                                            IDfetch = conn.execute(text("SELECT LAST_INSERT_ID()"))
                                            gameID = IDfetch.scalar()

                                            for n in range(2):
                                                gameParticipantCreateQuery = """INSERT INTO gameParticipant (gameID) 
                                                VALUES (:gameID)
                                                """
                                                gameParticipantCreateInputs = {'gameID': gameID}
                                                conn.execute(text(gameParticipantCreateQuery), gameParticipantCreateInputs)
                                    
                                    if currentRoundNo != 0:
                                        for currentMatchID in currentMatchArray:
                                            print("The currentMatchID is " + str(currentMatchID))
                                            counter = 0
                                            childMatchArrayCopy = childMatchArray.copy()
                                            print("The childMatchArrayCopy is: ")
                                            print(childMatchArrayCopy)
                                            
                                            for childMatchID in childMatchArrayCopy:
                                                if counter < 2:
                                                    print("The childMatchID is " + str(childMatchID))
                                                    counter += 1
                                                    print("The counter now is " + str(counter))
                                                    parentMatchIDQuery = "UPDATE matches SET parentMatchID = :parentMatchID WHERE matchID = :matchID"
                                                    parentMatchIDInputs = {'parentMatchID': currentMatchID, 'matchID': childMatchID}
                                                    conn.execute(text(parentMatchIDQuery), parentMatchIDInputs)
                                                    childMatchArray.remove(childMatchID)
                                                    print("The childMatchArray is: ")
                                                    print(childMatchArray)
                                                else:
                                                    break

                                    childMatchArray = currentMatchArray.copy()
                                    print("The childMatchArray is: ")
                                    print(childMatchArray)
                                    currentMatchArray = []
                                    print("The currentMatchArray is: ")
                                    print(currentMatchArray)
                                    print('Match/Rounds Created with Template!')

                            elif stageFormatID == 3 or stageFormatID == 4:
                                query = "SELECT * from roundFormat WHERE stageID = :stageID"
                                inputs = {'stageID': templateStageID}
                                getRoundFormat = conn.execute(text(query), inputs)
                                fetchRoundFormat = getRoundFormat.fetchall()
                                roundFormat = [row._asdict() for row in fetchRoundFormat]

                                roundRobinID = roundFormat[0]["roundRobinID"]
                                winPts = roundFormat[0]["winPts"]
                                drawPts = roundFormat[0]["drawPts"]
                                lossPts = roundFormat[0]["lossPts"]

                                query = "SELECT * from tiebreaker WHERE roundRobinID = :roundRobinID"
                                inputs = {'roundRobinID': roundRobinID}
                                getTieBreaker = conn.execute(text(query), inputs)
                                fetchTieBreaker = getTieBreaker.fetchall()
                                tieBreakerlist = [row._asdict() for row in fetchTieBreaker]

                                roundFormatQuery = "INSERT INTO roundFormat (winPts, drawPts, lossPts, stageID) VALUES (:winPts, :drawPts, :lossPts, :stageID)"
                                roundInputs = {'winPts': winPts, 'drawPts': drawPts, 'lossPts': lossPts, 'stageID': stageID}
                                conn.execute(text(roundFormatQuery), roundInputs)
                                IDfetch = conn.execute(text("SELECT LAST_INSERT_ID()"))
                                roundRobinID = IDfetch.scalar()

                                for tieBreaker in tieBreakerlist:
                                    # tieBreakerID = tieBreaker["tieBreakerID"]
                                    tbTypeID = tieBreaker["tbTypeID"]
                                    sequence = tieBreaker["sequence"]

                                    tieBreakerQuery = "INSERT INTO tieBreaker (tbTypeID, sequence, roundRobinID) VALUES (:tbTypeID, :sequence, :roundRobinID)"
                                    tiebreakerInput = {'tbTypeID': tbTypeID, 'sequence': sequence, 'roundRobinID': roundRobinID}
                                    createTiebreakers = conn.execute(text(tieBreakerQuery), tiebreakerInput)

                            else:
                                print("stageFormatID is invalid!")
                                
                            #for navbar
                            tournamentlist = updateNavTournaments(projID)
                            projectName = retrieveProjectNavName(projID)

                        flash('Tournament Created with Template!', 'success')
                        return redirect(url_for('loadCreateTour', projID=projID))
                        # return render_template('createTour.html', sportlist=sportsOptions, tournamentlist=tournamentlist, navtype=navtype, projectName=projectName, projID=projID, templatelist=templatelist)
        
                    except Exception as e:
                        flash('Oops, an error has occured while trying to create tournament with template.', 'error')
                        print(f"Error details: {e}")

                        #for navbar
                        tournamentlist = updateNavTournaments(projID)
                        projectName = retrieveProjectNavName(projID)
                        return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), sportlist=sportsOptions, projectName=projectName, tournamentlist=tournamentlist, projID=projID, templatelist=templatelist)

                else:
                    #no template when creating tournament

                    #convertion to correct types placed here after checking no empty strings
                    sport = int(sport)
                    tourSize = int(tourSize)
                    startDate = datetime.strptime(startDate, "%Y-%m-%d")
                    endDate = datetime.strptime(endDate, "%Y-%m-%d")

                    try:
                        with dbConnect.engine.connect() as conn:
                            # query = "SELECT * FROM sportsformats JOIN formats ON sportsformats.formatID = formats.formatID WHERE sportID = :sport AND formatName = :format"
                            # inputs = {'sport': sport, 'format': format}
                            # getsfID = conn.execute(text(query), inputs)
                            # rows = getsfID.fetchall()
                            # formatID = rows[0][2]


                            query = "INSERT INTO generalInfo SET generalInfoDesc = default;"
                            createNewGeneralInfo = conn.execute(text(query))
                            getID = createNewGeneralInfo.lastrowid

                            query = "INSERT INTO tournaments (tourName, tourSize, startDate, endDate, gender, projID, sportID, statusID, userID, generalInfoID, tourImageID, tourBannerID) VALUES (:tourName, :tourSize, :startDate, :endDate, :gender, :projID, :sportID, :formatID, :statusID, :userID, :generalInfoID, :tourImageID, :tourBannerID)"
                            file_id = upload_to_google_drive(tourImage, bannerImage, tourName)
                            inputs = {'tourName': tourName, 'tourSize': tourSize, 'startDate': startDate, 'endDate': endDate, 'gender':gender, 'projID':projID, 'sportID':sport, 'statusID':status, 'userID':userID, 'generalInfoID':getID, 'tourImageID': file_id[0], 'tourBannerID': file_id[1]}
                            createTournament = conn.execute(text(query), inputs)

                            #for navbar
                            tournamentlist = updateNavTournaments(projID)
                            projectName = retrieveProjectNavName(projID)

                        flash('Tournament Created!', 'success')
                        return redirect(url_for('loadCreateTour', projID=projID))
                        # return render_template('createTour.html', sportlist=sportsOptions, tournamentlist=tournamentlist, navtype=navtype, projectName=projectName, projID=projID, templatelist=templatelist)
        
                    except Exception as e:
                        flash('Oops, an error has occured.', 'error')
                        print(f"Error details: {e}")

                        #for navbar
                        tournamentlist = updateNavTournaments(projID)
                        projectName = retrieveProjectNavName(projID)
                        return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), sportlist=sportsOptions, projectName=projectName, tournamentlist=tournamentlist, projID=projID, templatelist=templatelist)
                
        else:
            with dbConnect.engine.connect() as conn:
                query = "SELECT * FROM sports"
                result = conn.execute(text(query))
                rows = result.fetchall()

                sportsOptions = [row._asdict() for row in rows]

                query = "SELECT * from template WHERE userID = :userID"
                inputs = {'userID': session["id"]}
                getTemplates = conn.execute(text(query), inputs)
                fetchTemplates = getTemplates.fetchall()
                templatelist = [row._asdict() for row in fetchTemplates]

                #for navbar
                tournamentlist = updateNavTournaments(projID)
                projectName = retrieveProjectNavName(projID)
            return render_template('createTour.html', sportlist=sportsOptions, navtype=navtype, tournamentlist=tournamentlist, templatelist=templatelist, projectName=projectName, projID=projID)

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
        moderatorPermissionList = gettingModeratorPermissions(tourID)
        isOwner = verifyOwner(tourID)
        
        return render_template('dashboard.html', navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
    
    #Structure
    def structure(projID, tourID):
        #for navbar
        tournamentName = retrieveDashboardNavName(tourID)
        moderatorPermissionList = gettingModeratorPermissions(tourID)
        isOwner = verifyOwner(tourID)
        
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
                                                    <li><a class="dropdown-item" href="/configureStage/{projID}/{tourID}/{stage["stageID"]}">Configure</a></li>
                                                    <li><a class="dropdown-item" href="#" onclick="deleteStage({tourID}, {stage["stageID"]})">Delete</a></li>
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                '''
                    
                    stageList += stage_html
                
                    
            return render_template('structure.html', navtype=navtype, tournamentName=tournamentName, projID=projID, tourID=tourID, stageList=stageList, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
        
        except Exception as e:
                flash('Oops, an error has occured.', 'error')
                print(f"Error details: {e}")
                return render_template('structure.html', navtype=navtype, tournamentName=tournamentName, projID=projID, tourID=tourID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
        
    

    #CreateStage
    @staticmethod
    def createStage(projID, tourID):
        
        #for navbar
        navtype = 'dashboard'
        tournamentName = retrieveDashboardNavName(tourID)
        moderatorPermissionList = gettingModeratorPermissions(tourID)
        isOwner = verifyOwner(tourID)
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
                        print("stageFormatID is " + stageFormatID)
                        elimFormatQuery = "INSERT INTO elimFormat (tfMatch, stageID) VALUES (:tfMatch, :stageID)"
                        elimInputs = {'tfMatch': tfMatch, 'stageID': stageID}
                        conn.execute(text(elimFormatQuery), elimInputs)

                        # noOfMatch = numberOfParticipants - 1
                        noOfRound = int(math.log2(int(numberOfParticipants)))
                        currentMatchArray = []
                        childMatchArray = []
                        print(noOfRound)

                        for currentRoundNo in range(int(noOfRound)):
                            print(currentRoundNo)
                            noOfRoundMatch = int(int(numberOfParticipants) / (math.pow(2, currentRoundNo + 1)))
                            print(noOfRoundMatch)
                            for m in range(noOfRoundMatch):
                                matchCreateQuery = """INSERT INTO matches (stageID, bracketSequence, matchStatus) 
                                VALUES (:stageID, :bracketSequence, matchStatus)
                                """
                                matchCreateInputs = {'stageID': stageID,'bracketSequence': currentRoundNo + 1, 'matchStatus': 0}
                                conn.execute(text(matchCreateQuery), matchCreateInputs)
                                IDfetch = conn.execute(text("SELECT LAST_INSERT_ID()"))
                                matchID = IDfetch.scalar()
                                currentMatchArray.append(matchID)
                                print(currentMatchArray)

                                for n in range(2):
                                    matchParticipantCreateQuery = """INSERT INTO matchParticipant (matchID) 
                                    VALUES (:matchID)
                                    """
                                    matchParticipantCreateInputs = {'matchID': matchID}
                                    conn.execute(text(matchParticipantCreateQuery), matchParticipantCreateInputs)
                                
                                for n in range(int(maxGames)):
                                    gameCreateQuery = """INSERT INTO games (matchID, gameNo) 
                                    VALUES (:matchID, :gameNo)
                                    """
                                    matchCreateInputs = {'matchID': matchID,'gameNo': n+1}
                                    conn.execute(text(gameCreateQuery), matchCreateInputs)
                                    IDfetch = conn.execute(text("SELECT LAST_INSERT_ID()"))
                                    gameID = IDfetch.scalar()

                                    for n in range(2):
                                        gameParticipantCreateQuery = """INSERT INTO gameParticipant (gameID) 
                                        VALUES (:gameID)
                                        """
                                        gameParticipantCreateInputs = {'gameID': gameID}
                                        conn.execute(text(gameParticipantCreateQuery), gameParticipantCreateInputs)
                            
                            if currentRoundNo != 0:
                                for currentMatchID in currentMatchArray:
                                    print("The currentMatchID is " + str(currentMatchID))
                                    counter = 0
                                    childMatchArrayCopy = childMatchArray.copy()
                                    print("The childMatchArrayCopy is: ")
                                    print(childMatchArrayCopy)
                                    
                                    for childMatchID in childMatchArrayCopy:
                                        if counter < 2:
                                            print("The childMatchID is " + str(childMatchID))
                                            counter += 1
                                            print("The counter now is " + str(counter))
                                            parentMatchIDQuery = "UPDATE matches SET parentMatchID = :parentMatchID WHERE matchID = :matchID"
                                            parentMatchIDInputs = {'parentMatchID': currentMatchID, 'matchID': childMatchID}
                                            conn.execute(text(parentMatchIDQuery), parentMatchIDInputs)
                                            childMatchArray.remove(childMatchID)
                                            print("The childMatchArray is: ")
                                            print(childMatchArray)
                                        else:
                                            break

                            childMatchArray = currentMatchArray.copy()
                            print("The childMatchArray is: ")
                            print(childMatchArray)
                            currentMatchArray = []
                            print("The currentMatchArray is: ")
                            print(currentMatchArray)
                                
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
            return render_template('createStage.html', navtype=navtype, tournamentName=tournamentName, projID=projID, tourID=tourID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
        else:
            return render_template('createStage.html', navtype=navtype, tournamentName=tournamentName, projID=projID, tourID=tourID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
    
    #Match
    def match(projID, tourID):
        #for navbar
        navtype = 'dashboard'
        tournamentName = retrieveDashboardNavName(tourID)
        moderatorPermissionList = gettingModeratorPermissions(tourID)
        isOwner = verifyOwner(tourID)
    
        try:
            with dbConnect.engine.connect() as conn:

                matchquery = "SELECT stageName, stageSequence, stageFormatID, stageStatusID, stageID FROM stages WHERE tourID = :tourID AND stageStatusID <> 4"
                inputs = {'tourID': tourID}
                result = conn.execute(text(matchquery), inputs)
                rows = result.fetchall()
                print(rows)
                matchStages = [row._asdict() for row in rows]
                print(matchStages)

                matchstageList = ''
                
                for matchstage in matchStages:

                    if int(matchstage["stageFormatID"]) == 1:
                        matchstage["stageFormatID"] = "Single Elimination"
                    elif int(matchstage["stageFormatID"]) == 2:
                        matchstage["stageFormatID"] = "Double Elimination"
                    elif int(matchstage["stageFormatID"]) == 3:
                        matchstage["stageFormatID"] = "Single Round Robin"
                    elif int(matchstage["stageFormatID"]) == 4:
                        matchstage["stageFormatID"] = "Double Round Robin"
                    else:
                        print("Invalid stage format!!!")

                    matchstage_html = f'''
                                    <div class="card mb-3">
                                        <div class="card-body">
                                            <div class="d-flex justify-content-between" id="{matchstage["stageID"]}">
                                                <label>{matchstage["stageSequence"]}. {matchstage["stageName"]} - {matchstage["stageFormatID"]}</label>
                                                <a href="/loadmatch/{projID}/{tourID}/{matchstage["stageID"]}">
                                                    <button class="btn btn-primary" type="button" aria-expanded="true">
                                                        View
                                                    </button>
                                                </a>
                                            </div>
                                        </div>
                                    </div>
                                '''
                    
                    matchstageList += matchstage_html

            return render_template('match.html', navtype=navtype, tournamentName=tournamentName, projID=projID, tourID=tourID, matchstageList = matchstageList, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
        except Exception as e:
            flash('Oops, an error has occured.', 'error')
            print(f"Error details: {e}")
            return render_template('match.html', navtype=navtype, tournamentName=tournamentName, projID=projID, tourID=tourID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
        
    #Settings
    def settingsGeneral(projID, tourID):
        #for navbar
        navtype = 'dashboard'
        tournamentName = retrieveDashboardNavName(tourID)
        moderatorPermissionList = gettingModeratorPermissions(tourID)
        isOwner = verifyOwner(tourID)
        
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
                    return render_template('generalsettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
                elif len(tourName) > 100:
                    flash('Please keep tournament name less than 100 characters!', 'error')
                    return render_template('generalsettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
                elif not tourSize:
                    flash('Please Enter a minimum participation size!', 'error')
                    return render_template('generalsettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
                elif int(tourSize) > 10000:
                    flash('Please enter participant size from 1-10,000!', 'error')
                    return render_template('generalsettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
                elif int(tourSize) < 0:
                    flash('Please enter participant size from 1-10,000!', 'error')
                    return render_template('generalsettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
                elif not format:
                    flash('That is not a valid format for the sport!', 'error')
                    return render_template('generalsettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
                elif not endDate or not startDate:
                    flash('Start or End Dates are not filled!', 'error')
                    return render_template('generalsettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
                elif endDate < startDate:
                    flash('End Date cannot be earlier than Start Date!', 'error')
                    return render_template('generalsettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
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
                        return render_template('generalsettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID)

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
                    return render_template('generalsettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID)

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
                    return render_template('generalsettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID)

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
      
            return render_template('generalsettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
        
    #End Tournament
    def SuspendTour(projID, tourID):
        #for navbar
        navtype = 'dashboard'

        if session["profileID"] == 3:
            navtype = 'sysAdmin'

        tournamentName = retrieveDashboardNavName(tourID)
        moderatorPermissionList = gettingModeratorPermissions(tourID)
        isOwner = verifyOwner(tourID)

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
                    if session["profileID"] == 3:
                        return redirect(url_for('loadTourAdminSetting', tourID=tourID))
                    else:
                        return redirect(url_for('loadsettings', projID=projID, tourID=tourID))
        
            except Exception as e:
                flash('Oops, an error has occured while changing status for tournament.', 'error')
                print(f"Error details: {e}")

                if session["profileID"] == 3:
                    return redirect(url_for('loadTourAdminSetting', tourID=tourID))
                else:
                    return render_template('suspendTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID)

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
                return render_template('suspendTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)

            except Exception as e:
                flash('Oops, an error has occured while ending tournament.', 'error')
                print(f"Error details: {e}")
                return render_template('suspendTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
         
      
    #View Participant List
    def participant(projID, tourID):
        #for navbar
        navtype = 'dashboard'
        tournamentName = retrieveDashboardNavName(tourID)
        moderatorPermissionList = gettingModeratorPermissions(tourID)
        isOwner = verifyOwner(tourID)

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
                return render_template('participant.html', participants=participants, total_participants=total_participants, tournamentSize = tournamentSize, navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)

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
        moderatorPermissionList = gettingModeratorPermissions(tourID)
        isOwner = verifyOwner(tourID)

        if request.method == "POST":
            participantName = request.form.get("participantName")
            participantEmail = request.form.get("participantEmail")
            playerName = request.form.getlist("playerName")

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
            
            return redirect(url_for("loadParticipant", projID=projID, tourID=tourID))
        else:
            return render_template('createParticipant.html',tourID=tourID, navtype=navtype, tournamentName=tournamentName, projID=projID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)

    #Edit Participant
    def editParticipant(projID, tourID, participantID):
        #for navbar
        navtype = 'dashboard'
        tournamentName = retrieveDashboardNavName(tourID)
        moderatorPermissionList = gettingModeratorPermissions(tourID)
        isOwner = verifyOwner(tourID)

        if request.method == "POST":
            participantName = request.form.get("participantName")
            participantEmail = request.form.get("participantEmail")
            playerName = request.form.getlist("playerName")
            playerID = request.form.getlist("playerID")
            playerList = list(zip(playerName, playerID))
            newPlayerName = request.form.getlist("newPlayerName")

            with dbConnect.engine.connect() as conn:
                # Update participant information in the database
                queryEditParticipants = """
                    UPDATE participants
                    SET participantName = :participantName, participantEmail = :participantEmail
                    WHERE participantID = :participantID AND tourID = :tourID
                """
                inputEditParticipants = {
                    'participantName': participantName,
                    'participantEmail': participantEmail,
                    'participantID': participantID,
                    'tourID': tourID
                }
                conn.execute(text(queryEditParticipants), inputEditParticipants)
                
                for playerName, playerID in playerList: 
                    # Update player names in the database
                    queryEditPlayers = """
                        UPDATE players
                        SET playerName = :playerName
                        WHERE playerID = :playerID AND participantID = :participantID
                    """
                    inputEditPlayers = {
                        'playerName': playerName,
                        'playerID': playerID,
                        'participantID': participantID,
                    }
                    conn.execute(text(queryEditPlayers), inputEditPlayers)              
                
                # Create New Player
                for i, newPlayerName in enumerate(newPlayerName, start=1):
                    queryNewPlayer = "INSERT INTO players (playerName, participantID) VALUES (:playerName, :participantID)"
                    inputNewPlayer = {'playerName': newPlayerName, 'participantID': participantID}
                    createNewPlayer = conn.execute(text(queryNewPlayer), inputNewPlayer)

            flash('Participant Information Updated!', 'success')
            
            return redirect(url_for("loadParticipant", projID=projID, tourID=tourID))
            
        else:
            with dbConnect.engine.connect() as conn:
                queryOne = """SELECT participantName, participantEmail, playerName, playerID
                FROM participants LEFT JOIN players
                ON participants.participantID = players.participantID
                WHERE participants.tourID = :tourID AND participants.participantID = :participantID"""
                inputOne = {'tourID': tourID, 'participantID': participantID}
                editParticipant = conn.execute(text(queryOne),inputOne)
                participants = editParticipant.fetchall()          

                # Check if the participant exists
                if participants:
                    participantName = participants[0][0]  # Assuming participantName is the first column
                    participantEmail = participants[0][1]  # Assuming participantEmail is the second column

                    # Fetch all player names for the participant
                    playerList = [(row[2], row[3]) for row in participants if row[2] is not None and row[3] is not None]  
                    # Assuming playerID is the third column
                    # Assuming playerName is the forth column

                    # Now, you have participant information and a list of player names
                    # You can use participantID, participantName, participantEmail, and playerNames in your template or further processing
                else:
                    # Handle the case when the participant does not exist
                    flash('Participant not found!', 'error')
                        
            return render_template('editParticipant.html',navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, playerList=playerList, participantName=participantName, participantEmail=participantEmail, participantID=participantID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
    
    # Delete Participant
    def deleteParticipant(projID, tourID, participantID):       
        #for navbar
        navtype = 'dashboard'
        tournamentName = retrieveDashboardNavName(tourID) 
        moderatorPermissionList = gettingModeratorPermissions(tourID)
        isOwner = verifyOwner(tourID)

        if request.method == "POST":
            participantName = request.form.get("participantName")
            participantEmail = request.form.get("participantEmail")
            playerName = request.form.getlist("playerName")
            playerID = request.form.getlist("playerID")
            playerList = list(zip(playerName, playerID))
            print("Player List: ",playerList)
            try:
                with dbConnect.engine.connect() as conn:   
                    # Check if playerList is empty
                    if not playerList:
                        # Delete participant from the database when there is no player
                        queryDeleteParticipantsOnly = """
                        DELETE FROM participants
                        WHERE participantID = :participantID 
                        AND tourID = :tourID
                        """
                        inputDeleteParticipantsOnly = {
                            'participantID': participantID,
                            'tourID': tourID
                        }
                        conn.execute(text(queryDeleteParticipantsOnly), inputDeleteParticipantsOnly)
                        flash('Participant Deleted Successfully!', 'success')
                    else:
                        # Delete participant from the database when there is player(s)
                        queryDeleteParticipantAndPlayer = """
                            DELETE participants, players FROM participants
                            LEFT JOIN players ON participants.participantID = players.participantID
                            WHERE players.playerID IN :playerIDs
                            AND participants.participantID = :participantID 
                            AND participants.tourID = :tourID
                        """
                        inputDeleteParticipantAndPlayer = {
                            'playerIDs': playerID,  # Make sure playerID is a list of player IDs
                            'participantID': participantID,
                            'tourID': tourID
                        }
                        conn.execute(text(queryDeleteParticipantAndPlayer), inputDeleteParticipantAndPlayer)
                        flash('Participant Deleted Successfully!', 'success')                 
                
                return redirect(url_for("loadParticipant", projID=projID, tourID=tourID))
            
            except Exception as e:
                flash('Oops, an error has occurred. Details: {}'.format(e), 'error')
                print(f"Error details: {e}")

            return redirect('participant.html')

        
        else:
          
            with dbConnect.engine.connect() as conn:
                    queryOne = """SELECT participantName, participantEmail, playerName, playerID
                    FROM participants LEFT JOIN players
                    ON participants.participantID = players.participantID
                    WHERE participants.tourID = :tourID AND participants.participantID = :participantID"""
                    inputOne = {'tourID': tourID, 'participantID': participantID}
                    editParticipant = conn.execute(text(queryOne),inputOne)
                    participants = editParticipant.fetchall()          

                    # Check if the participant exists
                    if participants:
                        participantName = participants[0][0]  # Assuming participantName is the first column
                        participantEmail = participants[0][1]  # Assuming participantEmail is the second column

                        # Fetch all player names for the participant
                        playerList = [(row[2], row[3]) for row in participants if row[2] is not None and row[3] is not None]  
                        # Assuming playerID is the third column
                        # Assuming playerName is the forth column

                        # Now, you have participant information and a list of player names
                        # You can use participantID, participantName, participantEmail, and playerNames in your template or further processing
                    else:
                        # Handle the case when the participant does not exist
                        flash('Participant not found!', 'error')
                        
            
            return render_template('deleteParticipant.html',navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, playerList=playerList, participantName=participantName, participantEmail=participantEmail, participantID=participantID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
  
    # Delete Player
    def deletePlayer(projID, tourID, participantID, playerID):       
        #for navbar
        navtype = 'dashboard'
        tournamentName = retrieveDashboardNavName(tourID) 
        moderatorPermissionList = gettingModeratorPermissions(tourID)
        isOwner = verifyOwner(tourID)
        

        if request.method == "POST":
            print(request.form)
            playerID = request.form.get("playerID")
            print(playerID)
            
            try:

                with dbConnect.engine.connect() as conn:
                    # Delete participant from the database
                        queryDeletePlayerOnly = """
                        DELETE FROM players
                        WHERE playerID = :playerID AND participantID = :participantID
                        """
                        inputDeletePlayerOnly = {
                            'playerID': playerID,
                            'participantID': participantID
                        }
                        conn.execute(text(queryDeletePlayerOnly), inputDeletePlayerOnly)
                        flash('Player Deleted Successfully!', 'success')                 
                
                return redirect(url_for("loadDeleteParticipant", projID=projID, tourID=tourID, participantID=participantID))
            
            except Exception as e:
                flash('Oops, an error has occurred. Details: {}'.format(e), 'error')
                print(f"Error details: {e}")

            return render_template('deleteParticipant.html',navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, participantID=participantID, playerID=playerID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
        
        else:                        
            return render_template('deleteParticipant.html',navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, participantID=participantID, playerID=playerID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
    
    #View Moderator List
    def moderator(projID, tourID):
        #for navbar
        navtype = 'dashboard'
        tournamentName = retrieveDashboardNavName(tourID)
        moderatorPermissionList = gettingModeratorPermissions(tourID)
        isOwner = verifyOwner(tourID)

        try:
            with dbConnect.engine.connect() as conn:            
                
                # Query the 'moderator' table
                queryModeratorList ="""
                SELECT moderators.moderatorEmail, GROUP_CONCAT(permissionName) AS permissionName, moderators.moderatorID
                FROM moderators
                LEFT JOIN moderatorPermissions ON moderators.moderatorID = moderatorPermissions.moderatorID 
                LEFT JOIN permissions ON moderatorPermissions.permissionID = permissions.permissionID
                WHERE moderators.tourID = :tourID
                GROUP BY moderators.moderatorID"""
                inputModeratorList = {'tourID': tourID}
                getmoderators = conn.execute(text(queryModeratorList),inputModeratorList)
                moderators = getmoderators.fetchall()  

                # Render the HTML template with the moderator data
                return render_template('moderator.html',moderators=moderators, navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
   
        except Exception as e:
            # Handle exceptions (e.g., database connection error)
            print(f"Error: {e}")
            flash("An error occurred while retrieving participant data.", "error")
            return render_template('moderator.html')  # Create an 'error.html' template for error handling 
        

    #Create Moderators    
    def createModerator(projID, tourID):
        # for navbar
        navtype = 'dashboard'
        tournamentName = retrieveDashboardNavName(tourID)
        moderatorPermissionList = gettingModeratorPermissions(tourID)
        isOwner = verifyOwner(tourID)

        if request.method == "POST":
            moderatorEmail = request.form.get("moderatorEmail")
            selectedPermissions = [
                request.form.get("SetupStructure"),
                request.form.get("ManageRegistration"),
                request.form.get("ManageParticipant"),
                request.form.get("PlaceParticipant"),
                request.form.get("StartMatch"),
                request.form.get("ManageFinalStanding"),
                request.form.get("ManagePublicPage"),
                request.form.get("ManageMedia"),
            ]
            # print(selectedPermissions)

            with dbConnect.engine.connect() as conn:
                # Check if the user already exists
                existingUser = conn.execute(
                    text("SELECT userID FROM users WHERE email = :moderatorEmail"),
                    {'moderatorEmail': moderatorEmail}
                ).fetchone()
                
                # print("Existing User: ", existingUser)

                if existingUser:
                    # User already exists, use their userID
                    userID = existingUser[0]
                else:
                    # User doesn't exist, redirect to registration page
                    return render_template('notfound.html')

                # Insert moderator into the 'moderators' table
                queryNewModerator = "INSERT INTO moderators (userID, tourID, moderatorEmail) VALUES (:userID, :tourID, :moderatorEmail)"
                inputNewModerator = {'userID': userID, 'tourID': tourID, 'moderatorEmail': moderatorEmail}
                conn.execute(text(queryNewModerator), inputNewModerator)
                    
                # Retrieve the newly inserted moderator's ID
                moderatorID = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()

                # Insert selected permissions into the 'moderatorPermissions' table
                for idx, permission in enumerate(selectedPermissions, start=1):
                    if permission:  # Check if the permission is selected
                        query_insert_permission = f"INSERT INTO moderatorPermissions (moderatorID, permissionID) VALUES (:moderatorID, :permissionID)"
                        input_insert_permission = {'moderatorID': moderatorID, 'permissionID': idx}
                        conn.execute(text(query_insert_permission), input_insert_permission)

            return redirect(url_for("loadModerator", projID=projID, tourID=tourID))
        else:
            return render_template('createModerator.html', tourID=tourID, navtype=navtype, tournamentName=tournamentName, projID=projID, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)

    #Edit Moderators    
    def editModerator(projID, tourID, moderatorID):
        # for navbar
        navtype = 'dashboard'
        tournamentName = retrieveDashboardNavName(tourID)
        moderatorPermissionList = gettingModeratorPermissions(tourID)
        isOwner = verifyOwner(tourID)
        
        # print(request.form)

        if request.method == "POST":
            moderatorEmail = request.form.get("moderatorEmail")
            selectedPermissions = [
                request.form.get("Setup Tournament"),
                request.form.get("Setup Structure"),
                request.form.get("Manage Registration"),
                request.form.get("Manage Participant"),
                request.form.get("Place Participant"),
                request.form.get("Manage Final Standing"),
                request.form.get("Report Result"),
            ]

            with dbConnect.engine.connect() as conn:
                # Check if the user already exists
                existingUser = conn.execute(
                    text("SELECT userID FROM users WHERE email = :moderatorEmail"),
                    {'moderatorEmail': moderatorEmail}
                ).fetchone()
                                
                # User already exists, use their userID
                userID = existingUser[0]
                
                # Check if a moderator with the specified userID and tourID already exists
                existingModerator = conn.execute(
                    text("SELECT moderatorID FROM moderators WHERE userID = :userID AND tourID = :tourID"),
                    {'userID': userID, 'tourID': tourID}
                ).fetchone()
                
                if existingModerator:
                    # Moderator already exists, use their moderatorID
                    moderatorID = existingModerator[0]
                else:
                    # Moderator does not exist, handle this situation accordingly (e.g., raise an error, log a message)
                    flash('Moderator not found!', 'error')
                    return redirect(url_for("loadModerator", projID=projID, tourID=tourID))

                # Delete existing permissions for the moderator
                conn.execute(
                    text("DELETE FROM moderatorPermissions WHERE moderatorID = :moderatorID"),
                    {'moderatorID': moderatorID}
                )

                # Insert selected permissions into the 'moderatorPermissions' table
                for idx, permission in enumerate(selectedPermissions, start=1):
                    if permission:  # Check if the permission is selected
                        query_insert_permission = f"INSERT INTO moderatorPermissions (moderatorID, permissionID) VALUES (:moderatorID, :permissionID)"
                        input_insert_permission = {'moderatorID': moderatorID, 'permissionID': idx}
                        conn.execute(text(query_insert_permission), input_insert_permission)

            return redirect(url_for("loadModerator", projID=projID, tourID=tourID))
            
        else:            
            
            with dbConnect.engine.connect() as conn:
                queryRetrieveModerator = """SELECT users.email, permissions.permissionName
                FROM tournaments JOIN users ON tournaments.userID = users.userID
                JOIN moderators ON users.userID = moderators.userID
                LEFT JOIN moderatorPermissions ON moderators.moderatorID = moderatorPermissions.moderatorID
                LEFT JOIN permissions ON moderatorPermissions.permissionID = permissions.permissionID
                WHERE moderators.tourID = :tourID AND moderators.moderatorID = :moderatorID
                GROUP BY users.email, permissions.permissionName, moderators.moderatorID, moderators.tourID"""
                inputRetrieveModerator = {'tourID': tourID, 'moderatorID': moderatorID}
                editModerator = conn.execute(text(queryRetrieveModerator),inputRetrieveModerator)
                moderators = editModerator.fetchall()
                
                print("Moderators: ",moderators)  
                
                # Check if the moderators exists
                if moderators:                    
                    moderatorEmail = moderators[0][0]  # Assuming moderatorEmail is the first column
                    permissionList = [row[1] for row in moderators if row[1] is not None] # Assuming permissionList is the second column
                    print("Moderator Email: ", moderatorEmail)
                    print("Permission List: ", permissionList)
                else:
                    # Handle the case when the participant does not exist
                    flash('Moderator not found!', 'error')

            return render_template('editModerator.html',navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, moderatorEmail=moderatorEmail, permissionList=permissionList, isOwner = isOwner)
        
    #Delete Moderators    
    def deleteModerator(projID, tourID, moderatorID):
        # for navbar
        navtype = 'dashboard'
        tournamentName = retrieveDashboardNavName(tourID)
        moderatorPermissionList = gettingModeratorPermissions(tourID)
        isOwner = verifyOwner(tourID)

        if request.method == "POST":
            moderatorEmail = request.form.get("moderatorEmail")
            selectedPermissions = [
                request.form.get("Setup Structure"),
                request.form.get("Manage Registration"),
                request.form.get("Manage Participant"),
                request.form.get("Place Participant"),
                request.form.get("Start Match"),
                request.form.get("Manage Final Standing"),
                request.form.get("Manage Public Page"),
                request.form.get("Manage Media"),
            ]

            with dbConnect.engine.connect() as conn:
                # Check if the user already exists
                existingModerator = conn.execute(
                    text("SELECT moderatorID FROM moderators WHERE moderatorEmail = :moderatorEmail"),
                    {'moderatorEmail': moderatorEmail}
                ).fetchone()

                print("Moderator ID", existingModerator)
                
                if existingModerator:
                    # Moderator already exists, use their moderatorID
                    moderatorID = existingModerator[0]
                else:
                    # Moderator does not exist, handle this situation accordingly (e.g., raise an error, log a message)
                    flash('Moderator not found!', 'error')
                    return redirect(url_for("loadModerator", projID=projID, tourID=tourID))

                # Delete existing permissions for the moderator
                conn.execute(
                    text("DELETE FROM moderatorPermissions WHERE moderatorID = :moderatorID"),
                    {'moderatorID': moderatorID}
                )

                # Delete the moderator
                conn.execute(
                    text("DELETE FROM moderators WHERE moderatorID = :moderatorID"),
                    {'moderatorID': moderatorID}
                )

                flash('Moderator deleted successfully!', 'success')
                return redirect(url_for("loadModerator", projID=projID, tourID=tourID))

            return redirect(url_for("loadModerator", projID=projID, tourID=tourID))
            
        else:            
            
            with dbConnect.engine.connect() as conn:
                queryRetrieveModerator = """SELECT moderators.moderatorEmail, permissions.permissionName
                FROM tournaments JOIN moderators ON tournaments.tourID = moderators.tourID
                LEFT JOIN moderatorPermissions ON moderators.moderatorID = moderatorPermissions.moderatorID
                LEFT JOIN permissions ON moderatorPermissions.permissionID = permissions.permissionID
                WHERE moderators.tourID = :tourID AND moderators.moderatorID = :moderatorID
                GROUP BY moderators.moderatorEmail, permissions.permissionName, moderators.moderatorID, moderators.tourID"""
                inputRetrieveModerator = {'tourID': tourID, 'moderatorID': moderatorID}
                editModerator = conn.execute(text(queryRetrieveModerator),inputRetrieveModerator)
                moderators = editModerator.fetchall()
                
                print("Moderators: ",moderators)  
                
                # Check if the moderators exists
                if moderators:                    
                    moderatorEmail = moderators[0][0]  # Assuming moderatorEmail is the first column
                    permissionList = [row[1] for row in moderators if row[1] is not None] # Assuming permissionList is the second column
                    print("Moderator Email: ", moderatorEmail)
                    print("Permission List: ", permissionList)
                else:
                    # Handle the case when the participant does not exist
                    flash('Moderator not found!', 'error')

            return render_template('deleteModerator.html',navtype=navtype, tournamentName=tournamentName, tourID=tourID, projID=projID, moderatorEmail=moderatorEmail, moderatorPermissionList=moderatorPermissionList, isOwner = isOwner)
    
    #View Moderator List
    @staticmethod
    def moderatorsTournament(userID):
        #for navbar
        with dbConnect.engine.connect() as conn:            
            
            # Query the 'moderator' table
            queryModeratorList ="""
            SELECT tournaments.tourName, tournaments.tourID, projects.projID
            FROM moderators
            LEFT JOIN tournaments ON moderators.tourID = tournaments.tourID 
            LEFT JOIN projects ON tournaments.projID = projects.projID 
            WHERE moderators.userID = :userID"""
            inputModeratorList = {'userID': session["id"]}
            getmoderators = conn.execute(text(queryModeratorList),inputModeratorList)
            moderatorsTournament = getmoderators.fetchall()  
            
            # print("moderatorsTournament",moderatorsTournament)

            # Render the HTML template with the moderator data
            return render_template('moderatorsTournament.html', moderatorsTournament=moderatorsTournament)
   
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
       
    def upload():
        if 'tourImage' not in request.files:
            flash('No file part', 'error')
            return redirect(url_for('createTour'))

        tourImage = request.files['tourImage']

        if tourImage.filename == '':
            flash('No selected file', 'error')
            return redirect(url_for('createTour'))
        
        
        

        #------------ Banner part -------------------#

        if 'bannerImage' not in request.files:
            flash('No file part', 'error')
            return redirect(url_for('createTour'))
        
        bannerImage = request.files['bannerImage']

        if bannerImage.filename == '':
            flash('No selected file', 'error')
            return redirect(url_for('createTour'))

        upload_to_google_drive(tourImage, bannerImage) 

        flash('File uploaded successfully', 'success')
        return redirect(url_for('createTour'))
    

    def createTemplate(projID):
        navtype = 'tournament'

        if request.method == "POST":
            templateName = request.form.get("templateName")
            tourID = request.form.get("tournament")
            
            if templateName is None or templateName == '':
                flash('Template Name cannot be empty!', 'error')
                return redirect(url_for('loadCreateTemplate', projID=projID))
            else:
                with dbConnect.engine.connect() as conn:
                    try:
                        query = "INSERT INTO template (templateName, tourID, userID) VALUES (:templateName, :tourID, :userID)"
                        inputs = {'templateName': templateName,'tourID': tourID, 'userID': session["id"]}
                        insertTemplate = conn.execute(text(query), inputs)
                        flash('Template Created!', 'success')
                        return redirect(url_for('loadCreateTour', projID=projID))

                    except Exception as e:
                        flash('Oops, an error has occured while creating template.', 'error')
                        print(f"Error details: {e}")
                        return redirect(url_for('loadCreateTemplate', projID=projID))
                    
        else:

            # projID = session["currentProj"]
            tournamentlist = updateNavTournaments(projID)
            projectName = retrieveProjectNavName(projID)

            with dbConnect.engine.connect() as conn:
                query = "SELECT DISTINCT tournaments.*, stages.tourID FROM tournaments JOIN stages ON tournaments.tourID = stages.tourID;"
                # inputs = {'projID': projID, 'userID': session["id"]}
                getTour = conn.execute(text(query))
                gettournaments = getTour.fetchall()
                tourlist = [row._asdict() for row in gettournaments]

            return render_template('createTemplate.html', tourlist=tourlist, navtype=navtype, tournamentlist=tournamentlist, projectName=projectName)
        
    def editTemplate(projID):
        navtype = 'tournament'

        if request.method == "POST":
            action = request.form.get('delete_template')
            templateID = request.form.get("template")
            tourID = request.form.get("tournament")
            
            
            if action == 'delete':
                try:
                    with dbConnect.engine.connect() as conn:
                        query = "DELETE from template WHERE templateID = :templateID"
                        inputs = {'templateID': templateID}
                        deleteTemplate = conn.execute(text(query), inputs)
                        flash('Template Deleted!', 'success')
                        return redirect(url_for('loadEditTemplate', projID=projID))
                except Exception as e:
                    flash('Oops, an error has occured while trying to delete template.', 'error')
                    print(f"Error details: {e}")
                    return redirect(url_for('loadEditTemplate', projID=projID))
            else:
                with dbConnect.engine.connect() as conn:
                    try:
                        query = "UPDATE template SET tourID = :tourID WHERE templateID = :templateID"
                        inputs = {'tourID': tourID, 'templateID': templateID}
                        updateTemplate = conn.execute(text(query), inputs)
                        flash('Template Updated!', 'success')
                        return redirect(url_for('loadEditTemplate', projID=projID))

                    except Exception as e:
                        flash('Oops, an error has occured while trying to update template.', 'error')
                        print(f"Error details: {e}")
                        return redirect(url_for('loadEditTemplate', projID=projID))
                    
        else:

            # projID = session["currentProj"]
            tournamentlist = updateNavTournaments(projID)
            projectName = retrieveProjectNavName(projID)

            with dbConnect.engine.connect() as conn:
                query = "SELECT DISTINCT tournaments.*, stages.tourID FROM tournaments JOIN stages ON tournaments.tourID = stages.tourID;"
                # inputs = {'projID': projID, 'userID': session["id"]}
                getTour = conn.execute(text(query))
                gettournaments = getTour.fetchall()
                tourlist = [row._asdict() for row in gettournaments]

                query = "SELECT * from template WHERE userID = :userID"
                inputs = {'userID': session["id"]}
                getTemplates = conn.execute(text(query), inputs)
                fetchTemplates = getTemplates.fetchall()
                templatelist = [row._asdict() for row in fetchTemplates]

            return render_template('editTemplate.html', tourlist=tourlist, navtype=navtype, tournamentlist=tournamentlist, projectName=projectName, templatelist=templatelist)
    
    def getTemplateInfo(tourID):
        with dbConnect.engine.connect() as conn:
            query = "SELECT stageName, stageSequence, numberOfParticipants, numberOfGroups, stageFormatID FROM stages WHERE tourID = :tourID"
            inputs = {'tourID': tourID}
            getStageInfo = conn.execute(text(query), inputs)
            stageInfo = getStageInfo.fetchall()
            stageInfoList = [row._asdict() for row in stageInfo]

        return jsonify(stageInfoList)
    
    def getCurrentTemplateTourInfo(tempID):
        with dbConnect.engine.connect() as conn:
            query = "SELECT tourID FROM template WHERE templateID = :templateID"
            inputs = {'templateID': tempID}
            getCurrentTourInfo = conn.execute(text(query), inputs)
            currentTour = getCurrentTourInfo.fetchone()
            currentTourID = currentTour[0]
        
            query = "SELECT DISTINCT tournaments.*, stages.tourID FROM tournaments JOIN stages ON tournaments.tourID = stages.tourID;"
            # inputs = {'projID': projID, 'userID': session["id"]}
            getTour = conn.execute(text(query))
            gettournaments = getTour.fetchall()
            tourlist = [row._asdict() for row in gettournaments]

        return jsonify(currentTourID, tourlist)