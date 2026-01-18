import os
import io
import numpy as np
import pandas as pd
import pickle
import random
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image

# --- 1. PYTORCH SETUP (For .pth Model) ---
try:
    import torch
    import torch.nn as nn
    from torchvision import models, transforms
    PYTORCH_AVAILABLE = True
    print(f"✅ PyTorch version {torch.__version__} detected.")
except ImportError:
    PYTORCH_AVAILABLE = False
    print("⚠️ PyTorch not found. Disease detection will run in SIMULATION mode.")

# --- 2. DASH IMPORTS ---
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px

# --- 3. APP SETUP ---
app = Flask(__name__)
# Enable CORS for React Frontend
CORS(app, supports_credentials=True, origins=["http://localhost:5173", "http://localhost:3000"])
app.secret_key = 'your_super_secret_key'

# --- 4. MONGODB CONNECTION ---
try:
    client = MongoClient("mongodb+srv://aravindans2004:Aravindans2004@userauth.joa6bii.mongodb.net/")
    db = client['market_data']
    db1 = client['auth_db']
    users_collection = db1['users']
    print("✅ Connected to MongoDB.")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")

# --- 5. LOAD MODELS ---

# A) Price Prediction Model (XGBoost .pkl)
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
        print("⚠️ Price model files not found. Using Simulation.")
except Exception as e:
    print(f"❌ Error loading pickle files: {e}")

# B) Disease Detection Model (PyTorch .pth)
disease_model = None
device = torch.device("cuda" if torch.cuda.is_available() and PYTORCH_AVAILABLE else "cpu")

# Standard 38 Classes
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

# Treatment Advice
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
            print("Loading ResNet34 Architecture...")
            disease_model = models.resnet34(pretrained=False)
            num_ftrs = disease_model.fc.in_features
            disease_model.fc = nn.Linear(num_ftrs, len(PLANT_CLASSES))
            
            # Load Weights
            disease_model.load_state_dict(torch.load(pth_path, map_location=device))
            disease_model = disease_model.to(device)
            disease_model.eval()
            print("✅ PyTorch Disease Model Loaded Successfully.")
        except Exception as e:
            print(f"❌ Error loading .pth file: {e}")
    else:
        print(f"⚠️ Model file not found at {pth_path}")

# Load the model immediately
load_pytorch_model()

# Image Transforms
if PYTORCH_AVAILABLE:
    data_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

# C) Historical Data for Dashboard
try:
    df_hist = pd.read_csv(r'filtered_apr2024_to_2025.csv')
    df_hist['Arrival_Date'] = pd.to_datetime(df_hist['Arrival_Date'])
    df_hist['Year'] = df_hist['Arrival_Date'].dt.year
    df_hist['Month'] = df_hist['Arrival_Date'].dt.month
except Exception as e:
    print(f"Warning: Historical CSV not found. {e}")
    df_hist = pd.DataFrame(columns=['Commodity', 'District', 'Arrival_Date', 'Modal_Price'])

# --- 6. HELPER FUNCTIONS ---

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
    # Add more defaults as needed
}

def generate_weekly_predictions(commodity_name, num_weeks=5):
    predictions = []
    start_date = datetime.today()
    
    # Get range or default
    ranges = COMMODITY_PRICE_RANGES.get(commodity_name, {"min": (1000, 2000), "max": (2000, 3000)})
    
    for i in range(num_weeks):
        future_date = start_date + timedelta(weeks=i)
        
        # Prepare inputs for XGBoost
        future_data = {
            'Min_Price': [random.randint(*ranges["min"])],
            'Max_Price': [random.randint(*ranges["max"])],
            'Arrival_Year': [future_date.year],
            'Arrival_Month': [future_date.month],
            'Arrival_Day': [future_date.day]
        }
        
        # One-Hot Encoding
        for col in column_order:
            if col not in future_data: future_data[col] = [0]
        
        comm_col = f'Commodity_{commodity_name}'
        if comm_col in column_order: future_data[comm_col] = [1]
        
        # Predict
        if price_model:
            try:
                future_df = pd.DataFrame(future_data)[column_order]
                future_price = price_model.predict(future_df)[0]
            except:
                future_price = random.randint(future_data['Min_Price'][0], future_data['Max_Price'][0])
        else:
            future_price = random.randint(future_data['Min_Price'][0], future_data['Max_Price'][0])
            
        predictions.append({
            'Date': future_date.strftime('%Y-%m-%d'),
            'Min_Price': future_data['Min_Price'][0],
            'Max_Price': future_data['Max_Price'][0],
            'Predicted_Modal_Price': round(float(future_price), 2)
        })
    return predictions

# --- 7. API ROUTES ---

