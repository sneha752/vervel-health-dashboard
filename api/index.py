from flask import Flask, render_template, request, jsonify, session, g
import os # Required for os.environ.get()
import re # Still used for basic string matching in get_health_report_summary (placeholder)
import json 
# Removed: pandas, sklearn, io, numpy, matplotlib, uuid, sqlite3, bcrypt, traceback
# These were causing ModuleNotFoundError or exceeding Vercel's function size limit.

# --- Flask App Setup ---
app = Flask(__name__)
# Set a secret key for session management from Vercel Environment Variables.
# If SECRET_KEY is not set in Vercel, this will fall back to None or an empty string,
# which can cause session errors. Ensure it's set in Vercel.
app.secret_key = os.environ.get('SECRET_KEY')

# No custom JSON encoder needed if NumPy types are not handled directly.
# app.json_encoder = NumpyEncoder # REMOVED

# --- Machine Learning Model (DISABLED) ---
# The ML model, pandas, numpy, and sklearn are removed due to size constraints.
# The get_health_report_summary function will return placeholder data.

# --- Load Doctor Data ---
# Loads doctor information from a local JSON file.
DOCTORS_FILE = 'doctors.json'
doctors_data = []
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
    elif "report" in user_message or "analysis" in user_message:
        return "Health report analysis is disabled in this free deployment. Please ask me about other topics."
    elif "doctor" in user_message or "appointment" in user_message:
        return "I can help you find a doctor. What kind of specialist are you looking for (e.g., Cardiologist, Nutritionist, General Physician)? Type 'find doctor [specialty]'."
    elif "signup" in user_message or "login" in user_message:
        return "User registration and login are disabled in this free deployment due to platform limitations."
    else:
        return "I'm still learning! You can ask me general health questions or about finding a doctor."

# --- Health Report Analysis Logic (DISABLED) ---
# This function is now a placeholder as the analysis capabilities are removed.
def get_health_report_summary(report_text):
    return {
        "summary": "Health report analysis is disabled in this free deployment to fit platform limitations.",
        "health_risk": "N/A",
        "diet_plan": ["Feature disabled."],
        "habits": ["Feature disabled."],
        "chart_url": None # No chart will be generated
    }

# --- Authentication Routes (DISABLED for Persistence) ---
# These routes will function as placeholders, not for actual user persistence.
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        return jsonify({"message": "Signup is disabled for this free deployment due to lack of a persistent database."}), 200
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return jsonify({"error": "Login is disabled for this free deployment due to lack of a persistent database. Try again later."}), 401
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None) 
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/get-user-id', methods=['GET'])
def get_user_id():
    # Returns current session ID if exists, but it's not persistent.
    return jsonify({"userId": session.get('user_id', None)}), 200 

# --- Main Dashboard Route ---
@app.route('/')
def home():
    # No persistent authentication check, page will always load.
    return render_template('index.html')

# --- Other API Endpoints ---
@app.route('/chat', methods=['POST'])
def chat():
    user_data = request.json
    user_message = user_data['message']
    
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
    return jsonify({"error": "Health report upload and analysis is disabled in this free deployment to fit platform limitations."}), 400

@app.route('/upload-smartwatch-data', methods=['POST'])
def upload_smartwatch_data():
    return jsonify({"error": "Smartwatch data upload and analysis is disabled in this free deployment to fit platform limitations."}), 400
    
# --- Doctor Search Function ---
def find_doctor_by_specialty(specialty_query):
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

# Removed if __name__ == '__main__': block as it's not needed for Vercel deployment.
