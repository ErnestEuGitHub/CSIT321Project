from flask import render_template, request, flash, session, url_for, redirect
from database import dbConnect
from sqlalchemy import text
from datetime import datetime

def settings(tourID):
    if request.method == "POST":
        identifier = request.form.get("formIdentifier")

        tourName = request.form.get("tourName")
        tourSize = request.form.get("tourSize")
        startDate = request.form.get("startDate")
        endDate = request.form.get("endDate")
        gender = request.form.get("gender")
        sport = request.form.get("sport")
        format = request.form.get("format")

        generalDesc = request.form.get("generalDesc")
        rules = request.form.get("rules")
        prize = request.form.get("prize")

        contact = request.form.get("contact")

        with dbConnect.engine.connect() as conn:
            query = "SELECT * FROM sports"
            result = conn.execute(text(query))
            rows = result.fetchall()

            sportsOptions = [row._asdict() for row in rows]

        if not tourName:
            flash('Please fill in a tournament name!', 'error')
            return render_template('settings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact)
        elif len(tourName) > 100:
            flash('Please keep tournament name less than 100 characters!', 'error')
            return render_template('settings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact)
        elif not tourSize:
            flash('Please Enter a minimum participation size!', 'error')
            return render_template('settings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact)
        elif int(tourSize) > 10000:
            flash('Please enter participant size from 1-10,000!', 'error')
            return render_template('settings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact)
        elif int(tourSize) < 0:
            flash('Please enter participant size from 1-10,000!', 'error')
            return render_template('settings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact)
        elif not format:
            flash('That is not a valid format for the sport!', 'error')
            return render_template('settings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact)
        elif not endDate or not startDate:
            flash('Start or End Dates are not filled!', 'error')
            return render_template('settings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact)
        elif endDate < startDate:
            flash('End Date cannot be earlier than Start Date!', 'error')
            return render_template('settings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact)
        else:
            if identifier == "general":
                try:
                    with dbConnect.engine.connect() as conn:
                        query = "SELECT * FROM sportsformats JOIN formats ON sportsformats.formatID = formats.formatID WHERE sportID = :sport AND formatName = :format"
                        inputs = {'sport': sport, 'format': format}
                        getsfID = conn.execute(text(query), inputs)
                        rows = getsfID.fetchall()
                        formatID = rows[0][2]

                        query = "UPDATE tournaments SET tourName = :tourName, tourSize = :tourSize, startDate = :startDate, endDate = :endDate, gender = :gender, sportID = :sportID, formatID = :formatID WHERE tourID = :tourID"
                        inputs = {'tourName': tourName, 'tourSize': tourSize, 'startDate': startDate, 'endDate': endDate, 'gender':gender, 'sportID':sport, 'formatID':formatID, 'tourID':tourID}
                        updateGeneralInfo = conn.execute(text(query), inputs)
                
                    flash('General Information Updated!', 'success')
                
                except Exception as e:
                    flash('Oops, an error has occured.', 'error')
                    print(f"Error details: {e}")

            elif identifier == "details":

                try:
                    with dbConnect.engine.connect() as conn:
                        query = "UPDATE generalInfo SET generalInfoDesc = :generalDesc, rules = :rules, prize = :prize WHERE tourID = :tourID"
                        inputs = {'generalDesc':generalDesc, 'rules':rules, 'prize':prize, 'tourID':tourID}
                        updateDetails = conn.execute(text(query), inputs)
                
                    flash('Details Updated!', 'success')
                
                except Exception as e:
                    flash('Oops, an error has occured.', 'error')
                    print(f"Error details: {e}")

            elif identifier == "contact":

                try:
                    with dbConnect.engine.connect() as conn:
                        query = "UPDATE generalInfo SET contact = :contact WHERE tourID = :tourID"
                        inputs = {'contact':contact, 'tourID':tourID}
                        updateDetails = conn.execute(text(query), inputs)
                
                    flash('Contact Updated!', 'success')
                
                except Exception as e:
                    flash('Oops, an error has occured.', 'error')
                    print(f"Error details: {e}")

            return redirect(url_for('loadsettings', tourID=tourID))


    else:
        with dbConnect.engine.connect() as conn:
            #getting general tab information
            query = "SELECT * FROM sports"
            result = conn.execute(text(query))
            rows = result.fetchall()

            sportsOptions = [row._asdict() for row in rows]
            
            query = "SELECT tournaments.tourName, tournaments.tourSize, tournaments.startDate, tournaments.endDate, tournaments.gender, tournaments.sportID, formats.formatName FROM tournaments JOIN formats ON tournaments.formatID = formats.formatID WHERE tournaments.tourID = :tourID"
            inputs = {'tourID': tourID}
            result = conn.execute(text(query), inputs)
            rows = result.fetchall()

            tourName = rows[0][0]
            tourSize = rows[0][1]
            startDate = rows[0][2]
            endDate = rows[0][3]
            gender = rows[0][4]
            sport = rows[0][5]
            format = rows[0][6]

            #getting details and contact information
            query = "SELECT * FROM generalInfo WHERE tourID = :tourID"
            inputs = {'tourID': tourID}
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
    
        return render_template('settings.html', tourName=tourName, tourSize=tourSize, startDate=startDate, endDate=endDate, gender=gender, sport=int(sport), format=format, sportlist=sportsOptions, generalDesc=generalDesc, rules=rules, prize=prize, contact=contact)