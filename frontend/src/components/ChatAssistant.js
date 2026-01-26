import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

const ChatAssistant = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        { sender: 'bot', text: 'Hi! I am your AI Agent. Ask me anything!' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    // Auto-scroll to bottom
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages, loading]);

    const handleSend = async () => {
        if (!input.trim()) return;

        // 1. Create User Message
        const userMsg = { sender: 'user', text: input };
        const newHistory = [...messages, userMsg];
        
        // 2. Update UI
        setMessages(newHistory);
        setInput('');
        setLoading(true);

        try {
            // 3. Send to Backend
            const res = await axios.post('http://127.0.0.1:5000/api/chat', { 
                message: userMsg.text,
                history: newHistory.map(m => ({ role: m.sender, content: m.text })) 
            });

            const botMsg = { sender: 'bot', text: res.data.reply };
            setMessages(prev => [...prev, botMsg]);
        } catch (error) {
            console.error("API Error:", error);
            setMessages(prev => [...prev, { sender: 'bot', text: "Sorry, I'm having trouble connecting." }]);
        } finally {
            setLoading(false);
        }
    };

    // Handle 'Enter' key
    const handleKeyDown = (e) => {
        if (e.key === 'Enter') handleSend();
    };

    return (
        <div style={{ position: 'fixed', bottom: '20px', right: '20px', zIndex: 1000, fontFamily: 'Arial, sans-serif' }}>
            
            {/* --- CHAT WINDOW --- */}
            {isOpen && (
                <div style={{
                    width: '350px',
                    height: '500px',
                    backgroundColor: 'white',
                    borderRadius: '12px',
                    boxShadow: '0 8px 30px rgba(0,0,0,0.15)',
                    display: 'flex',
                    flexDirection: 'column',
                    overflow: 'hidden',
                    marginBottom: '15px',
                    border: '1px solid #e5e7eb'
                }}>
                    {/* Header */}
                    <div style={{ background: '#2563EB', color: 'white', padding: '15px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            
                            {/* 1. HEADER LOGO */}
                            <div style={{ width: '32px', height: '32px', borderRadius: '50%', overflow: 'hidden', background: 'white', border: '1px solid white' }}>
                                <img 
                                    src="/static/content/ai_logo.jpg" 
                                    alt="AI"
                                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                    onError={(e) => {
                                        e.target.style.display='none'; 
                                        e.target.parentNode.innerHTML = '🤖'; // Fallback icon
                                        e.target.parentNode.style.display = 'flex';
                                        e.target.parentNode.style.alignItems = 'center';
                                        e.target.parentNode.style.justifyContent = 'center';
                                        e.target.parentNode.style.fontSize = '20px';
                                        e.target.parentNode.style.color = '#2563EB';
                                    }}
                                />
                            </div>

                            <h4 style={{ margin: 0, fontSize: '16px', fontWeight: '600' }}>AI Agent</h4>
                        </div>
                        <button onClick={() => setIsOpen(false)} style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', fontSize: '24px', lineHeight: '1' }}>×</button>
                    </div>

                    {/* Messages */}
                    <div style={{ flex: 1, padding: '15px', overflowY: 'auto', background: '#f3f4f6' }}>
                        {messages.map((msg, idx) => (
                            <div key={idx} style={{ display: 'flex', justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start', marginBottom: '12px' }}>
                                <div style={{
                                    padding: '12px 16px',
                                    borderRadius: '12px',
                                    background: msg.sender === 'user' ? '#2563EB' : 'white',
                                    color: msg.sender === 'user' ? 'white' : '#1f2937',
                                    border: msg.sender === 'bot' ? '1px solid #e5e7eb' : 'none',
                                    maxWidth: '85%',
                                    fontSize: '14px',
                                    lineHeight: '1.5',
                                    boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
                                    whiteSpace: 'pre-wrap', 
                                    wordBreak: 'break-word'
                                }}>
                                    {msg.text}
                                </div>
                            </div>
                        ))}
                        {loading && <div style={{ marginLeft: '10px', fontSize: '12px', color: '#6b7280', fontStyle: 'italic' }}>AI is thinking...</div>}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <div style={{ padding: '15px', background: 'white', borderTop: '1px solid #e5e7eb', display: 'flex', gap: '10px' }}>
                        <input 
                            type="text" 
                            value={input} 
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Ask a question..."
                            disabled={loading}
                            style={{ flex: 1, border: '1px solid #d1d5db', borderRadius: '20px', padding: '10px 15px', outline: 'none', fontSize: '14px' }}
                        />
                        <button onClick={handleSend} disabled={loading} style={{ background: loading ? '#93c5fd' : '#2563EB', color: 'white', border: 'none', borderRadius: '50%', width: '40px', height: '40px', cursor: loading ? 'default' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>➤</button>
                    </div>
                </div>
            )}

            {/* --- 2. FLOATING TOGGLE BUTTON --- */}
            <button 
                onClick={() => setIsOpen(!isOpen)} 
                style={{
                    width: '60px',
                    height: '60px',
                    borderRadius: '50%',
                    background: '#2563EB',
                    border: 'none',
                    boxShadow: '0 4px 12px rgba(37, 99, 235, 0.4)',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    overflow: 'hidden', // Keeps the image round
                    padding: 0 
                }}
            >
                {isOpen ? (
                    <span style={{ color: 'white', fontSize: '30px', lineHeight: '1' }}>×</span>
                ) : (
                    // YOUR LOGO CODE HERE
                    <img 
                        src="/static/content/ai_logo.jpg" 
                        alt="AI"
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                        onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.parentNode.innerHTML = '<span style="font-size: 28px; color: white;">💬</span>';
                        }}
                    />
                )}
            </button>
        </div>
    );
};

export default ChatAssistant;