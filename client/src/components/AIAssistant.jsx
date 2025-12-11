import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import api from '../services/api';

function AIAssistant({ isOpen, onClose }) {
    const [messages, setMessages] = useState([
        {
            role: 'assistant',
            content: "👋 Hello! I'm your AI legal research assistant. Ask me about cases, statutes, or legal concepts. I'll provide answers with source citations.\n\nTry asking:\n- \"Is Roe v. Wade still good law?\"\n- \"What is the statute of limitations for fraud?\"\n- \"What are Miranda rights?\""
        }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [examples, setExamples] = useState([]);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        api.getChatExamples()
            .then(data => setExamples(data.examples || []))
            .catch(err => console.error('Failed to load examples:', err));
    }, []);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSubmit = async (e) => {
        e?.preventDefault();
        const question = input.trim();
        if (!question || loading) return;

        // Add user message
        const userMessage = { role: 'user', content: question };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const response = await api.chat(question, messages.slice(-10));

            // Format assistant response with sources
            let content = response.answer;

            if (response.sources?.length > 0) {
                content += '\n\n---\n**Sources:**\n';
                response.sources.forEach((source, i) => {
                    content += `${i + 1}. *${source.case_title}* (${source.citation})\n`;
                });
            }

            if (response.follow_up_questions?.length > 0) {
                content += '\n\n**You might also ask:**\n';
                response.follow_up_questions.forEach((q) => {
                    content += `- ${q}\n`;
                });
            }

            setMessages(prev => [...prev, { role: 'assistant', content }]);
        } catch (error) {
            console.error('Chat failed:', error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: '❌ Sorry, I encountered an error. Please try again.'
            }]);
        } finally {
            setLoading(false);
        }
    };

    const handleExampleClick = (question) => {
        setInput(question);
    };

    return (
        <div className={`chat-panel ${isOpen ? 'open' : ''}`}>
            {/* Header */}
            <div className="chat-header">
                <div className="chat-title">
                    <span>🤖</span>
                    <span>AI Legal Assistant</span>
                </div>
                <button
                    onClick={onClose}
                    style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--color-text-secondary)',
                        cursor: 'pointer',
                        fontSize: '1.5rem'
                    }}
                >
                    ×
                </button>
            </div>

            {/* Messages */}
            <div className="chat-messages">
                {messages.map((msg, i) => (
                    <div key={i} className={`chat-message ${msg.role}`}>
                        {msg.role === 'assistant' ? (
                            <ReactMarkdown
                                components={{
                                    p: ({ children }) => <p style={{ margin: '0.5em 0' }}>{children}</p>,
                                    strong: ({ children }) => <strong style={{ color: 'var(--color-accent-primary)' }}>{children}</strong>,
                                    em: ({ children }) => <em style={{ color: 'var(--color-text-primary)' }}>{children}</em>,
                                    hr: () => <hr style={{ border: 'none', borderTop: '1px solid var(--color-border)', margin: '1em 0' }} />,
                                    ul: ({ children }) => <ul style={{ paddingLeft: '1.2em', margin: '0.5em 0' }}>{children}</ul>,
                                    li: ({ children }) => <li style={{ marginBottom: '0.25em' }}>{children}</li>
                                }}
                            >
                                {msg.content}
                            </ReactMarkdown>
                        ) : (
                            msg.content
                        )}
                    </div>
                ))}

                {loading && (
                    <div className="chat-message assistant">
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <div className="loading-spinner" />
                            <span>Researching...</span>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Quick Examples */}
            {messages.length <= 1 && examples.length > 0 && (
                <div style={{
                    padding: '0 1rem',
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: '0.5rem'
                }}>
                    {examples.slice(0, 3).map((ex, i) => (
                        <button
                            key={i}
                            onClick={() => handleExampleClick(ex.question)}
                            style={{
                                padding: '0.5rem 0.75rem',
                                background: 'var(--color-bg-tertiary)',
                                border: '1px solid var(--color-border)',
                                borderRadius: '8px',
                                color: 'var(--color-text-secondary)',
                                fontSize: '0.75rem',
                                cursor: 'pointer',
                                transition: 'all 0.2s'
                            }}
                        >
                            {ex.question.length > 40 ? ex.question.slice(0, 40) + '...' : ex.question}
                        </button>
                    ))}
                </div>
            )}

            {/* Input */}
            <form onSubmit={handleSubmit} className="chat-input-container">
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <textarea
                        className="chat-input"
                        placeholder="Ask a legal question..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                handleSubmit();
                            }
                        }}
                        rows={2}
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || loading}
                        style={{
                            padding: '0.5rem 1rem',
                            background: 'var(--color-accent-primary)',
                            border: 'none',
                            borderRadius: '8px',
                            color: 'white',
                            cursor: input.trim() && !loading ? 'pointer' : 'not-allowed',
                            opacity: input.trim() && !loading ? 1 : 0.5
                        }}
                    >
                        ➤
                    </button>
                </div>
                <p style={{
                    fontSize: '0.7rem',
                    color: 'var(--color-text-muted)',
                    marginTop: '0.5rem',
                    textAlign: 'center'
                }}>
                    AI responses may contain errors. Always verify with primary sources.
                </p>
            </form>
        </div>
    );
}

export default AIAssistant;
