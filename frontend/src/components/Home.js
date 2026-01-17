import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
    return (
        <div id="about" className="tab-content active" style={{ display: 'block', padding: '20px' }}>
            <div style={{ textAlign: 'center', marginBottom: '40px' }}>
                <h1><i className="fas fa-seedling"></i> Welcome to PANDAM VILAI</h1>
                <p style={{ fontSize: 'x-large', color: '#059669' }}>Empowering Agriculture with Predictive Market Intelligence</p>
            </div>
            
            {/* About Section */}
            <div className="sub-tab-content1 active">
                <h1><i className="fas fa-info-circle"></i> About PANDAM VILAI</h1>
                <p style={{ fontSize: 'large', textIndent: '30px', textAlign: 'justify' }}>
                    PANDAM VILAI is a cutting-edge agricultural market intelligence platform that delivers accurate price predictions for agri-horticultural commodities, 
                    empowering farmers, traders, policymakers, and consumers with the tools needed for smarter, data-driven decisions. By forecasting prices up to 10 weeks in advance, our platform transforms agricultural commerce through predictive analytics and intuitive design.
                </p>
            </div>
            
            {/* Features Section */}
            <div className="sub-tab-content1 active">
                <h1><i className="fas fa-gifts"></i> What We Offer</h1>
            
                <div className="feature-card">
                    {/* Path: frontend/public/static/content/a_prediction_resized.jpg */}
                    <img src="/static/content/a_prediction_resized.jpg" alt="Prediction Image" style={{ width: '40%', borderRadius: '10px' }} />
                    <div className="feature-icon"><i className="fas fa-chart-line"></i></div>
                    <div className="feature-content">
                        <h3>Advanced Price Predictions</h3>
                        <p>Leverages machine learning models to analyze historical data and forecast commodity prices up to 10 weeks ahead.</p>
                        <Link to="/prediction" className="tab-button blue" style={{ textDecoration: 'none', display: 'inline-block', textAlign: 'center' }}>
                            Try Prediction <i className="fas fa-arrow-right"></i>
                        </Link>
                    </div>
                </div>
            
                <div className="feature-card">
                    {/* Path: frontend/public/static/content/insight.jpg */}
                    <img src="/static/content/insight.jpg" alt="Insight Image" style={{ width: '40%', borderRadius: '10px' }} />
                    <div className="feature-icon"><i className="fas fa-lightbulb"></i></div>
                    <div className="feature-content">
                        <h3>Comprehensive Market Insights</h3>
                        <p>Provides detailed information on various pulses and vegetables, including their varieties, scientific names, growing seasons, and nutritional values.</p>
                        <Link to="/insight" className="tab-button blue" style={{ textDecoration: 'none', display: 'inline-block', textAlign: 'center' }}>
                            Explore Insights <i className="fas fa-arrow-right"></i>
                        </Link>
                    </div>
                </div>
            
                <div className="feature-card">
                    {/* Path: frontend/public/static/content/dashboard.jpg */}
                    <img src="/static/content/dashboard.jpg" alt="Dashboard Image" style={{ width: '40%', borderRadius: '10px' }} />
                    <div className="feature-icon"><i className="fas fa-tachometer-alt"></i></div>
                    <div className="feature-content">
                        <h3>Interactive Dashboard</h3>
                        <p>Explore trends through dynamic charts, district-wise price comparisons, and visual future price projections.</p>
                        <Link to="/dashboard" className="tab-button blue" style={{ textDecoration: 'none', display: 'inline-block', textAlign: 'center' }}>
                            Open Dashboard <i className="fas fa-arrow-right"></i>
                        </Link>
                    </div>
                </div>
            </div>

            {/* Mission Section */}
            <div className="sub-tab-content1 active">
                <h1><i className="fas fa-bullseye"></i> Our Mission</h1>
                <p style={{ fontSize: 'large', textIndent: '30px', textAlign: 'justify' }}>
                    To reduce market uncertainties and enhance decision-making in agricultural commerce through accurate price forecasting and comprehensive market analysis.
                </p>
                <div className="mission-stats">
                    <div className="stat-item">
                        <span className="stat-number">5+</span>
                        <span className="stat-label">Weeks of Advanced Prediction</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-number">25+</span>
                        <span className="stat-label">Varieties Analyzed</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-number">95%</span>
                        <span className="stat-label">Accuracy Rate</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Home;