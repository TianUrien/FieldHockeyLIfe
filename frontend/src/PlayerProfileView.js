import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PlayerProfileView = ({ playerId, onClose }) => {
  const [player, setPlayer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPlayerProfile = async () => {
      try {
        const response = await axios.get(`${API}/players/${playerId}/profile`);
        setPlayer(response.data);
      } catch (error) {
        setError('Failed to load player profile');
        console.error('Error fetching player profile:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPlayerProfile();
  }, [playerId]);

  if (loading) {
    return (
      <div className="profile-modal">
        <div className="profile-content">
          <div className="loading">Loading player profile...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="profile-modal">
        <div className="profile-content">
          <div className="error-message">{error}</div>
          <button onClick={onClose} className="btn secondary">Close</button>
        </div>
      </div>
    );
  }

  const getImageUrl = (filename) => {
    if (!filename) return null;
    return `${BACKEND_URL}/uploads/${filename}`;
  };

  return (
    <div className="profile-modal">
      <div className="profile-content">
        <div className="profile-header">
          <button onClick={onClose} className="close-btn">×</button>
          <div className="profile-avatar">
            {player.avatar ? (
              <img src={getImageUrl(player.avatar)} alt={player.name} />
            ) : (
              <div className="avatar-placeholder">
                {player.name.charAt(0).toUpperCase()}
              </div>
            )}
          </div>
          <h2>{player.name}</h2>
          <p className="profile-subtitle">{player.position} • {player.location}</p>
        </div>

        <div className="profile-body">
          <div className="profile-section">
            <h3>Player Information</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="label">Position:</span>
                <span className="value">{player.position}</span>
              </div>
              <div className="info-item">
                <span className="label">Experience Level:</span>
                <span className="value">{player.experience_level}</span>
              </div>
              <div className="info-item">
                <span className="label">Location:</span>
                <span className="value">{player.location}</span>
              </div>
              {player.country && (
                <div className="info-item">
                  <span className="label">Country:</span>
                  <span className="value">{player.country}</span>
                </div>
              )}
              {player.age && (
                <div className="info-item">
                  <span className="label">Age:</span>
                  <span className="value">{player.age}</span>
                </div>
              )}
              <div className="info-item">
                <span className="label">Email:</span>
                <span className="value">{player.email}</span>
              </div>
            </div>
          </div>

          {player.bio && (
            <div className="profile-section">
              <h3>About</h3>
              <p className="bio-text">{player.bio}</p>
            </div>
          )}

          {player.photos && player.photos.length > 0 && (
            <div className="profile-section">
              <h3>Photos</h3>
              <div className="media-grid">
                {player.photos.map((photo, index) => (
                  <div key={index} className="media-item">
                    <img src={getImageUrl(photo.filename)} alt={`Photo ${index + 1}`} />
                  </div>
                ))}
              </div>
            </div>
          )}

          {player.videos && player.videos.length > 0 && (
            <div className="profile-section">
              <h3>Videos</h3>
              <div className="media-grid">
                {player.videos.map((video, index) => (
                  <div key={index} className="media-item">
                    <video controls>
                      <source src={getImageUrl(video.filename)} type="video/mp4" />
                      Your browser does not support the video tag.
                    </video>
                  </div>
                ))}
              </div>
            </div>
          )}

          {player.cv_document && (
            <div className="profile-section">
              <h3>CV/Resume</h3>
              <div className="document-item">
                <a 
                  href={getImageUrl(player.cv_document)} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="document-link"
                >
                  📄 View CV/Resume
                </a>
              </div>
            </div>
          )}
        </div>

        <div className="profile-footer">
          <button onClick={onClose} className="btn primary">Close</button>
        </div>
      </div>
    </div>
  );
};

export default PlayerProfileView;