import React from 'react';

const DashboardProxy = () => {
    return (
        <div style={{ height: '100vh', width: '100%' }}>
            <iframe 
                src="http://127.0.0.1:5000/dashboard/" 
                title="Dash Analytics"
                style={{ width: '100%', height: '100%', border: 'none' }}
            />
        </div>
    );
};

export default DashboardProxy;