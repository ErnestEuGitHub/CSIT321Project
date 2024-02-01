from flask import Flask, render_template, session, request, flash, jsonify, url_for, redirect
from database import dbConnect
from sqlalchemy import text
from datetime import datetime

def venue():
    with dbConnect.engine.connect() as conn:

        query = "SELECT * FROM venue"
        getVenues = conn.execute(text(query))
        venuelist = getVenues.fetchall()

        query = "SELECT matches.*, venue.venueName, (SELECT facilitiyName FROM venueFacilities WHERE facilityID = matches.facilityID LIMIT 1) AS facilityName FROM matches LEFT JOIN venue ON matches.venueID = venue.venueID WHERE matchID = 1;"
        getMatchDetails = conn.execute(text(query))
        matchDetails = getMatchDetails.fetchall()
        matchstart = matchDetails[0][1]
        matchend = matchDetails[0][2]
        currentvenueID = matchDetails[0][3]

        print(matchDetails)
        print('Matchstart:', matchstart)
        print('Matchend:', matchend)
        print('Current Venue ID:', currentvenueID)
        

    #sql command for later to check for venues and facilites that overlaps with the dates
    # SELECT matchID, venueID, facilityID FROM matches WHERE ('2024-02-03 12:00:00' >= matches.startTime AND '2024-02-05 12:00:00' <= matches.endTime) OR (matches.endTime >= '2024-02-03 12:00:00' OR matches.startTime <= '2024-02-05 12:00:00') UNION SELECT exEventName, venueID, facilityID FROM venueExtEvent WHERE ('2024-02-03 12:00:00' >= venueExtEvent.startDateTime AND '2024-02-05 12:00:00' <= venueExtEvent.endDateTime) OR (venueExtEvent.endDateTime >= '2024-02-03 12:00:00' OR venueExtEvent.startDateTime <= '2024-02-05 12:00:00');

    return render_template('venuetest.html', venuelist=venuelist, currentvenueID=currentvenueID, matchstart=matchstart, matchend=matchend)