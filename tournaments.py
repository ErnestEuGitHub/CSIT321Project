from flask import render_template, session
from database import dbConnect
from sqlalchemy import text
from datetime import datetime

def tournaments(projID):
    with dbConnect.engine.connect() as conn:
        query = "SELECT * FROM tournaments WHERE projID = :projID AND userID = :userID;"
        inputs = {'projID': projID, 'userID': session["id"]}
        getTour = conn.execute(text(query), inputs)
        rows = getTour.fetchall()

        tournamentlist = [row._asdict() for row in rows]

        session["tournav"] = tournamentlist
        #for navbar
        navtype = 'tournament'

    return render_template('tournament.html', tournamentlist=tournamentlist, navtype=navtype)