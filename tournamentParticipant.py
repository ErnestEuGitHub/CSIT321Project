from flask import render_template, request, flash, session
from database import dbConnect
import bcrypt
from sqlalchemy import text

def tournamentParticipant():
    
    with dbConnect.engine.connect() as conn:
            query = "SELECT * FROM participants"
            result = conn.execute(text(query))
            rows = result.fetchall()

            participantsOptions = [row._asdict() for row in rows]
    
    return render_template('tournamentParticipant.html')