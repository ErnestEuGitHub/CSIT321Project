from flask import render_template, request, flash, session
from database import dbConnect
from sqlalchemy import text

def createStructure(tourID):
    if request.method == "POST":

        stageSequence = request.form.get("stageSequence")
        stageName = request.form.get("stageName")
        numberOfParticipants = request.form.get("numberOfParticipants")
        stageFormatID = request.form.get("stageFormat")
        maxGames = request.form.get("maximumNumberOfGames")
        matchFormatID = request.form.get("matchFormat")
        stageStatusID = 1

        if stageFormatID == 1:
             elimFormat = request.form.get("elimFormat")
             tfMatch = request.form.get("34match")
        elif stageFormatID == 2:
             roundFormat = request.form.get("roundFormat")
             winPts = request.form.get("winPoints")
             drawPts = request.form.get("drawPoints")
             lossPts = request.form.get("lossPoints")
             tieBreakers = request.form.get("tieBreakerSelect")
             print(tieBreakers)

        if not maxGames:
             maxGames = stageFormatID

        try:
                # with dbConnect.engine.connect() as conn:

                #     query = "INSERT INTO stages (stageName, stageSequence, stageFormatID, stageStatusID, tourID, numberOfParticipants, maxGames, tfMatch, matchFormatID) VALUES (:stageName, :stageSequence, :stageFormatID, :stageStatusID, :tourID, :numberOfParticipants, :maxGames, :tfMatch, :matchFormatID)"
                #     inputs = {'stageName': stageName, 'stageSequence': stageSequence, 'stageFormatID': stageFormatID, 'stageStatusID': stageStatusID, 'tourID': tourID, 'numberOfParticipants': numberOfParticipants,  'maxGames': maxGames, 'tfMatch': tfMatch, 'matchFormatID': matchFormatID}
                #     createStructure = conn.execute(text(query), inputs)
                
                # flash('Stage Created!', 'success')
                return render_template('createStructure.html')
            
        except Exception as e:
                flash('Oops, an error has occured.', 'error')
                print(f"Error details: {e}")
        return render_template('createStructure.html', tourID=tourID)

    else:
        return render_template('createStructure.html')