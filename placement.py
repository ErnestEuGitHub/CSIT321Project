from flask import render_template, request, flash, session
from database import dbConnect
import bcrypt
from sqlalchemy import text
from general import *

def placement(tourID):
    #fornavbar
    session["placementTour"] = tourID
    navtype = 'dashboard'
    tournamentName = retrieveDashboardNavName(tourID)

    with dbConnect.engine.connect() as conn:
        query = "SELECT stageID, stageName FROM stages WHERE tourID = :tourID ORDER BY stageSequence ASC"
        inputs = {'tourID': tourID}
        result = conn.execute(text(query), inputs)
        rows = result.fetchall()

        placementStages = [row._asdict() for row in rows]
 
    return render_template('placement.html', placementStages=placementStages, navtype=navtype, tournamentName=tournamentName, tourID=tourID)