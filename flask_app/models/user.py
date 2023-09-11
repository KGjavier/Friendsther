from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

class User:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.username = data['username']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.trips = []
    
    #VALIDATION REGISTRATION
    @staticmethod
    def validate_user(user):
        is_valid = True 
        # NAME
        if len(user['name']) < 3:
            flash("Name must be at least 3 characters.", "registration")
            is_valid = False
        # USERNAME
        if len(user['username']) < 3:
            flash("Username must be at least 3 characters.", "registration")
            is_valid = False
            
        # PASSWORD
        if len(user['password']) < 8:
            flash("Password must be at least 8 characters.", "registration")
            is_valid = False
        if not re.search(r"\d", user['password']):
            flash("Password must contain at least one number.", "registration")
            is_valid = False
        if not re.search(r"[A-Z]", user['password']):
            flash("Password must contain at least one uppercase letter.", "registration")
            is_valid = False
        if user['password']!=user['confirm_password']:
            flash("Password did not match!", "registration")
            is_valid = False
        return is_valid
    
    #------------------------------------------------------------------------------------
    #SAVE
    @classmethod
    def save_user(cls, data):
        query = "INSERT INTO users (name,username,password,created_at,updated_at) VALUES (%(name)s, %(username)s, %(password)s, NOW(), NOW());"
        return connectToMySQL('belt').query_db(query, data)
    
    #LOGIN
    @classmethod
    def login_user(cls, data):
        query = "SELECT * FROM users WHERE username= %(username)s;"
        result = connectToMySQL('belt').query_db(query, data)
        if len(result) < 1:
            return False
        return cls(result[0])
    
    #GET USER BY ID
    @classmethod
    def get_user_by_id(cls, user_id):
        query = "SELECT * FROM users WHERE id = %(user_id)s;"
        data = {"user_id": user_id}
        result = connectToMySQL('belt').query_db(query, data)
        if result:
            return cls(result[0])
        return None
    
