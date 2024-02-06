from flask import render_template, request, flash, session, url_for, redirect

from database import dbConnect
from sqlalchemy import text
from general import *
from datetime import datetime

from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO

def sysAdminHome():
    navtype = 'sysAdmin'
            
    return render_template('sysAdminHome.html', navtype=navtype)

def projAdmin():
    navtype = 'sysAdmin'
    with dbConnect.engine.connect() as conn:
        query = "SELECT * FROM projects"
        result = conn.execute(text(query))
        rows = result.fetchall()
        projectslist = [row._asdict() for row in rows]

    return render_template('sysAdminProjects.html', navtype=navtype, projectslist=projectslist)

def createProjAdmin():
    navtype = 'sysAdmin'

    if request.method == "POST":
        with dbConnect.engine.connect() as conn:
            query = "SELECT * FROM users WHERE profileID = 1"
            result = conn.execute(text(query))
            rows = result.fetchall()
            organiserlist = [row._asdict() for row in rows]

        projName = request.form.get("projName")
        startDate = request.form.get("startDate")
        endDate = request.form.get("endDate")
        projImage = request.files.get("projImage")
        status = int(request.form.get("status"))
        owner = int(request.form.get("owner"))

        if not projName:
            flash('Please fill in a project name!', 'error')
            return render_template('sysAdminCreateProj.html', projName=projName, startDate=startDate, endDate=endDate, status=status, owner=owner, organiserlist=organiserlist)
        
        elif not endDate or not startDate:
            flash('Start or End Dates are not filled!', 'error')
            return render_template('sysAdminCreateProj.html', projName=projName, startDate=startDate, endDate=endDate, status=status, owner=owner, organiserlist=organiserlist)

        elif endDate < startDate:
            flash('End Date cannot be earlier than Start Date!', 'error')
            return render_template('sysAdminCreateProj.html', projName=projName, startDate=startDate, endDate=endDate, status=status, owner=owner, organiserlist=organiserlist)
        
        else:
            #convertion to correct types placed here after checking no empty strings
            startDate = datetime.strptime(startDate, "%Y-%m-%d")
            endDate = datetime.strptime(endDate, "%Y-%m-%d")

            try:
                with dbConnect.engine.connect() as conn:
                    query = "INSERT INTO projects (projName, projStartDate, projEndDate, userID, statusID, projImageID) VALUES (:projName, :projStartDate, :projEndDate, :userID, :statusID, :projImageID)"
                    # file_id = upload_to_google_drive(projImage, projName)
                    inputs = {'projName': projName, 'projStartDate': startDate, 'projEndDate': endDate, 'userID': owner, 'statusID':status, 'projImageID': None}
                    createProject = conn.execute(text(query), inputs)

                # userID = session["id"]
                # projects = updateNavProjects()
                flash('Project Created!', 'success')
                return render_template('sysAdminCreateProj.html', navtype=navtype, organiserlist=organiserlist)
            
            except Exception as e:
                flash('Oops, an error has occured.', 'error')
                print(f"Error details: {e}")
                return render_template('sysAdminCreateProj.html', navtype=navtype, projName=projName, startDate=startDate, endDate=endDate, status=status, owner=owner, organiserlist=organiserlist)


    else:    
        with dbConnect.engine.connect() as conn:
            query = "SELECT * FROM users WHERE profileID = 1"
            result = conn.execute(text(query))
            rows = result.fetchall()
            organiserlist = [row._asdict() for row in rows]

        
        return render_template('sysAdminCreateProj.html', navtype=navtype, organiserlist=organiserlist)

def ProjSettingsAdmin(projID):
    navtype = 'sysAdmin'

    if request.method == "POST":

        with dbConnect.engine.connect() as conn:
            query = "SELECT * FROM users WHERE profileID = 1"
            result = conn.execute(text(query))
            rows = result.fetchall()
            organiserlist = [row._asdict() for row in rows]

        action = request.form.get('action')
        if action == 'delete':
            return redirect(url_for('loadSuspendProj', projID=projID))
        else:
            projName = request.form.get("projName")
            startDate = request.form.get("startDate")
            endDate = request.form.get("endDate")
            projImage = request.files.get("projImage")
            status = int(request.form.get("status"))
            owner = int(request.form.get("owner"))

            if not projName:
                flash('Please fill in a project name!', 'error')
                return render_template('sysAdminCreateProj.html', projName=projName, startDate=startDate, endDate=endDate, status=status, owner=owner, organiserlist=organiserlist)
            
            elif not endDate or not startDate:
                flash('Start or End Dates are not filled!', 'error')
                return render_template('sysAdminCreateProj.html', projName=projName, startDate=startDate, endDate=endDate, status=status, owner=owner, organiserlist=organiserlist)

            elif endDate < startDate:
                flash('End Date cannot be earlier than Start Date!', 'error')
                return render_template('sysAdminCreateProj.html', projName=projName, startDate=startDate, endDate=endDate, status=status, owner=owner, organiserlist=organiserlist)
            
            else:
                #convertion to correct types placed here after checking no empty strings
                startDate = datetime.strptime(startDate, "%Y-%m-%d")
                endDate = datetime.strptime(endDate, "%Y-%m-%d")

                try:
                    with dbConnect.engine.connect() as conn:
                        query = "UPDATE projects SET projName = :projName,  projStartDate = :projStartDate, projEndDate = :projEndDate, userID = :userID, projImageID = :projImageID, statusID = :statusID WHERE projID = :projID"
                        inputs = {'projName':projName, 'projStartDate':startDate, 'projEndDate':endDate, 'userID': owner, 'statusID':status, 'projImageID': None, 'projID':projID}
                        updateProject = conn.execute(text(query), inputs)
                        flash('Project Updated!', 'success')

                        return redirect(url_for('loadProjSettingsAdmin', projID=projID))

                except Exception as e:
                    flash('Oops, an error has occured.', 'error')
                    print(f"Error details: {e}")
                    return render_template('sysAdminProjSettings.html', navtype=navtype, projName=projName, startDate=startDate, endDate=endDate, status=status, owner=owner, organiserlist=organiserlist)
                

    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * FROM users WHERE profileID = 1"
            result = conn.execute(text(query))
            rows = result.fetchall()
            organiserlist = [row._asdict() for row in rows]

            query = "SELECT * FROM projects WHERE projID = :projID"
            inputs = {'projID': projID}
            getProj = conn.execute(text(query), inputs)
            rows = getProj.fetchall()
            projDetails = [row._asdict() for row in rows]

            projName = projDetails[0]['projName']
            startDate = projDetails[0]['projStartDate']
            endDate = projDetails[0]['projEndDate']
            status = projDetails[0]['statusID']
            owner = projDetails[0]['userID']

            if status == 5:
                return redirect(url_for('loadSuspendProj', projID=projID))
        return render_template('sysAdminProjSettings.html', navtype=navtype, organiserlist=organiserlist, projName=projName, startDate=startDate, endDate=endDate, status=status, owner=owner)