import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const EmailVerification = () => {
  const [status, setStatus] = useState('verifying');
  const [message, setMessage] = useState('Verifying your email...');
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const verifyEmail = async () => {
      try {
        const urlParams = new URLSearchParams(location.search);
        const token = urlParams.get('token');
        const userType = urlParams.get('type');

        if (!token || !userType) {
          setStatus('error');
          setMessage('Invalid verification link. Please check your email for the correct link.');
          return;
        }

        const response = await axios.post(`${API}/verify-email`, {
          token: token,
          user_type: userType
        });

        setStatus('success');
        setMessage(response.data.message);

        // Redirect to login after 3 seconds
        setTimeout(() => {
          navigate(`/${userType}-login`);
        }, 3000);

      } catch (error) {
        setStatus('error');
        setMessage(error.response?.data?.detail || 'Email verification failed. Please try again.');
      }
    };

    verifyEmail();
  }, [location, navigate]);

  const handleResendEmail = async () => {
    try {
      const urlParams = new URLSearchParams(location.search);
      const userType = urlParams.get('type');
      const email = prompt('Please enter your email address:');
      
      if (!email) return;

      await axios.post(`${API}/resend-verification`, {
        email: email,
        user_type: userType
      });

      setMessage('Verification email resent! Please check your inbox.');
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Failed to resend email.');
    }
  };

  return (
    <div className="verification-container">
      <div className="verification-card">
        <div className="verification-icon">
          {status === 'verifying' && (
            <div className="spinner">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M12 6v6l4 2"></path>
              </svg>
            </div>
          )}
          {status === 'success' && (
            <div className="success-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22,4 12,14.01 9,11.01"></polyline>
              </svg>
            </div>
          )}
          {status === 'error' && (
            <div className="error-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="15" y1="9" x2="9" y2="15"></line>
                <line x1="9" y1="9" x2="15" y2="15"></line>
              </svg>
            </div>
          )}
        </div>

        <h2>{status === 'success' ? 'Email Verified!' : status === 'error' ? 'Verification Failed' : 'Verifying Email'}</h2>
        <p className="verification-message">{message}</p>

        {status === 'success' && (
          <div className="success-actions">
            <p className="redirect-message">You'll be redirected to login in a few seconds...</p>
            <button 
              className="login-btn"
              onClick={() => {
                const urlParams = new URLSearchParams(location.search);
                const userType = urlParams.get('type');
                navigate(`/${userType}-login`);
              }}
            >
              Login Now
            </button>
          </div>
        )}

        {status === 'error' && (
          <div className="error-actions">
            <button className="resend-btn" onClick={handleResendEmail}>
              Resend Verification Email
            </button>
            <button 
              className="home-btn"
              onClick={() => navigate('/')}
            >
              Return Home
            </button>
          </div>
        )}
      </div>

      <style jsx>{`
        .verification-container {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 20px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .verification-card {
          background: white;
          padding: 40px;
          border-radius: 12px;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
          text-align: center;
          max-width: 400px;
          width: 100%;
        }

        .verification-icon {
          margin-bottom: 24px;
        }

        .spinner {
          color: #6366f1;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        .success-icon {
          color: #10b981;
        }

        .error-icon {
          color: #ef4444;
        }

        h2 {
          margin: 0 0 16px 0;
          color: #1f2937;
          font-size: 24px;
          font-weight: 600;
        }

        .verification-message {
          color: #6b7280;
          margin-bottom: 24px;
          line-height: 1.5;
        }

        .success-actions, .error-actions {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .redirect-message {
          font-size: 14px;
          color: #9ca3af;
          margin-bottom: 8px;
        }

        .login-btn, .resend-btn, .home-btn {
          padding: 12px 24px;
          border: none;
          border-radius: 6px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .login-btn {
          background: #10b981;
          color: white;
        }

        .login-btn:hover {
          background: #059669;
        }

        .resend-btn {
          background: #6366f1;
          color: white;
        }

        .resend-btn:hover {
          background: #4f46e5;
        }

        .home-btn {
          background: #f3f4f6;
          color: #374151;
        }

        .home-btn:hover {
          background: #e5e7eb;
        }
      `}</style>
    </div>
  );
};

export default EmailVerification;