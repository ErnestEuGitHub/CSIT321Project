from flask import render_template, request, flash, session, redirect, url_for
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
            # print(rows)

            if not rows:
                flash('This Email is not registered, try creating account instead.', 'error')
                return render_template('login.html', invalidEmail = True)
            elif bcrypt.checkpw(password.encode('utf-8'), rows[0][2].encode('utf-8')):
                # flash('Login Successful!', 'success')
                session["id"] = rows[0][0]
                session["profileID"] = rows[0][3]
                session["fname"] = rows[0][4]

                #profileID 1 = Org, 2 = Participant, 3 = System Admin
                if session["profileID"] == 1:
                    return redirect(url_for('loadhome'))
                elif session["profileID"] == 3:
                    flash('Login Successful As A Sys Admin!', 'success')
                    return render_template('login.html', invalidEmail = False, invalidPassword = False)
                else:
                    flash('Login Successful! But seems like theres no page for your role...', 'success')
                    return render_template('login.html', invalidEmail = False, invalidPassword = False)
            elif rows[0][2] != password:
                flash('Wrong password, please try again.', 'error')
                return render_template('login.html', invalidPassword = True)

    else:
        return render_template('login.html')