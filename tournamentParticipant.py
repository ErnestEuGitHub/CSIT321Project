from flask import render_template, request, flash, session
from database import dbConnect
import bcrypt
from sqlalchemy import text

def tournamentParticipant():
        try:
                with dbConnect.engine.connect() as conn:
                
                        # Query the 'participant' table
                        query = "SELECT * FROM participants"
                        getparticipants = conn.execute(text(query))
                        participants = getparticipants.fetchall()

                        # Convert the result to a list of dictionaries
                        participantsList = [participant._asdict() for participant in participants]
                        
                        # Render the HTML template with the participant data
                        return participantsList
        
        

        except Exception as e:
                # Handle exceptions (e.g., database connection error)
                print(f"Error: {e}")
                flash("An error occurred while retrieving participant data.", "error")
                return render_template('tournamentDashboard.html')  # Create an 'error.html' template for error handling

def updateNavProjects():
        with dbConnect.engine.connect() as conn:
            query = "SELECT * FROM projects WHERE userID = :userID;"
            inputs = {'userID': session["id"]}
            getprojs = conn.execute(text(query), inputs)
            rows = getprojs.fetchall()

            projects = [row._asdict() for row in rows]

            session["projnav"] = projects
            return projects       
    