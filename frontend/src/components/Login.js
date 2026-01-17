import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Login = ({ setUser }) => {
    const [isLogin, setIsLogin] = useState(true);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [email, setEmail] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        const endpoint = isLogin ? '/api/login' : '/api/signup';
        try {
            const res = await axios.post(`http://127.0.0.1:5000${endpoint}`, {
                username, password, email
            });
            
            if (isLogin) {
                setUser(username);
                navigate('/');
            } else {
                alert('Signup successful! Please login.');
                setIsLogin(true);
            }
        } catch (err) {
            alert(err.response?.data?.error || 'Error');
        }
    };

    return (
        // CORRECTION: Removed duplicate 'display: block'
        <div id="login" className="tab-content active" style={{ minHeight: '80vh', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <div className="container">
                <div className="form-box">
                    <h2 id="form-title">{isLogin ? 'Login' : 'Sign Up'}</h2>
                    <form id="auth-form" onSubmit={handleSubmit}>
                        <input 
                            type="text" 
                            id="username" 
                            placeholder="Username" 
                            value={username}
                            onChange={e => setUsername(e.target.value)} 
                            required 
                        />
                        
                        {!isLogin && (
                            <input 
                                type="email" 
                                id="email" 
                                placeholder="Email" 
                                value={email}
                                onChange={e => setEmail(e.target.value)} 
                                required 
                            />
                        )}
                        
                        <input 
                            type="password" 
                            id="password" 
                            placeholder="Password" 
                            value={password}
                            onChange={e => setPassword(e.target.value)} 
                            required 
                        />
                        
                        <button type="submit" id="submit-btn">
                            {isLogin ? 'Login' : 'Sign Up'}
                        </button>
                        
                        <h3 id="toggle-form" style={{ marginTop: '15px', fontSize: '14px' }}>
                            {isLogin ? "Don't have an account? " : "Already have an account? "}
                            <span 
                                onClick={() => setIsLogin(!isLogin)} 
                                style={{ color: '#059669', cursor: 'pointer', textDecoration: 'underline' }}
                            >
                                {isLogin ? 'Sign up' : 'Login'}
                            </span>
                        </h3>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default Login;