from flask import render_template, request, flash, session, jsonify, url_for, redirect
from database import dbConnect
import bcrypt
from sqlalchemy import text
from general import *

def media(projID, tourID):
    #fornavbar
    navtype = 'dashboard'
    tournamentName = retrieveDashboardNavName(tourID)

    with dbConnect.engine.connect() as conn:
        query = "SELECT newsID, newsTitle FROM news WHERE tourID = :tourID"
        inputs = {'tourID': tourID}
        result = conn.execute(text(query), inputs)
        rows = result.fetchall()

        newsBlock = [row._asdict() for row in rows]

    return render_template('media.html', newsBlock=newsBlock, navtype=navtype, tournamentName=tournamentName, projID=projID, tourID=tourID)

def createMedia(projID, tourID, userID):
    #for navbar
    navtype = 'dashboard'
    tournamentName = retrieveDashboardNavName(tourID)

    if request.method == "POST":
        newsTitle = request.form.get("newsTitle")
        newsDesc = request.form.get("newsDesc")

        with dbConnect.engine.connect() as conn:
            queryNews = "INSERT INTO news (newsTitle, newsDesc, tourID, userID) VALUES (:newsTitle, newsDesc, tourID, userID)"
            inputNews = {'newsTitle':newsTitle, 'newsDesc':newsDesc, 'tourID':tourID, 'userID':userID}
            createNewMedia = conn.execute(text(queryNews), inputNews)

            newsID = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()

            flash('Media Created!', 'success')

        return redirect(url_for("loadMedia", projID=projID, tourID=tourID))
    else:
        return render_template('createMedia.html', tournamentName=tournamentName, navtype=navtype, projID=projID, tourID=tourID)

def editMedia(projID, tourID, newsID, userID):
    #for navbar
    navtype = 'dashboard'
    tournamentName = retrieveDashboardNavName(tourID)

    # Fetch existing media details from the database based on newsID
    with dbConnect.engine.connect() as conn:
        query = "SELECT * FROM news WHERE newsID = :newsID"
        existingMedia = conn.execute(text(query), {'newsID': newsID}).fetchone()

        if request.method == "POST":
            # If it's a POST request, it means the user is saving the changes
            if existingMedia:
                updatedTitle = request.form.get("newsTitle")
                updatedDesc = request.form.get("newsDesc")

                with dbConnect.engine.connect() as conn:
                    queryUpdate = "UPDATE news SET newsTitle = :newsTitle, newsDesc = :newsDesc WHERE newsID = :newsID"
                    inputUpdate = {'newsTitle': updatedTitle, 'newsDesc': updatedDesc, 'newsID': newsID}
                    conn.execute(text(queryUpdate), inputUpdate)

                    flash('Media Updated!', 'success')

                return redirect(url_for("loadMedia", projID=projID, tourID=tourID))
            else:
                flash('Media not found!', 'error')
                return redirect(url_for("loadMedia", projID=projID, tourID=tourID))