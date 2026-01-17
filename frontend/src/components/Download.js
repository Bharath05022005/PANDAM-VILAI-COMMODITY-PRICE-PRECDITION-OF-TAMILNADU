import React from 'react';

const Download = () => {
    return (
        <div id="download" className="tab-content active" style={{display: 'block', padding: '20px'}}>
            <div className="download-container" style={{background: 'white', padding: '30px', borderRadius: '10px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)'}}>
                <h1 className="section-title"><i className="fas fa-download"></i> Download Market Data</h1>
                <p>Filter and download agricultural market data based on your specific requirements.</p>
                
                {/* Updated Action Path: Consistent 127.0.0.1 */}
                <form action="http://127.0.0.1:5000/api/download" method="GET">
                    <h3><i className="fas fa-filter"></i> Filter Options</h3>
                    
                    <div className="filter-section">
                        <div className="filter-group">
                            <label>State:</label>
                            <select name="state" className="form-select">
                                <option value="Tamil Nadu">Tamil Nadu</option>
                            </select>
                        </div>
                        <div className="filter-group">
                            <label>District:</label>
                            <select name="district" className="form-select">
                                <option value="">All Districts</option>
                                <option value="Chennai">Chennai</option>
                                <option value="Coimbatore">Coimbatore</option>
                                <option value="Madurai">Madurai</option>
                            </select>
                        </div>
                        <div className="filter-group">
                            <label>Commodity:</label>
                            <select name="commodity" className="form-select">
                                <option value="">All Commodities</option>
                                <option value="Tomato">Tomato</option>
                                <option value="Onion">Onion</option>
                            </select>
                        </div>
                    </div>

                    <div className="date-filters">
                        <h4><i className="fas fa-calendar"></i> Date Range</h4>
                        <div className="filter-section">
                            <div className="filter-group">
                                <label>Start Date:</label>
                                <input type="date" name="start-date" required />
                            </div>
                            <div className="filter-group">
                                <label>End Date:</label>
                                <input type="date" name="end-date" required />
                            </div>
                        </div>
                    </div>

                    <h3><i className="fas fa-file-export"></i> Export Options</h3>
                    <div className="format-options" style={{margin: '20px 0'}}>
                        <label style={{marginRight: '15px'}}><input type="radio" name="format" value="csv" defaultChecked /> CSV</label>
                        <label style={{marginRight: '15px'}}><input type="radio" name="format" value="excel" /> Excel</label>
                        <label><input type="radio" name="format" value="json" /> JSON</label>
                    </div>

                    <button type="submit" className="download-btn" style={{padding: '10px 20px', background: '#059669', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer'}}>
                        <i className="fas fa-download"></i> Download Data
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Download;