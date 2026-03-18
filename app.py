from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for, send_file
from flask_cors import CORS
from outfit_recommender import OutfitRecommender
from dataset import OutfitDataset
import joblib
import os
import traceback
from db_config import get_database, add_to_history
from functools import wraps
import bcrypt
from bson import ObjectId
from datetime import datetime

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'your-secret-key-here'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
recommender = OutfitRecommender()

# Initialize database connection
db = None
users_collection = None
user_history_collection = None

def init_db():
    global db, users_collection, user_history_collection
    try:
        db = get_database()
        users_collection = db['users']
        user_history_collection = db['user_history']
        print("Database collections initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise e

# Initialize database on startup
init_db()

# Serve HTML files
@app.route('/')
def home():
    return send_from_directory('.', 'index1.html')

@app.route('/signup.html')
def signup_page():
    return send_from_directory('.', 'signup.html')

@app.route('/login.html')
def login_page():
    return send_from_directory('.', 'login.html')

@app.route('/new.html')
def new_page():
    return send_from_directory('.', 'new.html')

@app.route('/profile.html')
def profile_page():
    return send_from_directory('.', 'profile.html')

# Serve CSS files
@app.route('/<path:filename>.css')
def serve_css(filename):
    return send_from_directory('.', f'{filename}.css')

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'status': 'error', 'message': 'Please login first'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Initialize or load the model
model_path = 'outfit_recommender_model.joblib'
if not os.path.exists(model_path):
    print("Model not found. Creating new model...")
    from prepare_dataset import main as train_model
    train_model()

# Load the trained model
try:
    recommender.load_model(model_path)
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {str(e)}")
    print(traceback.format_exc())

@app.route('/outfit_images/<path:filename>')
def serve_image(filename):
    return send_from_directory('outfit_images', filename)

@app.route('/<path:filename>')
def serve_file(filename):
    return send_file(filename)

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # Check if user already exists
        if users_collection.find_one({'email': email}):
            return jsonify({'error': 'Email already registered'}), 400

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user document
        user = {
            'username': username,
            'email': email,
            'password': hashed_password,
            'created_at': datetime.now()
        }
        
        # Insert user into database
        result = users_collection.insert_one(user)
        
        # Create initial history entry
        history_entry = {
            'user_id': str(result.inserted_id),
            'action': 'account_created',
            'timestamp': datetime.now()
        }
        user_history_collection.insert_one(history_entry)
        
        return jsonify({'message': 'Signup successful'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        user = users_collection.find_one({'email': email})
        if not user:
            return jsonify({'error': 'User not found'}), 404

        if bcrypt.checkpw(password.encode('utf-8'), user['password']):
            # Create login history entry
            history_entry = {
                'user_id': str(user['_id']),
                'action': 'login',
                'timestamp': datetime.now()
            }
            user_history_collection.insert_one(history_entry)
            
            return jsonify({
                'message': 'Login successful',
                'user_id': str(user['_id']),
                'username': user['username']
            }), 200
        else:
            return jsonify({'error': 'Invalid password'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return jsonify({'status': 'success', 'message': 'Logged out successfully'}), 200

@app.route('/profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    try:
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Get user history
        history = list(user_history_collection.find(
            {'user_id': user_id},
            {'_id': 0}
        ).sort('timestamp', -1).limit(10))
        
        return jsonify({
            'username': user['username'],
            'email': user['email'],
            'history': history
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/profile/update/<user_id>', methods=['PUT'])
def update_profile(user_id):
    try:
        data = request.json
        new_username = data.get('username')
        
        result = users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'username': new_username}}
        )
        
        if result.modified_count > 0:
            # Record profile update in history
            history_entry = {
                'user_id': user_id,
                'action': 'profile_updated',
                'details': 'Username updated',
                'timestamp': datetime.now()
            }
            user_history_collection.insert_one(history_entry)
            
            return jsonify({'message': 'Profile updated successfully'}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/profile/delete/<user_id>', methods=['DELETE'])
def delete_profile(user_id):
    try:
        # Delete user's history first
        user_history_collection.delete_many({'user_id': user_id})
        
        # Then delete the user
        result = users_collection.delete_one({'_id': ObjectId(user_id)})
        
        if result.deleted_count > 0:
            return jsonify({'message': 'Account deleted successfully'}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/profile/update-password/<user_id>', methods=['PUT'])
def update_password(user_id):
    try:
        data = request.json
        new_password = data.get('new_password')
        
        if not new_password:
            return jsonify({'error': 'New password is required'}), 400
            
        # Hash the new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        # Update password in database
        result = users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'password': hashed_password}}
        )
        
        if result.modified_count > 0:
            # Record password update in history
            history_entry = {
                'user_id': user_id,
                'action': 'password_updated',
                'timestamp': datetime.now()
            }
            user_history_collection.insert_one(history_entry)
            
            return jsonify({'message': 'Password updated successfully'}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    try:
        print("Received request with data:", request.get_json())
        user_input = request.get_json()
        
        if not user_input:
            return jsonify({
                'status': 'error',
                'message': 'No input data provided'
            }), 400

        # Validate required fields
        required_fields = ['weather', 'gender', 'skin_tone', 'body_type', 'occasion', 'hair_type', 'style']
        missing_fields = [field for field in required_fields if field not in user_input]
        
        if missing_fields:
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Create ordered input dictionary
        ordered_input = {
            'weather': user_input['weather'],
            'gender': user_input['gender'],
            'skin_tone': user_input['skin_tone'],
            'body_type': user_input['body_type'],
            'occasion': user_input['occasion'],
            'hair_type': user_input['hair_type'],
            'style': user_input['style']
        }

        # Print the validated input
        print("Validated input:", ordered_input)
        
        # Get recommendations
        recommendations = recommender.recommend(ordered_input, n_recommendations=4)
        print("Generated recommendations:", recommendations)
        
        # Get the outfit description from the dataset
        dataset = OutfitDataset()
        df = dataset.load_dataset()
        
        result_recommendations = []
        for rec in recommendations:
            try:
                outfit_data = df[df['outfit_id'] == rec['outfit_id']].iloc[0]
                result_recommendations.append({
                    'outfit_id': rec['outfit_id'],
                    'confidence': float(rec['confidence']),
                    'match_score': float(rec['match_score']),
                    'description': outfit_data['description']
                })
            except Exception as e:
                print(f"Error processing outfit {rec['outfit_id']}: {str(e)}")
                continue
        
        if not result_recommendations:
            return jsonify({
                'status': 'error',
                'message': 'No suitable recommendations found'
            }), 404
        
        # Add to user history if user_id is provided
        user_id = request.headers.get('X-User-ID')
        if user_id:
            try:
                add_to_history(user_id, {
                    'input': ordered_input,
                    'recommendations': result_recommendations
                })
            except Exception as e:
                print(f"Error adding to history: {str(e)}")
        
        return jsonify({
            'status': 'success',
            'recommendations': result_recommendations
        })
        
    except Exception as e:
        print(f"Error in get_recommendations: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

if __name__ == '__main__':
    # Make sure the outfit_images directory exists
    if not os.path.exists('outfit_images'):
        os.makedirs('outfit_images')
    app.run(debug=True, port=5000)