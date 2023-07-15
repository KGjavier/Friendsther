from flask import render_template, redirect, request, session
from flask_app import app
from flask import flash
from flask_app.models.user import User
from flask_app.models.trip import Trip
from flask_app.models.usertrip import TravelSchedule
from datetime import datetime


#RENDERING------------------------------------------

@app.route('/show')
def show_form():
    user_id = session['user_id']
    user = User.get_user_by_id(user_id)
    return render_template('addPlan.html',user = user )


@app.route('/travels/destination/<int:trip_id>')
def showDetail(trip_id):
    
    if "user_id" not in session:
        return redirect("/unauthorized")
    
    user_id = session['user_id']
    user = User.get_user_by_id(user_id)
    trip_details = Trip.get_one(trip_id)
    trip_attendees = Trip.get_attendees(trip_id)
    
    return render_template("details.html", user=user, trip=trip_details, attendees=trip_attendees)



#ADD TRIP------------------------------------------------

@app.route('/add', methods=['POST'])
def create_trip():
    destination = request.form['destination']
    description = request.form['description']
    travel_date_from = request.form['travel_date_from']
    travel_date_to = request.form['travel_date_to']
    creator_id = session['user_id']
    trip_id = None
    
    trip_data = {
        'destination': destination,
        'description': description,
        'travel_date_from': travel_date_from,
        'travel_date_to': travel_date_to,
        'creator_id': creator_id
    }
    
    if len(destination) <= 0:
        flash("Destination is Required.", "addTrip")
        trip_id = False
    if len(description) <= 0:
        flash("Description is Required.", "addTrip")
        trip_id = False
    if len(travel_date_from) <= 0:
        flash("Travel Date From is Required.", "addTrip")
        trip_id = False
    if len(travel_date_to) <= 0:
        flash("Travel Date To is Required.", "addTrip")
        trip_id = False
    if len(travel_date_to) > 0 and datetime.strptime(travel_date_to, '%Y-%m-%d') <= datetime.now():
        flash("Travel Date To must be in the future.", "addTrip")
        trip_id = False
    if len(travel_date_from) > 0 and  datetime.strptime(travel_date_from, '%Y-%m-%d') <= datetime.now():
        flash("Travel Date From must be in the future. ", "addTrip")
        trip_id = False
    if len(travel_date_from) <= 0 and len(travel_date_to) >= 1:
        flash("Travel Date From must be fill up first", "addTrip")
        trip_id = False
    if len(travel_date_from) > 0 and len(travel_date_to) > 0 and travel_date_to < travel_date_from:
        flash("End Date needs to be after the Start Date", "addTrip")
        trip_id = False
    if trip_id is None:
        trip_id = Trip.create(trip_data)

    if trip_id:
        flash('Trip created successfully!')
        return redirect('/travels')
    else:
        flash('Failed to create trip. Please try again.', "addTrip")
        return redirect('/show')

#JOIN TRIP--------------------------------------------------

@app.route('/join/<int:trip_id>', methods=['POST'])
def join_trip(trip_id):
    user_id = session['user_id']
    if Trip.join_trip(trip_id, user_id):
        flash('You have successfully joined the trip!')
    else:
        flash('Failed to join the trip. Please try again.')

    return redirect('/travels')