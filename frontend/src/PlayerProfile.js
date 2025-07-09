import React, { useState, useRef } from 'react';
import axios from 'axios';
import './PlayerProfile.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PlayerProfile = ({ player, onPlayerUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    name: player.name || '',
    country: player.country || '',
    position: player.position || '',
    experience_level: player.experience_level || '',
    location: player.location || '',
    bio: player.bio || '',
    age: player.age || ''
  });
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  
  const avatarInputRef = useRef(null);
  const cvInputRef = useRef(null);
  const photoInputRef = useRef(null);
  const videoInputRef = useRef(null);

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    try {
      const updateData = { ...editData };
      if (updateData.age) updateData.age = parseInt(updateData.age);
      
      const response = await axios.put(`${API}/players/${player.id}`, updateData);
      onPlayerUpdate(response.data);
      setIsEditing(false);
    } catch (error) {
      alert(error.response?.data?.detail || 'Error updating profile');
    }
  };

  const handleFileUpload = async (file, endpoint, type) => {
    if (!file) return;
    
    // Check file size before upload
    const maxSize = type === 'video' ? 300 * 1024 * 1024 : // 300MB for videos
                   type === 'cv' ? 10 * 1024 * 1024 : // 10MB for documents
                   type === 'photo' ? 10 * 1024 * 1024 : // 10MB for photos
                   5 * 1024 * 1024; // 5MB for avatars
    
    if (file.size > maxSize) {
      alert(`File too large. Maximum size: ${Math.round(maxSize / (1024 * 1024))}MB`);
      return;
    }
    
    setUploading(true);
    setUploadProgress(prev => ({ ...prev, [type]: 0 }));
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await axios.post(`${API}/players/${player.id}/${endpoint}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(prev => ({ ...prev, [type]: percentCompleted }));
        },
        // Increase timeout for large files
        timeout: type === 'video' ? 300000 : 60000 // 5 minutes for videos, 1 minute for others
      });
      
      // Refresh player data
      const updatedPlayer = await axios.get(`${API}/players/${player.id}`);
      onPlayerUpdate(updatedPlayer.data);
      
      setUploadProgress(prev => ({ ...prev, [type]: 100 }));
      setTimeout(() => {
        setUploadProgress(prev => ({ ...prev, [type]: undefined }));
      }, 2000);
      
    } catch (error) {
      if (error.code === 'ECONNABORTED') {
        alert(`Upload timeout. Try with a smaller file or check your connection.`);
      } else {
        alert(error.response?.data?.detail || `Error uploading ${type}`);
      }
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteMedia = async (mediaId, type) => {
    if (!confirm(`Are you sure you want to delete this ${type}?`)) return;
    
    try {
      await axios.delete(`${API}/players/${player.id}/${type}s/${mediaId}`);
      
      // Refresh player data
      const updatedPlayer = await axios.get(`${API}/players/${player.id}`);
      onPlayerUpdate(updatedPlayer.data);
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
    <div className="player-profile-modern">
      {/* Hero Section */}
      <div className="profile-hero">
        <div className="hero-background"></div>
        <div className="hero-content">
          <div className="avatar-section-modern">
            <div className="avatar-container-modern">
              {player.avatar ? (
                <img 
                  src={`${BACKEND_URL}/api/uploads/avatars/${player.avatar}`} 
                  alt="Profile" 
                  className="avatar-image-modern"
                />
              ) : (
                <div className="avatar-placeholder-modern">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                </div>
              )}
              <button 
                className="avatar-upload-btn-modern"
                onClick={() => avatarInputRef.current?.click()}
                disabled={uploading}
                title="Change profile picture"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
                  <circle cx="12" cy="13" r="4"></circle>
                </svg>
              </button>
              <input
                ref={avatarInputRef}
                type="file"
                accept="image/*"
                onChange={(e) => handleFileUpload(e.target.files[0], 'avatar', 'avatar')}
                style={{ display: 'none' }}
              />
            </div>
            
            {uploadProgress.avatar !== undefined && (
              <div className="upload-progress-modern">
                <div className="progress-bar-modern">
                  <div 
                    className="progress-fill-modern" 
                    style={{ width: `${uploadProgress.avatar}%` }}
                  ></div>
                </div>
                <span className="progress-text">{uploadProgress.avatar}%</span>
              </div>
            )}
          </div>

          <div className="profile-info-modern">
            <h1 className="profile-name">{player.name}</h1>
            <p className="profile-position">{player.position}</p>
            <div className="profile-meta">
              <span className="profile-location">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                  <circle cx="12" cy="10" r="3"></circle>
                </svg>
                {player.location}
              </span>
              {player.country && (
                <span className="profile-country">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <path d="M2 12h20"></path>
                    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
                  </svg>
                  {player.country}
                </span>
              )}
            </div>
            <div className="experience-badge-modern">{player.experience_level}</div>
          </div>

          <div className="profile-actions-modern">
            <button 
              className="edit-profile-btn-modern"
              onClick={() => setIsEditing(true)}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
              Edit Profile
            </button>
          </div>
        </div>
      </div>

      {/* Edit Modal */}
      {isEditing && (
        <div className="edit-modal-modern">
          <div className="edit-modal-backdrop" onClick={() => setIsEditing(false)}></div>
          <div className="edit-modal-content-modern">
            <div className="modal-header">
              <h3>Edit Profile</h3>
              <button 
                className="modal-close-btn"
                onClick={() => setIsEditing(false)}
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
            <form onSubmit={handleEditSubmit} className="edit-form-modern">
              <div className="form-grid-modern">
                <div className="form-group">
                  <label>Full Name</label>
                  <input
                    type="text"
                    value={editData.name}
                    onChange={(e) => setEditData({...editData, name: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Country</label>
                  <input
                    type="text"
                    value={editData.country}
                    onChange={(e) => setEditData({...editData, country: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Position</label>
                  <select
                    value={editData.position}
                    onChange={(e) => setEditData({...editData, position: e.target.value})}
                    required
                  >
                    <option value="">Select Position</option>
                    <option value="Forward">Forward</option>
                    <option value="Midfielder">Midfielder</option>
                    <option value="Defender">Defender</option>
                    <option value="Goalkeeper">Goalkeeper</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Experience Level</label>
                  <select
                    value={editData.experience_level}
                    onChange={(e) => setEditData({...editData, experience_level: e.target.value})}
                    required
                  >
                    <option value="">Select Experience</option>
                    <option value="Beginner">Beginner</option>
                    <option value="Intermediate">Intermediate</option>
                    <option value="Advanced">Advanced</option>
                    <option value="Professional">Professional</option>
                  </select>
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
                  <label>Age</label>
                  <input
                    type="number"
                    value={editData.age}
                    onChange={(e) => setEditData({...editData, age: e.target.value})}
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Bio</label>
                <textarea
                  value={editData.bio}
                  onChange={(e) => setEditData({...editData, bio: e.target.value})}
                  rows="4"
                  placeholder="Tell us about yourself..."
                />
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

      {/* Profile Content Sections */}
      <div className="profile-content-modern">
        {/* Personal Information */}
        <div className="section-modern">
          <div className="section-header">
            <h2>Personal Information</h2>
          </div>
          <div className="info-grid-modern">
            <div className="info-item-modern">
              <div className="info-label">Full Name</div>
              <div className="info-value">{player.name}</div>
            </div>
            <div className="info-item-modern">
              <div className="info-label">Country</div>
              <div className="info-value">{player.country || 'Not specified'}</div>
            </div>
            <div className="info-item-modern">
              <div className="info-label">Position</div>
              <div className="info-value">{player.position}</div>
            </div>
            <div className="info-item-modern">
              <div className="info-label">Experience</div>
              <div className="info-value">{player.experience_level}</div>
            </div>
            <div className="info-item-modern">
              <div className="info-label">Location</div>
              <div className="info-value">{player.location}</div>
            </div>
            <div className="info-item-modern">
              <div className="info-label">Age</div>
              <div className="info-value">{player.age || 'Not specified'}</div>
            </div>
          </div>
          {player.bio && (
            <div className="bio-section-modern">
              <div className="info-label">About</div>
              <p className="bio-text">{player.bio}</p>
            </div>
          )}
        </div>

        {/* Documents Section */}
        <div className="section-modern">
          <div className="section-header">
            <h2>Documents</h2>
            <button 
              className="upload-btn-modern secondary"
              onClick={() => cvInputRef.current?.click()}
              disabled={uploading}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14,2 14,8 20,8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10,9 9,9 8,9"></polyline>
              </svg>
              Upload CV
            </button>
            <input
              ref={cvInputRef}
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={(e) => handleFileUpload(e.target.files[0], 'cv', 'cv')}
              style={{ display: 'none' }}
            />
          </div>
          
          <div className="documents-grid">
            {player.cv_document ? (
              <div className="document-card">
                <div className="document-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14,2 14,8 20,8"></polyline>
                  </svg>
                </div>
                <div className="document-info">
                  <div className="document-name">CV/Resume</div>
                  <div className="document-type">PDF Document</div>
                </div>
                <a 
                  href={`${BACKEND_URL}/api/uploads/documents/${player.cv_document}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="document-action"
                  title="View document"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                </a>
              </div>
            ) : (
              <div className="empty-state">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14,2 14,8 20,8"></polyline>
                </svg>
                <p>No CV uploaded yet</p>
                <p className="empty-subtitle">Upload your resume to showcase your experience</p>
              </div>
            )}
          </div>
          
          {uploadProgress.cv !== undefined && (
            <div className="upload-progress-modern">
              <div className="progress-bar-modern">
                <div 
                  className="progress-fill-modern" 
                  style={{ width: `${uploadProgress.cv}%` }}
                ></div>
              </div>
              <span className="progress-text">{uploadProgress.cv}%</span>
            </div>
          )}
        </div>

        {/* Photos Section */}
        <div className="section-modern">
          <div className="section-header">
            <h2>Photos</h2>
            <button 
              className="upload-btn-modern secondary"
              onClick={() => photoInputRef.current?.click()}
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
              ref={photoInputRef}
              type="file"
              accept="image/*"
              onChange={(e) => handleFileUpload(e.target.files[0], 'photos', 'photo')}
              style={{ display: 'none' }}
            />
          </div>
          
          <div className="media-grid-modern">
            {player.photos && player.photos.length > 0 ? (
              player.photos.map((photo) => (
                <div key={photo.id} className="media-card">
                  <div className="media-thumbnail-container">
                    <img 
                      src={`${BACKEND_URL}/api/uploads/photos/${photo.filename}`} 
                      alt={photo.original_name}
                      className="media-thumbnail-modern"
                    />
                    <button 
                      className="delete-media-btn-modern"
                      onClick={() => handleDeleteMedia(photo.id, 'photo')}
                      title="Delete photo"
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="3,6 5,6 21,6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                      </svg>
                    </button>
                  </div>
                  <div className="media-info-modern">
                    <div className="media-name">{photo.original_name}</div>
                    <div className="media-size">{formatFileSize(photo.file_size)}</div>
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
                <p className="empty-subtitle">Share your field hockey moments</p>
              </div>
            )}
          </div>
          
          {uploadProgress.photo !== undefined && (
            <div className="upload-progress-modern">
              <div className="progress-bar-modern">
                <div 
                  className="progress-fill-modern" 
                  style={{ width: `${uploadProgress.photo}%` }}
                ></div>
              </div>
              <span className="progress-text">{uploadProgress.photo}%</span>
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
            {player.videos && player.videos.length > 0 ? (
              player.videos.map((video) => (
                <div key={video.id} className="media-card">
                  <div className="media-thumbnail-container">
                    <video 
                      src={`${BACKEND_URL}/api/uploads/videos/${video.filename}`} 
                      className="media-thumbnail-modern"
                      controls
                      preload="metadata"
                      muted
                      playsInline
                      onError={(e) => {
                        console.error('Video load error:', e);
                        e.target.style.display = 'none';
                        e.target.parentNode.querySelector('.video-error').style.display = 'flex';
                      }}
                    />
                    <div className="video-error" style={{ display: 'none' }}>
                      <p>Video format not supported</p>
                      <a 
                        href={`${BACKEND_URL}/api/uploads/videos/${video.filename}`} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="download-link"
                      >
                        Download to view
                      </a>
                    </div>
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
                <p className="empty-subtitle">Upload gameplay footage and training videos</p>
              </div>
            )}
          </div>
          
          {uploadProgress.video !== undefined && (
            <div className="upload-progress-modern">
              <div className="progress-bar-modern">
                <div 
                  className="progress-fill-modern" 
                  style={{ width: `${uploadProgress.video}%` }}
                ></div>
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

export default PlayerProfile;