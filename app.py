from flask import Flask, render_template, request, flash
from database import engine
from sqlalchemy import text
import re, bcrypt

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

        if not email or not password:
            flash('Please fill in both Email and Password!', 'error')
            return render_template('login.html', emptyForm = True)
    
    # try:
        with engine.connect() as conn:
            searchUser = conn.execute(text("SELECT * FROM users WHERE EMAIL = '" + email +"'"))
            rows = searchUser.fetchall()
        
            if not rows:
                flash('This Email is not registered, try creating account instead.', 'error')
                return render_template('login.html', invalidEmail = True)
            elif bcrypt.checkpw(password.encode('utf-8'), rows[0][2].encode('utf-8')):
                flash('Login Successful!', 'success')
                return render_template('login.html', invalidEmail = False, invalidPassword = False)
            elif rows[0][2] != password:
                flash('Wrong password, please try again.', 'error')
                return render_template('login.html', invalidPassword = True)
           
    # except Exception as e:
    #     flash('Oops, an error has occured.', 'error')
    #     return render_template('login.html', error = True)


    else:
        return render_template('login.html')

@app.route('/register', methods=["POST", "GET"])
def register():
    emptyForm = False
    invalidEmail = False
    invalidPassword = False
    emptyForm = False
    error = False

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        cpassword = request.form.get("cpassword")
        fname = request.form.get("fname")
        lname = request.form.get("lname")

        emailregex = r"^[\w.-]+@([\w-]+\.)+[\w-]{2,4}$"
        match = bool(re.match(emailregex, email))

        if not email or not password or not cpassword or not fname or not lname:
            flash('Please fill in all fields!', 'error')
            return render_template('register.html', emptyForm = True, email=email, fname=fname, lname=lname)
        elif not match:
            flash('That does not look like a valid Email Address. Please try again!', 'error')
            return render_template('register.html', invalidEmail = True, email=email, fname=fname, lname=lname)
        elif password != cpassword:
            flash('Password and Confirm Password does not match!', 'error')
            return render_template('register.html', invalidPassword = True, email=email, fname=fname, lname=lname)
        else: 
            try:
                hashedpw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                print(type(hashedpw))
                # print(hashedpw.decode('utf-8'))
                with engine.connect() as conn:
                    query = "INSERT INTO users (email, password, profileID, fname, lname) VALUES (:email, :password, 1, :fname, :lname)"
                    inputs = {'email': email, 'password': hashedpw, 'fname': fname, 'lname': lname}
                    addUser = conn.execute(text(query), inputs)

                flash('Account Created! Try logging in.', 'success')
                return render_template('login.html')

            except Exception as e:
                flash('Oops, an error has occured.', 'error')
                print(f"Error details: {e}")
                return render_template('register.html', error = True, email=email, fname=fname, lname=lname)

    else:
        return render_template('register.html')

@app.route('/tournamentOverviewPage', methods=["POST", "GET"])
def loadTournamentOverviewPage():
    return render_template('tournamentOverviewPage.html')

if __name__ == "__main__":
    app.run(debug=True)