@app.route('/api/detect_disease', methods=['POST'])
def detect_disease():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        # Read Image
        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        
        if disease_model and PYTORCH_AVAILABLE:
            # 1. Preprocess
            img_tensor = data_transform(img).unsqueeze(0).to(device)
            
            # 2. Predict
            with torch.no_grad():
                outputs = disease_model(img_tensor)
                probs = torch.nn.functional.softmax(outputs, dim=1)
                conf, idx = torch.max(probs, 1)
                
                class_index = idx.item()
                confidence = conf.item()
            
            # 3. Map Result
            if class_index < len(PLANT_CLASSES):
                disease_name = PLANT_CLASSES[class_index]
            else:
                disease_name = "Unknown"
            
            readable = disease_name.replace("___", " - ").replace("_", " ")
            status = "Healthy" if "healthy" in disease_name.lower() else "Infected"
            advice = get_advice(disease_name)

            return jsonify({
                "status": status,
                "disease": readable,
                "confidence": f"{confidence*100:.1f}%",
                "advice": advice
            })
        else:
            # Fallback Simulation
            return jsonify({
                "status": "Infected",
                "disease": "Simulation: Late Blight",
                "confidence": "95.0%",
                "advice": "Model not loaded. Using Simulation mode."
            })

    except Exception as e:
        print(f"Prediction Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        variety = data.get("variety")
        # Generate predictions (uses Model if loaded, else Fallback)
        weekly_predictions = generate_weekly_predictions(variety, num_weeks=5)
        return jsonify({"weekly_predictions": weekly_predictions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- AUTH ROUTES ---
@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        username = data.get('username')
        if users_collection.find_one({"username": username}):
            return jsonify({"error": "Username already exists"}), 400
        hashed_password = generate_password_hash(data.get('password'))
        users_collection.insert_one({
            "username": username,
            "email": data.get('email'),
            "password": hashed_password
        })
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        user = users_collection.find_one({"username": data.get('username')})
        if not user or not check_password_hash(user['password'], data.get('password')):
            return jsonify({"error": "Invalid credentials"}), 401
        session["user"] = data.get('username')
        return jsonify({"message": "Login successful", "username": data.get('username')}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop("user", None)
    return jsonify({"message": "Logged out successfully"}), 200

# --- CHATBOT ---
@app.route('/api/chat', methods=['POST'])
def chat_assistant():
    try:
        data = request.json
        user_message = data.get('message', '').lower()
        
        # Extract keywords
        found_commodity = next((c for c in df_hist['Commodity'].unique() if c.lower() in user_message), None)
        found_district = next((d for d in df_hist['District'].unique() if d.lower() in user_message), None)

        response_text = ""
        
        if "highest" in user_message or "max" in user_message:
            if found_commodity:
                subset = df_hist[df_hist['Commodity'] == found_commodity]
                max_row = subset.loc[subset['Modal_Price'].idxmax()]
                response_text = f"Highest price for {found_commodity}: ₹{max_row['Modal_Price']} in {max_row['District']}."
            else:
                max_row = df_hist.loc[df_hist['Modal_Price'].idxmax()]
                response_text = f"Highest overall price: ₹{max_row['Modal_Price']} ({max_row['Commodity']})."
        elif "hello" in user_message:
            response_text = "Hello! Ask me about market prices and trends."
        else:
            response_text = "I can tell you about highest/lowest prices if you mention a commodity."
            
        return jsonify({"reply": response_text})

    except Exception as e:
        return jsonify({"reply": "Sorry, I couldn't process that."}), 500

# --- DASHBOARD ---
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dashboard/', external_stylesheets=[dbc.themes.BOOTSTRAP])
dash_app.layout = dbc.Container([
    html.H1("Market Dashboard", className="text-center my-4"),
    dbc.Row([
        dbc.Col(dcc.Dropdown(id='c-drop', options=[{'label':c, 'value':c} for c in df_hist['Commodity'].unique()], value=df_hist['Commodity'].unique()[0] if not df_hist.empty else None), width=6),
        dbc.Col(dcc.Dropdown(id='d-drop'), width=6)
    ]),
    dcc.Graph(id='price-chart')
])

@dash_app.callback(Output('d-drop', 'options'), Input('c-drop', 'value'))
def update_dist(comm):
    if not comm: return []
    return [{'label': d, 'value': d} for d in df_hist[df_hist['Commodity']==comm]['District'].unique()]

@dash_app.callback(Output('price-chart', 'figure'), [Input('c-drop', 'value'), Input('d-drop', 'value')])
def update_graph(comm, dist):
    if not comm: return {}
    d = df_hist[df_hist['Commodity'] == comm]
    if dist: d = d[d['District'] == dist]
    return px.line(d, x='Arrival_Date', y='Modal_Price', title=f'{comm} Prices')

# --- 8. RUN SERVER (WITH WAITRESS) ---
if __name__ == "__main__":
    from waitress import serve
    print("✅ Server running on http://0.0.0.0:5000")
    serve(app, host='0.0.0.0', port=5000, threads=6)
