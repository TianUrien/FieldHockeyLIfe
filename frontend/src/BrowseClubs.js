import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const BrowseClubs = () => {
  const navigate = useNavigate();
  const [clubs, setClubs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    location: '',
    club_type: '',
    league: ''
  });
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadStats();
    loadClubs();
  }, []);

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API}/public/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const loadClubs = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      
      const response = await axios.get(`${API}/public/clubs/browse?${params}`);
      setClubs(response.data);
    } catch (error) {
      console.error('Error loading clubs:', error);
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
    loadClubs();
  };

  const clearFilters = () => {
    setFilters({
      location: '',
      club_type: '',
      league: ''
    });
    setTimeout(() => loadClubs(), 100);
  };

  const getImageUrl = (filename) => {
    if (!filename) return null;
    return `${BACKEND_URL}/uploads/${filename}`;
  };

  const handleClubClick = (clubId) => {
    navigate(`/clubs/${clubId}`);
  };

  return (
    <div className="browse-container">
      {/* Header */}
      <div className="browse-header">
        <div className="browse-title">
          <h1>Browse Clubs</h1>
          <p>Discover field hockey clubs and opportunities worldwide</p>
        </div>
        
        {stats && (
          <div className="browse-stats">
            <div className="stat-item">
              <span className="stat-number">{stats.total_clubs}</span>
              <span className="stat-label">Clubs</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{stats.active_vacancies}</span>
              <span className="stat-label">Open Positions</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{stats.total_players}</span>
              <span className="stat-label">Players</span>
            </div>
          </div>
        )}
      </div>

      {/* Filters */}
      <div className="browse-filters">
        <form onSubmit={handleFilterSubmit} className="filter-form">
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
            <label>Club Type</label>
            <select 
              value={filters.club_type} 
              onChange={(e) => handleFilterChange('club_type', e.target.value)}
            >
              <option value="">All Types</option>
              <option value="Professional">Professional</option>
              <option value="Amateur">Amateur</option>
              <option value="Youth">Youth</option>
              <option value="University">University</option>
            </select>
          </div>

          <div className="filter-group">
            <label>League</label>
            <input 
              type="text" 
              placeholder="Enter league name"
              value={filters.league}
              onChange={(e) => handleFilterChange('league', e.target.value)}
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
            <p>Loading clubs...</p>
          </div>
        ) : (
          <>
            <div className="results-header">
              <h3>Clubs ({clubs.length})</h3>
            </div>
            
            <div className="clubs-grid">
              {clubs.map(club => (
                <div 
                  key={club.id} 
                  className="club-card-browse"
                  onClick={() => handleClubClick(club.id)}
                >
                  <div className="club-logo">
                    {club.logo ? (
                      <img src={getImageUrl(club.logo)} alt={club.name} />
                    ) : (
                      <div className="logo-placeholder">
                        {club.name.charAt(0).toUpperCase()}
                      </div>
                    )}
                  </div>
                  
                  <div className="club-info">
                    <h4>{club.name}</h4>
                    <div className="club-details">
                      {club.club_type && <span className="type">{club.club_type}</span>}
                      {club.league && <span className="league">{club.league}</span>}
                    </div>
                    <p className="location">📍 {club.location}</p>
                    {club.established_year && (
                      <p className="established">🏆 Est. {club.established_year}</p>
                    )}
                  </div>
                  
                  <div className="club-actions">
                    <button className="view-profile-btn-small">
                      View Profile
                    </button>
                  </div>
                </div>
              ))}
            </div>
            
            {clubs.length === 0 && (
              <div className="no-results">
                <h3>No clubs found</h3>
                <p>Try adjusting your filters or search criteria</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default BrowseClubs;