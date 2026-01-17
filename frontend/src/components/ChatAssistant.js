import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

const ChatAssistant = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        { sender: 'bot', text: 'Hi! I am the AI Chart Assistant. Ask me about price trends, highest prices, or commodity stats!' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg = { sender: 'user', text: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const res = await axios.post('http://127.0.0.1:5000/api/chat', { message: userMsg.text });
            const botMsg = { sender: 'bot', text: res.data.reply };
            setMessages(prev => [...prev, botMsg]);
        } catch (error) {
            setMessages(prev => [...prev, { sender: 'bot', text: "Sorry, I couldn't reach the server." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ position: 'fixed', bottom: '20px', right: '20px', zIndex: 1000 }}>
            {/* Chat Window */}
            {isOpen && (
                <div style={{
                    width: '350px',
                    height: '450px',
                    backgroundColor: 'white',
                    borderRadius: '15px',
                    boxShadow: '0 5px 25px rgba(0,0,0,0.2)',
                    display: 'flex',
                    flexDirection: 'column',
                    overflow: 'hidden',
                    marginBottom: '15px',
                    border: '1px solid #ddd'
                }}>
                    {/* Header with Logo */}
                    <div style={{ background: '#059669', color: 'white', padding: '15px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div style={{ display: 'flex', alignItems: 'center' }}>
                            {/* Header Logo */}
                            <img 
                                src="/static/content/ai_logo.png" 
                                alt="AI" 
                                style={{ width: '30px', height: '30px', borderRadius: '50%', marginRight: '10px', background: 'white' }}
                                onError={(e) => {e.target.style.display='none'}} // Hide if missing
                            />
                            <h4 style={{ margin: 0, fontSize: '16px' }}>Chart Assistant</h4>
                        </div>
                        <button onClick={() => setIsOpen(false)} style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', fontSize: '18px' }}>×</button>
                    </div>

                    {/* Messages Area */}
                    <div style={{ flex: 1, padding: '15px', overflowY: 'auto', background: '#f9f9f9' }}>
                        {messages.map((msg, idx) => (
                            <div key={idx} style={{ 
                                textAlign: msg.sender === 'user' ? 'right' : 'left', 
                                marginBottom: '10px' 
                            }}>
                                <span style={{
                                    display: 'inline-block',
                                    padding: '10px 15px',
                                    borderRadius: '15px',
                                    background: msg.sender === 'user' ? '#059669' : '#e0e0e0',
                                    color: msg.sender === 'user' ? 'white' : 'black',
                                    maxWidth: '80%',
                                    fontSize: '14px',
                                    boxShadow: '0 2px 5px rgba(0,0,0,0.05)'
                                }}>
                                    {msg.text}
                                </span>
                            </div>
                        ))}
                        {loading && <div style={{ textAlign: 'left', color: '#888', fontStyle: 'italic', fontSize: '12px' }}>Thinking...</div>}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input Area */}
                    <div style={{ padding: '10px', background: 'white', borderTop: '1px solid #eee', display: 'flex' }}>
                        <input 
                            type="text" 
                            value={input} 
                            onChange={(e) => setInput(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                            placeholder="Ask about prices..."
                            style={{ flex: 1, border: '1px solid #ddd', borderRadius: '20px', padding: '8px 15px', outline: 'none' }}
                        />
                        <button onClick={handleSend} style={{ background: '#059669', color: 'white', border: 'none', borderRadius: '50%', width: '35px', height: '35px', marginLeft: '10px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <i className="fas fa-paper-plane" style={{ fontSize: '14px' }}></i>
                        </button>
                    </div>
                </div>
            )}

            {/* Floating Toggle Button with CUSTOM IMAGE */}
            <button 
                onClick={() => setIsOpen(!isOpen)} 
                style={{
                    width: '60px',
                    height: '60px',
                    borderRadius: '50%',
                    background: '#059669', // Background color if image has transparency
                    border: 'none',
                    boxShadow: '0 4px 10px rgba(0,0,0,0.3)',
                    cursor: 'pointer',
                    padding: 0, // Remove padding to fit image
                    overflow: 'hidden',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                }}
            >
                {isOpen ? (
                    <i className="fas fa-times" style={{ color: 'white', fontSize: '24px' }}></i>
                ) : (
                    // MAIN LOGO IMAGE
                    <img 
                        src="/static/content/ai_logo.jpg" 
                        alt="AI"
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                        // Fallback to Robot Icon if image is missing
                        onError={(e) => {
                            e.target.style.display='none';
                            e.target.parentNode.innerHTML = '<i class="fas fa-robot" style="color: white; font-size: 24px;"></i>';
                        }}
                    />
                )}
            </button>
        </div>
    );
};

export default ChatAssistant;