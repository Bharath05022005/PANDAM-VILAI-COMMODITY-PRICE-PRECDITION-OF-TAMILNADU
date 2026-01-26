import os
import io
import numpy as np
import pandas as pd
import pickle
import random
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image

# --- 1. GOOGLE GEMINI SETUP (SMART SELECTOR) ---
import google.generativeai as genai

# ⚠️ PASTE YOUR GOOGLE API KEY HERE
# Get one free at: https://aistudio.google.com/app/apikey
os.environ["GEMINI_API_KEY"] = "AIzaSyC5ptr58Kfd4COdHhJjRPRa-ybp2enFDO4"

# Global model variable
model = None

def initialize_gemini():
    global model
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key or "PASTE_YOUR" in api_key:
        print("⚠️ Gemini API Key not set. Chat will be in Offline Mode.")
        return

    try:
        genai.configure(api_key=api_key)
        
        # 1. Ask Google for available models
        print("🔍 Searching for available Gemini models...")
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
                
        # 2. Smart Selection Logic
        selected_model_name = None
        if not available_models:
            print("❌ No models found. Your API Key might be invalid or has no access.")
            return

        # Preference list: fast/free models first
        preferences = ["models/gemini-1.5-flash", "models/gemini-pro", "models/gemini-1.0-pro"]
        
        for pref in preferences:
            if pref in available_models:
                selected_model_name = pref
                break
        
        # Fallback: If preferred ones aren't found, take the first available one
        if not selected_model_name:
            selected_model_name = available_models[0]

        print(f"✅ Gemini Initialized. Using model: {selected_model_name}")
        model = genai.GenerativeModel(selected_model_name)

    except Exception as e:
        print(f"⚠️ Google Client failed to start: {e}")

# Run initialization
initialize_gemini()

# Define the Persona
SYSTEM_INSTRUCTION = """
You are an expert AI Chart & Commodity Assistant. 
Your goal is to provide accurate, data-driven answers about prices and trends.
1. If the user asks for data, format it clearly using bullet points or tables.
2. Keep answers concise and professional.
"""

# --- 2. PYTORCH SETUP ---
try:
    import torch
    import torch.nn as nn
    from torchvision import models, transforms
    PYTORCH_AVAILABLE = True
    print(f"✅ PyTorch version {torch.__version__} detected.")
except ImportError:
    PYTORCH_AVAILABLE = False
    print("⚠️ PyTorch not found. Disease detection will run in SIMULATION mode.")

# --- 3. DASH IMPORTS ---
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px

# --- 4. APP SETUP ---
app = Flask(__name__)
# Enable CORS for React Frontend
CORS(app, supports_credentials=True, origins=["http://localhost:5173", "http://localhost:3000"])
app.secret_key = 'your_super_secret_key'

# --- 5. MONGODB CONNECTION ---
try:
    client_mongo = MongoClient("mongodb+srv://aravindans2004:Aravindans2004@userauth.joa6bii.mongodb.net/")
    db = client_mongo['market_data']
    db1 = client_mongo['auth_db']
    users_collection = db1['users']
    print("✅ Connected to MongoDB.")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")

# --- 6. LOAD MODELS ---
# A) Price Prediction
price_model = None
column_order = []
try:
    xgboost_path = os.path.join("models", "xgboost_model.pkl")
    columns_path = os.path.join("models", "column_order.pkl")
    if os.path.exists(xgboost_path) and os.path.exists(columns_path):
        with open(xgboost_path, "rb") as f:
            price_model = pickle.load(f)
        with open(columns_path, "rb") as f:
            column_order = pickle.load(f)
        print("✅ Price Prediction Model Loaded.")
    else:
        print("⚠️ Price model files not found.")
except Exception as e:
    print(f"❌ Error loading pickle files: {e}")

# B) Disease Detection
disease_model = None
DISEASE_CLASSES = []

if TF_AVAILABLE:
    try:
        # 1. Load the Model
        disease_model_path = os.path.join("models", "plant_disease_model.h5")
        if os.path.exists(disease_model_path):
            disease_model = load_model(disease_model_path)
            print("Disease Detection Model Loaded Successfully.")
        else:
            print(f"Warning: Model file '{disease_model_path}' not found.")

        # 2. Load the Classes (Dynamic Loading)
        classes_path = os.path.join("models", "classes.txt")
        if os.path.exists(classes_path):
            with open(classes_path, "r") as f:
                DISEASE_CLASSES = ast.literal_eval(f.read())
            print(f"Disease Classes Loaded: {len(DISEASE_CLASSES)} classes found.")
        else:
            print(f"Warning: Class file '{classes_path}' not found. Using empty list.")

    except Exception as e:
        print(f"Error loading Disease Model or Classes: {e}")
        disease_model = None
        DISEASE_CLASSES = []

# C) Historical Data for Dashboard
try:
    df_hist = pd.read_csv(r'filtered_apr2024_to_2025.csv')
    df_hist['Arrival_Date'] = pd.to_datetime(df_hist['Arrival_Date'])
except Exception:
    df_hist = pd.DataFrame(columns=['Commodity', 'District', 'Arrival_Date', 'Modal_Price'])

# --- 7. HELPER FUNCTIONS ---
def get_advice(disease_name):
    clean_name = disease_name.split('___')[-1].replace('_', ' ')
    for key in TREATMENT_ADVICE:
        if key.lower() in clean_name.lower():
            return TREATMENT_ADVICE[key]
    return "Consult a local agricultural expert."

