import React, { useState } from 'react';
import axios from 'axios';

const DiseaseDetection = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setSelectedFile(file);
            setPreview(URL.createObjectURL(file));
            setResult(null);
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
        try {
            const response = await axios.post('http://127.0.0.1:5000/api/detect_disease', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            setResult(response.data);
        } catch (error) {
            console.error("Error detecting disease:", error);
            alert("Failed to detect disease. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div id="disease" className="tab-content active" style={{display: 'block', padding: '20px'}}>
            <div className="header-image-container" style={{ textAlign: 'center', marginBottom: '30px' }}>
                <h1><i className="fas fa-microscope"></i> Plant Disease Detection</h1>
                <p>Upload a clear photo of a plant leaf to detect diseases and get treatment advice.</p>
            </div>

            <div className="container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                
                {/* Upload Box */}
                <div className="upload-box" style={{ 
                    border: '2px dashed #059669', 
                    padding: '40px', 
                    borderRadius: '15px', 
                    textAlign: 'center', 
                    background: 'white',
                    width: '100%',
                    maxWidth: '500px',
                    marginBottom: '20px'
                }}>
                    <input 
                        type="file" 
                        accept="image/*" 
                        onChange={handleFileChange} 
                        style={{ display: 'none' }} 
                        id="file-upload"
                    />
                    <label htmlFor="file-upload" style={{ cursor: 'pointer', display: 'block' }}>
                        {preview ? (
                            <img src={preview} alt="Preview" style={{ maxWidth: '100%', maxHeight: '300px', borderRadius: '10px' }} />
                        ) : (
                            <div>
                                <i className="fas fa-cloud-upload-alt" style={{ fontSize: '50px', color: '#059669', marginBottom: '10px' }}></i>
                                <h3>Click to Upload Leaf Image</h3>
                                <p style={{ color: '#666' }}>Supports JPG, PNG</p>
                            </div>
                        )}
                    </label>
                </div>

                {/* Detect Button */}
                <button 
                    onClick={handleDetect} 
                    className="tab-button blue" 
                    disabled={loading}
                    style={{ width: '200px', textAlign: 'center', justifyContent: 'center', fontSize: '18px' }}
                >
                    {loading ? "Analyzing..." : "Detect Disease"}
                </button>

                {/* Results Section */}
                {result && (
                    <div className="result-card" style={{ 
                        marginTop: '30px', 
                        background: 'white', 
                        padding: '30px', 
                        borderRadius: '15px', 
                        boxShadow: '0 5px 15px rgba(0,0,0,0.1)',
                        width: '100%',
                        maxWidth: '600px',
                        borderLeft: result.status === 'Healthy' ? '5px solid #059669' : '5px solid #dc3545'
                    }}>
                        <h2 style={{ color: result.status === 'Healthy' ? '#059669' : '#dc3545' }}>
                            {result.status === 'Healthy' ? <i className="fas fa-check-circle"></i> : <i className="fas fa-exclamation-circle"></i>}
                            {' '}{result.status}
                        </h2>
                        <hr />
                        <div style={{ textAlign: 'left', marginTop: '15px' }}>
                            <p><strong>Predicted Disease:</strong> {result.disease}</p>
                            <p><strong>Confidence:</strong> {result.confidence}</p>
                            <div style={{ background: '#f8f9fa', padding: '15px', borderRadius: '8px', marginTop: '15px' }}>
                                <strong><i className="fas fa-user-md"></i> Advice:</strong>
                                <p style={{ margin: '5px 0 0 0' }}>{result.advice}</p>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default DiseaseDetection;