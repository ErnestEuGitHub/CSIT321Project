from flask import render_template, request, flash, session
from database import dbConnect
import bcrypt
from sqlalchemy import text

def tournamentCreateParticipant():

    invalidTeamName = False
    invalidEmail = False
    logo = False
    emptyForm = False
    error = False
    
    if request.method == "POST":
        teamName = request.form.get("teamName")
        email = request.form.get("email")

        if not email or not teamName:
            flash('Please fill in both team name and email!', 'error')
            return render_template('tournamentParticipantCreate.html', emptyForm = True)
    
        with dbConnect.engine.connect() as conn:
            searchEmail = conn.execute(text("SELECT * FROM regParticipants WHERE EMAIL = '" + email +"'"))
            existing_participants = searchEmail.fetchall()
            # print(rows)

            if existing_participants:
                flash('Participant with this email already exists!', 'error')
                return render_template('tournamentParticipantCreate.html', invalidEmail = True)
            # Insert the new participant into the database
            insert_participant_query = text("INSERT INTO participants (EMAIL, NAME) VALUES (:email, :teamName)")
            conn.execute(insert_participant_query, email=email, teamName=teamName)
            
            flash('Participant created successfully!', 'success')
        return render_template('tournamentParticipant.html')


    else:
        return render_template('tournamentParticipantCreate.html')
