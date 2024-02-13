from flask import Flask, render_template, session, request, flash, jsonify, url_for, redirect
from database import dbConnect
from sqlalchemy import text
from general import *
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO

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

def upload_to_google_drive(image):
    try: 
        drive_service = get_drive_service()

        google_drive_folder_id = PARENT_FOLDER_ID

        if image:
            # Prepare metadata
            file_metadata = {'parents': [google_drive_folder_id]}

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




# Create Tournament
def accountSetting(userID):
    #for navbar
    navtype = 'tournament'

    return render_template('accountSetting.html', navtype=navtype, userID=userID)