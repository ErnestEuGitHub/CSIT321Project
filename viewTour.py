from flask import render_template, flash
from database import dbConnect
from sqlalchemy import text
from datetime import datetime

def TourOverviewDetails(tourID):
    
    try:
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
        
        return render_template('tournamentOverviewPage.html', sportName=sportName, tourName=tourName, startDate=startDate, endDate=endDate, gender=gender)

    except Exception as e:
        flash('Oops, an error has occured.', 'error')
        print(f"Error details: {e}")
    
    return render_template('tournamentOverviewPage.html')

            
