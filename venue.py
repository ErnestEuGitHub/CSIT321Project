from flask import Flask, render_template, session, request, flash, jsonify, url_for, redirect
from database import dbConnect
from sqlalchemy import text
from datetime import datetime

def venue():
    with dbConnect.engine.connect() as conn:

        query = "SELECT * from matches LEFT JOIN venue ON matches.venueID = venue.venueID WHERE matchID = 1"
        getMatchDetails = conn.execute(text(query))
        matchfetchDetails = getMatchDetails.fetchall()
        matchDetails = [row._asdict() for row in matchfetchDetails]

        matchstart = matchDetails[0]["startTime"]
        matchend = matchDetails[0]["endTime"]
        currentvenueID = matchDetails[0]["venueID"]
        currentvenueName = matchDetails[0]["venueName"]

        print('matchstart: ', matchstart)
        print('matchend: ', matchend)

        if matchstart is None or matchend is None:
            query = "SELECT * from venue"
            getVenues = conn.execute(text(query))
            venuelist = getVenues.fetchall()

            return render_template('venuetest.html', venuelistFiltered=venuelist, currentvenueID=currentvenueID, currentvenueName=currentvenueName, matchstart=matchstart, matchend=matchend)

        else:
            query = "SELECT matchID, venueID FROM matches WHERE (:matchstart >= matches.startTime AND :matchend <= matches.endTime) OR (:matchstart <= matches.startTime AND :matchend >= matches.endTime) OR (:matchstart >= matches.startTime AND :matchstart <= matches.endTime) OR (:matchend >= matches.startTime AND :matchend <= matches.endTime) UNION SELECT exEventName, venueID FROM venueExtEvent WHERE (:matchstart >= venueExtEvent.startDateTime AND :matchend <= venueExtEvent.endDateTime) OR (:matchstart <= venueExtEvent.startDateTime AND :matchend >= venueExtEvent.endDateTime) OR (:matchstart >= venueExtEvent.startDateTime AND :matchstart <= venueExtEvent.endDateTime) OR (:matchend >= venueExtEvent.startDateTime AND :matchend <= venueExtEvent.endDateTime)"
            inputs = {'matchstart': matchstart, 'matchend': matchend}
            getUnavailableVenues = conn.execute(text(query), inputs)
            unavailableVenuesfetch = getUnavailableVenues.fetchall()

            unavailableVenuesListDict = [row._asdict() for row in unavailableVenuesfetch]
            venueIDs = [row['venueID'] for row in unavailableVenuesListDict]
            venueIDs = [venueID for venueID in venueIDs if venueID is not None]
            unavailableVenueIDs = set(venueIDs)
            
            # print('VenueIDs are: ', venueIDs)
            # print('uniqueVenueIDs are: ', unavailableVenueIDs)

            query = "SELECT * from venue"
            getVenues = conn.execute(text(query))
            venuelist = getVenues.fetchall()

            # print('venuelist: ',venuelist)
            
            venuelistFiltered = [venue for venue in venuelist if venue[0] not in unavailableVenueIDs]

            return render_template('venuetest.html', venuelistFiltered=venuelistFiltered, currentvenueID=currentvenueID, currentvenueName=currentvenueName, matchstart=matchstart, matchend=matchend)



        # print(matchDetails)
        # print('Matchstart:', matchstart)
        # print('Matchend:', matchend)
        # print('Current Venue ID:', currentvenueID)
        

    #sql command for later to check for venues and facilites that overlaps with the dates
    # SELECT matchID, venueID FROM matches WHERE ('2024-02-03 12:00:00' >= matches.startTime AND '2024-02-05 12:00:00' <= matches.endTime) OR (matches.endTime >= '2024-02-03 12:00:00' OR matches.startTime <= '2024-02-05 12:00:00') UNION SELECT exEventName, venueID FROM venueExtEvent WHERE ('2024-02-03 12:00:00' >= venueExtEvent.startDateTime AND '2024-02-05 12:00:00' <= venueExtEvent.endDateTime) OR (venueExtEvent.endDateTime >= '2024-02-03 12:00:00' OR venueExtEvent.startDateTime <= '2024-02-05 12:00:00');
