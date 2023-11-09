from flask import Flask, render_template, request
from database import engine
from sqlalchemy import text

app = Flask(__name__)

def load_desc_from_db():
    with engine.connect() as conn:
        result = conn.execute(text("Select * from testtable"))
        rows = result.fetchall()

        descriptions = [row._asdict() for row in rows]
    return descriptions

@app.route('/')
def loadhome():
    desc = load_desc_from_db()
    return render_template('index.html', desc=desc)
    
@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        with engine.connect() as conn:
            searchUser = conn.execute(text("SELECT * FROM USERS WHERE EMAIL = " + email))
            rows = searchUser.fetchall()
        return rows
    else:
        return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)