import React, { useState } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MessageComposer = ({ 
  isOpen, 
  onClose, 
  receiverId, 
  receiverType, 
  receiverName, 
  currentUser, 
  userType,
  replyToMessageId = null,
  subject = ''
}) => {
  const [formData, setFormData] = useState({
    subject: subject || `Message from ${currentUser?.name}`,
    content: ''
  });
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.content.trim()) {
      setError('Please enter a message');
      return;
    }

    setSending(true);
    setError(null);

    try {
      await axios.post(`${API}/messages/send?sender_id=${currentUser.id}&sender_type=${userType}`, {
        receiver_id: receiverId,
        receiver_type: receiverType,
        subject: formData.subject,
        content: formData.content,
        reply_to_message_id: replyToMessageId
      });

      // Reset form and close modal
      setFormData({ subject: '', content: '' });
      onClose();
      
      // Optional: Show success message
      alert('Message sent successfully!');
      
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to send message');
    } finally {
      setSending(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="message-composer-overlay">
      <div className="message-composer-modal">
        <div className="composer-header">
          <h3>Send Message to {receiverName}</h3>
          <button onClick={onClose} className="close-btn">×</button>
        </div>

        <form onSubmit={handleSubmit} className="composer-form">
          <div className="form-group">
            <label htmlFor="subject">Subject</label>
            <input
              id="subject"
              type="text"
              value={formData.subject}
              onChange={(e) => handleChange('subject', e.target.value)}
              placeholder="Enter subject"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="content">Message</label>
            <textarea
              id="content"
              value={formData.content}
              onChange={(e) => handleChange('content', e.target.value)}
              placeholder="Type your message here..."
              rows={6}
              required
            />
            <div className="char-count">
              {formData.content.length}/1000 characters
            </div>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="composer-actions">
            <button 
              type="button" 
              onClick={onClose} 
              className="btn secondary"
              disabled={sending}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn primary"
              disabled={sending || !formData.content.trim()}
            >
              {sending ? 'Sending...' : 'Send Message'}
            </button>
          </div>
        </form>
      </div>

      <style jsx>{`
        .message-composer-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          padding: var(--space-4);
        }

        .message-composer-modal {
          background: white;
          border-radius: var(--radius-lg);
          box-shadow: var(--shadow-xl);
          max-width: 600px;
          width: 100%;
          max-height: 80vh;
          overflow-y: auto;
        }

        .composer-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: var(--space-4);
          border-bottom: 1px solid var(--border-light);
          background: var(--background-gray);
          border-radius: var(--radius-lg) var(--radius-lg) 0 0;
        }

        .composer-header h3 {
          margin: 0;
          color: var(--text-primary);
          font-size: var(--font-size-lg);
        }

        .close-btn {
          background: none;
          border: none;
          font-size: 24px;
          color: var(--text-secondary);
          cursor: pointer;
          padding: var(--space-1);
          border-radius: var(--radius-sm);
          transition: all 0.2s ease;
        }

        .close-btn:hover {
          background: var(--border-light);
          color: var(--text-primary);
        }

        .composer-form {
          padding: var(--space-4);
        }

        .form-group {
          margin-bottom: var(--space-4);
        }

        .form-group label {
          display: block;
          margin-bottom: var(--space-2);
          font-weight: 500;
          color: var(--text-primary);
          font-size: var(--font-size-sm);
        }

        .form-group input,
        .form-group textarea {
          width: 100%;
          padding: var(--space-3);
          border: 2px solid var(--border-light);
          border-radius: var(--radius-md);
          font-size: var(--font-size-sm);
          transition: all 0.2s ease;
          font-family: inherit;
          resize: vertical;
        }

        .form-group input:focus,
        .form-group textarea:focus {
          outline: none;
          border-color: var(--primary-blue);
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .char-count {
          text-align: right;
          font-size: var(--font-size-xs);
          color: var(--text-secondary);
          margin-top: var(--space-1);
        }

        .error-message {
          background: rgba(239, 68, 68, 0.1);
          color: var(--error-red);
          padding: var(--space-3);
          border-radius: var(--radius-md);
          font-size: var(--font-size-sm);
          margin-bottom: var(--space-4);
        }

        .composer-actions {
          display: flex;
          gap: var(--space-3);
          justify-content: flex-end;
          padding-top: var(--space-4);
          border-top: 1px solid var(--border-light);
        }

        .btn {
          padding: var(--space-2) var(--space-4);
          border-radius: var(--radius-md);
          font-size: var(--font-size-sm);
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;
          border: none;
        }

        .btn.primary {
          background: var(--primary-blue);
          color: white;
        }

        .btn.primary:hover:not(:disabled) {
          background: var(--dark-blue);
        }

        .btn.primary:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .btn.secondary {
          background: var(--background-gray);
          color: var(--text-secondary);
        }

        .btn.secondary:hover:not(:disabled) {
          background: var(--border-light);
        }

        @media (max-width: 768px) {
          .message-composer-overlay {
            padding: var(--space-2);
          }

          .message-composer-modal {
            max-height: 90vh;
          }

          .composer-actions {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
};

export default MessageComposer;