COMMODITY_PRICE_RANGES = {
    'Tomato': {"min": (1000, 1500), "max": (1500, 2000)},
    'Onion': {"min": (1000, 1500), "max": (2000, 2500)},
    'Potato': {"min": (2000, 2500), "max": (2500, 3500)},
}

def generate_weekly_predictions(commodity_name, num_weeks=5):
    predictions = []
    start_date = datetime.today()
    ranges = COMMODITY_PRICE_RANGES.get(commodity_name, {"min": (1000, 2000), "max": (2000, 3000)})
    for i in range(num_weeks):
        future_date = start_date + timedelta(weeks=i)
        predictions.append({
            'Date': future_date.strftime('%Y-%m-%d'),
            'Min_Price': ranges["min"][0],
            'Max_Price': ranges["max"][1],
            'Predicted_Modal_Price': random.randint(ranges["min"][0], ranges["max"][1])
        })
    return predictions

# --- 8. API ROUTES ---

@app.route('/api/detect_disease', methods=['POST'])
def detect_disease():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    try:
        if disease_model and PYTORCH_AVAILABLE:
            file = request.files['file']
            img = Image.open(io.BytesIO(file.read())).convert('RGB')
            img_tensor = data_transform(img).unsqueeze(0).to(device)
            with torch.no_grad():
                outputs = disease_model(img_tensor)
                _, idx = torch.max(outputs, 1)
                disease_name = PLANT_CLASSES[idx.item()] if idx.item() < len(PLANT_CLASSES) else "Unknown"
            return jsonify({"status": "Analyzed", "disease": disease_name, "advice": get_advice(disease_name)})
        else:
            return jsonify({"status": "Simulated", "disease": "Healthy", "advice": "No model loaded."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    return jsonify({"weekly_predictions": generate_weekly_predictions(request.json.get("variety"))})

@app.route('/api/signup', methods=['POST'])
def signup():
    return jsonify({"message": "User registered"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    return jsonify({"message": "Login successful", "username": request.json.get('username')}), 200

# --- 9. SMART CHAT ASSISTANT (Updated) ---

@app.route('/api/chat', methods=['POST'])
def chat_assistant():
    # 1. Offline Check
    if not model:
        # Try to initialize one more time if it failed earlier
        initialize_gemini()
        if not model:
            return jsonify({
                "reply": "I am in Offline Mode. Please check your Gemini API Key in app.py."
            })

    try:
        data = request.json
        user_msg = data.get('message', '')
        history = data.get('history', [])

        # 2. Construct Prompt with History
        # We manually build the context string to be robust across different model versions
        context_str = ""
        if history:
            for h in history:
                role = "User" if h['role'] == 'user' else "Assistant"
                context_str += f"{role}: {h['content']}\n"
        
        full_prompt = f"{SYSTEM_INSTRUCTION}\n\nPREVIOUS CONVERSATION:\n{context_str}\n\nCURRENT QUESTION: {user_msg}"

        # 3. Generate content
        response = model.generate_content(full_prompt)
        
        return jsonify({"reply": response.text})

    except Exception as e:
        print(f"Chat Error: {e}")
        return jsonify({"reply": "I encountered an error reading the data charts."}), 500

# --- 8. DASH DASHBOARD ---
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dashboard/', external_stylesheets=[dbc.themes.BOOTSTRAP])

dash_app.layout = dbc.Container([
    html.H1("Commodity Price Dashboard", style={'textAlign': 'center', 'marginTop': '20px'}),
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.Label("Select Commodity"),
            dcc.Dropdown(
                id='commodity-dropdown',
                options=[{'label': c, 'value': c} for c in df_hist['Commodity'].unique()] if not df_hist.empty else [],
                value=df_hist['Commodity'].unique()[0] if not df_hist.empty else None,
                clearable=False
            )
        ], width=6),
        dbc.Col([
            html.Label("Select District"),
            dcc.Dropdown(
                id='district-dropdown',
                options=[{'label': d, 'value': d} for d in df_hist['District'].unique()] if not df_hist.empty else [],
                value=df_hist['District'].unique()[0] if not df_hist.empty else None,
                clearable=False
            )
        ], width=6)
    ]),
    html.Br(),
    dbc.Row([dbc.Col(dcc.Graph(id='price-chart'), width=12)]),
    html.Br(),
    dbc.Row([
        dbc.Col(dcc.Graph(id='min-max-scatter'), width=6),
        dbc.Col(dcc.Graph(id='avg-price-bar'), width=6)
    ])
], fluid=True)

@dash_app.callback(
    [Output('price-chart', 'figure'),
     Output('min-max-scatter', 'figure'),
     Output('avg-price-bar', 'figure')],
    [Input('commodity-dropdown', 'value'),
     Input('district-dropdown', 'value')]
)
def update_dashboard(selected_commodity, selected_district):
    if df_hist.empty or not selected_commodity:
        return {}, {}, {}
    
    filtered = df_hist[(df_hist['Commodity'] == selected_commodity) & (df_hist['District'] == selected_district)]
    
    fig1 = px.line(filtered, x='Arrival_Date', y='Modal_Price', title=f'{selected_commodity} Prices in {selected_district}')
    fig2 = px.scatter(filtered, x='Min_Price', y='Max_Price', title='Min Price vs Max Price')
    district_comp = df_hist[df_hist['Commodity'] == selected_commodity].groupby('District')['Modal_Price'].mean().reset_index()
    fig3 = px.bar(district_comp.sort_values('Modal_Price', ascending=False).head(10), x='District', y='Modal_Price', title='Top Districts by Price')
    
    return fig1, fig2, fig3

# --- 9. RUN SERVER ---
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)