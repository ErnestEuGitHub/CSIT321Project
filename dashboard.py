from flask import render_template, request, flash, session
from database import dbConnect
import bcrypt
from sqlalchemy import text

def dashboard():
    if request.method == "POST":
        # Handle the POST request, perform some action
        return render_template('dashboard.html', message="Form submitted successfully")
    else:
        return render_template('dashboard.html')