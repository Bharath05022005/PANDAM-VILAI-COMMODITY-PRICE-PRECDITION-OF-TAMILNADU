import React, { useState } from 'react';
import axios from 'axios';

const DiseaseDetection = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setSelectedFile(file);
            setPreview(URL.createObjectURL(file));
            setResult(null);
            setError(null);
        }
    };

    const handleDetect = async () => {
        if (!selectedFile) {
            alert("Please upload an image first.");
            return;
        }

        const formData = new FormData();
        formData.append('file', selectedFile);

        setLoading(true);
        setError(null);

        try {
            // Connects to your Flask Backend
            const response = await axios.post('http://localhost:5000/api/detect_disease', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
                withCredentials: true // Important for session handling if needed
            });

            setResult(response.data);
        } catch (err) {
            console.error("Error detecting disease:", err);
            setError("Failed to analyze image. Check if backend is running.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container" style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
            <div style={{ textAlign: 'center', marginBottom: '30px' }}>
                <h2 style={{ color: '#2d3748' }}>🌱Plant Disease Detection</h2>
                <p style={{ color: '#718096' }}>Upload a leaf photo to get an instant diagnosis and treatment plan.</p>
            </div>

            {/* Upload Area */}
            <div style={{ 
                border: '3px dashed #cbd5e0', 
                borderRadius: '15px', 
                padding: '40px', 
                textAlign: 'center',
                backgroundColor: '#f7fafc',
                marginBottom: '20px'
            }}>
                <input 
                    type="file" 
                    accept="image/*" 
                    onChange={handleFileChange} 
                    style={{ display: 'none' }} 
                    id="leaf-upload"
                />
                <label htmlFor="leaf-upload" style={{ cursor: 'pointer', display: 'block' }}>
                    {preview ? (
                        <img 
                            src={preview} 
                            alt="Preview" 
                            style={{ maxHeight: '300px', maxWidth: '100%', borderRadius: '10px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }} 
                        />
                    ) : (
                        <div>
                            <i className="fas fa-cloud-upload-alt" style={{ fontSize: '48px', color: '#48bb78', marginBottom: '10px' }}></i>
                            <h4 style={{ color: '#4a5568' }}>Click to Upload Image</h4>
                            <p style={{ color: '#a0aec0' }}>Supports JPG, PNG</p>
                        </div>
                    )}
                </label>
            </div>

            {/* Action Button */}
            <div style={{ textAlign: 'center' }}>
                <button 
                    onClick={handleDetect} 
                    disabled={loading || !selectedFile}
                    style={{
                        padding: '12px 40px',
                        fontSize: '18px',
                        backgroundColor: loading ? '#cbd5e0' : '#48bb78',
                        color: 'white',
                        border: 'none',
                        borderRadius: '30px',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        transition: 'background 0.3s'
                    }}
                >
                    {loading ? "Analyzing..." : "Detect Disease"}
                </button>
            </div>

            {/* Error Message */}
            {error && (
                <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#fff5f5', color: '#c53030', borderRadius: '8px', textAlign: 'center' }}>
                    {error}
                </div>
            )}

            {/* Results Display */}
            {result && (
                <div style={{ 
                    marginTop: '30px', 
                    padding: '25px', 
                    borderRadius: '12px', 
                    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                    backgroundColor: 'white',
                    borderLeft: result.status === 'Healthy' ? '6px solid #48bb78' : '6px solid #e53e3e'
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                        <h3 style={{ margin: 0, color: result.status === 'Healthy' ? '#2f855a' : '#c53030' }}>
                            {result.status}
                        </h3>
                        <span style={{ backgroundColor: '#edf2f7', padding: '5px 12px', borderRadius: '20px', fontSize: '0.9em', fontWeight: 'bold', color: '#4a5568' }}>
                            Confidence: {result.confidence}
                        </span>
                    </div>

                    <h4 style={{ color: '#2d3748', borderBottom: '1px solid #e2e8f0', paddingBottom: '10px' }}>
                        Identified: {result.disease}
                    </h4>

                    <div style={{ marginTop: '15px', backgroundColor: '#ebf8ff', padding: '15px', borderRadius: '8px' }}>
                        <strong style={{ color: '#2b6cb0', display: 'block', marginBottom: '5px' }}>
                            <i className="fas fa-user-md"></i> Expert Advice:
                        </strong>
                        <p style={{ margin: 0, color: '#2c5282' }}>{result.advice}</p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default DiseaseDetection;
