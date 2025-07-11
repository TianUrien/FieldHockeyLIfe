import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PublicClubProfile = () => {
  const { clubId } = useParams();
  const navigate = useNavigate();
  const [club, setClub] = useState(null);
  const [vacancies, setVacancies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchClubData = async () => {
      try {
        const [clubResponse, vacanciesResponse] = await Promise.all([
          axios.get(`${API}/public/clubs/${clubId}`),
          axios.get(`${API}/public/clubs/${clubId}/vacancies`)
        ]);
        setClub(clubResponse.data);
        setVacancies(vacanciesResponse.data);
      } catch (error) {
        setError(error.response?.status === 404 ? 'Club not found' : 'Failed to load club profile');
        console.error('Error fetching club profile:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchClubData();
  }, [clubId]);

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

  const handleApplyClick = (vacancyId) => {
    // TODO: Implement apply functionality
    alert('Apply functionality will be implemented soon!');
  };

  if (loading) {
    return (
      <div className="public-profile-container">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading club profile...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="public-profile-container">
        <div className="error-state">
          <h2>Club Not Found</h2>
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
              Contact Club
            </button>
          </div>
        </div>
        
        <div className="profile-hero">
          <div className="profile-avatar-large">
            {club.logo ? (
              <img src={getImageUrl(club.logo)} alt={club.name} />
            ) : (
              <div className="avatar-placeholder-large">
                {club.name.charAt(0).toUpperCase()}
              </div>
            )}
          </div>
          
          <div className="profile-hero-content">
            <h1>{club.name}</h1>
            <div className="profile-details">
              {club.club_type && <span className="type-badge">{club.club_type}</span>}
              {club.league && <span className="league-badge">{club.league}</span>}
              <span className="location-text">📍 {club.location}</span>
            </div>
            
            <div className="profile-stats">
              {club.established_year && (
                <div className="stat-item">
                  <span className="stat-label">Established</span>
                  <span className="stat-value">{club.established_year}</span>
                </div>
              )}
              {club.club_type && (
                <div className="stat-item">
                  <span className="stat-label">Type</span>
                  <span className="stat-value">{club.club_type}</span>
                </div>
              )}
              {club.league && (
                <div className="stat-item">
                  <span className="stat-label">League</span>
                  <span className="stat-value">{club.league}</span>
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
          {club.description && (
            <div className="profile-section">
              <h3>About {club.name}</h3>
              <p className="bio-text">{club.description}</p>
            </div>
          )}

          {/* Club Story */}
          {club.club_story && (
            <div className="profile-section">
              <h3>Our Story</h3>
              <p className="bio-text">{club.club_story}</p>
            </div>
          )}

          {/* Achievements */}
          {club.achievements && (
            <div className="profile-section">
              <h3>Achievements</h3>
              <p className="bio-text">{club.achievements}</p>
            </div>
          )}

          {/* Facilities */}
          {club.facilities && (
            <div className="profile-section">
              <h3>Facilities</h3>
              <p className="bio-text">{club.facilities}</p>
            </div>
          )}

          {/* Current Opportunities */}
          {vacancies.length > 0 && (
            <div className="profile-section">
              <h3>Current Opportunities</h3>
              <div className="vacancies-grid">
                {vacancies.map(vacancy => (
                  <div key={vacancy.id} className="vacancy-card-public">
                    <div className="vacancy-header">
                      <h4>{vacancy.title || vacancy.position}</h4>
                      <span className="experience-badge">{vacancy.experience_level}</span>
                    </div>
                    <p className="vacancy-description">{vacancy.description}</p>
                    <div className="vacancy-details">
                      <p><strong>Location:</strong> {vacancy.location}</p>
                      <p><strong>Posted:</strong> {new Date(vacancy.created_at).toLocaleDateString()}</p>
                    </div>
                    <button 
                      onClick={() => handleApplyClick(vacancy.id)}
                      className="apply-btn-public"
                    >
                      Apply Now
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Gallery */}
          {club.gallery_images && club.gallery_images.length > 0 && (
            <div className="profile-section">
              <h3>Gallery</h3>
              <div className="media-gallery">
                {club.gallery_images.map((image, index) => (
                  <div key={index} className="media-item">
                    <img src={getImageUrl(image.filename)} alt={`Gallery ${index + 1}`} />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Videos */}
          {club.videos && club.videos.length > 0 && (
            <div className="profile-section">
              <h3>Club Videos</h3>
              <div className="media-gallery">
                {club.videos.map((video, index) => (
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
            <h4>Club Info</h4>
            <div className="quick-info">
              <div className="info-row">
                <span className="label">Location:</span>
                <span className="value">{club.location}</span>
              </div>
              {club.club_type && (
                <div className="info-row">
                  <span className="label">Type:</span>
                  <span className="value">{club.club_type}</span>
                </div>
              )}
              {club.established_year && (
                <div className="info-row">
                  <span className="label">Established:</span>
                  <span className="value">{club.established_year}</span>
                </div>
              )}
              {club.league && (
                <div className="info-row">
                  <span className="label">League:</span>
                  <span className="value">{club.league}</span>
                </div>
              )}
              {club.website && (
                <div className="info-row">
                  <span className="label">Website:</span>
                  <span className="value">
                    <a href={club.website} target="_blank" rel="noopener noreferrer">
                      Visit Website
                    </a>
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Contact Information */}
          {club.contact_info && (
            <div className="sidebar-section">
              <h4>Contact Information</h4>
              <p className="contact-info">{club.contact_info}</p>
            </div>
          )}

          {/* Social Media */}
          {club.social_media && Object.keys(club.social_media).length > 0 && (
            <div className="sidebar-section">
              <h4>Follow Us</h4>
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

          {/* Opportunities Count */}
          <div className="sidebar-section">
            <h4>Opportunities</h4>
            <div className="opportunities-count">
              <span className="count-number">{vacancies.length}</span>
              <span className="count-label">Open Positions</span>
            </div>
          </div>

          {/* Contact Section */}
          <div className="sidebar-section">
            <h4>Get in Touch</h4>
            <button onClick={handleContactClick} className="contact-btn-full">
              Contact {club.name}
            </button>
            <p className="contact-note">
              Interested in joining? Send them a message to start a conversation.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PublicClubProfile;