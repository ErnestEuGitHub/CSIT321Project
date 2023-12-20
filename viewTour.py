from flask import render_template, flash, session
from database import dbConnect
from sqlalchemy import text
from datetime import datetime

def TourOverviewDetails(tourID):
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
            tournamentlist = session["tournav"]
    
    return render_template('tournamentOverviewPage.html', sportName=sportName, tourName=tourName, startDate=startDate, endDate=endDate, gender=gender, navtype=navtype, tournamentlist=tournamentlist)

