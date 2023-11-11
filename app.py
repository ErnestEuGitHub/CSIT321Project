from flask import Flask, render_template, request, flash
from database import engine
from sqlalchemy import text

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

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
    invalidEmail = False
    invalidPassword = False
    emptyForm = False
    error = False

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if not email or not password:
            return render_template('login.html', emptyForm = True)

        with engine.connect() as conn:
            searchUser = conn.execute(text("SELECT * FROM users WHERE EMAIL = '" + email +"'"))
            rows = searchUser.fetchall()
            print(rows)

            if not rows:
                return render_template('login.html', invalidEmail = True)
            elif rows[3] == password:
                flash('Login Successful!')
                return render_template('login.html', invalidEmail = False, invalidPassword = False)
            elif rows[3] != password:
                flash('Help lah, you forgot your password!')
                return render_template('login.html', invalidPassword = True,)
            else:
                flash('Oops, an error has occured.')

    else:
        return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)