from flask import Flask, request, jsonify, session, send_file
import pickle
import pandas as pd
from datetime import datetime, timedelta
import random
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import os
from io import BytesIO
from PIL import Image
import numpy as np
import ast  # Needed to read the classes.txt file safely

# --- 1. LOAD OPTIONAL LIBRARIES (TensorFlow) ---
try:
    import tensorflow as tf
    from tensorflow.keras.models import load_model
    from tensorflow.keras.preprocessing import image
    TF_AVAILABLE = True
except ImportError:
    print("TensorFlow not installed. Disease detection will run in DEMO mode.")
    TF_AVAILABLE = False

# --- 2. DASH IMPORTS ---
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px

# --- 3. APP SETUP ---
app = Flask(__name__)
# Enable CORS for React Frontend (Port 5173) with credentials allowed
CORS(app, supports_credentials=True, origins=["http://localhost:5173"])
app.secret_key = 'your_secret_key'

# --- 4. MONGODB CONNECTION ---
try:
    client = MongoClient("mongodb+srv://aravindans2004:Aravindans2004@userauth.joa6bii.mongodb.net/")
    db = client['market_data']
    commodities = db['commodities']
    db1 = client['auth_db']
    users_collection = db1['users']
    print("Connected to MongoDB.")
except Exception as e:
    print(f"MongoDB Connection Error: {e}")

# --- 5. LOAD MODELS ---

# A) Price Prediction Model (XGBoost)
try:
    with open(r"models/xgboost_model.pkl", "rb") as model_file:
        price_model = pickle.load(model_file)
    with open(r"models/column_order.pkl", "rb") as columns_file:
        column_order = pickle.load(columns_file)
    print("Price Prediction Model Loaded.")
except Exception as e:
    print(f"Warning: Price model not found ({e}). Predictions will be simulated.")
    price_model = None
    column_order = []

# B) Disease Detection Model (Keras)
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
    df_hist['Year'] = df_hist['Arrival_Date'].dt.year
    df_hist['Month'] = df_hist['Arrival_Date'].dt.month
except Exception as e:
    print(f"Warning: Historical CSV not found. Dashboard will be empty. {e}")
    df_hist = pd.DataFrame(columns=['Commodity', 'District', 'Arrival_Date', 'Modal_Price', 'Min_Price', 'Max_Price'])

# --- 6. HELPERS ---
COMMODITY_PRICE_RANGES = {
    'Ashgourd': {"min_price_range": (1000, 1500), "max_price_range": (1800, 2500)},
    'Broad Beans': {"min_price_range": (2000, 3000), "max_price_range": (3000, 4000)},
    'Bitter Gourd': {"min_price_range": (2000, 3000), "max_price_range": (3700, 4000)},
    'Bottle Gourd': {"min_price_range": (1000, 2500), "max_price_range": (2500, 3500)},
    'Brinjal': {"min_price_range": (2000, 3300), "max_price_range": (3400, 4000)},
    'Cabbage': {"min_price_range": (1000, 1500), "max_price_range": (1500, 2000)},
    'Capsicum': {"min_price_range": (3000, 3800), "max_price_range": (3900, 4600)},
    'Carrot': {"min_price_range": (3000, 3700), "max_price_range": (3700, 4200)},
    'Cluster Beans': {"min_price_range": (3000, 3700), "max_price_range": (3800, 4300)},
    'Coriander (Leaves)': {"min_price_range": (500, 800), "max_price_range": (800, 1300)},
    'Cauliflower': {"min_price_range": (1800, 2800), "max_price_range": (2500, 3000)},
    'Drumstick': {"min_price_range": (7000, 7500), "max_price_range": (7800, 8400)},
    'Green Chilli': {"min_price_range": (2000, 3200), "max_price_range": (3000, 4500)},
    'Onion': {"min_price_range": (1000, 1500), "max_price_range": (2000, 2500)},
    'Potato': {"min_price_range": (2000, 2500), "max_price_range": (2500, 3500)},
    'Pumpkin': {"min_price_range": (900, 1700), "max_price_range": (1800, 2400)},
    'Raddish': {"min_price_range": (2000, 2000), "max_price_range": (2200, 3000)},
    'Snakeguard': {"min_price_range": (1400, 2500), "max_price_range": (2700, 3400)},
    'Sweet Potato': {"min_price_range": (4500, 5700), "max_price_range": (5500, 6500)},
    'Tomato': {"min_price_range": (1000, 1500), "max_price_range": (1500, 2000)},
    "Arhar (Tur/Red Gram)(Whole)": {"min_price_range": (2000, 4500), "max_price_range": (4800, 6000)},
    "Bengal Gram (Gram)(Whole)": {"min_price_range": (3000, 3800), "max_price_range": (4000, 4500)},
    "Bengal Gram Dal (Chana Dal)": {"min_price_range": (6000, 8000), "max_price_range": (8000, 10000)},
    "Black Gram (Urd Beans)(Whole)": {"min_price_range": (6000, 7600), "max_price_range": (7700, 8500)},
    "Black Gram Dal (Urd Dal)": {"min_price_range": (9000, 13500), "max_price_range": (13000, 15000)},
    "Green Gram (Moong)(Whole)": {"min_price_range": (6000, 7000), "max_price_range": (7000, 8000)},
    "Green Gram Dal (Moong Dal)": {"min_price_range": (8000, 9000), "max_price_range": (9200, 10000)},
    "Kabuli Chana (Chickpeas-White)": {"min_price_range": (6000, 8500), "max_price_range": (8000, 9000)},
    "Kulthi (Horse Gram)": {"min_price_range": (4000, 5300), "max_price_range": (5500, 6500)},
    "Moath Dal": {"min_price_range": (1700, 1900), "max_price_range": (1900, 2400)},
}

