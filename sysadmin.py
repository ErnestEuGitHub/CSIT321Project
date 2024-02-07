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
    
def tourAdmin():
    navtype = 'sysAdmin'
    with dbConnect.engine.connect() as conn:
        query = "SELECT * FROM tournaments"
        result = conn.execute(text(query))
        rows = result.fetchall()
        tournamentslist = [row._asdict() for row in rows]

    return render_template('sysAdminTournaments.html', navtype=navtype, tournamentslist=tournamentslist)

def createTourAdmin():
    navtype = 'sysAdmin'

    if request.method == "POST":

        with dbConnect.engine.connect() as conn:
            query = "SELECT * FROM sports"
            result = conn.execute(text(query))
            rows = result.fetchall()

            sportsOptions = [row._asdict() for row in rows]

            query = "SELECT * FROM users WHERE profileID = 1"
            result = conn.execute(text(query))
            rows = result.fetchall()
            organiserlist = [row._asdict() for row in rows]

            query = "SELECT * FROM projects"
            result = conn.execute(text(query))
            rows = result.fetchall()
            projectslist = [row._asdict() for row in rows]

        tourName = request.form.get("tourName")
        tourSize = request.form.get("tourSize")
        startDate = request.form.get("startDate")
        endDate = request.form.get("endDate")
        gender = request.form.get("gender")
        sport = request.form.get("sport")
        format = request.form.get("format")
        tourImage = request.files.get("tourImage")
        bannerImage = request.files.get("bannerImage")
        status = int(request.form.get("status"))
        owner = int(request.form.get("owner"))
        projID = int(request.form.get("project"))

        if not sport:
            flash('Please select a sport!', 'error')
            return render_template('sysAdminCreateTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=sport, format=format, sportlist=sportsOptions, status=status, owner=owner, projID=projID, organiserlist=organiserlist, projectslist=projectslist)
        elif not tourName:
            flash('Please fill in a tournament name!', 'error')
            return render_template('sysAdminCreateTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, status=status, owner=owner, projID=projID, organiserlist=organiserlist, projectslist=projectslist)
        elif len(tourName) > 100:
            flash('Please keep tournament name less than 100 characters!', 'error')
            return render_template('sysAdminCreateTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, status=status, owner=owner, projID=projID, organiserlist=organiserlist, projectslist=projectslist)
        elif not tourSize:
            flash('Please Enter a minimum participation size!', 'error')
            return render_template('sysAdminCreateTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, status=status, owner=owner, projID=projID, organiserlist=organiserlist, projectslist=projectslist)
        elif int(tourSize) > 10000:
            flash('Please enter participant size from 1-10,000!', 'error')
            return render_template('sysAdminCreateTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, status=status, owner=owner, projID=projID, organiserlist=organiserlist, projectslist=projectslist)
        elif int(tourSize) < 0:
            flash('Please enter participant size from 1-10,000!', 'error')
            return render_template('sysAdminCreateTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, status=status, owner=owner, projID=projID, organiserlist=organiserlist, projectslist=projectslist)
        elif not format:
            flash('That is not a valid format for the sport!', 'error')
            return render_template('sysAdminCreateTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, status=status, owner=owner, projID=projID, organiserlist=organiserlist, projectslist=projectslist)
        elif not endDate or not startDate:
            flash('Start or End Dates are not filled!', 'error')
            return render_template('sysAdminCreateTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, status=status, owner=owner, projID=projID, organiserlist=organiserlist, projectslist=projectslist)
        elif endDate < startDate:
            flash('End Date cannot be earlier than Start Date!', 'error')
            return render_template('sysAdminCreateTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, status=status, owner=owner, projID=projID, organiserlist=organiserlist, projectslist=projectslist)
        else:
            startDate = datetime.strptime(startDate, "%Y-%m-%d")
            endDate = datetime.strptime(endDate, "%Y-%m-%d")

            try:
                with dbConnect.engine.connect() as conn:
                    query = "SELECT * FROM sportsformats JOIN formats ON sportsformats.formatID = formats.formatID WHERE sportID = :sport AND formatName = :format"
                    inputs = {'sport': sport, 'format': format}
                    getsfID = conn.execute(text(query), inputs)
                    rows = getsfID.fetchall()
                    formatID = rows[0][2]

                    query = "INSERT INTO generalInfo SET generalInfoDesc = default;"
                    createNewGeneralInfo = conn.execute(text(query))
                    getID = createNewGeneralInfo.lastrowid

                    query = "INSERT INTO tournaments (tourName, tourSize, startDate, endDate, gender, projID, sportID, formatID, statusID, userID, generalInfoID, tourImageID, tourBannerID) VALUES (:tourName, :tourSize, :startDate, :endDate, :gender, :projID, :sportID, :formatID, :statusID, :userID, :generalInfoID, :tourImageID, :tourBannerID)"
                    # file_id = upload_to_google_drive(tourImage, bannerImage, tourName)
                    inputs = {'tourName': tourName, 'tourSize': tourSize, 'startDate': startDate, 'endDate': endDate, 'gender':gender, 'projID':projID, 'sportID':sport, 'formatID':formatID, 'statusID':status, 'userID':owner, 'generalInfoID':getID, 'tourImageID': None, 'tourBannerID': None}
                    createTournament = conn.execute(text(query), inputs)
                
                flash('Tournament Created!', 'success')
                return render_template('sysAdminCreateTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=sport, format=format, sportlist=sportsOptions, status=status, owner=owner, projID=projID)
                    
            except Exception as e:
                flash('Oops, an error has occured.', 'error')
                print(f"Error details: {e}")
                return render_template('sysAdminCreateTour.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=sport, format=format, sportlist=sportsOptions, status=status, owner=owner, projID=projID)

    else:           
        #get request:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * FROM sports"
            result = conn.execute(text(query))
            rows = result.fetchall()

            sportsOptions = [row._asdict() for row in rows]

            query = "SELECT * FROM users WHERE profileID = 1"
            result = conn.execute(text(query))
            rows = result.fetchall()
            organiserlist = [row._asdict() for row in rows]

            query = "SELECT * FROM projects"
            result = conn.execute(text(query))
            rows = result.fetchall()
            projectslist = [row._asdict() for row in rows]

    return render_template('sysAdminCreateTour.html', navtype=navtype, sportlist=sportsOptions, organiserlist=organiserlist, projectslist=projectslist)

def TourSettingsAdmin(tourID):
    navtype = 'sysAdmin'

    if request.method == "POST":
        identifier = request.form.get("formIdentifier")
        action = request.form.get('action')

        tourName = request.form.get("tourName")
        tourSize = request.form.get("tourSize")
        startDate = request.form.get("startDate")
        endDate = request.form.get("endDate")
        gender = request.form.get("gender")
        sport = request.form.get("sport")
        format = request.form.get("format")
        status = int(request.form.get("status"))
        owner = int(request.form.get("owner"))
        projID = int(request.form.get("project"))
        tourImage = request.files.get("tourImage")
        bannerImage = request.files.get("bannerImage")

        # if action == 'delete':
        #     print('action form delete triggered!')
        #     return redirect(url_for('loadSuspendTour', projID=projID, tourID=tourID))
                
        with dbConnect.engine.connect() as conn:
            query = "SELECT * FROM sports"
            result = conn.execute(text(query))
            rows = result.fetchall()

            sportsOptions = [row._asdict() for row in rows]

            query = "SELECT * FROM users WHERE profileID = 1"
            result = conn.execute(text(query))
            rows = result.fetchall()
            organiserlist = [row._asdict() for row in rows]

            query = "SELECT * FROM projects"
            result = conn.execute(text(query))
            rows = result.fetchall()
            projectslist = [row._asdict() for row in rows]

            if not sport:
                flash('Please select a sport!', 'error')
                return render_template('sysAdminTourSettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=sport, format=format, sportlist=sportsOptions, status=status, owner=owner, projID=projID, organiserlist=organiserlist, projectslist=projectslist, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact)
            elif not tourName:
                flash('Please fill in a tournament name!', 'error')
                return render_template('sysAdminTourSettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, status=status, owner=owner, projID=projID, organiserlist=organiserlist, projectslist=projectslist, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact)
            elif len(tourName) > 100:
                flash('Please keep tournament name less than 100 characters!', 'error')
                return render_template('sysAdminTourSettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, status=status, owner=owner, projID=projID, organiserlist=organiserlist, projectslist=projectslist, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact)
            elif not tourSize:
                flash('Please Enter a minimum participation size!', 'error')
                return render_template('sysAdminTourSettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, status=status, owner=owner, projID=projID, organiserlist=organiserlist, projectslist=projectslist, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact)
            elif int(tourSize) > 10000:
                flash('Please enter participant size from 1-10,000!', 'error')
                return render_template('sysAdminTourSettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, status=status, owner=owner, projID=projID, organiserlist=organiserlist, projectslist=projectslist, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact)
            elif int(tourSize) < 0:
                flash('Please enter participant size from 1-10,000!', 'error')
                return render_template('sysAdminTourSettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, status=status, owner=owner, projID=projID, organiserlist=organiserlist, projectslist=projectslist, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact)
            elif not format:
                flash('That is not a valid format for the sport!', 'error')
                return render_template('sysAdminTourSettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, status=status, owner=owner, projID=projID, organiserlist=organiserlist, projectslist=projectslist, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact)
            elif not endDate or not startDate:
                flash('Start or End Dates are not filled!', 'error')
                return render_template('sysAdminTourSettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, status=status, owner=owner, projID=projID, organiserlist=organiserlist, projectslist=projectslist, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact)
            elif endDate < startDate:
                flash('End Date cannot be earlier than Start Date!', 'error')
                return render_template('sysAdminTourSettings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, status=status, owner=owner, projID=projID, organiserlist=organiserlist, projectslist=projectslist, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact)
            else:
                # startDate = datetime.strptime(startDate, "%Y-%m-%d")
                # endDate = datetime.strptime(endDate, "%Y-%m-%d")
                try:
                    query = "SELECT * FROM sportsformats JOIN formats ON sportsformats.formatID = formats.formatID WHERE sportID = :sport AND formatName = :format"
                    inputs = {'sport': sport, 'format': format}
                    getsfID = conn.execute(text(query), inputs)
                    rows = getsfID.fetchall()
                    formatID = rows[0][2]

                    query = "UPDATE tournaments SET tourName = :tourName, tourSize = :tourSize, startDate = :startDate, endDate = :endDate, gender = :gender, projID = :projID, sportID = :sportID, formatID = :formatID, statusID = :statusID, userID = :userID WHERE tourID = :tourID"
                    inputs = {'tourName': tourName, 'tourSize': tourSize, 'startDate': startDate, 'endDate': endDate, 'gender':gender, 'projID':projID, 'sportID':sport, 'formatID':formatID, 'statusID':status, 'userID':owner, 'tourID':tourID}
                    updateGeneralInfo = conn.execute(text(query), inputs)
                
                except Exception as e:
                    flash('Oops, an error has occured in updating general details tab.', 'error')
                    print(f"Error details: {e}")

            generalDesc = request.form.get("generalDesc")
            rules = request.form.get("rules")
            prize = request.form.get("prize")

            try:
                query = "SELECT generalInfoID from tournaments WHERE tourID = :tourID"
                inputs = {'tourID':tourID}
                getGeneralInfoID = conn.execute(text(query), inputs)
                rows = getGeneralInfoID.fetchall()
                generalInfoID = rows[0][0]

                query = "UPDATE generalInfo SET generalInfoDesc = :generalDesc, rules = :rules, prize = :prize WHERE generalInfoID = :generalInfoID"
                inputs = {'generalDesc':generalDesc, 'rules':rules, 'prize':prize, 'generalInfoID':generalInfoID}
                updateDetails = conn.execute(text(query), inputs)
            
            except Exception as e:
                    flash('Oops, an error has occured in updating details tab.', 'error')
                    print(f"Error details: {e}")


            contact = request.form.get("contact")
            try:
                with dbConnect.engine.connect() as conn:
                    query = "UPDATE generalInfo SET contact = :contact WHERE generalInfoID = :generalInfoID"
                    inputs = {'contact':contact, 'generalInfoID':generalInfoID}
                    updateDetails = conn.execute(text(query), inputs)
            
                # flash('Contact Updated!', 'success')
            
            except Exception as e:
                flash('Oops, an error has occured in updating contact tab.', 'error')
                print(f"Error details: {e}")

            flash('Tournament Details Updated!', 'success')
            return redirect(url_for('loadTourSettingsAdmin', tourID=tourID))


    else:
        with dbConnect.engine.connect() as conn:
            query = "SELECT * FROM sports"
            result = conn.execute(text(query))
            rows = result.fetchall()

            sportsOptions = [row._asdict() for row in rows]

            query = "SELECT * FROM users WHERE profileID = 1"
            result = conn.execute(text(query))
            rows = result.fetchall()
            organiserlist = [row._asdict() for row in rows]

            query = "SELECT * FROM projects"
            result = conn.execute(text(query))
            rows = result.fetchall()
            projectslist = [row._asdict() for row in rows]
            
            #getting general tab information
            query = "SELECT tournaments.tourName, tournaments.tourSize, tournaments.startDate, tournaments.endDate, tournaments.gender, tournaments.projID, tournaments.sportID, formats.formatName, tournaments.statusID, tournaments.userID, tournaments.generalInfoID FROM tournaments JOIN formats ON tournaments.formatID = formats.formatID WHERE tournaments.tourID = :tourID"
            inputs = {'tourID': tourID}
            result = conn.execute(text(query), inputs)
            rows = result.fetchall()
            tourDetails = [row._asdict() for row in rows]

            tourName = tourDetails[0]['tourName']
            tourSize = tourDetails[0]['tourSize']
            startDate = tourDetails[0]['startDate']
            endDate = tourDetails[0]['endDate']
            gender = tourDetails[0]['gender']
            sport = tourDetails[0]['sportID']
            format = tourDetails[0]['formatName']
            status = tourDetails[0]['statusID']
            generalInfoID = tourDetails[0]['generalInfoID']
            projID = tourDetails[0]['projID']
            owner = tourDetails[0]['userID']

            if status == 5:
                return redirect(url_for('loadSuspendTour', projID=projID, tourID=tourID))

            #getting details and contact information
            query = "SELECT * FROM generalInfo WHERE generalInfoID = :generalInfoID"
            inputs = {'generalInfoID': generalInfoID}
            result = conn.execute(text(query), inputs)
            rows = result.fetchall()

            if rows:
                generalDesc = rows[0][1]
                rules = rows[0][2]
                prize = rows[0][3]
                contact = rows[0][4]
            else: 
                generalDesc = ""
                rules = ""
                prize = ""
                contact = ""

            #getting details and contact information
            query = "SELECT * FROM generalInfo WHERE generalInfoID = :generalInfoID"
            inputs = {'generalInfoID': generalInfoID}
            result = conn.execute(text(query), inputs)
            rows = result.fetchall()

            if rows:
                generalDesc = rows[0][1]
                rules = rows[0][2]
                prize = rows[0][3]
                contact = rows[0][4]
            else: 
                generalDesc = ""
                rules = ""
                prize = ""
                contact = ""

        return render_template('sysAdminTourSettings.html', navtype=navtype, sportlist=sportsOptions, organiserlist=organiserlist, projectslist=projectslist, tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, status=status, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact, owner=owner, project=projID, tourID=tourID)
