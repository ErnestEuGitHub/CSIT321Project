from flask import Flask, render_template, session, request, flash, jsonify, url_for, redirect
from database import dbConnect
from sqlalchemy import text
from datetime import datetime
from general import *
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO

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
        return render_template('tournament.html', tournamentlist=tournamentlist, navtype=navtype, projectName=projectName)
    
    #Tournament Overview Page
    def TourOverviewDetails(tourID):
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
            tournamentlist = session["tournav"]
            projID = session["currentProj"]
            projectName = retrieveProjectNavName(projID)
    
        return render_template('tournamentOverviewPage.html', sportName=sportName, tourName=tourName, startDate=startDate, endDate=endDate, gender=gender, navtype=navtype, tournamentlist=tournamentlist, projectName=projectName, tourID=tourID, tourBannerID=tourBannerID)
    
    @staticmethod
    #Create Tournament
    def createTour():
        #for navbar
        navtype = 'tournament'
        projID = session["currentProj"]

        if request.method == "POST":
            tourName = request.form.get("tourName")
            tourSize = request.form.get("tourSize")
            startDate = request.form.get("startDate")
            endDate = request.form.get("endDate")
            gender = request.form.get("gender")
            sport = request.form.get("sport")
            format = request.form.get("format")
            tourImage = request.files.get("tourImage")
            bannerImage = request.files.get("bannerImage")
            userID = session["id"]
            status = 4

            with dbConnect.engine.connect() as conn:
                query = "SELECT * FROM sports"
                result = conn.execute(text(query))
                rows = result.fetchall()

                sportsOptions = [row._asdict() for row in rows]

            if not sport:
                flash('Please select a sport!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=sport, format=format, sportlist=sportsOptions)
            elif not tourName:
                flash('Please fill in a tournament name!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions)
            elif len(tourName) > 100:
                flash('Please keep tournament name less than 100 characters!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions)
            elif not tourSize:
                flash('Please Enter a minimum participation size!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions)
            elif int(tourSize) > 10000:
                flash('Please enter participant size from 1-10,000!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions)
            elif int(tourSize) < 0:
                flash('Please enter participant size from 1-10,000!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions)
            elif not format:
                flash('That is not a valid format for the sport!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions)
            elif not endDate or not startDate:
                flash('Start or End Dates are not filled!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions)
            elif endDate < startDate:
                flash('End Date cannot be earlier than Start Date!', 'error')
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions)
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

                        query = "INSERT INTO tournaments (tourName, tourSize, startDate, endDate, gender, projID, sportID, formatID, statusID, userID, tourImageID, tourBannerID) VALUES (:tourName, :tourSize, :startDate, :endDate, :gender, :projID, :sportID, :formatID, :statusID, :userID, :tourImageID, :tourBannerID)"
                        file_id = upload_to_google_drive(tourImage, bannerImage, tourName)
                        inputs = {'tourName': tourName, 'tourSize': tourSize, 'startDate': startDate, 'endDate': endDate, 'gender':gender, 'projID':projID, 'sportID':sport, 'formatID':formatID, 'statusID':status, 'userID':userID, 'tourImageID': file_id[0], 'tourBannerID': file_id[1]}
                        createTournament = conn.execute(text(query), inputs)
                        getID = createTournament.lastrowid

                        query = "INSERT INTO generalInfo (tourID) VALUES (:getID)"
                        inputs = {'getID':getID}
                        createNewGeneralInfo = conn.execute(text(query), inputs)

                        #for navbar
                        tournamentlist = updateNavTournaments(projID)
                        projectName = retrieveProjectNavName(projID)

                    flash('Tournament Created!', 'success')
                    tournamentlist = updateNavTournaments(projID)  # Define tournamentlist here
                    projectName = retrieveProjectNavName(projID)  # Define projectName here
                    return render_template('createTour.html', sportlist=sportsOptions, tournamentlist=tournamentlist, navtype=navtype, projectName=projectName)
                
                except Exception as e:
                    flash('Oops, an error has occured.', 'error')
                    print(f"Error details: {e}")
                    tournamentlist = updateNavTournaments(projID)  # Define tournamentlist here
                    projectName = retrieveProjectNavName(projID)  # Define projectName here
                return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, projectName=projectName, tournamentlist=tournamentlist)
                
        else:
            with dbConnect.engine.connect() as conn:
                query = "SELECT * FROM sports"
                result = conn.execute(text(query))
                rows = result.fetchall()

                sportsOptions = [row._asdict() for row in rows]

                #for navbar
                tournamentlist = updateNavTournaments(projID)
                projectName = retrieveProjectNavName(projID)
            return render_template('createTour.html', sportlist=sportsOptions, navtype=navtype, tournamentlist=tournamentlist, projectName=projectName)

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
    def dashboard(tourID):
        #for navbar
        tournamentName = retrieveDashboardNavName(tourID)

        navtype = 'dashboard'
        return render_template('dashboard.html', navtype=navtype, tournamentName=tournamentName, tourID=tourID)
    
    #Structure
    def structure(tourID):
        #for navbar
        tournamentName = retrieveDashboardNavName(tourID)

        navtype = 'dashboard'
        return render_template('structure.html', navtype=navtype, tournamentName=tournamentName, tourID=tourID)
    
    #CreateStructure
    def createStructure(tourID):
  
        #for navbar
        tournamentName = retrieveDashboardNavName(tourID)
        navtype = 'dashboard'

        if request.method == "POST":

            stageName = request.form.get("stageName")
            stageSequence = request.form.get("stageSequence")
            stageFormatID = request.form.get("stageFormat")
            stageStatusID = 1
            numberOfParticipants = request.form.get("numberOfParticipants")
            matchFormatID = request.form.get("matchFormat")
            maxGames = request.form.get("maximumNumberOfGames")
            
            elimFormatID = request.form.get("elimFormatID")
            tfMatch = request.form.get("34match")

            roundFormatID = request.form.get("roundFormatID")
            winPts = request.form.get("winPoints")
            drawPts = request.form.get("drawPoints")
            lossPts = request.form.get("lossPoints")
            tieBreakers = request.form.getlist("tieBreakerSelect")
            
            if not maxGames:
                maxGames = matchFormatID
            
            try:
                with dbConnect.engine.connect() as conn:
                    
                    stageQuery = """
                        INSERT INTO stages (stageName, stageSequence, stageFormatID, stageStatusID, tourID, numberOfParticipants, matchFormatID, maxGames)
                        VALUES (:stageName, :stageSequence, :stageFormatID, :stageStatusID, :tourID, :numberOfParticipants, :matchFormatID, :maxGames)
                        """
                    stageInputs = {'stageName': stageName, 'stageSequence': stageSequence, 'stageFormatID': stageFormatID, 'stageStatusID': stageStatusID, 'tourID': tourID, 'numberOfParticipants': numberOfParticipants, 'matchFormatID': matchFormatID, 'maxGames': maxGames}
                    conn.execute(text(stageQuery), stageInputs)
                    IDfetch = conn.execute(text("SELECT LAST_INSERT_ID()"))
                    stageID = IDfetch.scalar()
                    print(f"Inserted stage with stageID: {stageID}")
                    print(type(stageFormatID))

                    if int(stageFormatID) == 1:
                        print("stageFormatID is 1")
                        elimFormatQuery = "INSERT INTO elimFormat (elimFormatID, tfMatch, stageID) VALUES (:elimFormatID, :tfMatch, :stageID)"
                        elimInputs = {'elimFormatID': elimFormatID, 'tfMatch': tfMatch, 'stageID': stageID}
                        conn.execute(text(elimFormatQuery), elimInputs)

                    elif int(stageFormatID) == 2:
                        print("stageFormatID is 2")
                        roundFormatQuery = """INSERT INTO roundFormat (roundFormatID, winPts, drawPts, lossPts, stageID) VALUES (:roundFormatID, :winPts, :drawPts, :lossPts, :stageID)"""
                        roundInputs = {'roundFormatID': roundFormatID, 'winPts': winPts, 'drawPts': drawPts, 'lossPts': lossPts, 'stageID': stageID}
                        conn.execute(text(roundFormatQuery), roundInputs)
                        IDfetch = conn.execute(text("SELECT LAST_INSERT_ID()"))
                        roundRobinID = IDfetch.scalar()
                        print(f"Inserted stage with stageID: {roundRobinID}")

                        for tbTypeID in tieBreakers:
                            sequence = tieBreakers.index(tbTypeID) + 1
                            tieBreakerQuery = "INSERT INTO tieBreaker (tbTypeID, sequence, roundRobinID) VALUES (:tbTypeID, :sequence, :roundRobinID)"
                            tiebreakerInput = {'tbTypeID': tbTypeID, 'sequence': sequence, 'roundRobinID': roundRobinID}
                            createTiebreakers = conn.execute(text(tieBreakerQuery), tiebreakerInput)
                    else:
                        print("stageFormatID is invalid!")
                
                flash('Stage Created!', 'success')
                return render_template('createStructure.html', navtype=navtype, tournamentName=tournamentName, tourID=tourID)
            
            except Exception as e:
                flash('Oops, an error has occured.', 'error')
                print(f"Error details: {e}")
            return render_template('createStructure.html', navtype=navtype, tournamentName=tournamentName, tourID=tourID)
        else:
            return render_template('createStructure.html', navtype=navtype, tournamentName=tournamentName, tourID=tourID)
        

   
    #Settings
    def settings(tourID):
        #for navbar
        navtype = 'dashboard'
        navexpand = 'Yes'
        tournamentName = retrieveDashboardNavName(tourID)

        if request.method == "POST":
            identifier = request.form.get("formIdentifier")

            with dbConnect.engine.connect() as conn:
                query = "SELECT * FROM sports"
                result = conn.execute(text(query))
                rows = result.fetchall()

                sportsOptions = [row._asdict() for row in rows]

            if identifier == "general":

                tourName = request.form.get("tourName")
                tourSize = request.form.get("tourSize")
                startDate = request.form.get("startDate")
                endDate = request.form.get("endDate")
                gender = request.form.get("gender")
                sport = request.form.get("sport")
                format = request.form.get("format")

                if not tourName:
                    flash('Please fill in a tournament name!', 'error')
                    return render_template('settings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, navexpand=navexpand, tournamentName=tournamentName, tourID=tourID)
                elif len(tourName) > 100:
                    flash('Please keep tournament name less than 100 characters!', 'error')
                    return render_template('settings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, navexpand=navexpand, tournamentName=tournamentName, tourID=tourID)
                elif not tourSize:
                    flash('Please Enter a minimum participation size!', 'error')
                    return render_template('settings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, navexpand=navexpand, tournamentName=tournamentName, tourID=tourID)
                elif int(tourSize) > 10000:
                    flash('Please enter participant size from 1-10,000!', 'error')
                    return render_template('settings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, navexpand=navexpand, tournamentName=tournamentName, tourID=tourID)
                elif int(tourSize) < 0:
                    flash('Please enter participant size from 1-10,000!', 'error')
                    return render_template('settings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, navexpand=navexpand, tournamentName=tournamentName, tourID=tourID)
                elif not format:
                    flash('That is not a valid format for the sport!', 'error')
                    return render_template('settings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, navexpand=navexpand, tournamentName=tournamentName, tourID=tourID)
                elif not endDate or not startDate:
                    flash('Start or End Dates are not filled!', 'error')
                    return render_template('settings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, navexpand=navexpand, tournamentName=tournamentName, tourID=tourID)
                elif endDate < startDate:
                    flash('End Date cannot be earlier than Start Date!', 'error')
                    return render_template('settings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, navexpand=navexpand, tournamentName=tournamentName, tourID=tourID)
                else:
            
                    try:
                        with dbConnect.engine.connect() as conn:
                            query = "SELECT * FROM sportsformats JOIN formats ON sportsformats.formatID = formats.formatID WHERE sportID = :sport AND formatName = :format"
                            inputs = {'sport': sport, 'format': format}
                            getsfID = conn.execute(text(query), inputs)
                            rows = getsfID.fetchall()
                            formatID = rows[0][2]

                            query = "UPDATE tournaments SET tourName = :tourName, tourSize = :tourSize, startDate = :startDate, endDate = :endDate, gender = :gender, sportID = :sportID, formatID = :formatID WHERE tourID = :tourID"
                            inputs = {'tourName': tourName, 'tourSize': tourSize, 'startDate': startDate, 'endDate': endDate, 'gender':gender, 'sportID':sport, 'formatID':formatID, 'tourID':tourID}
                            updateGeneralInfo = conn.execute(text(query), inputs)
                    
                        flash('General Information Updated!', 'success')
                    
                    except Exception as e:
                        flash('Oops, an error has occured.', 'error')
                        print(f"Error details: {e}")

            elif identifier == "details":

                generalDesc = request.form.get("generalDesc")
                rules = request.form.get("rules")
                prize = request.form.get("prize")

                try:
                    with dbConnect.engine.connect() as conn:
                        query = "UPDATE generalInfo SET generalInfoDesc = :generalDesc, rules = :rules, prize = :prize WHERE tourID = :tourID"
                        inputs = {'generalDesc':generalDesc, 'rules':rules, 'prize':prize, 'tourID':tourID}
                        updateDetails = conn.execute(text(query), inputs)
                
                    flash('Details Updated!', 'success')
                
                except Exception as e:
                    flash('Oops, an error has occured.', 'error')
                    print(f"Error details: {e}")

            elif identifier == "contact":

                contact = request.form.get("contact")
                
                try:
                    with dbConnect.engine.connect() as conn:
                        query = "UPDATE generalInfo SET contact = :contact WHERE tourID = :tourID"
                        inputs = {'contact':contact, 'tourID':tourID}
                        updateDetails = conn.execute(text(query), inputs)
                
                    flash('Contact Updated!', 'success')
                
                except Exception as e:
                    flash('Oops, an error has occured.', 'error')
                    print(f"Error details: {e}")

            return redirect(url_for('loadsettings', tourID=tourID, navtype=navtype, navexpand=navexpand, tournamentName=tournamentName))


        else:
            with dbConnect.engine.connect() as conn:
                #getting general tab information
                query = "SELECT * FROM sports"
                result = conn.execute(text(query))
                rows = result.fetchall()

                sportsOptions = [row._asdict() for row in rows]
                
                query = "SELECT tournaments.tourName, tournaments.tourSize, tournaments.startDate, tournaments.endDate, tournaments.gender, tournaments.sportID, formats.formatName FROM tournaments JOIN formats ON tournaments.formatID = formats.formatID WHERE tournaments.tourID = :tourID"
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

                #getting details and contact information
                query = "SELECT * FROM generalInfo WHERE tourID = :tourID"
                inputs = {'tourID': tourID}
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
        
            return render_template('settings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, navtype=navtype, navexpand=navexpand, tournamentName=tournamentName, tourID=tourID)
        
    #Create Participant
    def createParticipant(tourID):
        #for navbar
        navtype = 'dashboard'
        tournamentName = retrieveDashboardNavName(tourID)
        
        form_submitted = False

        if request.method == "POST":
            participantName = request.form.get("participantName")
            participantEmail = request.form.get("participantEmail")

            print(participantName)

            try:
                with dbConnect.engine.connect() as conn:
                    query = "INSERT INTO participants (participantName, participantEmail, tourID) VALUES (:participantName, :participantEmail, :tourID)"
                    inputs = {'participantName': participantName, 'participantEmail':participantEmail, 'tourID':tourID}
                    createNewParticipant = conn.execute(text(query),inputs)
                
                    # Set form_submitted to True after successful form submission
                    form_submitted = True
                    flash('Tournament Created!', 'success')
                    return render_template('createParticipant.html',participantName=participantName, participantEmail=participantEmail, tourID=tourID, navtype=navtype, tournamentName=tournamentName, form_submitted=form_submitted)

            except Exception as e:
                flash('Oops, an error has occured.', 'error')
                print(f"Error details: {e}")
            return render_template('createParticipant.html',participantName=participantName, participantEmail=participantEmail, navtype=navtype, tournamentName=tournamentName, tourID=tourID, form_submitted=form_submitted)
        
        else:
            return render_template('createParticipant.html',navtype=navtype, tournamentName=tournamentName, tourID=tourID, form_submitted=form_submitted)
 

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