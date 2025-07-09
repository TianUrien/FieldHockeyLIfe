import React, { useState, useRef } from 'react';
import axios from 'axios';
import './ClubProfile.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ClubProfile = ({ club, onClubUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    name: club.name || '',
    location: club.location || '',
    description: club.description || '',
    contact_info: club.contact_info || '',
    established_year: club.established_year || '',
    website: club.website || '',
    phone: club.phone || '',
    club_type: club.club_type || '',
    league: club.league || '',
    achievements: club.achievements || '',
    club_story: club.club_story || '',
    facilities: club.facilities || '',
    social_media: club.social_media || {}
  });
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  
  const logoInputRef = useRef(null);
  const galleryInputRef = useRef(null);
  const videoInputRef = useRef(null);

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    try {
      const updateData = { ...editData };
      if (updateData.established_year) updateData.established_year = parseInt(updateData.established_year);
      
      const response = await axios.put(`${API}/clubs/${club.id}`, updateData);
      onClubUpdate(response.data);
      setIsEditing(false);
    } catch (error) {
      alert(error.response?.data?.detail || 'Error updating club profile');
    }
  };

  const handleFileUpload = async (file, endpoint, type) => {
    if (!file) return;
    
    const maxSize = type === 'video' ? 300 * 1024 * 1024 : 10 * 1024 * 1024;
    
    if (file.size > maxSize) {
      alert(`File too large. Maximum size: ${Math.round(maxSize / (1024 * 1024))}MB`);
      return;
    }
    
    setUploading(true);
    setUploadProgress(prev => ({ ...prev, [type]: 0 }));
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      await axios.post(`${API}/clubs/${club.id}/${endpoint}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(prev => ({ ...prev, [type]: percentCompleted }));
        },
        timeout: type === 'video' ? 300000 : 60000
      });
      
      const updatedClub = await axios.get(`${API}/clubs/${club.id}`);
      onClubUpdate(updatedClub.data);
      
      setUploadProgress(prev => ({ ...prev, [type]: 100 }));
      setTimeout(() => {
        setUploadProgress(prev => ({ ...prev, [type]: undefined }));
      }, 2000);
      
    } catch (error) {
      alert(error.response?.data?.detail || `Error uploading ${type}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteMedia = async (mediaId, type) => {
    if (!confirm(`Are you sure you want to delete this ${type}?`)) return;
    
    try {
      const endpoint = type === 'image' ? 'gallery' : 'videos';
      await axios.delete(`${API}/clubs/${club.id}/${endpoint}/${mediaId}`);
      
      const updatedClub = await axios.get(`${API}/clubs/${club.id}`);
      onClubUpdate(updatedClub.data);
    } catch (error) {
      alert(error.response?.data?.detail || `Error deleting ${type}`);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="club-profile-modern">
      {/* Club Hero Section */}
      <div className="club-hero">
        <div className="hero-background-club"></div>
        <div className="hero-content-club">
          <div className="logo-section">
            <div className="logo-container">
              {club.logo ? (
                <img 
                  src={`${BACKEND_URL}/api/uploads/logos/${club.logo}`} 
                  alt="Club Logo" 
                  className="club-logo"
                />
              ) : (
                <div className="logo-placeholder">
                  <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                    <circle cx="8.5" cy="8.5" r="1.5"></circle>
                    <polyline points="21,15 16,10 5,21"></polyline>
                  </svg>
                </div>
              )}
              <button 
                className="logo-upload-btn"
                onClick={() => logoInputRef.current?.click()}
                disabled={uploading}
                title="Change club logo"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
                  <circle cx="12" cy="13" r="4"></circle>
                </svg>
              </button>
              <input
                ref={logoInputRef}
                type="file"
                accept="image/*"
                onChange={(e) => handleFileUpload(e.target.files[0], 'logo', 'logo')}
                style={{ display: 'none' }}
              />
            </div>
            
            {uploadProgress.logo !== undefined && (
              <div className="upload-progress-modern">
                <div className="progress-bar-modern">
                  <div className="progress-fill-modern" style={{ width: `${uploadProgress.logo}%` }}></div>
                </div>
                <span className="progress-text">{uploadProgress.logo}%</span>
              </div>
            )}
          </div>

          <div className="club-info">
            <h1 className="club-name">{club.name}</h1>
            <div className="club-meta">
              <span className="club-location">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                  <circle cx="12" cy="10" r="3"></circle>
                </svg>
                {club.location}
              </span>
              {club.established_year && (
                <span className="club-established">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                    <line x1="16" y1="2" x2="16" y2="6"></line>
                    <line x1="8" y1="2" x2="8" y2="6"></line>
                    <line x1="3" y1="10" x2="21" y2="10"></line>
                  </svg>
                  Est. {club.established_year}
                </span>
              )}
              {club.club_type && (
                <span className="club-type-badge">{club.club_type}</span>
              )}
            </div>
            {club.league && (
              <div className="club-league">League: {club.league}</div>
            )}
          </div>

          <div className="club-actions">
            <button 
              className="edit-club-btn"
              onClick={() => setIsEditing(true)}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
              Edit Club Profile
            </button>
          </div>
        </div>
      </div>

      {/* Edit Modal */}
      {isEditing && (
        <div className="edit-modal-modern">
          <div className="edit-modal-backdrop" onClick={() => setIsEditing(false)}></div>
          <div className="edit-modal-content-modern club-edit-modal">
            <div className="modal-header">
              <h3>Edit Club Profile</h3>
              <button className="modal-close-btn" onClick={() => setIsEditing(false)}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
            <form onSubmit={handleEditSubmit} className="edit-form-modern">
              <div className="form-section">
                <h4>Basic Information</h4>
                <div className="form-grid-modern">
                  <div className="form-group">
                    <label>Club Name</label>
                    <input
                      type="text"
                      value={editData.name}
                      onChange={(e) => setEditData({...editData, name: e.target.value})}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Location</label>
                    <input
                      type="text"
                      value={editData.location}
                      onChange={(e) => setEditData({...editData, location: e.target.value})}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Club Type</label>
                    <select
                      value={editData.club_type}
                      onChange={(e) => setEditData({...editData, club_type: e.target.value})}
                    >
                      <option value="">Select Type</option>
                      <option value="Professional">Professional</option>
                      <option value="Amateur">Amateur</option>
                      <option value="Youth">Youth</option>
                      <option value="University">University</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Established Year</label>
                    <input
                      type="number"
                      value={editData.established_year}
                      onChange={(e) => setEditData({...editData, established_year: e.target.value})}
                    />
                  </div>
                  <div className="form-group">
                    <label>League</label>
                    <input
                      type="text"
                      value={editData.league}
                      onChange={(e) => setEditData({...editData, league: e.target.value})}
                    />
                  </div>
                  <div className="form-group">
                    <label>Website</label>
                    <input
                      type="url"
                      value={editData.website}
                      onChange={(e) => setEditData({...editData, website: e.target.value})}
                      placeholder="https://"
                    />
                  </div>
                </div>
              </div>

              <div className="form-section">
                <h4>Contact Information</h4>
                <div className="form-grid-modern">
                  <div className="form-group">
                    <label>Phone</label>
                    <input
                      type="tel"
                      value={editData.phone}
                      onChange={(e) => setEditData({...editData, phone: e.target.value})}
                    />
                  </div>
                  <div className="form-group">
                    <label>Contact Info</label>
                    <input
                      type="text"
                      value={editData.contact_info}
                      onChange={(e) => setEditData({...editData, contact_info: e.target.value})}
                    />
                  </div>
                </div>
              </div>

              <div className="form-section">
                <h4>About the Club</h4>
                <div className="form-group">
                  <label>Description</label>
                  <textarea
                    value={editData.description}
                    onChange={(e) => setEditData({...editData, description: e.target.value})}
                    rows="3"
                    placeholder="Brief description of your club..."
                  />
                </div>
                <div className="form-group">
                  <label>Club Story</label>
                  <textarea
                    value={editData.club_story}
                    onChange={(e) => setEditData({...editData, club_story: e.target.value})}
                    rows="4"
                    placeholder="Tell your club's story, history, and values..."
                  />
                </div>
                <div className="form-group">
                  <label>Achievements</label>
                  <textarea
                    value={editData.achievements}
                    onChange={(e) => setEditData({...editData, achievements: e.target.value})}
                    rows="3"
                    placeholder="Notable achievements, trophies, championships..."
                  />
                </div>
                <div className="form-group">
                  <label>Facilities</label>
                  <textarea
                    value={editData.facilities}
                    onChange={(e) => setEditData({...editData, facilities: e.target.value})}
                    rows="3"
                    placeholder="Training facilities, equipment, stadium details..."
                  />
                </div>
              </div>

              <div className="modal-actions">
                <button type="button" className="cancel-btn-modern" onClick={() => setIsEditing(false)}>
                  Cancel
                </button>
                <button type="submit" className="save-btn-modern">Save Changes</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Club Content Sections */}
      <div className="club-content">
        {/* About Section */}
        <div className="section-modern">
          <div className="section-header">
            <h2>About {club.name}</h2>
          </div>
          <div className="about-content">
            {club.description && (
              <div className="about-item">
                <h4>Description</h4>
                <p>{club.description}</p>
              </div>
            )}
            {club.club_story && (
              <div className="about-item">
                <h4>Our Story</h4>
                <p>{club.club_story}</p>
              </div>
            )}
            {club.achievements && (
              <div className="about-item">
                <h4>Achievements</h4>
                <p>{club.achievements}</p>
              </div>
            )}
            {club.facilities && (
              <div className="about-item">
                <h4>Facilities</h4>
                <p>{club.facilities}</p>
              </div>
            )}
            
            <div className="club-details-grid">
              <div className="detail-item">
                <label>Location</label>
                <span>{club.location}</span>
              </div>
              {club.established_year && (
                <div className="detail-item">
                  <label>Established</label>
                  <span>{club.established_year}</span>
                </div>
              )}
              {club.club_type && (
                <div className="detail-item">
                  <label>Type</label>
                  <span>{club.club_type}</span>
                </div>
              )}
              {club.league && (
                <div className="detail-item">
                  <label>League</label>
                  <span>{club.league}</span>
                </div>
              )}
              {club.website && (
                <div className="detail-item">
                  <label>Website</label>
                  <a href={club.website} target="_blank" rel="noopener noreferrer">{club.website}</a>
                </div>
              )}
              {club.phone && (
                <div className="detail-item">
                  <label>Phone</label>
                  <span>{club.phone}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Gallery Section */}
        <div className="section-modern">
          <div className="section-header">
            <h2>Gallery</h2>
            <button 
              className="upload-btn-modern secondary"
              onClick={() => galleryInputRef.current?.click()}
              disabled={uploading}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <circle cx="8.5" cy="8.5" r="1.5"></circle>
                <polyline points="21,15 16,10 5,21"></polyline>
              </svg>
              Add Photo
            </button>
            <input
              ref={galleryInputRef}
              type="file"
              accept="image/*"
              onChange={(e) => handleFileUpload(e.target.files[0], 'gallery', 'gallery')}
              style={{ display: 'none' }}
            />
          </div>
          
          <div className="media-grid-modern">
            {club.gallery_images && club.gallery_images.length > 0 ? (
              club.gallery_images.map((image) => (
                <div key={image.id} className="media-card">
                  <div className="media-thumbnail-container">
                    <img 
                      src={`${BACKEND_URL}/api/uploads/club_gallery/${image.filename}`} 
                      alt={image.original_name}
                      className="media-thumbnail-modern"
                    />
                    <button 
                      className="delete-media-btn-modern"
                      onClick={() => handleDeleteMedia(image.id, 'image')}
                      title="Delete photo"
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="3,6 5,6 21,6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                      </svg>
                    </button>
                  </div>
                  <div className="media-info-modern">
                    <div className="media-name">{image.original_name}</div>
                    <div className="media-size">{formatFileSize(image.file_size)}</div>
                  </div>
                </div>
              ))
            ) : (
              <div className="empty-state">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                  <circle cx="8.5" cy="8.5" r="1.5"></circle>
                  <polyline points="21,15 16,10 5,21"></polyline>
                </svg>
                <p>No photos yet</p>
                <p className="empty-subtitle">Showcase your club with photos</p>
              </div>
            )}
          </div>
          
          {uploadProgress.gallery !== undefined && (
            <div className="upload-progress-modern">
              <div className="progress-bar-modern">
                <div className="progress-fill-modern" style={{ width: `${uploadProgress.gallery}%` }}></div>
              </div>
              <span className="progress-text">{uploadProgress.gallery}%</span>
            </div>
          )}
        </div>

        {/* Videos Section */}
        <div className="section-modern">
          <div className="section-header">
            <h2>Videos</h2>
            <button 
              className="upload-btn-modern secondary"
              onClick={() => videoInputRef.current?.click()}
              disabled={uploading}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polygon points="23 7 16 12 23 17 23 7"></polygon>
                <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
              </svg>
              Add Video (max 300MB)
            </button>
            <input
              ref={videoInputRef}
              type="file"
              accept="video/mp4,video/mov,video/avi,video/quicktime,.mp4,.mov,.avi"
              onChange={(e) => handleFileUpload(e.target.files[0], 'videos', 'video')}
              style={{ display: 'none' }}
            />
          </div>
          
          <div className="media-grid-modern">
            {club.videos && club.videos.length > 0 ? (
              club.videos.map((video) => (
                <div key={video.id} className="media-card">
                  <div className="media-thumbnail-container">
                    <video 
                      src={`${BACKEND_URL}/api/uploads/club_videos/${video.filename}`} 
                      className="media-thumbnail-modern"
                      controls
                      preload="metadata"
                      muted
                      playsInline
                    />
                    <button 
                      className="delete-media-btn-modern"
                      onClick={() => handleDeleteMedia(video.id, 'video')}
                      title="Delete video"
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="3,6 5,6 21,6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                      </svg>
                    </button>
                  </div>
                  <div className="media-info-modern">
                    <div className="media-name">{video.original_name}</div>
                    <div className="media-size">{formatFileSize(video.file_size)}</div>
                    <div className="media-type">{video.file_type}</div>
                  </div>
                </div>
              ))
            ) : (
              <div className="empty-state">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
                  <polygon points="23 7 16 12 23 17 23 7"></polygon>
                  <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
                </svg>
                <p>No videos yet</p>
                <p className="empty-subtitle">Share club highlights and promotional videos</p>
              </div>
            )}
          </div>
          
          {uploadProgress.video !== undefined && (
            <div className="upload-progress-modern">
              <div className="progress-bar-modern">
                <div className="progress-fill-modern" style={{ width: `${uploadProgress.video}%` }}></div>
              </div>
              <span className="progress-text">
                {uploadProgress.video}%
                {uploadProgress.video < 100 && (
                  <span className="upload-status"> Uploading large file...</span>
                )}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ClubProfile;