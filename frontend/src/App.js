import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:8000/api';

function App() {
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [useCompanyData, setUseCompanyData] = useState(false);
  const [currentPage, setCurrentPage] = useState('chat'); // 'chat' or 'admin'
  const [dataSources, setDataSources] = useState([]);
  const [ragStats, setRagStats] = useState({});
  const [uploadingFile, setUploadingFile] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    fetchConversations();
    if (currentPage === 'admin') {
      fetchDataSources();
      fetchRagStats();
    }
  }, [currentPage]);

  useEffect(() => {
    scrollToBottom();
  }, [currentConversation]);

  const fetchConversations = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/conversations/`);
      setConversations(response.data);
    } catch (error) {
      console.error('Error fetching conversations:', error);
    }
  };

  const fetchConversation = async (conversationId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/conversations/${conversationId}/`);
      setCurrentConversation(response.data);
    } catch (error) {
      console.error('Error fetching conversation:', error);
    }
  };

  const fetchDataSources = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/data-sources/`);
      setDataSources(response.data);
    } catch (error) {
      console.error('Error fetching data sources:', error);
    }
  };

  const fetchRagStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/rag-stats/`);
      setRagStats(response.data);
    } catch (error) {
      console.error('Error fetching RAG stats:', error);
    }
  };

  const createNewChat = () => {
    setCurrentConversation(null);
    setMessage('');
  };

  const selectConversation = (conversation) => {
    setCurrentConversation(conversation);
    fetchConversation(conversation.id);
  };

  const sendMessage = async () => {
    if (!message.trim()) return;

    setLoading(true);
    const messageToSend = message;
    setMessage('');

    try {
      let response;
      if (!currentConversation) {
        // Create new conversation
        response = await axios.post(`${API_BASE_URL}/conversations/`, {
          message: messageToSend,
          use_company_data: useCompanyData
        });
        setCurrentConversation(response.data);
        await fetchConversations(); // Refresh conversation list
      } else {
        // Add message to existing conversation
        response = await axios.post(`${API_BASE_URL}/conversations/${currentConversation.id}/`, {
          message: messageToSend
        });
        setCurrentConversation(response.data);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessage(messageToSend); // Restore message if failed
    } finally {
      setLoading(false);
    }
  };

  const submitFeedback = async (messageId, feedbackType, rating = null, comment = '') => {
    try {
      await axios.post(`${API_BASE_URL}/conversations/${currentConversation.id}/feedback/`, {
        message_id: messageId,
        feedback_type: feedbackType,
        rating: rating,
        comment: comment
      });
      
      // Refresh conversation to show updated feedback count
      await fetchConversation(currentConversation.id);
      await fetchConversations();
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  const deleteConversation = async (conversationId, e) => {
    e.stopPropagation();
    try {
      await axios.delete(`${API_BASE_URL}/conversations/${conversationId}/delete/`);
      if (currentConversation && currentConversation.id === conversationId) {
        setCurrentConversation(null);
      }
      await fetchConversations();
    } catch (error) {
      console.error('Error deleting conversation:', error);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      alert('Only PDF files are supported');
      return;
    }

    setUploadingFile(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', file.name);

    try {
      await axios.post(`${API_BASE_URL}/data-sources/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      await fetchDataSources();
      await fetchRagStats();
      alert('File uploaded successfully! Processing in background...');
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Error uploading file');
    } finally {
      setUploadingFile(false);
    }
  };

  const toggleDataSource = async (dataSourceId, isActive) => {
    try {
      await axios.put(`${API_BASE_URL}/data-sources/${dataSourceId}/`, {
        is_active: isActive
      });
      await fetchDataSources();
    } catch (error) {
      console.error('Error toggling data source:', error);
    }
  };

  const deleteDataSource = async (dataSourceId) => {
    if (!window.confirm('Are you sure you want to delete this data source?')) return;
    
    try {
      await axios.delete(`${API_BASE_URL}/data-sources/${dataSourceId}/`);
      await fetchDataSources();
      await fetchRagStats();
    } catch (error) {
      console.error('Error deleting data source:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const FeedbackButtons = ({ message }) => {
    if (message.role !== 'assistant') return null;

    return (
      <div className="feedback-buttons">
        <button
          className="feedback-btn thumbs-up"
          onClick={() => submitFeedback(message.id, 'thumbs_up')}
          title="Thumbs up"
        >
          👍
        </button>
        <button
          className="feedback-btn thumbs-down"
          onClick={() => submitFeedback(message.id, 'thumbs_down')}
          title="Thumbs down"
        >
          👎
        </button>
        <button
          className="feedback-btn rating"
          onClick={() => {
            const rating = prompt('Rate this response (1-5):');
            if (rating && rating >= 1 && rating <= 5) {
              submitFeedback(message.id, 'rating', parseInt(rating));
            }
          }}
          title="Rate response"
        >
          ⭐
        </button>
      </div>
    );
  };

  const AdminPage = () => (
    <div className="admin-page">
      <div className="admin-header">
        <h1>Company Data Management</h1>
        <button className="back-btn" onClick={() => setCurrentPage('chat')}>
          ← Back to Chat
        </button>
      </div>

      <div className="admin-content">
        <div className="stats-section">
          <h2>RAG System Statistics</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <h3>Total Sources</h3>
              <p>{ragStats.total_sources || 0}</p>
            </div>
            <div className="stat-card">
              <h3>Active Sources</h3>
              <p>{ragStats.active_sources || 0}</p>
            </div>
            <div className="stat-card">
              <h3>Total Chunks</h3>
              <p>{ragStats.total_chunks || 0}</p>
            </div>
            <div className="stat-card">
              <h3>Total Tokens</h3>
              <p>{ragStats.total_tokens || 0}</p>
            </div>
          </div>
        </div>

        <div className="upload-section">
          <h2>Upload New Document</h2>
          <div className="upload-area">
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileUpload}
              disabled={uploadingFile}
              id="file-upload"
            />
            <label htmlFor="file-upload" className="upload-label">
              {uploadingFile ? 'Uploading...' : 'Choose PDF file'}
            </label>
          </div>
        </div>

        <div className="sources-section">
          <h2>Data Sources</h2>
          <div className="sources-list">
            {dataSources.map((source) => (
              <div key={source.id} className="source-item">
                <div className="source-info">
                  <h3>{source.name}</h3>
                  <p>Type: {source.source_type}</p>
                  <p>Status: <span className={`status ${source.status}`}>{source.status}</span></p>
                  <p>Chunks: {source.total_chunks}</p>
                  <p>Tokens: {source.total_tokens}</p>
                </div>
                <div className="source-actions">
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={source.is_active}
                      onChange={(e) => toggleDataSource(source.id, e.target.checked)}
                      disabled={source.status !== 'completed'}
                    />
                    <span className="slider"></span>
                  </label>
                  <button
                    className="delete-btn"
                    onClick={() => deleteDataSource(source.id)}
                    disabled={source.status === 'processing'}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="app">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <button className="new-chat-btn" onClick={createNewChat}>
            New chat
          </button>
          <button 
            className="admin-btn" 
            onClick={() => setCurrentPage(currentPage === 'chat' ? 'admin' : 'chat')}
          >
            {currentPage === 'chat' ? 'Admin' : 'Chat'}
          </button>
        </div>
        
        {currentPage === 'chat' && (
          <>
            <div className="company-data-toggle">
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={useCompanyData}
                  onChange={(e) => setUseCompanyData(e.target.checked)}
                />
                <span className="slider"></span>
              </label>
              <span>Use company data</span>
            </div>
            
            <div className="conversations-section">
              <div className="conversations-title">Chats</div>
              {conversations.map((conversation) => (
                <div
                  key={conversation.id}
                  className={`conversation-item ${
                    currentConversation?.id === conversation.id ? 'active' : ''
                  }`}
                  onClick={() => selectConversation(conversation)}
                >
                  <div className="conversation-title">
                    {conversation.title}
                    {conversation.use_company_data && <span className="rag-indicator">📄</span>}
                  </div>
                  <div className="conversation-meta">
                    {conversation.message_count} messages • {formatTime(conversation.updated_at)}
                    {conversation.feedback_count > 0 && (
                      <span className="feedback-indicator"> • {conversation.feedback_count} feedback</span>
                    )}
                    <button
                      className="delete-btn"
                      onClick={(e) => deleteConversation(conversation.id, e)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Main Content */}
      <div className="main-content">
        {currentPage === 'admin' ? (
          <AdminPage />
        ) : currentConversation ? (
          <>
            <div className="chat-header">
              <h1 className="chat-title">
                {currentConversation.title}
                {currentConversation.use_company_data && <span className="rag-indicator">📄</span>}
              </h1>
            </div>
            
            <div className="chat-messages">
              {currentConversation.messages.map((msg) => (
                <div key={msg.id} className={`message ${msg.role}`}>
                  <div className="message-content">
                    {msg.content}
                    <div className="message-time">{formatTime(msg.created_at)}</div>
                    <FeedbackButtons message={msg} />
                  </div>
                </div>
              ))}
              {loading && (
                <div className="message assistant">
                  <div className="message-content">
                    <div className="loading">
                      <div className="spinner"></div>
                      Thinking...
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </>
        ) : (
          <div className="empty-state">
            <h2>What can I help with?</h2>
            <p>Start a new conversation to begin chatting</p>
            {useCompanyData && (
              <p className="rag-notice">📄 Company data will be used for responses</p>
            )}
          </div>
        )}

        {currentPage === 'chat' && (
          <div className="chat-input">
            <div className="input-container">
              <textarea
                className="message-input"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask anything..."
                disabled={loading}
                rows={1}
              />
              <button
                className="send-btn"
                onClick={sendMessage}
                disabled={!message.trim() || loading}
              >
                Send
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
