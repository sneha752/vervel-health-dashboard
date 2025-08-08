from flask import Flask, render_template, request, jsonify, redirect, url_for, session, g
import os # For SECRET_KEY and checking doctors.json
import json # For loading doctors.json

# Removed: pandas, re, sklearn.tree, io, numpy, matplotlib, uuid, sqlite3, bcrypt, traceback
# These libraries and their related code are removed or commented out to fit Vercel's size limit
# and due to the ephemeral nature of serverless functions (no persistent SQLite).

# --- Flask App Setup ---
app = Flask(__name__)
# Set a secret key for session management from Vercel Environment Variables.
# IMPORTANT: This must be set securely in Vercel project settings.
app.secret_key = os.environ.get('SECRET_KEY') 

# --- Removed: Custom JSON Encoder (No NumPy usage) ---
# app.json_encoder = NumpyEncoder # This line is no longer needed

# --- Removed: SQLite Database Configuration and Functions ---
# get_db_path(), get_db(), close_connection(), init_db() are removed.
# Database persistence is not supported on Vercel's free tier.

# --- Removed: Machine Learning Model ---
# The ML model and its training data are removed as sklearn is not available.

# --- Load Doctor Data ---
# Loads doctor information from a local JSON file.
# Ensure 'doctors.json' is located directly in your project's root directory,
# alongside 'api/' and 'templates/'.
DOCTORS_FILE = 'doctors.json'
doctors_data = []
# It's safer to use app.root_path for file access in Flask deployments
doctor_json_path = os.path.join(app.root_path, DOCTORS_FILE)
if os.path.exists(doctor_json_path):
    try:
        with open(doctor_json_path, 'r') as f:
            doctors_data = json.load(f)
    except Exception as e:
        print(f"ERROR: Could not load doctors.json at {doctor_json_path}: {e}")
else:
    print(f"WARNING: {DOCTORS_FILE} not found at {doctor_json_path}. Doctor search will be unavailable.")


# --- Chatbot Response Logic ---
def get_chatbot_response(user_message):
    """Generates a response based on user input for the chatbot."""
    user_message = user_message.lower()
    if "hello" in user_message or "hi" in user_message:
        return "Hello there! How can I help with your health today?"
    elif "report" in user_message or "analysis" in user_message or "smartwatch" in user_message:
        return "Health report and smartwatch data analysis features are disabled in this free deployment to fit platform limitations."
    elif "doctor" in user_message or "appointment" in user_message:
        return "I can help you find a doctor. What kind of specialist are you looking for (e.g., Cardiologist, Nutritionist, General Physician)? Type 'find doctor [specialty]'."
    elif "signup" in user_message or "login" in user_message or "account" in user_message:
        return "User registration and login are disabled in this free deployment due to lack of a persistent database."
    else:
        return "I'm still learning! You can ask me general health questions or about finding a doctor."

# --- Health Report Analysis Logic (DISABLED) ---
# This function is now a placeholder as the analysis capabilities are removed.
def get_health_report_summary(report_text):
    """Placeholder for health report analysis, as main functionality is disabled."""
    return {
        "summary": "Health report analysis is currently disabled in this free deployment to fit platform limitations.",
        "health_risk": "N/A",
        "diet_plan": ["Feature disabled."],
        "habits": ["Feature disabled."],
        "chart_url": None # No chart generation
    }

# --- Authentication Routes (DISABLED for Persistence) ---
# These routes will function as placeholders, not for actual user persistence.
# Frontend JS will need to be adjusted to understand these responses.
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Simulated response for signup, no actual user creation
        return jsonify({"message": "Signup is disabled for this free deployment due to lack of a persistent database."}), 200
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Simulated response for login, no actual user authentication
        return jsonify({"error": "Login is disabled for this free deployment due to lack of a persistent database."}), 401
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    # Simulate logout, clear session but it's not truly persistent
    session.pop('user_id', None)
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/get-user-id', methods=['GET'])
def get_user_id():
    # Provide a non-persistent, generic user ID for demonstration
    # In a real app with auth, you'd check session or token
    # Here, we'll just indicate "Not logged in" as a default
    return jsonify({"userId": "Not persistent"}), 200 

# --- Main Dashboard Route ---
@app.route('/')
def home():
    # No persistent authentication check; the page will always load.
    # Frontend JS handles redirecting to login if no "user_id" is found locally.
    return render_template('index.html')

# --- Other API Endpoints (Modified for Vercel - No Persistence/Analysis) ---
@app.route('/chat', methods=['POST'])
def chat():
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
    # Always return disabled message
    return jsonify({"error": "Health report upload and analysis is disabled in this free deployment to fit platform limitations."}), 400

@app.route('/upload-smartwatch-data', methods=['POST'])
def upload_smartwatch_data():
    """Handles uploading and processing of smartwatch data (DISABLED)."""
    # Always return disabled message
    return jsonify({"error": "Smartwatch data upload and analysis is disabled in this free deployment to fit platform limitations."}), 400
    
# --- Doctor Search Function ---
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

# The if __name__ == '__main__': block should be completely removed for Vercel.
# Vercel's build system runs your Flask app via 'wsgi.py' or by directly importing 'app'.
