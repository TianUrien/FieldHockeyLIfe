import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const BrowsePlayers = () => {
  const navigate = useNavigate();
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    position: '',
    experience_level: '',
    location: '',
    country: ''
  });
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadStats();
    loadPlayers();
  }, []);

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API}/public/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const loadPlayers = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      
      const response = await axios.get(`${API}/public/players/browse?${params}`);
      setPlayers(response.data);
    } catch (error) {
      console.error('Error loading players:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleFilterSubmit = (e) => {
    e.preventDefault();
    loadPlayers();
  };

  const clearFilters = () => {
    setFilters({
      position: '',
      experience_level: '',
      location: '',
      country: ''
    });
    setTimeout(() => loadPlayers(), 100);
  };

  const getImageUrl = (filename) => {
    if (!filename) return null;
    return `${BACKEND_URL}/uploads/${filename}`;
  };

  const handlePlayerClick = (playerId) => {
    navigate(`/players/${playerId}`);
  };

  return (
    <div className="browse-container">
      {/* Header */}
      <div className="browse-header">
        <div className="browse-title">
          <h1>Browse Players</h1>
          <p>Discover talented field hockey players from around the world</p>
        </div>
        
        {stats && (
          <div className="browse-stats">
            <div className="stat-item">
              <span className="stat-number">{stats.total_players}</span>
              <span className="stat-label">Players</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{stats.total_clubs}</span>
              <span className="stat-label">Clubs</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{stats.active_vacancies}</span>
              <span className="stat-label">Opportunities</span>
            </div>
          </div>
        )}
      </div>

      {/* Filters */}
      <div className="browse-filters">
        <form onSubmit={handleFilterSubmit} className="filter-form">
          <div className="filter-group">
            <label>Position</label>
            <select 
              value={filters.position} 
              onChange={(e) => handleFilterChange('position', e.target.value)}
            >
              <option value="">All Positions</option>
              <option value="Forward">Forward</option>
              <option value="Midfielder">Midfielder</option>
              <option value="Defender">Defender</option>
              <option value="Goalkeeper">Goalkeeper</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Experience Level</label>
            <select 
              value={filters.experience_level} 
              onChange={(e) => handleFilterChange('experience_level', e.target.value)}
            >
              <option value="">All Levels</option>
              <option value="Beginner">Beginner</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Advanced">Advanced</option>
              <option value="Professional">Professional</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Location</label>
            <input 
              type="text" 
              placeholder="Enter city or region"
              value={filters.location}
              onChange={(e) => handleFilterChange('location', e.target.value)}
            />
          </div>

          <div className="filter-group">
            <label>Country</label>
            <input 
              type="text" 
              placeholder="Enter country"
              value={filters.country}
              onChange={(e) => handleFilterChange('country', e.target.value)}
            />
          </div>

          <div className="filter-actions">
            <button type="submit" className="btn primary">Filter</button>
            <button type="button" onClick={clearFilters} className="btn secondary">Clear</button>
          </div>
        </form>
      </div>

      {/* Results */}
      <div className="browse-results">
        {loading ? (
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Loading players...</p>
          </div>
        ) : (
          <>
            <div className="results-header">
              <h3>Players ({players.length})</h3>
            </div>
            
            <div className="players-grid">
              {players.map(player => (
                <div 
                  key={player.id} 
                  className="player-card-browse"
                  onClick={() => handlePlayerClick(player.id)}
                >
                  <div className="player-avatar">
                    {player.avatar ? (
                      <img src={getImageUrl(player.avatar)} alt={player.name} />
                    ) : (
                      <div className="avatar-placeholder">
                        {player.name.charAt(0).toUpperCase()}
                      </div>
                    )}
                  </div>
                  
                  <div className="player-info">
                    <h4>{player.name}</h4>
                    <div className="player-details">
                      <span className="position">{player.position}</span>
                      <span className="experience">{player.experience_level}</span>
                    </div>
                    <p className="location">📍 {player.location}</p>
                    {player.country && (
                      <p className="country">🌍 {player.country}</p>
                    )}
                  </div>
                  
                  <div className="player-actions">
                    <button className="view-profile-btn-small">
                      View Profile
                    </button>
                  </div>
                </div>
              ))}
            </div>
            
            {players.length === 0 && (
              <div className="no-results">
                <h3>No players found</h3>
                <p>Try adjusting your filters or search criteria</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default BrowsePlayers;