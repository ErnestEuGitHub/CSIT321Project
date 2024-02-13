from flask import Flask, render_template, session, request, flash, url_for, redirect
from database import dbConnect
from sqlalchemy import text
from general import *
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO

app = Flask(__name__)

#Google Drive API credentials
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'
PARENT_FOLDER_ID = "1LussvyUWnydZNcnSqbleBFaQ0TpyXouI"

def authenticate():
    # Authentication
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

def get_drive_service():
    # Create and return a Google Drive service instance using the authenticated credentials
    creds = authenticate()
    return build('drive', 'v3', credentials=creds)

def upload_to_google_drive(accountImage):
    try: 
        drive_service = get_drive_service()

        google_drive_folder_id = PARENT_FOLDER_ID

        if accountImage:
            # Prepare metadata
            file_metadata = {'parents': [google_drive_folder_id]}

            file_bytes = accountImage.read()

            file_like_object = BytesIO(file_bytes)

            media = MediaIoBaseUpload(file_like_object, mimetype='application/octet-stream', resumable=True)

            file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

            # Get the file ID
            file_id = file.get('id')

              # Log the file ID
            print(f"File uploaded successfully. File ID: {file_id}")

            return file_id
        else:
            # Log that no upload provided
            print("No upload provided. Skipping upload.")
            return None

    except Exception as e:
        print(f"Error uploading to Google Drive: {e}")
        return None


class AccountSetting:
    
    def accountSetting(userID):
        navtype = 'tournament'

        if request.method == "POST":
            fname = request.form.get("fname")
            lname = request.form.get("lname")
            accountImage = request.files.get("accountImage")

            with dbConnect.engine.connect() as conn:
                query = "UPDATE users SET fname = :fname, lname = :lname, profileMediaID = :profileMediaID WHERE userID = :userID"
                file_id = upload_to_google_drive(accountImage)
                print(f"File ID from Google Drive: {file_id}")  # THis line is for debugging
                inputs = {'userID' :userID, 'fname':fname, 'lname':lname, 'profileMediaID':file_id}
                updateAccount = conn.execute(text(query), inputs)
                #This part is to start a new sessions
                session["fname"] = fname
                session["profileMediaID"] = file_id
                return redirect(url_for('loadAccountSetting', userID=userID))

        else:
            return render_template('accountSetting.html', navtype=navtype, userID=userID)
        
    def upload():
        if 'accountImage' not in request.files:
            flash('No file part', 'error')
            return redirect(url_for('loadAccountSetting'))

        accountImage = request.files['accountImage']

        if accountImage.filename == '':
            flash('No selected file', 'error')
            return redirect(url_for('loadAccountSetting'))

        upload_to_google_drive(accountImage) 

        flash('File uploaded successfully', 'success')
        return redirect(url_for('loadAccountSetting'))

        