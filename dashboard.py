from flask import render_template, request, flash, session
from database import dbConnect
import bcrypt
from sqlalchemy import text

def dashboard(tourID):
    #for navbar
    with dbConnect.engine.connect() as conn:
        query = "SELECT * FROM tournaments WHERE tourID = :tourID"
        inputs = {'tourID': tourID}
        getTour = conn.execute(text(query), inputs)
        rows = getTour.fetchall()

        tournamentName = rows[0][1]

    navtype = 'dashboard'
    return render_template('dashboard.html', navtype=navtype, tournamentName=tournamentName, tourID=tourID)