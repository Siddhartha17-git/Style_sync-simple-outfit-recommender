from pymongo import MongoClient
import os
from datetime import datetime
import bcrypt
from bson.objectid import ObjectId
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_database():
    """
    Function to get the MongoDB database connection
    Returns the database instance
    """
    try:
        # Get connection string from environment variable
        connection_string = os.getenv('MONGODB_URI')
        if not connection_string:
            raise ValueError("MONGODB_URI environment variable is not set")
        
        # Create a connection using MongoClient
        client = MongoClient(connection_string)
        
        # Get the database
        db = client['outfit_recommender_db']
        
        # Test the connection
        client.server_info()
        print("MongoDB Atlas connection successful")
        
        return db
    
    except Exception as e:
        print(f"Error connecting to MongoDB Atlas: {str(e)}")
        raise e

def create_user(username, email, password):
    """
    Create a new user in the database
    Returns (success: bool, message: str, user_id: str)
    """
    try:
        db = get_database()
        users = db['users']
        
        # Check if email already exists
        if users.find_one({'email': email}):
            return False, "Email already registered", None
            
        # Check if username already exists
        if users.find_one({'username': username}):
            return False, "Username already taken", None
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user document
        user = {
            'username': username,
            'email': email,
            'password': hashed_password,
            'created_at': datetime.utcnow(),
            'last_login': None
        }
        
        result = users.insert_one(user)
        return True, "User created successfully", str(result.inserted_id)
        
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return False, f"Error creating user: {str(e)}", None

def verify_user(email, password):
    """
    Verify user credentials
    Returns (success: bool, user_data: dict/None, message: str)
    """
    try:
        db = get_database()
        users = db['users']
        
        user = users.find_one({'email': email})
        if not user:
            return False, None, "User not found"
        
        if bcrypt.checkpw(password.encode('utf-8'), user['password']):
            # Update last login
            users.update_one(
                {'_id': user['_id']},
                {'$set': {'last_login': datetime.utcnow()}}
            )
            
            # Return user data without password
            user_data = {
                'user_id': str(user['_id']),
                'username': user['username'],
                'email': user['email']
            }
            return True, user_data, "Login successful"
        
        return False, None, "Invalid password"
        
    except Exception as e:
        print(f"Error verifying user: {str(e)}")
        return False, None, f"Error during login: {str(e)}"

def update_username(user_id, new_username):
    """
    Update user's username
    Returns (success: bool, message: str)
    """
    try:
        db = get_database()
        users = db['users']
        
        # Check if new username already exists
        if users.find_one({'username': new_username}):
            return False, "Username already taken"
        
        result = users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'username': new_username}}
        )
        
        if result.modified_count > 0:
            return True, "Username updated successfully"
        return False, "User not found"
        
    except Exception as e:
        return False, f"Error updating username: {str(e)}"

def delete_account(user_id):
    """
    Delete user account and all associated data
    Returns (success: bool, message: str)
    """
    try:
        db = get_database()
        users = db['users']
        history = db['user_history']
        
        # Delete user's history first
        history.delete_many({'user_id': user_id})
        
        # Then delete the user
        result = users.delete_one({'_id': ObjectId(user_id)})
        
        if result.deleted_count > 0:
            return True, "Account deleted successfully"
        return False, "User not found"
        
    except Exception as e:
        return False, f"Error deleting account: {str(e)}"

def add_to_history(user_id, recommendation_data):
    """
    Add a recommendation to user's history
    Returns (success: bool)
    """
    try:
        db = get_database()
        history = db['user_history']
        
        history_entry = {
            'user_id': user_id,
            'timestamp': datetime.utcnow(),
            'recommendation': recommendation_data
        }
        
        history.insert_one(history_entry)
        return True
        
    except Exception as e:
        print(f"Error adding to history: {str(e)}")
        return False

def get_user_history(user_id):
    """
    Get user's recommendation history
    Returns list of history entries
    """
    try:
        db = get_database()
        history = db['user_history']
        
        user_history = list(
            history.find(
                {'user_id': user_id},
                {'_id': 0}
            ).sort('timestamp', -1)
        )
        return user_history
        
    except Exception as e:
        print(f"Error getting history: {str(e)}")
        return []

# Remove the test connection code at the bottom 