import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:8000/api';

function App() {
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    fetchConversations();
  }, []);

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
          message: messageToSend
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

  return (
    <div className="app">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <button className="new-chat-btn" onClick={createNewChat}>
            New chat
          </button>
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
              <div className="conversation-title">{conversation.title}</div>
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
      </div>

      {/* Main Content */}
      <div className="main-content">
        {currentConversation ? (
          <>
            <div className="chat-header">
              <h1 className="chat-title">{currentConversation.title}</h1>
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
          </div>
        )}

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
      </div>
    </div>
  );
}

export default App;
