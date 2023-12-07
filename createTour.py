from flask import render_template, request, flash, session
from database import dbConnect
from sqlalchemy import text
from datetime import datetime

def createTour():
    if request.method == "POST":

        tourName = request.form.get("tourName")
        tourSize = request.form.get("tourSize")
        startDate = request.form.get("startDate")
        endDate = request.form.get("endDate")
        gender = request.form.get("gender")
        sport = request.form.get("sport")
        format = request.form.get("format")
        # generalInfo = request.form.get("generalInfo")
        # projID = session["projID"]
        userID = session["id"]
        projID = 1
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
            flash('Please reduce participant size to less than 10,000!', 'error')
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

                    print(rows)
                    print(formatID)

                    query = "INSERT INTO tournaments (tourName, tourSize, startDate, endDate, gender, projID, sportID, formatID, statusID, userID) VALUES (:tourName, :tourSize, :startDate, :endDate, :gender, :projID, :sportID, :formatID, :statusID, :userID)"
                    inputs = {'tourName': tourName, 'tourSize': tourSize, 'startDate': startDate, 'endDate': endDate, 'gender':gender, 'projID':projID, 'sportID':sport, 'formatID':formatID, 'statusID':status, 'userID':userID}
                    createTournament = conn.execute(text(query), inputs)
                
                flash('Tournament Created!', 'success')
                return render_template('createTour.html', sportlist=sportsOptions)
            
            except Exception as e:
                flash('Oops, an error has occured.', 'error')
                print(f"Error details: {e}")
            return render_template('createTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions)
            
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * FROM sports"
            result = conn.execute(text(query))
            rows = result.fetchall()

            sportsOptions = [row._asdict() for row in rows]

        return render_template('createTour.html', sportlist=sportsOptions)