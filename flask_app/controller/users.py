from flask import Flask, render_template, request, redirect, flash, session
from flask_app.models.user import User
from flask_app.models.trip import Trip
from flask_app import app
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

#RENDERING------------------------------------------

@app.route('/')
def index():
    return render_template('loginReg.html')



# REGISTRATION--------------------------------------
@app.route('/register', methods=['POST'])
def register():
    if not User.validate_user(request.form):
        return redirect('/')
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    print(pw_hash)
    data = {
        "name":request.form['name'],
        "username":request.form['username'],
        "password":pw_hash
    }
    User.save_user(data)
    flash("User Registered!")
    return redirect('/')



#LOGIN----------------------------------------------
@app.route('/login', methods=['POST'])
def login():
    data = {
        "username": request.form["username"]
    }
    user = User.login_user(data)
    if not user:
        flash("Invalid Username","login")
        return redirect('/')
    if not bcrypt.check_password_hash(user.password, request.form['password']):
        flash("Invalid Password","login")
        return redirect('/')
    session['user_id'] = user.id
    return redirect('/travels')

@app.route('/travels')
def home():
    if "user_id" not in session:
        return redirect("/unauthorized")
    
    user_id = session['user_id']
    user = User.get_user_by_id(user_id)
    user_trips = Trip.get_user_trips(user_id)
    other_trips = Trip.get_other_user_trips(user_id)
    
    return render_template("travel.html", user=user, trips=user_trips, other_trips=other_trips)

# LOGOUT----------------------------------------------
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "login")
    return redirect('/')

