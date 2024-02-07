from flask import render_template, request, flash, session, url_for, redirect
from database import dbConnect
from sqlalchemy import text
from datetime import datetime
from general import *

class Projects:

    #Organiser Projects Page or Home Page
    def home():
        projects = updateNavProjects()
        # print("projects:", projects)
        #for navbar
        navtype = 'project'

        return render_template('home.html', projects=projects, navtype=navtype)

    #Create Project
    def createProj():
        #for navbar
        navtype = 'project'
        userID = session["id"]

        if request.method == "POST":
            projName = request.form.get("projName")
            startDate = request.form.get("startDate")
            endDate = request.form.get("endDate")

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
                        query = "INSERT INTO projects (projName, projStartDate, projEndDate, userID, statusID) VALUES (:projName, :projStartDate, :projEndDate, :userID, 4)"
                        inputs = {'projName':projName, 'projStartDate':startDate, 'projEndDate':endDate, 'userID':userID}
                        createProject = conn.execute(text(query), inputs)

                    userID = session["id"]
                    projects = updateNavProjects()
                    flash('Project Created!', 'success')
                    return render_template('createProj.html', navtype=navtype, projects=projects)
                
                except Exception as e:
                    projects = updateNavProjects()
                    flash('Oops, an error has occured.', 'error')
                    print(f"Error details: {e}")
                return render_template('createProj.html', projName=projName, startDate=startDate, endDate=endDate, navtype=navtype, projects=projects)
                
        else:
            projects = updateNavProjects()
            return render_template('createProj.html', navtype=navtype, projects=projects)
        
    def ProjSettings(projID):
        #for navbar
        navtype = 'project'
        projects = updateNavProjects()

        if request.method == "POST":

            action = request.form.get('action')
            if action == 'delete':
                return redirect(url_for('loadSuspendProj', projID=projID))
            else:
                projName = request.form.get("projName")
                startDate = request.form.get("startDate")
                endDate = request.form.get("endDate")
                getstatus = request.form.get("status")
                status = int(getstatus)

                if not projName:
                    flash('Please fill in a project name!', 'error')
                    return render_template('projSettings.html', projName=projName, startDate=startDate, endDate=endDate, projID=projID, projects=projects, status=status)
                
                elif not endDate or not startDate:
                    flash('Start or End Dates are not filled!', 'error')
                    return render_template('projSettings.html', projName=projName, startDate=startDate, endDate=endDate, projID=projID, projects=projects, status=status)

                elif endDate < startDate:
                    flash('End Date cannot be earlier than Start Date!', 'error')
                    return render_template('projSettings.html', projName=projName, startDate=startDate, endDate=endDate, projID=projID, projects=projects, status=status)

                else:
                    #convertion to correct types placed here after checking no empty strings
                    startDate = datetime.strptime(startDate, "%Y-%m-%d")
                    endDate = datetime.strptime(endDate, "%Y-%m-%d")

                    try:
                        with dbConnect.engine.connect() as conn:
                            query = "UPDATE projects SET projName = :projName,  projStartDate = :projStartDate, projEndDate = :projEndDate, statusID = :statusID WHERE projID = :projID"
                            inputs = {'projName':projName, 'projStartDate':startDate, 'projEndDate':endDate, 'projID':projID, 'statusID':status}
                            updateProject = conn.execute(text(query), inputs)

                            projects = updateNavProjects()
                            flash('Project Updated!', 'success')
                            return redirect(url_for('loadProjSettings', projID=projID))
                    
                    except Exception as e:
                            flash('Oops, an error has occured.', 'error')
                            print(f"Error details: {e}")
                            return render_template('projSettings.html', projName=projName, startDate=startDate, endDate=endDate, projID=projID, projects=projects, status=status)
        else:
            with dbConnect.engine.connect() as conn:
                query = "SELECT * FROM projects WHERE projID = :projID"
                inputs = {'projID': projID}
                getProj = conn.execute(text(query), inputs)
                rows = getProj.fetchall()

                projName = rows[0][1]
                startDate = rows[0][2]
                endDate = rows[0][3]
                status = rows[0][6]

                if status == 5:
                    return redirect(url_for('loadSuspendProj', projID=projID))
                else:
                    return render_template('projSettings.html', projName=projName, startDate=startDate, endDate=endDate, status=status, navtype=navtype, projID=projID, projects=projects)
            
    def SuspendProj(projID):
        #for navbar
        navtype = 'project'
        projects = updateNavProjects()

        if request.method == "POST":
            getstatus = request.form.get("status")
            status = int(getstatus)

            if status == 5:
                return redirect(url_for('loadSuspendProj', projID=projID))
            
            try:
                with dbConnect.engine.connect() as conn:
                    query = "UPDATE projects SET statusID = :statusID WHERE projID = :projID"
                    inputs = {'statusID':status,'projID':projID}
                    updateStatus = conn.execute(text(query), inputs)

                    projects = updateNavProjects()
                    flash('Status Updated!', 'success')
                    return redirect(url_for('loadProjSettings', projID=projID))
        
            except Exception as e:
                flash('Oops, an error has occured while changing status for project.', 'error')
                print(f"Error details: {e}")
                return render_template('suspendProj.html', projName=projName, startDate=startDate, endDate=endDate, status=status, navtype=navtype, projID=projID, projects=projects)

        else:
            try:
                with dbConnect.engine.connect() as conn:
                    query = "UPDATE projects SET statusID = 5 WHERE projID = :projID"
                    inputs = {'projID':projID}
                    endProject = conn.execute(text(query), inputs)

                    query = "SELECT * FROM projects WHERE projID = :projID"
                    inputs = {'projID': projID}
                    getProj = conn.execute(text(query), inputs)
                    rows = getProj.fetchall()

                    projName = rows[0][1]
                    startDate = rows[0][2]
                    endDate = rows[0][3]
                    status = rows[0][6]

                    projects = updateNavProjects()
                    flash('This project is Suspended!', 'error')
                    return render_template('suspendProj.html', projName=projName, startDate=startDate, endDate=endDate, status=status, navtype=navtype, projID=projID, projects=projects)
                    
            except Exception as e:
                flash('Oops, an error has occured while ending project.', 'error')
                print(f"Error details: {e}")
                return render_template('suspendProj.html', projID=projID, projects=projects)