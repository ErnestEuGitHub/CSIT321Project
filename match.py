from flask import render_template, session, request, flash, session, jsonify, url_for, redirect
from database import dbConnect
from sqlalchemy import text
from datetime import datetime
from general import *

class Match:

    def loadMatch(projID, tourID, stageID):
        navtype = 'dashboard'
        tournamentName = retrieveDashboardNavName(tourID)
    
        try:
            with dbConnect.engine.connect() as conn:

                query = ""
                
            return render_template('stageMatch.html', navtype=navtype, tournamentName=tournamentName, projID=projID, tourID=tourID, stageID = stageID)
        except Exception as e:
            flash('Oops, an error has occured.', 'error')
            print(f"Error details: {e}")
            return render_template('stageMatch.html', navtype=navtype, tournamentName=tournamentName, projID=projID, tourID=tourID, stageID = stageID)
    
    def configureMatch():
        return
    
    def deleteMatch():
        return
    
