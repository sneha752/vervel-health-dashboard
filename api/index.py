from flask import Flask, render_template, request, jsonify, redirect, url_for, session, g
import re
# import pandas as pd # COMMENTED OUT: Removed for Vercel size limit
# from sklearn.tree import DecisionTreeClassifier # COMMENTED OUT: Removed for Vercel size limit
import io
# import numpy as np # COMMENTED OUT: Removed for Vercel size limit
# import matplotlib # COMMENTED OUT: Removed for Vercel size limit
# matplotlib.use('Agg') # COMMENTED OUT
# import matplotlib.pyplot as plt # COMMENTED OUT
import os
import uuid # For generating unique filenames for charts (though chart saving is disabled)
import json 

# --- Custom JSON Encoder for NumPy Types (COMMENTED OUT: No NumPy usage) ---
# class NumpyEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, np.integer):
#             return int(obj)
#         elif isinstance(obj, np.floating):
#             return float(obj)
#         elif isinstance(obj, np.ndarray):
#             return obj.tolist()
#         elif pd.isna(obj):
#             return None
#         return json.JSONEncoder.default(self, obj)
# -------------------------------------------

# --- Flask App Setup ---
app = Flask(__name__)
# Set a secret key for session management from Vercel Environment Variables
# IMPORTANT: This must be set securely in Vercel project settings.
app.secret_key = os.environ.get('SECRET_KEY') 

# --- Configure Flask to use the custom JSON encoder (COMMENTED OUT: No NumPy types) ---
# app.json_encoder = NumpyEncoder 

# --- SQLite Database Configuration (COMMENTED OUT for Vercel) ---
# All SQLite related code remains commented out as before.

# --- Machine Learning Model (COMMENTED OUT for Vcel) ---
# A very basic Decision Tree Classifier for health risk prediction
# data = {
#     'cholesterol': [220, 180, 250, 190, 210, 160],
#     'blood_pressure': [140, 120, 160, 130, 150, 110],
#     'risk': ['high', 'low', 'high', 'low', 'medium', 'low']
# }
# df = pd.DataFrame(data)

# X = df[['cholesterol', 'blood_pressure']]
# y = df['risk']

# model = DecisionTreeClassifier()
# model.fit(X, y)
# -----------------------------------------------------------

# --- Load Doctor Data ---
# Loads doctor information from a local JSON file
DOCTORS_FILE = 'doctors.json'
doctors_data = []
# Ensure doctors.json is loaded correctly, handling potential Vercel path issues
doctor_json_path = os.path.join(app.root_path, DOCTORS_FILE)
if os.path.exists(doctor_json_path):
    try:
        with open(doctor_json_path, 'r') as f:
            doctors_data = json.load(f)
    except Exception as e:
        print(f"ERROR: Could not load doctors.json: {e}")
else:
    print(f"WARNING: {DOCTORS_FILE} not found at {doctor_json_path}. Doctor search will be unavailable.")


# --- Chatbot Response Logic ---
def get_chatbot_response(user_message):
    """Generates a response based on user input for the chatbot."""
    user_message = user_message.lower()
    if "hello" in user_message or "hi" in user_message:
        return "Hello there! How can I help with your health today?"
    elif "heart rate" in user_message or "heartbeat" in user_message:
        return "I can help with that. Please tell me your heart rate. What is your current pulse?"
    elif "blood pressure" in user_message:
        return "To provide an accurate report, please tell me your blood pressure numbers (e.g., 120/80)."
    elif "diet" in user_message:
        return "I can create a basic diet chart. Please provide me with your health goals and any dietary restrictions."
    elif "report" in user_message:
        return "The health report analysis feature is disabled in this free deployment. Please ask me about other topics."
    elif "doctor" in user_message or "appointment" in user_message:
        return "I can help you find a doctor. What kind of specialist are you looking for (e.g., Cardiologist, Nutritionist, General Physician)? Type 'find doctor [specialty]'."
    else:
        return "I'm still learning! Please ask me about available features like finding a doctor or general health topics."

# --- Health Report Analysis Logic (DISABLED for Vercel) ---
def get_health_report_summary(report_text):
    """Placeholder for health report analysis, as main functionality is disabled."""
    return {
        "summary": "Health report analysis is currently disabled in this free deployment to fit platform limitations.",
        "health_risk": "N/A",
        "diet_plan": ["Feature disabled."],
        "habits": ["Feature disabled."],
        "chart_url": None # No chart generation
    }

# --- Authentication Routes (Modified for Vercel - No Persistence) ---
# These routes will function as placeholders.

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handles user registration (Non-functional on Vercel without persistent DB)."""
    if request.method == 'POST':
        return jsonify({"message": "Signup is disabled for this free deployment due to lack of a persistent database."}), 200
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login (Non-functional on Vercel without persistent DB)."""
    if request.method == 'POST':
        return jsonify({"error": "Login is disabled for this free deployment due to lack of a persistent database. Try again later."}), 401
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    """Handles user logout by clearing the session."""
    session.pop('user_id', None) 
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/get-user-id', methods=['GET'])
def get_user_id():
    """Returns a placeholder user ID as persistent login is not supported."""
    return jsonify({"userId": session.get('user_id', None)}), 200 

# --- Protected Route for Dashboard (main page) ---
@app.route('/')
def home():
    """Renders the main dashboard page."""
    # Authentication check removed as persistent login is not supported.
    return render_template('index.html')

# --- Other API Endpoints (Modified for Vercel - No Persistence) ---
@app.route('/chat', methods=['POST'])
def chat():
    """Handles chatbot interactions."""
    # Removed session check as persistent auth is not supported. Chat functionality remains.
    user_data = request.json
    user_message = user_data['message']
    
    # Check for doctor search query
    if user_message.lower().startswith('find doctor'):
        specialty_query = user_message.lower().replace('find doctor', '').strip()
        if specialty_query:
            return find_doctor_by_specialty(specialty_query)
        else:
            return jsonify({"response": "Please specify a specialty, e.g., 'find doctor cardiologist'."})
    
    bot_response = get_chatbot_response(user_message)
    return jsonify({"response": bot_response})

@app.route('/upload-report', methods=['POST'])
def upload_report():
    """Handles uploading and processing of health reports (DISABLED)."""
    return jsonify({"error": "Health report upload and analysis is disabled in this free deployment to fit platform limitations."}), 400

@app.route('/upload-smartwatch-data', methods=['POST'])
def upload_smartwatch_data():
    """Handles uploading and processing of smartwatch data (DISABLED)."""
    return jsonify({"error": "Smartwatch data upload and analysis is disabled in this free deployment to fit platform limitations."}), 400
    
# --- NEW: Doctor Search Function ---
def find_doctor_by_specialty(specialty_query):
    """Searches for doctors by specialty from the loaded doctors_data."""
    found_doctors = [
        doc for doc in doctors_data 
        if specialty_query.lower() in doc['specialty'].lower()
    ]
    
    if found_doctors:
        response_message = "Here are some doctors specializing in your area of interest:\n\n"
        for doc in found_doctors:
            response_message += (
                f"**{doc['name']}**\n"
                f"Specialty: {doc['specialty']}\n"
                f"Location: {doc['location']}\n"
                f"Contact: {doc['contact']} | Phone: {doc['phone']}\n"
                f"Availability: {doc['availability']}\n\n"
            )
    else:
        response_message = f"Sorry, I couldn't find any doctors specializing in '{specialty_query}'. Please try a different specialty."
    
    return jsonify({"response": response_message})

# The if __name__ == '__main__': block was removed in the previous iteration, which is correct.
