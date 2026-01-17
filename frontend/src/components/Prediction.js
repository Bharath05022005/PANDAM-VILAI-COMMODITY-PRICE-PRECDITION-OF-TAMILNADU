import React, { useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const Prediction = () => {
    const [category, setCategory] = useState('');
    const [variety, setVariety] = useState('');
    const [predictions, setPredictions] = useState([]);
    const [chartData, setChartData] = useState(null);

    // EXACT KEYS matching backend/app.py COMMODITY_PRICE_RANGES
    const varieties = {
        pulses: [
            "Arhar (Tur/Red Gram)(Whole)",
            "Bengal Gram (Gram)(Whole)",
            "Bengal Gram Dal (Chana Dal)",
            "Black Gram (Urd Beans)(Whole)",
            "Black Gram Dal (Urd Dal)",
            "Green Gram (Moong)(Whole)",
            "Green Gram Dal (Moong Dal)",
            "Kabuli Chana (Chickpeas-White)",
            "Kulthi (Horse Gram)",
            "Moath Dal"
        ],
        vegetables: [
            "Ashgourd",
            "Broad Beans",
            "Bitter Gourd",
            "Bottle Gourd",
            "Brinjal",
            "Cabbage",
            "Capsicum",
            "Carrot",
            "Cluster Beans",
            "Coriander (Leaves)",
            "Cauliflower",
            "Drumstick",
            "Green Chilli",
            "Onion",
            "Potato",
            "Pumpkin",
            "Raddish",
            "Snakeguard",
            "Sweet Potato",
            "Tomato"
        ]
    };

    const handlePredict = async () => {
        if (!category || !variety) {
            alert("Please select both category and variety");
            return;
        }

        try {
            // Updated Path: consistent with backend port
            const response = await axios.post('http://127.0.0.1:5000/api/predict', {
                category,
                variety
            });
            
            const data = response.data.weekly_predictions;
            setPredictions(data);

            setChartData({
                labels: data.map(p => p.Date),
                datasets: [{
                    label: 'Predicted Modal Price',
                    data: data.map(p => p.Predicted_Modal_Price),
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.5)',
                    fill: true
                }]
            });
        } catch (error) {
            console.error("Prediction Error:", error);
            alert(error.response?.data?.error || "Error fetching prediction");
        }
    };

    return (
        <div id="prediction" className="tab-content active" style={{display: 'block'}}>
            <div className="header-image-container">
                {/* Path: frontend/public/static/content/prediction_page.png */}
                <img 
                    src="/static/content/prediction_page.png" 
                    className="header-image" 
                    style={{ width: '100%', height: 'auto', objectFit: 'cover' }} 
                    alt="Horticultural Crops" 
                />
                
                <div className="overlay-content">
                    <h1>Commodity Price Prediction</h1>

                    <div>
                        <label htmlFor="category">Select Category:</label>
                        <select id="category" className="form-select" value={category} onChange={(e) => setCategory(e.target.value)}>
                            <option value="">--Select--</option>
                            <option value="pulses">Pulses</option>
                            <option value="vegetables">Vegetables</option>
                        </select>
                    </div>

                    {category && (
                        <div id="variety-section" style={{ marginTop: '20px' }}>
                            <label htmlFor="variety">Select Variety:</label>
                            <select id="variety" className="form-select" value={variety} onChange={(e) => setVariety(e.target.value)}>
                                <option value="">Select Variety</option>
                                {varieties[category]?.map(v => (
                                    <option key={v} value={v}>{v}</option>
                                ))}
                            </select>
                            <button id="getPrediction" onClick={handlePredict} style={{marginLeft: '10px', padding: '5px 15px'}}>Get Prediction</button>
                        </div>
                    )}

                    {predictions.length > 0 && (
                        <div id="predictions" style={{ textAlign: 'left', marginTop: '20px', background: 'rgba(255,255,255,0.95)', padding: '20px', borderRadius: '10px', color: 'black' }}>
                            <h3>Weekly Predictions:</h3>
                            
                            {chartData && (
                                <div className="chart-container" style={{backgroundColor: 'white', padding: '10px'}}>
                                    <Line data={chartData} />
                                </div>
                            )}

                            <table id="predictionTable" className="table table-striped mt-3">
                                <thead className="table-success">
                                    <tr>
                                        <th>Date</th>
                                        <th>Min Price</th>
                                        <th>Max Price</th>
                                        <th>Predicted Modal</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {predictions.map((p, index) => (
                                        <tr key={index}>
                                            <td>{p.Date}</td>
                                            <td>₹{p.Min_Price}</td>
                                            <td>₹{p.Max_Price}</td>
                                            <td>₹{p.Predicted_Modal_Price}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Prediction;