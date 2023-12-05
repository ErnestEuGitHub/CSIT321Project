from flask import render_template, request, flash
from database import dbConnect
import re, bcrypt
from sqlalchemy import text

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
                with dbConnect.engine.connect() as conn:
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