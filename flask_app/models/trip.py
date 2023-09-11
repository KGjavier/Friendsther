from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models.user import User
from flask import flash, redirect



class Trip:
    def __init__(self, data): 
        self.id = data.get('id')
        self.destination = data.get('destination')
        self.description = data.get('description')
        self.travel_date_from = data.get('travel_date_from')
        self.travel_date_to = data.get('travel_date_to')
        self.creator_id = data.get('creator_id')
        self.creator_name = data.get('creator_name')
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
    
    #CREATE TRIPS------------------------------------------------------------------------------------------------
    
    @classmethod
    def create(cls, data):
        query = "INSERT INTO trips (destination, description, travel_date_from, travel_date_to, creator_id, created_at, updated_at) VALUES (%(destination)s, %(description)s, %(travel_date_from)s, %(travel_date_to)s, %(creator_id)s, NOW(), NOW());"
        return connectToMySQL('belt').query_db(query, data)
    
    #GET TRIPS DETAILS----------------------------------------------------------------------------------------
    @classmethod
    def get_trip_details(cls, trip_id):
        query_trip = "SELECT trips.destination, trips.description, trips.travel_date_from, trips.travel_date_to, users.name AS creator_name FROM trips INNER JOIN users ON trips.creator_id = users.id WHERE trips.id = %(trip_id)s;"
        trip_data = connectToMySQL('belt').query_db(query_trip, {'trip_id': trip_id})

        query_joined_users = "SELECT users.name AS joined_user_name FROM users INNER JOIN usertrips ON users.id = usertrips.joiner_id WHERE usertrips.trip_id = %(trip_id)s;"
        joined_users = connectToMySQL('belt').query_db(query_joined_users, {'trip_id': trip_id})

        return trip_data, joined_users
    
    
    #GET ONE TRIP------------------------------------------------------------------------------------------------
    @classmethod
    def get_one(cls, trip_id):
        query = "SELECT *, users.name AS creator_name FROM trips INNER JOIN users ON trips.creator_id = users.id WHERE trips.id = %(trip_id)s;"
        result = connectToMySQL('belt').query_db(query, {'trip_id': trip_id})
        return Trip(result[0]) if result else None

    #GET ATTENDEES------------------------------------------------------------------------------------------------
    @classmethod
    def get_attendees(cls, trip_id):
        query = "SELECT * FROM users WHERE id in (select user_id from usertrips where trip_id = %(trip_id)s);"
        results = connectToMySQL('belt').query_db(query, {'trip_id': trip_id})
        attendees = [User(result) for result in results]
        return attendees
    
    #GET USER TRIPS--- USED IN /TRAVEL--------------------------------------------------------------------------------
    @classmethod
    def get_user_trips(cls, user_id):
        query = "SELECT trips.id, trips.destination, trips.description, trips.travel_date_from, trips.travel_date_to, users.name AS creator_name FROM trips INNER JOIN users ON trips.creator_id = users.id WHERE trips.creator_id = %(user_id)s OR trips.id in (SELECT trip_id from usertrips where user_id =  %(user_id)s);"
        trips_data = connectToMySQL('belt').query_db(query, {'user_id': user_id})
        trips = [Trip(trip_data) for trip_data in trips_data]
        return trips
    
    #GET OTHER USERS TRIPS--- USED IN /TRAVEL-------------------------------------------------------------------------
    @classmethod
    def get_other_user_trips(cls, user_id):
        query = "SELECT trips.id, trips.destination, trips.description, trips.travel_date_from, trips.travel_date_to, users.name AS creator_name FROM trips INNER JOIN users ON trips.creator_id = users.id WHERE trips.creator_id != %(user_id)s AND trips.id not in (SELECT trip_id from usertrips where user_id =  %(user_id)s);; "
        other_trips_data = connectToMySQL('belt').query_db(query, {'user_id': user_id})
        other_trips = [Trip(trip_data) for trip_data in other_trips_data]
        return other_trips
    
    #JOIN TRIP--------------------------------------------------------------------------------
    @classmethod
    def join_trip(cls, trip_id, user_id):
        query_check = "SELECT * FROM usertrips WHERE trip_id = %(trip_id)s AND user_id = %(user_id)s;"
        result = connectToMySQL('belt').query_db(query_check, {'trip_id': trip_id, 'user_id': user_id})

        if result:
            flash("You have already joined this trip.")
            return False
        else:
            query_insert = "INSERT INTO usertrips (trip_id, user_id) VALUES (%(trip_id)s, %(user_id)s);"
            connectToMySQL('belt').query_db(query_insert, {'trip_id': trip_id, 'user_id': user_id})
            return True
    
    #GET ONE TRIP DETAILS------------------------------------------------------------------------
    @classmethod
    def get_onetrip_details(cls, trip_id):
        query = "SELECT trips.*, users.name AS creator_name FROM trips JOIN users ON trips.creator_id = users.id WHERE trips.id = %(trip_id)s;"
        result = connectToMySQL('belt').query_db(query, {'trip_id': trip_id})
        return Trip(result[0]) if result else None
    
    # DELETE TRIP BY ID--------------------------------------------------------------------------
    @classmethod
    def delete_trip(cls, trip_id):
        # First, check if the trip exists
        trip = cls.get_one(trip_id)
        if not trip:
            flash("Trip not found.")
            return False

        # Delete the trip
        query = "DELETE FROM trips WHERE id = %(trip_id)s;"
        result = connectToMySQL('belt').query_db(query, {'trip_id': trip_id})

        print(result)
        if result is None:
            flash(f"Trip to {trip.destination} deleted successfully.")
            return True
        else:
            flash(f"Failed to delete trip to {trip.destination}.")
            return False
    
    # UPDATE TRIP BY ID--------------------------------------------------------------------------
    @classmethod
    def update_trip(cls, data):
        # First, check if the trip exists
        trip = cls.get_one(data['id'])
        if not trip:
            flash("Trip not found.")
            return False

        # Update the trip
        query = """
            UPDATE trips
            SET destination = %(destination)s,
                description = %(description)s,
                travel_date_from = %(travel_date_from)s,
                travel_date_to = %(travel_date_to)s,
                updated_at = NOW()
            WHERE id = %(id)s;
        """
        result = connectToMySQL('belt').query_db(query, data)

        if result is None:
            flash(f"Trip to {data['destination']} updated successfully.")
            return True
        else:
            flash(f"Failed to update trip to {data['destination']}.")
            return False