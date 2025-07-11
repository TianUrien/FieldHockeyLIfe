import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PublicPlayerProfile = () => {
  const { playerId } = useParams();
  const navigate = useNavigate();
  const [player, setPlayer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPlayerProfile = async () => {
      try {
        const response = await axios.get(`${API}/public/players/${playerId}`);
        setPlayer(response.data);
      } catch (error) {
        setError(error.response?.status === 404 ? 'Player not found' : 'Failed to load player profile');
        console.error('Error fetching player profile:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPlayerProfile();
  }, [playerId]);

  const getImageUrl = (filename) => {
    if (!filename) return null;
    return `${BACKEND_URL}/uploads/${filename}`;
  };

  const handleBackClick = () => {
    navigate(-1);
  };

  const handleContactClick = () => {
    // TODO: Implement contact functionality
    alert('Contact functionality will be implemented soon!');
  };

  if (loading) {
    return (
      <div className="public-profile-container">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading player profile...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="public-profile-container">
        <div className="error-state">
          <h2>Profile Not Found</h2>
          <p>{error}</p>
          <button onClick={handleBackClick} className="btn secondary">
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="public-profile-container">
      {/* Header Section */}
      <div className="profile-header-section">
        <div className="profile-nav">
          <button onClick={handleBackClick} className="back-btn">
            ← Back
          </button>
          <div className="profile-actions">
            <button onClick={handleContactClick} className="contact-btn">
              Contact Player
            </button>
          </div>
        </div>
        
        <div className="profile-hero">
          <div className="profile-avatar-large">
            {player.avatar ? (
              <img src={getImageUrl(player.avatar)} alt={player.name} />
            ) : (
              <div className="avatar-placeholder-large">
                {player.name.charAt(0).toUpperCase()}
              </div>
            )}
          </div>
          
          <div className="profile-hero-content">
            <h1>{player.name}</h1>
            <div className="profile-details">
              <span className="position-badge">{player.position}</span>
              <span className="experience-badge">{player.experience_level}</span>
              <span className="location-text">📍 {player.location}</span>
            </div>
            
            <div className="profile-stats">
              <div className="stat-item">
                <span className="stat-label">Experience</span>
                <span className="stat-value">{player.experience_level}</span>
              </div>
              {player.age && (
                <div className="stat-item">
                  <span className="stat-label">Age</span>
                  <span className="stat-value">{player.age}</span>
                </div>
              )}
              {player.country && (
                <div className="stat-item">
                  <span className="stat-label">Nationality</span>
                  <span className="stat-value">{player.country}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Content Sections */}
      <div className="profile-content">
        <div className="profile-main">
          {/* About Section */}
          {player.bio && (
            <div className="profile-section">
              <h3>About {player.name}</h3>
              <p className="bio-text">{player.bio}</p>
            </div>
          )}

          {/* Experience & Skills */}
          <div className="profile-section">
            <h3>Playing Information</h3>
            <div className="info-cards">
              <div className="info-card">
                <h4>Position</h4>
                <p>{player.position}</p>
              </div>
              <div className="info-card">
                <h4>Experience Level</h4>
                <p>{player.experience_level}</p>
              </div>
              <div className="info-card">
                <h4>Location</h4>
                <p>{player.location}</p>
              </div>
              {player.country && (
                <div className="info-card">
                  <h4>Country</h4>
                  <p>{player.country}</p>
                </div>
              )}
            </div>
          </div>

          {/* Media Gallery */}
          {player.photos && player.photos.length > 0 && (
            <div className="profile-section">
              <h3>Photo Gallery</h3>
              <div className="media-gallery">
                {player.photos.map((photo, index) => (
                  <div key={index} className="media-item">
                    <img src={getImageUrl(photo.filename)} alt={`Photo ${index + 1}`} />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Highlight Videos */}
          {player.videos && player.videos.length > 0 && (
            <div className="profile-section">
              <h3>Highlight Videos</h3>
              <div className="media-gallery">
                {player.videos.map((video, index) => (
                  <div key={index} className="media-item">
                    <video controls poster="">
                      <source src={getImageUrl(video.filename)} type="video/mp4" />
                      Your browser does not support the video tag.
                    </video>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="profile-sidebar">
          <div className="sidebar-section">
            <h4>Quick Info</h4>
            <div className="quick-info">
              <div className="info-row">
                <span className="label">Position:</span>
                <span className="value">{player.position}</span>
              </div>
              <div className="info-row">
                <span className="label">Experience:</span>
                <span className="value">{player.experience_level}</span>
              </div>
              <div className="info-row">
                <span className="label">Location:</span>
                <span className="value">{player.location}</span>
              </div>
              {player.age && (
                <div className="info-row">
                  <span className="label">Age:</span>
                  <span className="value">{player.age}</span>
                </div>
              )}
              {player.country && (
                <div className="info-row">
                  <span className="label">Country:</span>
                  <span className="value">{player.country}</span>
                </div>
              )}
            </div>
          </div>

          {/* CV/Resume */}
          {player.cv_document && (
            <div className="sidebar-section">
              <h4>CV/Resume</h4>
              <div className="cv-section">
                <a 
                  href={getImageUrl(player.cv_document)} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="cv-link"
                >
                  📄 Download CV/Resume
                </a>
              </div>
            </div>
          )}

          {/* Contact Section */}
          <div className="sidebar-section">
            <h4>Get in Touch</h4>
            <button onClick={handleContactClick} className="contact-btn-full">
              Contact {player.name}
            </button>
            <p className="contact-note">
              Interested in this player? Send them a message to start a conversation.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PublicPlayerProfile;