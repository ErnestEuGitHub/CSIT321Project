from flask import render_template
from database import dbConnect
from sqlalchemy import text

# def landingPage():
#         with dbConnect.engine.connect() as conn:
#             result = conn.execute(text("Select * from testtable"))
#             rows = result.fetchall()

#             descriptions = [row._asdict() for row in rows]
#         return descriptions

def landing():
    with dbConnect.engine.connect() as conn:
            result = conn.execute(text("Select * from testtable"))
            rows = result.fetchall()

            descriptions = [row._asdict() for row in rows]
    return render_template('index.html', desc=descriptions)
