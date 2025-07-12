import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import MessageComposer from './MessageComposer';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MessagingCenter = ({ currentUser, userType, onClose }) => {
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [messagesLoading, setMessagesLoading] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showComposer, setShowComposer] = useState(false);
  const [newMessageData, setNewMessageData] = useState(null);
  const [messageInput, setMessageInput] = useState('');
  const [sending, setSending] = useState(false);
  
  const messagesEndRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (currentUser && userType) {
      loadConversations();
      loadUnreadCount();
    }
  }, [currentUser, userType]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadConversations = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/conversations/${currentUser.id}/${userType}`);
      setConversations(response.data);
    } catch (error) {
      console.error('Error loading conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUnreadCount = async () => {
    try {
      const response = await axios.get(`${API}/messages/unread-count/${currentUser.id}/${userType}`);
      setUnreadCount(response.data.unread_count);
    } catch (error) {
      console.error('Error loading unread count:', error);
    }
  };

  const loadMessages = async (conversationId) => {
    try {
      setMessagesLoading(true);
      const response = await axios.get(
        `${API}/conversations/${conversationId}/messages?user_id=${currentUser.id}&user_type=${userType}`
      );
      setMessages(response.data);
      
      // Mark conversation as read
      await axios.put(`${API}/conversations/${conversationId}/mark-read?user_id=${currentUser.id}&user_type=${userType}`);
      
      // Refresh conversations to update unread counts
      loadConversations();
      loadUnreadCount();
      
    } catch (error) {
      console.error('Error loading messages:', error);
    } finally {
      setMessagesLoading(false);
    }
  };

  const sendQuickMessage = async (e) => {
    e.preventDefault();
    
    if (!messageInput.trim() || !selectedConversation) return;
    
    setSending(true);
    
    try {
      // Determine receiver from conversation
      const conversation = selectedConversation.conversation;
      const receiverId = conversation.participant_1_id === currentUser.id ? 
        conversation.participant_2_id : conversation.participant_1_id;
      const receiverType = conversation.participant_1_id === currentUser.id ? 
        conversation.participant_2_type : conversation.participant_1_type;
      
      await axios.post(`${API}/messages/send?sender_id=${currentUser.id}&sender_type=${userType}`, {
        receiver_id: receiverId,
        receiver_type: receiverType,
        content: messageInput
      });
      
      // Clear input and reload messages
      setMessageInput('');
      loadMessages(selectedConversation.conversation.id);
      
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Failed to send message');
    } finally {
      setSending(false);
    }
  };

  const handleConversationSelect = (conversation) => {
    setSelectedConversation(conversation);
    loadMessages(conversation.conversation.id);
  };

  const handleDeleteConversation = async (conversationId) => {
    if (!confirm('Are you sure you want to delete this conversation?')) return;
    
    try {
      await axios.delete(`${API}/conversations/${conversationId}?user_id=${currentUser.id}&user_type=${userType}`);
      loadConversations();
      
      if (selectedConversation?.conversation.id === conversationId) {
        setSelectedConversation(null);
        setMessages([]);
      }
    } catch (error) {
      console.error('Error deleting conversation:', error);
      alert('Failed to delete conversation');
    }
  };

  const handleNewMessage = (receiverId, receiverType, receiverName) => {
    setNewMessageData({ receiverId, receiverType, receiverName });
    setShowComposer(true);
  };

  const handleComposerClose = () => {
    setShowComposer(false);
    setNewMessageData(null);
    // Refresh conversations after sending
    loadConversations();
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatMessageTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (days === 1) {
      return 'Yesterday';
    } else if (days < 7) {
      return date.toLocaleDateString([], { weekday: 'short' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };

  const getOtherParticipant = (conversation) => {
    if (conversation.participant_1_id === currentUser.id) {
      return {
        id: conversation.participant_2_id,
        type: conversation.participant_2_type,
        name: conversation.participant_2_name
      };
    } else {
      return {
        id: conversation.participant_1_id,
        type: conversation.participant_1_type,
        name: conversation.participant_1_name
      };
    }
  };

  return (
    <div className="messaging-center">
      <div className="messaging-header">
        <div className="header-title">
          <h2>Messages</h2>
          {unreadCount > 0 && (
            <span className="unread-badge">{unreadCount}</span>
          )}
        </div>
        <div className="header-actions">
          <button 
            className="btn secondary"
            onClick={() => setShowComposer(true)}
          >
            New Message
          </button>
          <button onClick={onClose} className="close-btn">×</button>
        </div>
      </div>

      <div className="messaging-content">
        {/* Conversations List */}
        <div className="conversations-panel">
          <div className="conversations-header">
            <h3>Conversations</h3>
          </div>
          
          {loading ? (
            <div className="loading-state">Loading conversations...</div>
          ) : conversations.length === 0 ? (
            <div className="empty-state">
              <p>No conversations yet</p>
              <button 
                className="btn primary"
                onClick={() => setShowComposer(true)}
              >
                Start a conversation
              </button>
            </div>
          ) : (
            <div className="conversations-list">
              {conversations.map((conv) => {
                const otherParticipant = getOtherParticipant(conv.conversation);
                const isSelected = selectedConversation?.conversation.id === conv.conversation.id;
                
                return (
                  <div
                    key={conv.conversation.id}
                    className={`conversation-item ${isSelected ? 'selected' : ''}`}
                    onClick={() => handleConversationSelect(conv)}
                  >
                    <div className="conversation-avatar">
                      {otherParticipant.name.charAt(0).toUpperCase()}
                    </div>
                    
                    <div className="conversation-content">
                      <div className="conversation-header">
                        <h4>{otherParticipant.name}</h4>
                        <span className="conversation-time">
                          {conv.conversation.last_message_at && 
                            formatMessageTime(conv.conversation.last_message_at)}
                        </span>
                      </div>
                      
                      <div className="conversation-preview">
                        <p>{conv.conversation.last_message_content || 'No messages yet'}</p>
                        {conv.unread_count > 0 && (
                          <span className="unread-count">{conv.unread_count}</span>
                        )}
                      </div>
                    </div>
                    
                    <button
                      className="delete-conversation-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteConversation(conv.conversation.id);
                      }}
                      title="Delete conversation"
                    >
                      🗑️
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Messages Panel */}
        <div className="messages-panel">
          {selectedConversation ? (
            <>
              <div className="messages-header">
                <div className="chat-participant">
                  <div className="participant-avatar">
                    {getOtherParticipant(selectedConversation.conversation).name.charAt(0).toUpperCase()}
                  </div>
                  <div className="participant-info">
                    <h4>{getOtherParticipant(selectedConversation.conversation).name}</h4>
                    <span className="participant-type">
                      {getOtherParticipant(selectedConversation.conversation).type === 'player' ? 'Player' : 'Club'}
                    </span>
                  </div>
                </div>
                
                <button
                  className="view-profile-btn"
                  onClick={() => {
                    const participant = getOtherParticipant(selectedConversation.conversation);
                    navigate(`/${participant.type === 'player' ? 'players' : 'clubs'}/${participant.id}`);
                  }}
                >
                  View Profile
                </button>
              </div>

              <div className="messages-container">
                {messagesLoading ? (
                  <div className="loading-state">Loading messages...</div>
                ) : messages.length === 0 ? (
                  <div className="empty-messages">
                    <p>No messages in this conversation yet.</p>
                  </div>
                ) : (
                  <div className="messages-list">
                    {messages.map((message) => (
                      <div
                        key={message.id}
                        className={`message-item ${message.sender_id === currentUser.id ? 'sent' : 'received'}`}
                      >
                        <div className="message-content">
                          <div className="message-text">{message.content}</div>
                          <div className="message-time">
                            {formatMessageTime(message.created_at)}
                          </div>
                        </div>
                      </div>
                    ))}
                    <div ref={messagesEndRef} />
                  </div>
                )}
              </div>

              <form onSubmit={sendQuickMessage} className="message-input-form">
                <input
                  type="text"
                  value={messageInput}
                  onChange={(e) => setMessageInput(e.target.value)}
                  placeholder="Type your message..."
                  disabled={sending}
                />
                <button 
                  type="submit" 
                  disabled={!messageInput.trim() || sending}
                  className="send-btn"
                >
                  {sending ? '...' : 'Send'}
                </button>
              </form>
            </>
          ) : (
            <div className="no-conversation-selected">
              <h3>Select a conversation</h3>
              <p>Choose a conversation from the list to start messaging</p>
            </div>
          )}
        </div>
      </div>

      {/* Message Composer Modal */}
      {showComposer && (
        <MessageComposer
          isOpen={showComposer}
          onClose={handleComposerClose}
          receiverId={newMessageData?.receiverId}
          receiverType={newMessageData?.receiverType}
          receiverName={newMessageData?.receiverName}
          currentUser={currentUser}
          userType={userType}
        />
      )}
    </div>
  );
};

export default MessagingCenter;