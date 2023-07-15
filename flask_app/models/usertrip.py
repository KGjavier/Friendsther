from flask_app.config.mysqlconnection import connectToMySQL

class TravelSchedule:
    def __init__(self, trip_id, user_id):
        self.trip_id = trip_id
        self.user_id = user_id
    
    #SAVE USER TRIPS
    def save(self):
        query = "INSERT INTO usertrips (trip_id, user_id) VALUES (%(trip_id)s, %(user_id)s);"
        data = {
            'trip_id': self.trip_id,
            'user_id': self.user_id
        }
        return connectToMySQL('belt').query_db(query, data)