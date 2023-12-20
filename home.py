from flask import render_template, session
from database import dbConnect
from sqlalchemy import text
from datetime import datetime

def home():
    with dbConnect.engine.connect() as conn:
        query = "SELECT * FROM projects WHERE userID = :userID;"
        inputs = {'userID': session["id"]}
        getprojs = conn.execute(text(query), inputs)
        rows = getprojs.fetchall()

        projects = [row._asdict() for row in rows]

        session["projnav"] = projects
        #for navbar
        navtype = 'project'

    return render_template('home.html', projects=projects, navtype=navtype)