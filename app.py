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
        email = request.form.get("email")
        password = request.form.get("password")
        print(email, password)
        print("POST activated")

        if not email or not password:
            flash('Please fill in both Email and Password!')
            return render_template('login.html', emptyForm = True)

        with engine.connect() as conn:
            searchUser = conn.execute(text("SELECT * FROM users WHERE EMAIL = '" + email +"'"))
            rows = searchUser.fetchall()
            print(rows)

            if not rows:
                print('if not rows triggered')
                flash('This Email is not registered, try creating account instead.')
                return render_template('login.html', invalidEmail = True)
            elif rows[0][2] == password:
                print('login success')
                flash('Login Successful!')
                return render_template('login.html', invalidEmail = False, invalidPassword = False)
            elif rows[0][2] != password:
                print('elif not equals password triggered')
                flash('Help lah, you forgot your password!')
                return render_template('login.html', invalidPassword = True)
            else:
                flash('Oops, an error has occured.')

    else:
        return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)