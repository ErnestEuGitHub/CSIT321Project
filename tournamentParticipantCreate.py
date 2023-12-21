from flask import render_template, request, flash, session
from database import dbConnect
import bcrypt
from sqlalchemy import text

def tournamentParticipantCreate():
    
        if request.method == "POST":
            email = request.form.get("email")
            teamName = request.form.get("teamName")

            if not email or not teamName:
                flash('Please fill in all fields!', 'error')
                return render_template('tournamentParticipantCreate.html', emptyForm = True, email=email, teamName=teamName)
            else: 
                try:
                    with dbConnect.engine.connect() as conn:
                        query = "INSERT INTO participants (participantEmail, participantTeamName) VALUES (:participantEmail, :participantTeamName)"
                        addParticipant = {'participantEmail': email, 'participantTeamName': teamName}
                        participant = conn.execute(text(query), addParticipant)

                    flash('Account Created! Try logging in.', 'success')
                    return render_template('tournamentParticipant.html')

                except Exception as e:
                    flash('Oops, an error has occured.', 'error')
                    print(f"Error details: {e}")
                    return render_template('tournamentParticipantCreate.html', error = True, email=email, teamName=teamName)

        else:
            return render_template('tournamentParticipantCreate.html')