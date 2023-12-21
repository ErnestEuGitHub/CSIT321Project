from flask import render_template, request, flash, session
from database import dbConnect
import bcrypt
from sqlalchemy import text
from general import retrieveDashboardNavName

def tournamentParticipant(tourID):
        #for navbar
        navtype = 'dashboard'
        tournamentName = retrieveDashboardNavName(tourID)

        try:
                with dbConnect.engine.connect() as conn:
                
                        # Query the 'participants' table
                        queryOne = """
                        SELECT participantEmail, participantName, GROUP_CONCAT(playerName) AS playerNames
                        FROM participants JOIN players
                        WHERE participants.participantID = players.participantID
                        GROUP BY participants.participantID, participantEmail, participantName"""
                        getparticipants = conn.execute(text(queryOne))
                        participants = getparticipants.fetchall()

                        # Get the total number of participants
                        total_participants = len(participants)

                        # Query the 'tournaments' table
                        queryTwo = "SELECT tourSize FROM tournaments where tourID = '1'"
                        getTournamentSize = conn.execute(text(queryTwo))
                        tournamentSize = getTournamentSize.scalar() #scalar only extract the value

                        # Get the size of tournament
                        tournamentSize = tournamentSize

                        # Render the HTML template with the participant data and total number
                        return render_template('tournamentParticipant.html', participants=participants, total_participants=total_participants, tournamentSize = tournamentSize, navtype=navtype, tournamentName=tournamentName, tourID=tourID)

                        
        
        

        except Exception as e:
                # Handle exceptions (e.g., database connection error)
                print(f"Error: {e}")
                flash("An error occurred while retrieving participant data.", "error")
                return render_template('tournamentDashboard.html')  # Create an 'error.html' template for error handling 
    