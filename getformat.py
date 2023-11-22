from flask import Flask, render_template, request, jsonify
from database import dbConnect
from sqlalchemy import text

def getformat():
    sportID = request.form.get('sport_id')
    
    with dbConnect.engine.connect() as conn:
        query = "SELECT formats.formatName FROM sportsformats JOIN formats ON sportsformats.formatID = formats.formatID WHERE sportID = (:sportID)"
        inputs = {'sportID': sportID}
        result = conn.execute(text(query), inputs)
        rows = result.fetchall()

        formatOptions = [row._asdict() for row in rows]

    options_html = ''.join([f'<option value="{formatOption["formatName"]}">{formatOption["formatName"]}</option>' for formatOption in formatOptions])

    return jsonify({"options": options_html})