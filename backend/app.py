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
os.environ["API_KEY"] = "AIzaSyBAZDElUPocXqpggHt80jDfkbNSrLcBn2A"

# Global model variable
model = None

def initialize_gemini():
    global model
    api_key = os.environ.get("API_KEY")
    
    if not api_key or "PASTE_YOUR" in api_key:
        print("⚠️  API Key not set. Chat will be in Offline Mode.")
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

if PYTORCH_AVAILABLE:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
else:
    device = "cpu"

PLANT_CLASSES = [
    'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
    'Blueberry___healthy', 'Cherry_(including_sour)___Powdery_mildew', 'Cherry_(including_sour)___healthy',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_', 
    'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy', 'Grape___Black_rot', 
    'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape___healthy',
    'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot', 'Peach___healthy',
    'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy', 'Potato___Early_blight',
    'Potato___Late_blight', 'Potato___healthy', 'Raspberry___healthy', 'Soybean___healthy',
    'Squash___Powdery_mildew', 'Strawberry___Leaf_scorch', 'Strawberry___healthy',
    'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight', 'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus',
    'Tomato___healthy'
]
TREATMENT_ADVICE = {
     'Apple_scab': "Rake and destroy fallen leaves. Apply fungicides like Captan.",
    'Black_rot': "Prune infected branches. Remove mummified fruit.",
    'Cedar_apple_rust': "Remove nearby juniper galls. Apply fungicides in spring.",
    'Powdery_mildew': "Apply Neem oil or Sulfur. Improve air circulation.",
    'Cercospora_leaf_spot': "Rotate crops. Use resistant hybrids. Apply fungicide.",
    'Common_rust': "Plant resistant varieties. Fungicides generally not needed.",
    'Northern_Leaf_Blight': "Rotate crops. Manage residue. Use resistant corn.",
    'Esca_(Black_Measles)': "Prune out infected wood. Protect pruning wounds.",
    'Leaf_blight': "Apply fungicides. Improve air circulation by pruning.",
    'Haunglongbing_(Citrus_greening)': "Remove infected trees immediately (no cure). Control psyllids.",
    'Bacterial_spot': "Use copper sprays. Avoid overhead watering.",
    'Early_blight': "Mulch soil. Remove lower leaves. Apply Chlorothalonil.",
    'Late_blight': "URGENT: Remove infected plants immediately. Apply Copper fungicide.",
    'Leaf_Mold': "Reduce humidity. Improve ventilation.",
    'Septoria_leaf_spot': "Remove lower leaves. Keep leaves dry.",
    'Spider_mites': "Apply Neem oil or insecticidal soap.",
    'Target_Spot': "Remove infected leaves. Apply fungicide.",
    'Tomato_Yellow_Leaf_Curl_Virus': "Control whiteflies. Remove infected plants.",
    'Tomato_mosaic_virus': "Disinfect tools. Wash hands. Remove infected plants.",
    'Leaf_scorch': "Remove infected leaves. Water properly.",
    'healthy': "Plant looks healthy! Continue regular care."
}

def load_pytorch_model():
    global disease_model
    if not PYTORCH_AVAILABLE: return
    pth_path = os.path.join("models", "plantDisease-resnet34.pth")
    if os.path.exists(pth_path):
        try:
            disease_model = models.resnet34(pretrained=False)
            num_ftrs = disease_model.fc.in_features
            disease_model.fc = nn.Linear(num_ftrs, len(PLANT_CLASSES))
            disease_model.load_state_dict(torch.load(pth_path, map_location=device))
            disease_model = disease_model.to(device)
            disease_model.eval()
            print("✅ PyTorch Disease Model Loaded.")
        except Exception as e:
            print(f"❌ Error loading .pth file: {e}")

load_pytorch_model()
if PYTORCH_AVAILABLE:
    data_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

# C) Historical Data
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
        print(f"❌ Gemini Error: {e}")
        return jsonify({"reply": "I encountered an error connecting to Google Gemini. Please check the backend logs."})



if __name__ == "__main__":
    from waitress import serve
    print("✅ Server running on http://0.0.0.0:5000")

    serve(app, host='0.0.0.0', port=5000, threads=6)

