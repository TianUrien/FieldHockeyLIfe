import React, { useState, useRef } from 'react';
import axios from 'axios';

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
        }
      });
      
      // Refresh player data
      const updatedPlayer = await axios.get(`${API}/players/${player.id}`);
      onPlayerUpdate(updatedPlayer.data);
      
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
    <div className="player-profile">
      <div className="profile-header">
        <div className="avatar-section">
          <div className="avatar-container">
            {player.avatar ? (
              <img 
                src={`${BACKEND_URL}/uploads/avatars/${player.avatar}`} 
                alt="Profile" 
                className="avatar-image"
              />
            ) : (
              <div className="avatar-placeholder">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
              </div>
            )}
            <button 
              className="avatar-upload-btn"
              onClick={() => avatarInputRef.current?.click()}
              disabled={uploading}
            >
              📷
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
            <div className="upload-progress">
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${uploadProgress.avatar}%` }}
                ></div>
              </div>
              <span>{uploadProgress.avatar}%</span>
            </div>
          )}
        </div>

        <div className="profile-info">
          <h2>{player.name}</h2>
          <p className="profile-position">{player.position}</p>
          <p className="profile-location">{player.location}</p>
          {player.country && <p className="profile-country">🌍 {player.country}</p>}
          <span className="experience-badge">{player.experience_level}</span>
        </div>

        <div className="profile-actions">
          <button 
            className="edit-profile-btn"
            onClick={() => setIsEditing(true)}
          >
            ✏️ Edit Profile
          </button>
        </div>
      </div>

      {isEditing && (
        <div className="edit-modal">
          <div className="edit-modal-content">
            <h3>Edit Profile</h3>
            <form onSubmit={handleEditSubmit}>
              <div className="form-grid">
                <input
                  type="text"
                  placeholder="Full Name"
                  value={editData.name}
                  onChange={(e) => setEditData({...editData, name: e.target.value})}
                  required
                />
                <input
                  type="text"
                  placeholder="Country"
                  value={editData.country}
                  onChange={(e) => setEditData({...editData, country: e.target.value})}
                />
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
                <select
                  value={editData.experience_level}
                  onChange={(e) => setEditData({...editData, experience_level: e.target.value})}
                  required
                >
                  <option value="">Select Experience Level</option>
                  <option value="Beginner">Beginner</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Advanced">Advanced</option>
                  <option value="Professional">Professional</option>
                </select>
                <input
                  type="text"
                  placeholder="Location"
                  value={editData.location}
                  onChange={(e) => setEditData({...editData, location: e.target.value})}
                  required
                />
                <input
                  type="number"
                  placeholder="Age"
                  value={editData.age}
                  onChange={(e) => setEditData({...editData, age: e.target.value})}
                />
              </div>
              <textarea
                placeholder="Bio"
                value={editData.bio}
                onChange={(e) => setEditData({...editData, bio: e.target.value})}
                rows="4"
              />
              <div className="modal-actions">
                <button type="submit" className="save-btn">Save Changes</button>
                <button type="button" className="cancel-btn" onClick={() => setIsEditing(false)}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="profile-content">
        <div className="profile-section">
          <h3>Personal Information</h3>
          <div className="info-grid">
            <div className="info-item">
              <label>Full Name</label>
              <span>{player.name}</span>
            </div>
            <div className="info-item">
              <label>Country</label>
              <span>{player.country || 'Not specified'}</span>
            </div>
            <div className="info-item">
              <label>Position</label>
              <span>{player.position}</span>
            </div>
            <div className="info-item">
              <label>Experience</label>
              <span>{player.experience_level}</span>
            </div>
            <div className="info-item">
              <label>Location</label>
              <span>{player.location}</span>
            </div>
            <div className="info-item">
              <label>Age</label>
              <span>{player.age || 'Not specified'}</span>
            </div>
          </div>
          {player.bio && (
            <div className="bio-section">
              <label>Bio</label>
              <p>{player.bio}</p>
            </div>
          )}
        </div>

        <div className="profile-section">
          <h3>Documents</h3>
          <div className="document-section">
            {player.cv_document ? (
              <div className="document-item">
                <div className="document-info">
                  <span className="document-icon">📄</span>
                  <span className="document-name">CV/Resume</span>
                  <a 
                    href={`${BACKEND_URL}/uploads/documents/${player.cv_document}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="document-link"
                  >
                    View
                  </a>
                </div>
              </div>
            ) : (
              <div className="no-documents">
                <p>No CV uploaded</p>
              </div>
            )}
            
            <div className="upload-section">
              <button 
                className="upload-btn"
                onClick={() => cvInputRef.current?.click()}
                disabled={uploading}
              >
                📁 Upload CV
              </button>
              <input
                ref={cvInputRef}
                type="file"
                accept=".pdf,.doc,.docx"
                onChange={(e) => handleFileUpload(e.target.files[0], 'cv', 'cv')}
                style={{ display: 'none' }}
              />
              {uploadProgress.cv !== undefined && (
                <div className="upload-progress">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${uploadProgress.cv}%` }}
                    ></div>
                  </div>
                  <span>{uploadProgress.cv}%</span>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="profile-section">
          <h3>Photos</h3>
          <div className="media-grid">
            {player.photos && player.photos.length > 0 ? (
              player.photos.map((photo) => (
                <div key={photo.id} className="media-item">
                  <img 
                    src={`${BACKEND_URL}/uploads/photos/${photo.filename}`} 
                    alt={photo.original_name}
                    className="media-thumbnail"
                  />
                  <div className="media-info">
                    <span className="media-name">{photo.original_name}</span>
                    <span className="media-size">{formatFileSize(photo.file_size)}</span>
                  </div>
                  <button 
                    className="delete-media-btn"
                    onClick={() => handleDeleteMedia(photo.id, 'photo')}
                  >
                    🗑️
                  </button>
                </div>
              ))
            ) : (
              <div className="no-media">
                <p>No photos uploaded</p>
              </div>
            )}
          </div>
          
          <div className="upload-section">
            <button 
              className="upload-btn"
              onClick={() => photoInputRef.current?.click()}
              disabled={uploading}
            >
              📸 Upload Photo
            </button>
            <input
              ref={photoInputRef}
              type="file"
              accept="image/*"
              onChange={(e) => handleFileUpload(e.target.files[0], 'photos', 'photo')}
              style={{ display: 'none' }}
            />
            {uploadProgress.photo !== undefined && (
              <div className="upload-progress">
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${uploadProgress.photo}%` }}
                  ></div>
                </div>
                <span>{uploadProgress.photo}%</span>
              </div>
            )}
          </div>
        </div>

        <div className="profile-section">
          <h3>Videos</h3>
          <div className="media-grid">
            {player.videos && player.videos.length > 0 ? (
              player.videos.map((video) => (
                <div key={video.id} className="media-item">
                  <video 
                    src={`${BACKEND_URL}/uploads/videos/${video.filename}`} 
                    className="media-thumbnail"
                    controls
                  />
                  <div className="media-info">
                    <span className="media-name">{video.original_name}</span>
                    <span className="media-size">{formatFileSize(video.file_size)}</span>
                  </div>
                  <button 
                    className="delete-media-btn"
                    onClick={() => handleDeleteMedia(video.id, 'video')}
                  >
                    🗑️
                  </button>
                </div>
              ))
            ) : (
              <div className="no-media">
                <p>No videos uploaded</p>
              </div>
            )}
          </div>
          
          <div className="upload-section">
            <button 
              className="upload-btn"
              onClick={() => videoInputRef.current?.click()}
              disabled={uploading}
            >
              🎥 Upload Video
            </button>
            <input
              ref={videoInputRef}
              type="file"
              accept="video/*"
              onChange={(e) => handleFileUpload(e.target.files[0], 'videos', 'video')}
              style={{ display: 'none' }}
            />
            {uploadProgress.video !== undefined && (
              <div className="upload-progress">
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${uploadProgress.video}%` }}
                  ></div>
                </div>
                <span>{uploadProgress.video}%</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlayerProfile;