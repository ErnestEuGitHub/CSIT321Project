from flask import render_template, request, flash, session
from database import dbConnect
from sqlalchemy import text

def createTour():
    if request.method == "POST":

        generalInfo = ''
        tourName = request.form.get("tourName")
        tourSize = request.form.get("tourSize")
        startDate = request.form.get("startDate")
        endDate = request.form.get("endDate")
        gender = request.form.get("gender")
        sport = request.form.get("sport")
        format = request.form.get("format")
        generalInfo = request.form.get("generalInfo")
        # projID = session["projID"]
        projID = 1
        sfID = 1

        if not tourName:
            flash('Please fill in a tournament name!', 'error')
        elif endDate < startDate:
            flash('End Date cannot be earlier than Start Date', 'error')
        else:
            try:
                with dbConnect.engine.connect() as conn:
                    query = "INSERT INTO tournaments (tourName, tourSize, startDate, endDate, gender, generalInfo, projID, sfID) VALUES (:tourName, :tourSize, :startDate, :endDate, :gender, :generalInfo, :projID, :sfID)"
                    inputs = {'tourName': tourName, 'tourSize': tourSize, 'startDate': startDate, 'endDate': endDate, 'gender':gender, 'sport':sport, 'format':format, 'generalInfo':generalInfo, 'projID':projID, 'sfID':sfID}
                    createTournament = conn.execute(text(query), inputs)
                
                flash('Tournament Created!', 'success')
                return render_template('createTour.html')
            
            except Exception as e:
                flash('Oops, an error has occured.', 'error')
                print(f"Error details: {e}")
                return render_template('createTour.html')
            
    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * FROM sports"
            result = conn.execute(text(query))
            rows = result.fetchall()

            sportsOptions = [row._asdict() for row in rows]
            print(sportsOptions)
        return render_template('createTour.html', sportlist=sportsOptions)