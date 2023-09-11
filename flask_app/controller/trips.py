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

#DELETE TRIP--------------------------------------------------
@app.route('/trips/delete/<int:trip_id>', methods=['GET', 'POST'])
def delete_trip(trip_id):
    # Check if the user is authorized to delete the trip
    if "user_id" not in session:
        return redirect("/unauthorized")

    user_id = session['user_id']

    # Check if the user is the creator of the trip
    trip = Trip.get_one(trip_id)
    if trip.creator_id != user_id:
        flash('You are not authorized to delete this trip.')
        return redirect('/travels')

    if request.method == 'POST':
        # If the user confirms the deletion, delete the trip
        if Trip.delete_trip(trip_id):
            flash('Trip deleted successfully!')
            return redirect('/travels')
        else:
            flash('Failed to delete trip. Please try again.')

    # Render a confirmation page
    return render_template('confirmDelete.html', trip=trip)

# TRIP DETAILS PAGE----------------------------------------------------------------
@app.route('/travels/destination/<int:trip_id>')
def show_details(trip_id):
    
    if "user_id" not in session:
        return redirect("/unauthorized")
    
    user_id = session['user_id']
    user = User.get_user_by_id(user_id)
    trip_details = Trip.get_one(trip_id)
    trip_attendees = Trip.get_attendees(trip_id)
    
    if user_id == trip_details.creator_id:
        return render_template("detailsEditDelete.html", user=user, trip=trip_details, attendees=trip_attendees)
    else:
        return render_template("details.html", user=user, trip=trip_details, attendees=trip_attendees)
    
# Display the edit form with prepopulated data----------------------------------------------------------------
@app.route('/trips/edit/<int:trip_id>', methods=['GET'])
def edit_trip_form(trip_id):
    # Check if the user is authorized to edit the trip
    if "user_id" not in session:
        return redirect("/unauthorized")

    user_id = session['user_id']

    # Check if the user is the creator of the trip
    trip = Trip.get_one(trip_id)
    if trip.creator_id != user_id:
        flash('You are not authorized to edit this trip.')
        return redirect('/travels')

    return render_template('addPlanEdit.html', trip=trip)

# Handle form submission to update trip details----------------------------------------------------------------
@app.route('/update_trip/<int:trip_id>', methods=['POST'])
def update_trip(trip_id):
    # Check if the user is authorized to update the trip
    if "user_id" not in session:
        return redirect("/unauthorized")

    user_id = session['user_id']

    # Check if the user is the creator of the trip
    trip = Trip.get_one(trip_id)
    if trip.creator_id != user_id:
        flash('You are not authorized to update this trip.')
        return redirect('/travels')

    if request.method == 'POST':
        # Get the updated data from the form
        destination = request.form['destination']
        description = request.form['description']
        travel_date_from = request.form['travel_date_from']
        travel_date_to = request.form['travel_date_to']

        # Update the trip's data
        updated_data = {
            'id': trip_id,
            'destination': destination,
            'description': description,
            'travel_date_from': travel_date_from,
            'travel_date_to': travel_date_to,
        }
        if Trip.update_trip(updated_data):
            flash('Trip updated successfully!')
        else:
            flash('Failed to update trip. Please try again.')

    return redirect('/travels')



# Not used anymore----------------------------------------------------------------
# @app.route('/travels/destination/<int:trip_id>')
# def showDetail(trip_id):
    
#     if "user_id" not in session:
#         return redirect("/unauthorized")
    
#     user_id = session['user_id']
#     user = User.get_user_by_id(user_id)
#     trip_details = Trip.get_one(trip_id)
#     trip_attendees = Trip.get_attendees(trip_id)
    
#     return render_template("details.html", user=user, trip=trip_details, attendees=trip_attendees)

# @app.route('/travels/mydestination/<int:trip_id>')
# def showMyDetail(trip_id):
    
#     if "user_id" not in session:
#         return redirect("/unauthorized")
    
#     user_id = session['user_id']
#     user = User.get_user_by_id(user_id)
#     trip_details = Trip.get_one(trip_id)
#     trip_attendees = Trip.get_attendees(trip_id)
    
#     return render_template("detailsEditDelete.html", user=user, trip=trip_details, attendees=trip_attendees)