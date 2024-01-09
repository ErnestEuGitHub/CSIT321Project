from flask import render_template, request, flash, session, redirect, url_for
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
PARENT_FOLDER_ID = "1pXEfSCViy_yQTXJyS27_dH-un0fJoBdm"

def authenticate():
    # Authentication
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

def get_drive_service():
    # Create and return a Google Drive service instance using the authenticated credentials
    creds = authenticate()
    return build('drive', 'v3', credentials=creds)

def upload_to_google_drive(image, proj_name):
    try: 
        drive_service = get_drive_service()

        google_drive_folder_id = PARENT_FOLDER_ID

        if image:
            # Prepare metadata
            file_metadata = {'name': f'{proj_name}', 'parents': [google_drive_folder_id]}

            file_bytes = image.read()

            file_like_object = BytesIO(file_bytes)

            media = MediaIoBaseUpload(file_like_object, mimetype='application/octet-stream', resumable=True)

            file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

            # Get the file ID
            file_id = file.get('id')

            return file_id
        else:
            # skip upload if no upload provided
            return None

    except Exception as e:
        print(f"Error uploading to Google Drive: {e}")
        return None

class Projects:
    @staticmethod
    def home():
        projects = updateNavProjects()
        # for navbar
        navtype = 'project'
        
        return render_template('home.html', projects=projects, navtype=navtype)

    @staticmethod
    # Create Project
    def createProj():
        #for navbar
        navtype = 'project'

        if request.method == "POST":
            projName = request.form.get("projName")
            startDate = request.form.get("startDate")
            endDate = request.form.get("endDate")
            projImage = request.files.get("projImage")
            userID = session["id"]

            if not projName:
                flash('Please fill in a project name!', 'error')
                return render_template('createProj.html', projName=projName, startDate=startDate, endDate=endDate)
            
            elif not endDate or not startDate:
                flash('Start or End Dates are not filled!', 'error')
                return render_template('createProj.html', projName=projName, startDate=startDate, endDate=endDate)

            elif endDate < startDate:
                flash('End Date cannot be earlier than Start Date!', 'error')
                return render_template('createProj.html', projName=projName, startDate=startDate, endDate=endDate)

            else:
                #convertion to correct types placed here after checking no empty strings
                startDate = datetime.strptime(startDate, "%Y-%m-%d")
                endDate = datetime.strptime(endDate, "%Y-%m-%d")

                try:
                    with dbConnect.engine.connect() as conn:
                        query = "INSERT INTO projects (projName, projStartDate, projEndDate, userID, projImageID) VALUES (:projName, :projStartDate, :projEndDate, :userID, :projImageID)"
                        file_id = upload_to_google_drive(projImage, projName)
                        inputs = {'projName': projName, 'projStartDate': startDate, 'projEndDate': endDate, 'userID': userID, 'projImageID': file_id}
                        createProject = conn.execute(text(query), inputs)

                    userID = session["id"]
                    projects = updateNavProjects()
                    flash('Project Created!', 'success')
                    return render_template('createProj.html', navtype=navtype, projects=projects)
                
                except Exception as e:
                    flash('Oops, an error has occured.', 'error')
                    print(f"Error details: {e}")
                return render_template('createProj.html', projName=projName, startDate=startDate, endDate=endDate, navtype=navtype, projects=session["projnav"])
                
        else:
            return render_template('createProj.html', navtype=navtype, projects=session["projnav"])

def upload():
    if 'projImage' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('createProj'))

    projImage = request.files['projImage']

    if projImage.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('createProj'))

    upload_to_google_drive(projImage) 

    flash('File uploaded successfully', 'success')
    return redirect(url_for('createProj'))