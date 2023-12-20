from flask import render_template, request, flash, session
from database import dbConnect
from sqlalchemy import text
from datetime import datetime
from general import *

class Projects:

    #Organiser Projects Page or Home Page
    def home():
        projects = updateNavProjects()
        #for navbar
        navtype = 'project'

        return render_template('home.html', projects=projects, navtype=navtype)

    #Create Project
    def createProj():
        #for navbar
        navtype = 'project'

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
                    userID = session["id"]
                    projects = updateNavProjects(userID)
                    flash('Project Created!', 'success')
                    return render_template('createProj.html', navtype=navtype, projects=projects)
                
                except Exception as e:
                    flash('Oops, an error has occured.', 'error')
                    print(f"Error details: {e}")
                return render_template('createProj.html', projName=projName, startDate=startDate, endDate=endDate, navtype=navtype, projects=session["projnav"])
                
        else:
            return render_template('createProj.html', navtype=navtype, projects=session["projnav"])