def prepare_image(img):
    img = img.resize((224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0
    return img_array

def generate_weekly_predictions(commodity_name, num_weeks=5):
    predictions = []
    start_date = datetime.today()
    if commodity_name not in COMMODITY_PRICE_RANGES: return []
    price_ranges = COMMODITY_PRICE_RANGES[commodity_name]
    
    for i in range(num_weeks):
        future_date = start_date + timedelta(weeks=i)
        future_data = {
            'Min_Price': [random.randint(*price_ranges["min_price_range"])],
            'Max_Price': [random.randint(*price_ranges["max_price_range"])],
            'Arrival_Year': [future_date.year],
            'Arrival_Month': [future_date.month],
            'Arrival_Day': [future_date.day]
        }
        for col in column_order:
            if col not in future_data: future_data[col] = [0]
        
        commodity_col = f'Commodity_{commodity_name}'
        if commodity_col in column_order: future_data[commodity_col] = [1]
        
        future_df = pd.DataFrame(future_data)[column_order]
        
        if price_model:
            future_price = price_model.predict(future_df)[0]
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

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        variety = data.get("variety")
        if variety not in COMMODITY_PRICE_RANGES:
            return jsonify({"error": f"Unknown commodity: {variety}"}), 400
        weekly_predictions = generate_weekly_predictions(variety, num_weeks=5)
        return jsonify({"weekly_predictions": weekly_predictions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/detect_disease', methods=['POST'])
def detect_disease():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        img = Image.open(file.stream)
        
        if disease_model and TF_AVAILABLE and DISEASE_CLASSES:
            # REAL PREDICTION
            processed_img = prepare_image(img)
            preds = disease_model.predict(processed_img)
            class_idx = np.argmax(preds, axis=1)[0]
            confidence = float(np.max(preds))
            
            if class_idx < len(DISEASE_CLASSES):
                result = DISEASE_CLASSES[class_idx]
            else:
                result = "Unknown Disease"
                
            status = "Healthy" if "healthy" in result.lower() else "Infected"
            
            return jsonify({
                "disease": result.replace("_", " "),
                "confidence": f"{confidence*100:.2f}%",
                "status": status,
                "advice": "Consult an expert." if status == "Infected" else "Plant looks healthy!"
            })
        else:
            # DEMO RESPONSE
            return jsonify({
                "disease": "Demo: Tomato Bacterial Spot",
                "confidence": "98.5% (Mock)",
                "status": "Infected",
                "advice": "Demo mode: Ensure 'plant_disease_model.h5' and 'classes.txt' exist."
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

# --- NEW LOGOUT ROUTE ---
@app.route('/api/logout', methods=['POST'])
def logout():
    try:
        session.pop("user", None)
        return jsonify({"message": "Logged out successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/download", methods=["GET"])
def download_data():
    try:
        query = {}
        state = request.args.get("state")
        district = request.args.get("district")
        commodity = request.args.get("commodity")
        
        filtered_df = df_hist.copy()
        if district: filtered_df = filtered_df[filtered_df['District'] == district]
        if commodity: filtered_df = filtered_df[filtered_df['Commodity'] == commodity]
        
        output = BytesIO()
        export_format = request.args.get("format", "csv")
        
        if export_format == "excel":
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                filtered_df.to_excel(writer, index=False)
            mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = "market_data.xlsx"
        elif export_format == "json":
            output.write(filtered_df.to_json(orient="records").encode())
            mimetype = "application/json"
            filename = "market_data.json"
        else:
            filtered_df.to_csv(output, index=False)
            mimetype = "text/csv"
            filename = "market_data.csv"

        output.seek(0)
        return send_file(output, download_name=filename, as_attachment=True, mimetype=mimetype)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    # --- NEW: AI CHART ASSISTANT CHATBOT ---
@app.route('/api/chat', methods=['POST'])
def chat_assistant():
    try:
        data = request.json
        user_message = data.get('message', '').lower()
        
        # 1. Identify Commodity in message
        found_commodity = None
        unique_commodities = df_hist['Commodity'].unique() if not df_hist.empty else []
        for comm in unique_commodities:
            if comm.lower() in user_message:
                found_commodity = comm
                break
        
        # 2. Identify District in message
        found_district = None
        unique_districts = df_hist['District'].unique() if not df_hist.empty else []
        for dist in unique_districts:
            if dist.lower() in user_message:
                found_district = dist
                break

        response_text = ""

        # LOGIC: Answer based on Data
        if "highest" in user_message or "max" in user_message:
            if found_commodity:
                subset = df_hist[df_hist['Commodity'] == found_commodity]
                max_row = subset.loc[subset['Modal_Price'].idxmax()]
                response_text = f"The highest recorded price for {found_commodity} was ₹{max_row['Modal_Price']} in {max_row['District']} on {max_row['Arrival_Date'].strftime('%Y-%m-%d')}."
            else:
                max_row = df_hist.loc[df_hist['Modal_Price'].idxmax()]
                response_text = f"The highest overall price in the dataset is ₹{max_row['Modal_Price']} for {max_row['Commodity']}."

        elif "lowest" in user_message or "min" in user_message:
            if found_commodity:
                subset = df_hist[df_hist['Commodity'] == found_commodity]
                min_row = subset.loc[subset['Modal_Price'].idxmin()]
                response_text = f"The lowest recorded price for {found_commodity} was ₹{min_row['Modal_Price']} in {min_row['District']}."
            else:
                min_row = df_hist.loc[df_hist['Modal_Price'].idxmin()]
                response_text = f"The lowest overall price is ₹{min_row['Modal_Price']} for {min_row['Commodity']}."

        elif "average" in user_message or "avg" in user_message:
            if found_commodity:
                avg_price = df_hist[df_hist['Commodity'] == found_commodity]['Modal_Price'].mean()
                response_text = f"The average market price for {found_commodity} is approx ₹{int(avg_price)}."
            else:
                response_text = "Which commodity's average price would you like to know? (e.g., 'Average price of Tomato')"

        elif "predict" in user_message or "forecast" in user_message:
            if found_commodity:
                response_text = f"I can generate a 5-week prediction for {found_commodity}. Please visit the 'Prediction' tab for the full chart!"
            else:
                response_text = "I can predict prices for Tomato, Onion, etc. Mention a commodity name!"

        elif "hello" in user_message or "hi" in user_message:
            response_text = "Hello! I am your Market AI Assistant. Ask me about commodity prices, trends, or high/low records!"

        else:
            response_text = "I'm trained on your market charts. Try asking: 'Highest price of Tomato', 'Average price of Onion', or 'Lowest price in Chennai'."

        return jsonify({"reply": response_text})

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