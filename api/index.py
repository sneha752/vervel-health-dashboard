from flask import Flask, render_template, request, jsonify, redirect, url_for, session, g
import pandas as pd
import re
from sklearn.tree import DecisionTreeClassifier
import io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import uuid # For generating unique filenames for charts
# import sqlite3 # COMMENTED OUT: Not compatible with Vercel's ephemeral filesystem for persistence
# import bcrypt # COMMENTED OUT: Not needed without user authentication for persistence
import json 
# import traceback # COMMENTED OUT: Can be useful for local debugging, but not necessary for Vercel runtime logs here

# --- Custom JSON Encoder for NumPy Types ---
# This class extends the default JSONEncoder to handle NumPy specific types (int64, float64)
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        # Handle pandas NaN values, convert to None for JSON
        elif pd.isna(obj):
            return None
        return json.JSONEncoder.default(self, obj)
# -------------------------------------------

# --- Flask App Setup ---
app = Flask(__name__)
# Set a secret key for session management from Vercel Environment Variables
# IMPORTANT: This must be set securely in Vercel project settings, not generated on each function invocation.
app.secret_key = os.environ.get('SECRET_KEY', 'a_very_secret_key_fallback_for_dev') 

# --- Configure Flask to use the custom JSON encoder ---
# This line is CRUCIAL for jsonify to work with NumPy types
app.json_encoder = NumpyEncoder 

# --- SQLite Database Configuration (COMMENTED OUT for Vercel) ---
# DATABASE = 'health_data.db'

# def get_db():
#     """Establishes a database connection or returns the existing one."""
#     db = getattr(g, '_database', None)
#     if db is None:
#         db = g._database = sqlite3.connect(DATABASE)
#         db.row_factory = sqlite3.Row # This allows access to columns by name
#     return db

# @app.teardown_appcontext
# def close_connection(exception):
#     """Closes the database connection at the end of the request."""
#     db = getattr(g, '_database', None)
#     if db is not None:
#         db.close()

