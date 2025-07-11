import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ClubProfileView = ({ clubId, onClose }) => {
  const [club, setClub] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchClubProfile = async () => {
      try {
        const response = await axios.get(`${API}/clubs/${clubId}/profile`);
        setClub(response.data);
      } catch (error) {
        setError('Failed to load club profile');
        console.error('Error fetching club profile:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchClubProfile();
  }, [clubId]);

  if (loading) {
    return (
      <div className="profile-modal">
        <div className="profile-content">
          <div className="loading">Loading club profile...</div>
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
            {club.logo ? (
              <img src={getImageUrl(club.logo)} alt={club.name} />
            ) : (
              <div className="avatar-placeholder">
                {club.name.charAt(0).toUpperCase()}
              </div>
            )}
          </div>
          <h2>{club.name}</h2>
          <p className="profile-subtitle">{club.location}</p>
        </div>

        <div className="profile-body">
          <div className="profile-section">
            <h3>Club Information</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="label">Location:</span>
                <span className="value">{club.location}</span>
              </div>
              {club.club_type && (
                <div className="info-item">
                  <span className="label">Type:</span>
                  <span className="value">{club.club_type}</span>
                </div>
              )}
              {club.established_year && (
                <div className="info-item">
                  <span className="label">Established:</span>
                  <span className="value">{club.established_year}</span>
                </div>
              )}
              {club.league && (
                <div className="info-item">
                  <span className="label">League:</span>
                  <span className="value">{club.league}</span>
                </div>
              )}
              <div className="info-item">
                <span className="label">Email:</span>
                <span className="value">{club.email}</span>
              </div>
              {club.phone && (
                <div className="info-item">
                  <span className="label">Phone:</span>
                  <span className="value">{club.phone}</span>
                </div>
              )}
              {club.website && (
                <div className="info-item">
                  <span className="label">Website:</span>
                  <span className="value">
                    <a href={club.website} target="_blank" rel="noopener noreferrer">
                      {club.website}
                    </a>
                  </span>
                </div>
              )}
            </div>
          </div>

          {club.description && (
            <div className="profile-section">
              <h3>About the Club</h3>
              <p className="bio-text">{club.description}</p>
            </div>
          )}

          {club.club_story && (
            <div className="profile-section">
              <h3>Our Story</h3>
              <p className="bio-text">{club.club_story}</p>
            </div>
          )}

          {club.achievements && (
            <div className="profile-section">
              <h3>Achievements</h3>
              <p className="bio-text">{club.achievements}</p>
            </div>
          )}

          {club.facilities && (
            <div className="profile-section">
              <h3>Facilities</h3>
              <p className="bio-text">{club.facilities}</p>
            </div>
          )}

          {club.contact_info && (
            <div className="profile-section">
              <h3>Contact Information</h3>
              <p className="bio-text">{club.contact_info}</p>
            </div>
          )}

          {club.gallery_images && club.gallery_images.length > 0 && (
            <div className="profile-section">
              <h3>Gallery</h3>
              <div className="media-grid">
                {club.gallery_images.map((image, index) => (
                  <div key={index} className="media-item">
                    <img src={getImageUrl(image.filename)} alt={`Gallery ${index + 1}`} />
                  </div>
                ))}
              </div>
            </div>
          )}

          {club.videos && club.videos.length > 0 && (
            <div className="profile-section">
              <h3>Videos</h3>
              <div className="media-grid">
                {club.videos.map((video, index) => (
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

          {club.social_media && Object.keys(club.social_media).length > 0 && (
            <div className="profile-section">
              <h3>Social Media</h3>
              <div className="social-links">
                {club.social_media.instagram && (
                  <a href={club.social_media.instagram} target="_blank" rel="noopener noreferrer" className="social-link">
                    📷 Instagram
                  </a>
                )}
                {club.social_media.facebook && (
                  <a href={club.social_media.facebook} target="_blank" rel="noopener noreferrer" className="social-link">
                    👥 Facebook
                  </a>
                )}
                {club.social_media.twitter && (
                  <a href={club.social_media.twitter} target="_blank" rel="noopener noreferrer" className="social-link">
                    🐦 Twitter
                  </a>
                )}
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

export default ClubProfileView;