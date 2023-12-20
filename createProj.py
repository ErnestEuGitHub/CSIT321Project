from flask import render_template, request, flash, session
from database import dbConnect
from sqlalchemy import text
from datetime import datetime

def createProj():
    if request.method == "POST":
        projName = request.form.get("projName")
        startDate = request.form.get("startDate")
        endDate = request.form.get("endDate")
        userID = session["id"]

        if not projName:
            flash('Please fill in a project name!', 'error')
            return render_template('createProj.html', projName=projName, startDate=startDate, endDate=endDate)
        
        elif not endDate or not startDate:
            flash('Start or End Dates are not filled!', 'error')
            return render_template('createProj.html', projName=projName, startDate=startDate, endDate=endDate)

        elif endDate < startDate:
            flash('End Date cannot be earlier than Start Date!', 'error')
            return render_template('createProj.html', projName=projName, startDate=startDate, endDate=endDate)

        else:
            #convertion to correct types placed here after checking no empty strings
            startDate = datetime.strptime(startDate, "%Y-%m-%d")
            endDate = datetime.strptime(endDate, "%Y-%m-%d")

            try:
                with dbConnect.engine.connect() as conn:
                    query = "INSERT INTO projects (projName, projStartDate, projEndDate, userID) VALUES (:projName, :projStartDate, :projEndDate, :userID)"
                    inputs = {'projName': projName, 'projStartDate': startDate, 'projEndDate': endDate, 'userID':userID}
                    createProject = conn.execute(text(query), inputs)

                    #for navbar
                    query = "SELECT * FROM projects WHERE userID = :userID;"
                    inputs = {'userID': session["id"]}
                    getprojs = conn.execute(text(query), inputs)
                    rows = getprojs.fetchall()

                    projects = [row._asdict() for row in rows]

                    session["projnav"] = projects
                    navtype = 'project'

                flash('Project Created!', 'success')
                return render_template('createProj.html', navtype=navtype, projects=projects)
            
            except Exception as e:
                flash('Oops, an error has occured.', 'error')
                print(f"Error details: {e}")
            return render_template('createProj.html', projName=projName, startDate=startDate, endDate=endDate, navtype=navtype, projects=session["projnav"])
            
    else:
        # for navbar
        navtype = 'project'
        return render_template('createProj.html', navtype=navtype, projects=session["projnav"])