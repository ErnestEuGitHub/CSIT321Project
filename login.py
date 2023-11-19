from flask import render_template, request, flash
from database import dbConnect
import bcrypt
from sqlalchemy import text

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
    
        with dbConnect.engine.connect() as conn:
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

    else:
        return render_template('login.html')