# def init_db():
#     """Initializes the database schema if tables do not exist."""
#     with app.app_context():
#         db = get_db()
#         cursor = db.cursor()
#         # Create users table for authentication
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS users (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 email TEXT UNIQUE NOT NULL,
#                 password TEXT NOT NULL
#             )
#         ''')
#         # Create health_reports table to store user health report summaries
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS health_reports (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 user_id INTEGER NOT NULL,
#                 timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
#                 report_content TEXT,
#                 summary TEXT,
#                 health_risk TEXT,
#                 diet_plan TEXT,
#                 habits TEXT, -- Stored as JSON string
#                 chart_filename TEXT,
#                 FOREIGN KEY (user_id) REFERENCES users(id)
#             )
#         ''')
#         # Create smartwatch_data table to store user smartwatch data
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS smartwatch_data (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 user_id INTEGER NOT NULL,
#                 timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
#                 filename TEXT,
#                 data TEXT, -- Stored as JSON string
#                 FOREIGN KEY (user_id) REFERENCES users(id)
#             )
#         ''')
#         db.commit()

# --- Machine Learning Model (Simplified for Demonstration) ---
# A very basic Decision Tree Classifier for health risk prediction
data = {
    'cholesterol': [220, 180, 250, 190, 210, 160],
    'blood_pressure': [140, 120, 160, 130, 150, 110],
    'risk': ['high', 'low', 'high', 'low', 'medium', 'low']
}
df = pd.DataFrame(data)

X = df[['cholesterol', 'blood_pressure']]
y = df['risk']

model = DecisionTreeClassifier()
model.fit(X, y)
# -----------------------------------------------------------

# --- Load Doctor Data ---
# Loads doctor information from a local JSON file
DOCTORS_FILE = 'doctors.json'
doctors_data = []
# Ensure doctors.json is loaded correctly, handling potential Vercel path issues
# Using app.root_path for Vercel compatibility
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
        return "Please upload your health report on the right-hand panel, and I will analyze it for you."
    elif "doctor" in user_message or "appointment" in user_message:
        return "I can help you find a doctor. What kind of specialist are you looking for (e.g., Cardiologist, Nutritionist, General Physician)? Type 'find doctor [specialty]'."
    else:
        return "I'm still learning! Please ask me about heart rate, blood pressure, or uploading reports."

# --- Health Report Analysis Logic ---
def get_health_report_summary(report_text):
    """Analyzes health report text and generates a summary and chart."""
    cholesterol = re.search(r'cholesterol:\s*(\d+)', report_text, re.IGNORECASE)
    blood_pressure_sys = re.search(r'blood pressure:\s*(\d+)/(\d+)', report_text, re.IGNORECASE)

    cholesterol_val = int(cholesterol.group(1)) if cholesterol else 0 
    blood_pressure_val = int(blood_pressure_sys.group(1)) if blood_pressure_sys else 0 
    
    summary = "Report analysis successful. Key metrics extracted:"
    health_risk = "unknown"
    diet_plan = ["Eat more greens.", "Reduce processed foods.", "Stay hydrated with 8 glasses of water."]
    habits = ["Walk for 30 minutes daily.", "Get at least 7 hours of sleep.", "Practice mindfulness."]
    
    if cholesterol_val is not None and blood_pressure_val is not None:
        prediction = model.predict([[cholesterol_val, blood_pressure_val]])
        health_risk = prediction[0]
        summary += f" Cholesterol: {cholesterol_val}, Blood Pressure: {blood_pressure_val}."
    
    if health_risk == "high":
        summary += " Detected high-risk indicators. Consult a doctor immediately."
        diet_plan.append("Incorporate more oats and fish into your diet.")
        habits.append("Monitor vitals daily.")
    elif health_risk == "medium":
        summary += " Detected medium-risk indicators. Follow a balanced lifestyle."

    # Generate a unique filename for the chart to avoid caching issues
    chart_filename = f"health_chart_{uuid.uuid4().hex}.png" 
    # Use a temporary directory for chart saving on serverless, if `static` isn't writable
    # For Vercel, static directory is often read-only for writes after deployment.
    # We will attempt to save in static, but if it fails, the chart won't be saved.
    chart_path = os.path.join(app.root_path, 'static', chart_filename)
    
    plt.figure(figsize=(6, 4))
    plt.bar(['Cholesterol', 'Blood Pressure'], [cholesterol_val, blood_pressure_val], color=['blue', 'red'])
    plt.title('Key Vitals from Report')
    plt.ylabel('Value')
    plt.ylim(0, 300)
    
    try:
        # Create static directory if it doesn't exist (e.g., in a temporary writeable location)
        # This might not be needed if app.root_path/static is correctly mapped and writable by Vercel
        # However, for charts, Vercel's ephemeral file system will delete these.
        # Consider external storage for persistent charts.
        if not os.path.exists(os.path.join(app.root_path, 'static')):
            os.makedirs(os.path.join(app.root_path, 'static'))
        
        plt.savefig(chart_path)
        print(f"Chart saved to: {chart_path}") # Debugging
    except Exception as e:
        print(f"WARNING: Could not save chart to {chart_path}: {e}")
        chart_filename = None # Chart won't be available

    plt.close() # Close the plot to free memory
    
    return {
        "summary": summary,
        "health_risk": health_risk,
        "diet_plan": diet_plan,
        "habits": habits,
        "chart_url": url_for('static', filename=chart_filename) if chart_filename else None
    }

# --- Authentication Routes (Modified for Vercel - No Persistence) ---

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handles user registration (Non-functional on Vercel without persistent DB)."""
    if request.method == 'POST':
        # These operations would normally save to DB, but are disabled for Vercel's free tier
        # email = request.json.get('email',)
        # password = request.json.get('password')
        return jsonify({"message": "Signup is disabled for this free deployment due to lack of a persistent database."}), 200
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login (Non-functional on Vercel without persistent DB)."""
    if request.method == 'POST':
        # These operations would normally check DB, but are disabled for Vercel's free tier
        # email = request.json.get('email')
        # password = request.json.get('password')
        return jsonify({"error": "Login is disabled for this free deployment due to lack of a persistent database. Try again later."}), 401
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    """Handles user logout by clearing the session."""
    session.pop('user_id', None) # Session will still clear, but won't affect persistent login
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/get-user-id', methods=['GET'])
def get_user_id():
    """Returns a placeholder user ID as persistent login is not supported."""
    # Since sessions are ephemeral on Vercel, persistent user ID is not available
    # For the purpose of getting the dashboard to load, we'll return a placeholder.
    return jsonify({"userId": session.get('user_id', None)}), 200 # Returns current session ID if exists, but it's not persistent

# --- Protected Route for Dashboard (main page) ---
@app.route('/')
def home():
    """Renders the main dashboard page."""
    # Authentication check removed as persistent login is not supported.
    # The page will always load.
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
    """Handles uploading and processing of health reports (Data will NOT be saved persistently)."""
    # Removed session check as persistent auth is not supported.
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        file_content = file.read().decode("utf-8")
        report_data = get_health_report_summary(file_content)
        
        # user_id = session['user_id'] # User ID won't be persistent
        # db = get_db() # No persistent database connection
        # cursor = db.cursor()
        
        # chart_filename = report_data.get('chart_url', '').split('/')[-1]

        try:
            # All database insert operations are COMMENTED OUT
            # cursor.execute('''
            #     INSERT INTO health_reports (user_id, report_content, summary, health_risk, diet_plan, habits, chart_filename)
            #     VALUES (?, ?, ?, ?, ?, ?, ?)
            # ''', (user_id, file_content, report_data['summary'], report_data['health_risk'], 
            #         json.dumps(report_data['diet_plan'], cls=NumpyEncoder), 
            #         json.dumps(report_data['habits'], cls=NumpyEncoder), chart_filename)) 
            # db.commit()
            print("INFO: Health report data processed, but NOT saved due to ephemeral storage.") # Debugging
            return jsonify(report_data) # Still return analysis data to frontend
        except Exception as e:
            # print(f"DEBUG: Error inserting health report: {e}") # Debugging
            # traceback.print_exc() # Debugging
            return jsonify({"error": f"Error processing health report: {str(e)}. Data not saved due to ephemeral storage."}), 400
    
    return jsonify({"error": "Something went wrong during file processing."}), 500


@app.route('/upload-smartwatch-data', methods=['POST'])
def upload_smartwatch_data():
    """Handles uploading and processing of smartwatch data (Data will NOT be saved persistently)."""
    # Removed session check as persistent auth is not supported.
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.csv'):
        try:
            df_smartwatch = pd.read_csv(io.StringIO(file.read().decode('utf-8')))
            
            # Check for specific columns to determine if it's an activity file
            activity_columns = ['TotalSteps', 'TotalDistance', 'VeryActiveMinutes', 
                                 'FairlyActiveMinutes', 'LightlyActiveMinutes', 'SedentaryMinutes', 'Calories']
            
            is_activity_file = all(col in df_smartwatch.columns for col in activity_columns)

            analysis_summary = {}

            if is_activity_file:
                # Perform detailed activity analysis
                analysis_summary['type'] = 'activity_data'
                analysis_summary['average_daily_steps'] = float(df_smartwatch['TotalSteps'].mean()) if 'TotalSteps' in df_smartwatch.columns else 'N/A'
                analysis_summary['average_daily_calories'] = float(df_smartwatch['Calories'].mean()) if 'Calories' in df_smartwatch.columns else 'N/A'
                analysis_summary['total_very_active_minutes'] = int(df_smartwatch['VeryActiveMinutes'].sum()) if 'VeryActiveMinutes' in df_smartwatch.columns else 'N/A'
                analysis_summary['total_sedentary_minutes'] = int(df_smartwatch['SedentaryMinutes'].sum()) if 'SedentaryMinutes' in df_smartwatch.columns else 'N/A'
                analysis_summary['message'] = "Activity data analyzed successfully!"
            else:
                # Default smartwatch data analysis (e.g., heart rate, steps from simpler files)
                analysis_summary['type'] = 'generic_smartwatch_data'
                analysis_summary['average_heart_rate'] = float(df_smartwatch['heart_rate'].mean()) if 'heart_rate' in df_smartwatch.columns else 'N/A'
                analysis_summary['total_steps'] = int(df_smartwatch['steps'].sum()) if 'steps' in df_smartwatch.columns else 'N/A'
                analysis_summary['message'] = "Generic smartwatch data analyzed successfully!"


            # smartwatch_data_list = df_smartwatch.to_dict(orient='records') # Not saving to DB
            # user_id = session['user_id'] # Not saving to DB
            # db = get_db() # Not saving to DB
            # cursor = db.cursor() # Not saving to DB
            
            # json_data_to_store = json.dumps(smartwatch_data_list, cls=NumpyEncoder) # Not saving to DB
            
            # All database insert operations are COMMENTED OUT
            # cursor.execute('''
            #     INSERT INTO smartwatch_data (user_id, filename, data)
            #     VALUES (?, ?, ?)
            # ''', (user_id, file.filename, json_data_to_store)) 
            # db.commit()
            print("INFO: Smartwatch data processed, but NOT saved due to ephemeral storage.") # Debugging
            
            return jsonify({
                "message": f"Smartwatch data '{file.filename}' uploaded and processed successfully!",
                "summary": analysis_summary # Return the detailed analysis summary
            })

        except Exception as e:
            # print(f"DEBUG: Error processing smartwatch data: {e}") # Debugging
            # traceback.print_exc() # Debugging
            return jsonify({"error": f"Error processing smartwatch data: {str(e)}. Data not saved due to ephemeral storage."}), 400
    
    return jsonify({"error": "Invalid file type. Please upload a CSV file."}), 400

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

# Removed the if __name__ == '__main__': block as Vercel handles app execution
# and the Flask app object is exposed directly.
# The init_db() call would also cause errors due to no persistence.
