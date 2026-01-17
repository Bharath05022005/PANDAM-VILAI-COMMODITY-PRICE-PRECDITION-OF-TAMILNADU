import React, { useState } from 'react';

const Insight = () => {
    // State to track which main category is active (pulses or vegetables)
    const [activeCategory, setActiveCategory] = useState('pulses');
    // State to track if we are viewing the 'list' (Category & Variety) or 'details' (Scientific names etc)
    const [viewMode, setViewMode] = useState('list'); // 'list' or 'details'

    // Helper to switch main tabs
    const handleCategoryChange = (category) => {
        setActiveCategory(category);
        setViewMode('list'); // Reset to list view when switching category
    };

    return (
        <div id="insight" className="tab-content active" style={{ display: 'block', padding: '20px' }}>
            <h1 style={{ textAlign: 'center' }}>Market trends and analysis for pulses and vegetables.</h1>
            
            {/* Top Navigation for Pulses vs Vegetables */}
            <div className="sub-tabs" style={{ textAlign: 'center', marginBottom: '20px' }}>
                <button 
                    className={`sub-tab-button ${activeCategory === 'pulses' ? 'active' : ''}`} 
                    onClick={() => handleCategoryChange('pulses')}
                    style={{ marginRight: '10px', padding: '10px', cursor: 'pointer' }}
                >
                    Pulses (Category & Variety)
                </button>
                <button 
                    className={`sub-tab-button ${activeCategory === 'vegetables' ? 'active' : ''}`} 
                    onClick={() => handleCategoryChange('vegetables')}
                    style={{ padding: '10px', cursor: 'pointer' }}
                >
                    Vegetables (Category & Variety)
                </button>
            </div>

            {/* PULSES SECTION */}
            {activeCategory === 'pulses' && (
                <>
                    {viewMode === 'list' ? (
                        <div id="pulses" className="sub-tab-content active">
                            <h3>
                                Pulses 
                                <button 
                                    className="sub-tab-button" 
                                    onClick={() => setViewMode('details')}
                                    style={{ marginLeft: '15px', padding: '5px 15px', fontSize: '0.9em', cursor: 'pointer' }}
                                >
                                    Details about the Pulses
                                </button>
                            </h3>
                            <table className="table table-bordered table-striped" style={{ width: '100%', marginBottom: '30px' }}>
                                <thead className="table-dark">
                                    <tr>
                                        <th>Category</th>
                                        <th>Variety</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {/* Lentils */}
                                    <tr><td rowSpan="5" style={{ verticalAlign: 'middle' }}>Lentils</td><td>Toor Dal (Pigeon Pea / Thuvaram Paruppu)</td></tr>
                                    <tr><td>Moong Dal (Green Gram / Payatham Paruppu)</td></tr>
                                    <tr><td>Urad Dal (Black Gram / Ulundhu Paruppu)</td></tr>
                                    <tr><td>Masoor Dal (Red Lentil / Mysore Paruppu)</td></tr>
                                    <tr><td>Horse Gram (Kollu Paruppu)</td></tr>
                                    {/* Beans */}
                                    <tr><td rowSpan="4" style={{ verticalAlign: 'middle' }}>Beans</td><td>Kidney Beans (Rajma)</td></tr>
                                    <tr><td>Moth Beans (Matki)</td></tr>
                                    <tr><td>Black Gram Beans (Karuppu Ulundhu)</td></tr>
                                    <tr><td>Broad Beans (Avarai Kottai)</td></tr>
                                    {/* Peas */}
                                    <tr><td rowSpan="4" style={{ verticalAlign: 'middle' }}>Peas</td><td>Green Peas (Pachai Pattani)</td></tr>
                                    <tr><td>Yellow Peas (Manjal Pattani)</td></tr>
                                    <tr><td>Black-Eyed Peas (Thatta Payaru)</td></tr>
                                    <tr><td>Bambara Peas (Mochai Kottai)</td></tr>
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <div id="pulses-details" className="sub-tab-content active">
                            <button 
                                onClick={() => setViewMode('list')}
                                style={{ marginBottom: '15px', padding: '5px 15px', cursor: 'pointer' }}
                            >
                                ← Back to List
                            </button>
                            <h2 style={{ textAlign: 'center' }}>Details about the Pulses</h2>
                    
                            <h2 style={{ textAlign: 'center', marginTop: '30px' }}>Lentils</h2>
                            <table className="table table-bordered" style={{ width: '100%' }}>
                                <thead className="table-light">
                                    <tr><th>Name</th><th>Common Name</th><th>Scientific Name</th><th>Season</th><th>Temperature</th><th>Nutritional Value</th><th>Uses</th></tr>
                                </thead>
                                <tbody>
                                    <tr><td>Toor Dal</td><td>Pigeon Pea</td><td>Cajanus cajan</td><td>Kharif</td><td>18-30°C</td><td>Protein: 22g, Fiber: 15g, Iron: 6.5mg</td><td>Sambar, Dal</td></tr>
                                    <tr><td>Moong Dal</td><td>Green Gram</td><td>Vigna radiata</td><td>Kharif & Summer</td><td>25-35°C</td><td>Protein: 24g, Fiber: 16g, Calcium: 132mg</td><td>Sprouts, Dal</td></tr>
                                    <tr><td>Urad Dal</td><td>Black Gram</td><td>Vigna mungo</td><td>Kharif</td><td>20-30°C</td><td>Protein: 25g, Fiber: 18g, Iron: 7mg</td><td>Idli, Dosa</td></tr>
                                    <tr><td>Masoor Dal</td><td>Red Lentil</td><td>Lens culinaris</td><td>Rabi</td><td>15-25°C</td><td>Protein: 25g, Fiber: 15g, Potassium: 450mg</td><td>Soups, Dal, Curries</td></tr>
                                    <tr><td>Horse Gram</td><td>Kollu Paruppu</td><td>Macrotyloma uniflorum</td><td>Rabi & Summer</td><td>20-30°C</td><td>Protein: 22g, Fiber: 10g, Iron: 7mg</td><td>Kollu Rasam, Sprouts</td></tr>
                                </tbody>
                            </table>

                            <h2 style={{ textAlign: 'center', marginTop: '30px' }}>Beans</h2>
                            <table className="table table-bordered" style={{ width: '100%' }}>
                                <thead className="table-light">
                                    <tr><th>Name</th><th>Common Name</th><th>Scientific Name</th><th>Season</th><th>Temperature</th><th>Nutritional Value</th><th>Uses</th></tr>
                                </thead>
                                <tbody>
                                    <tr><td>Kidney Beans</td><td>Rajma</td><td>Phaseolus vulgaris</td><td>Rabi</td><td>15-25°C</td><td>Protein: 24g, Fiber: 25g, Iron: 8mg</td><td>Rajma Masala</td></tr>
                                    <tr><td>Moth Beans</td><td>Matki</td><td>Vigna aconitifolia</td><td>Kharif</td><td>25-35°C</td><td>Protein: 23g, Fiber: 16g, Calcium: 120mg</td><td>Sprouts, Dal</td></tr>
                                    <tr><td>Black Gram Beans</td><td>Karuppu Ulundhu</td><td>Vigna mungo</td><td>Kharif</td><td>20-30°C</td><td>Protein: 25g, Fiber: 18g, Iron: 7mg</td><td>Idli, Dosa, Papad</td></tr>
                                    <tr><td>Broad Beans</td><td>Avarai Kottai</td><td>Vicia faba</td><td>Rabi & Kharif</td><td>15-25°C</td><td>Protein: 26g, Fiber: 10g, Iron: 6mg</td><td>Stir-Fry, Curries</td></tr>
                                </tbody>
                            </table>

                            <h2 style={{ textAlign: 'center', marginTop: '30px' }}>Peas</h2>
                            <table className="table table-bordered" style={{ width: '100%' }}>
                                <thead className="table-light">
                                    <tr><th>Name</th><th>Common Name</th><th>Scientific Name</th><th>Season</th><th>Temperature</th><th>Nutritional Value</th><th>Uses</th></tr>
                                </thead>
                                <tbody>
                                    <tr><td>Green Peas</td><td>Pachai Pattani</td><td>Pisum sativum</td><td>Rabi</td><td>10-20°C</td><td>Protein: 5g, Fiber: 7g, Vitamin C: 40mg</td><td>Soups, Snacks</td></tr>
                                    <tr><td>Yellow Peas</td><td>Manjal Pattani</td><td>Pisum sativum</td><td>Rabi</td><td>10-20°C</td><td>Protein: 6g, Fiber: 10g, Iron: 3mg</td><td>Dal, Flour</td></tr>
                                    <tr><td>Black-Eyed Peas</td><td>Thatta Payaru</td><td>Vigna unguiculata</td><td>Kharif & Rabi</td><td>20-30°C</td><td>Protein: 23g, Fiber: 10g, Iron: 8mg</td><td>Curries, Sprouts</td></tr>
                                    <tr><td>Bambara Peas</td><td>Mochai Kottai</td><td>Vigna subterranea</td><td>Kharif</td><td>25-35°C</td><td>Protein: 24g, Fiber: 12g, Calcium: 110mg</td><td>Soups, Roasted Snacks</td></tr>
                                </tbody>
                            </table>
                        </div>
                    )}
                </>
            )}

            {/* VEGETABLES SECTION */}
            {activeCategory === 'vegetables' && (
                <>
                    {viewMode === 'list' ? (
                        <div id="vegetables" className="sub-tab-content active">
                            <h3>
                                Vegetables 
                                <button 
                                    className="sub-tab-button" 
                                    onClick={() => setViewMode('details')}
                                    style={{ marginLeft: '15px', padding: '5px 15px', fontSize: '0.9em', cursor: 'pointer' }}
                                >
                                    Details about the Vegetables
                                </button>
                            </h3>
                            <table className="table table-bordered table-striped" style={{ width: '100%', marginBottom: '30px' }}>
                                <thead className="table-success">
                                    <tr>
                                        <th>Category</th>
                                        <th>Variety</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {/* Leafy Greens */}
                                    <tr><td rowSpan="3" style={{ verticalAlign: 'middle' }}>Leafy Greens</td><td>Spinach (Palak)</td></tr>
                                    <tr><td>Mustard Greens (Sarson)</td></tr>
                                    <tr><td>Fenugreek (Methi)</td></tr>
                                    {/* Root Vegetables */}
                                    <tr><td rowSpan="3" style={{ verticalAlign: 'middle' }}>Root Vegetables</td><td>Carrot (Gajar)</td></tr>
                                    <tr><td>Beetroot (Chukandar)</td></tr>
                                    <tr><td>Radish (Muli)</td></tr>
                                    {/* Fruiting Vegetables */}
                                    <tr><td rowSpan="3" style={{ verticalAlign: 'middle' }}>Fruiting Vegetables</td><td>Tomato (Tamatar)</td></tr>
                                    <tr><td>Brinjal (Baingan)</td></tr>
                                    <tr><td>Capsicum (Shimla Mirch)</td></tr>
                                    {/* Cruciferous Vegetables */}
                                    <tr><td rowSpan="3" style={{ verticalAlign: 'middle' }}>Cruciferous Vegetables</td><td>Cabbage (Patta Gobhi)</td></tr>
                                    <tr><td>Cauliflower (Phool Gobhi)</td></tr>
                                    <tr><td>Broccoli</td></tr>
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <div id="vegetables-details" className="sub-tab-content active">
                            <button 
                                onClick={() => setViewMode('list')}
                                style={{ marginBottom: '15px', padding: '5px 15px', cursor: 'pointer' }}
                            >
                                ← Back to List
                            </button>
                            <h2 style={{ textAlign: 'center' }}>Details about the Vegetables</h2>

                            <h2 style={{ textAlign: 'center', marginTop: '30px' }}>Leafy Greens</h2>
                            <table className="table table-bordered" style={{ width: '100%' }}>
                                <thead className="table-light">
                                    <tr><th>Name</th><th>Common Name</th><th>Scientific Name</th><th>Season</th><th>Temperature</th><th>Nutritional Value</th><th>Uses</th></tr>
                                </thead>
                                <tbody>
                                    <tr><td>Spinach</td><td>Palak</td><td>Spinacia oleracea</td><td>Winter</td><td>15-20°C</td><td>Vitamin A, Iron</td><td>Salads, Curries</td></tr>
                                    <tr><td>Mustard Greens</td><td>Sarson</td><td>Brassica juncea</td><td>Winter</td><td>10-20°C</td><td>Vitamins K, C</td><td>Saag, Salads</td></tr>
                                    <tr><td>Fenugreek</td><td>Methi</td><td>Trigonella foenum-graecum</td><td>Winter</td><td>15-25°C</td><td>Iron, Calcium</td><td>Curries, Parathas</td></tr>
                                </tbody>
                            </table>
                        
                            <h2 style={{ textAlign: 'center', marginTop: '30px' }}>Root Vegetables</h2>
                            <table className="table table-bordered" style={{ width: '100%' }}>
                                <thead className="table-light">
                                    <tr><th>Name</th><th>Common Name</th><th>Scientific Name</th><th>Season</th><th>Temperature</th><th>Nutritional Value</th><th>Uses</th></tr>
                                </thead>
                                <tbody>
                                    <tr><td>Carrot</td><td>Gajar</td><td>Daucus carota</td><td>Winter</td><td>15-20°C</td><td>Vitamin A, Fiber</td><td>Salads, Soups</td></tr>
                                    <tr><td>Beetroot</td><td>Chukandar</td><td>Beta vulgaris</td><td>Winter</td><td>10-20°C</td><td>Folate, Manganese</td><td>Salads, Juices</td></tr>
                                    <tr><td>Radish</td><td>Muli</td><td>Raphanus sativus</td><td>Winter</td><td>10-20°C</td><td>Vitamin C, Potassium</td><td>Salads, Pickles</td></tr>
                                </tbody>
                            </table>
                        
                            <h2 style={{ textAlign: 'center', marginTop: '30px' }}>Fruiting Vegetables</h2>
                            <table className="table table-bordered" style={{ width: '100%' }}>
                                <thead className="table-light">
                                    <tr><th>Name</th><th>Common Name</th><th>Scientific Name</th><th>Season</th><th>Temperature</th><th>Nutritional Value</th><th>Uses</th></tr>
                                </thead>
                                <tbody>
                                    <tr><td>Tomato</td><td>Tamatar</td><td>Solanum lycopersicum</td><td>Summer</td><td>20-30°C</td><td>Vitamin C, Potassium</td><td>Salads, Sauces</td></tr>
                                    <tr><td>Brinjal</td><td>Baingan</td><td>Solanum melongena</td><td>Summer</td><td>20-30°C</td><td>Fiber, Vitamins B1, B6</td><td>Curries, Grilled</td></tr>
                                    <tr><td>Capsicum</td><td>Shimla Mirch</td><td>Capsicum annuum</td><td>Summer</td><td>20-30°C</td><td>Vitamin C, Antioxidants</td><td>Salads, Stir-Fry</td></tr>
                                </tbody>
                            </table>
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default Insight;