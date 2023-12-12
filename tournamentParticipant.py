from flask import render_template, request, flash, session
from database import dbConnect
import bcrypt
from sqlalchemy import text

def tournamentParticipant():
    return render_template('tournamentParticipant.html')