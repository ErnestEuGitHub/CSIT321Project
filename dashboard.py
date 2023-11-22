from flask import render_template, request, flash, session
from database import dbConnect
import bcrypt
from sqlalchemy import text

def dashboard():
    return render_template('dashboard.html')