from flask import render_template, session
from database import dbConnect
from sqlalchemy import text
from datetime import datetime

def tournaments(projID):
    with dbConnect.engine.connect() as conn:
        query = "SELECT * FROM tournaments WHERE projID = :projID;"
        inputs = {'projID': projID}
        getTour = conn.execute(text(query), inputs)
        rows = getTour.fetchall()

        tournamentlist = [row._asdict() for row in rows]

        session["tournav"] = tournamentlist
        #for navbar
        type = 'tournament'

    return render_template('tournament.html', tournamentlist=tournamentlist, type=type)