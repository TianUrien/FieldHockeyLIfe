import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";
import PlayerProfile from "./PlayerProfile";
import ClubProfile from "./ClubProfile";
import EmailVerification from "./EmailVerification";
import PlayerProfileView from "./PlayerProfileView";
import ClubProfileView from "./ClubProfileView";
import PublicPlayerProfile from "./PublicPlayerProfile";
import PublicClubProfile from "./PublicClubProfile";
import BrowsePlayers from "./BrowsePlayers";
import BrowseClubs from "./BrowseClubs";
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from "react-router-dom";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Main App Component wrapped in Router
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/verify-email" element={<EmailVerification />} />
        <Route path="/players/:playerId" element={<PublicPlayerProfile />} />
        <Route path="/clubs/:clubId" element={<PublicClubProfile />} />
        <Route path="/browse/players" element={<BrowsePlayers />} />
        <Route path="/browse/clubs" element={<BrowseClubs />} />
        <Route path="/*" element={<MainApp />} />
      </Routes>
    </Router>
  );
}

function MainApp() {
  const [currentView, setCurrentView] = useState("home");
  const [players, setPlayers] = useState([]);
  const [clubs, setClubs] = useState([]);
  const [vacancies, setVacancies] = useState([]);
  const [applications, setApplications] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [userType, setUserType] = useState(null); // 'player' or 'club'
  const [showVerificationAlert, setShowVerificationAlert] = useState(false);
  const [verificationEmail, setVerificationEmail] = useState('');
  const [viewingPlayerProfile, setViewingPlayerProfile] = useState(null);
  const [viewingClubProfile, setViewingClubProfile] = useState(null);
  const [enrichedApplications, setEnrichedApplications] = useState([]);

  const [editingVacancy, setEditingVacancy] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    loadData();
    
    // Check if redirected from registration
    const urlParams = new URLSearchParams(location.search);
    if (urlParams.get('registered') === 'true') {
      setShowVerificationAlert(true);
      setVerificationEmail(urlParams.get('email') || '');
    }
  }, [location]);

  const loadData = async () => {
    try {
      const [playersRes, clubsRes, vacanciesRes, applicationsRes] = await Promise.all([
        axios.get(`${API}/players`),
        axios.get(`${API}/clubs`),
        axios.get(`${API}/vacancies`),
        axios.get(`${API}/applications`)
      ]);
      setPlayers(playersRes.data);
      setClubs(clubsRes.data);
      setVacancies(vacanciesRes.data);
      setApplications(applicationsRes.data);
    } catch (error) {
      console.error("Error loading data:", error);
    }
  };

  const handleVacancyEdit = async (vacancyData) => {
    try {
      await axios.put(`${API}/vacancies/${editingVacancy.id}`, vacancyData);
      loadData();
      setEditingVacancy(null);
      setCurrentView('club-dashboard');
    } catch (error) {
      alert(error.response?.data?.detail || "Error updating vacancy");
    }
  };

  const handleVacancyDelete = async (vacancyId) => {
    if (!confirm("Are you sure you want to delete this vacancy? This action cannot be undone.")) return;
    
    try {
      await axios.delete(`${API}/vacancies/${vacancyId}`);
      loadData();
    } catch (error) {
      alert(error.response?.data?.detail || "Error deleting vacancy");
    }
  };

  const handlePlayerRegister = async (playerData) => {
    try {
      const response = await axios.post(`${API}/players`, playerData);
      alert(response.data.message);
      setShowVerificationAlert(true);
      setVerificationEmail(playerData.email);
      setCurrentView('home');
    } catch (error) {
      alert(error.response?.data?.detail || "Error registering player");
    }
  };

  const handleClubRegister = async (clubData) => {
    try {
      const response = await axios.post(`${API}/clubs`, clubData);
      alert(response.data.message);
      setShowVerificationAlert(true);
      setVerificationEmail(clubData.email);
      setCurrentView('home');
    } catch (error) {
      alert(error.response?.data?.detail || "Error registering club");
    }
  };

  const handlePlayerLogin = async (loginData) => {
    try {
      const response = await axios.post(`${API}/players/login`, loginData);
      setCurrentUser(response.data);
      setUserType('player');
      loadData();
      setCurrentView('player-dashboard');
    } catch (error) {
      if (error.response?.status === 403) {
        // Email not verified
        setShowVerificationAlert(true);
        setVerificationEmail(loginData.email);
        alert("Please verify your email address before logging in. Check your inbox for a verification email.");
      } else {
        alert(error.response?.data?.detail || "Invalid email or password");
      }
    }
  };

  const handleClubLogin = async (loginData) => {
    try {
      const response = await axios.post(`${API}/clubs/login`, loginData);
      setCurrentUser(response.data);
      setUserType('club');
      loadData();
      setCurrentView('club-dashboard');
    } catch (error) {
      if (error.response?.status === 403) {
        // Email not verified
        setShowVerificationAlert(true);
        setVerificationEmail(loginData.email);
        alert("Please verify your email address before logging in. Check your inbox for a verification email.");
      } else {
        alert(error.response?.data?.detail || "Invalid email or password");
      }
    }
  };

  const handleVacancyCreate = async (vacancyData) => {
    try {
      vacancyData.club_id = currentUser.id;
      await axios.post(`${API}/vacancies`, vacancyData);
      loadData();
      setCurrentView('club-dashboard');
    } catch (error) {
      alert(error.response?.data?.detail || "Error creating vacancy");
    }
  };

  const handleApplication = async (vacancyId) => {
    try {
      await axios.post(`${API}/applications`, {
        player_id: currentUser.id,
        vacancy_id: vacancyId
      });
      loadData();
      alert("Application submitted successfully!");
    } catch (error) {
      alert(error.response?.data?.detail || "Error submitting application");
    }
  };

  const getPlayerApplications = () => {
    return applications.filter(app => app.player_id === currentUser?.id);
  };

  const getClubApplications = () => {
    return applications.filter(app => {
      const vacancy = vacancies.find(v => v.id === app.vacancy_id);
      return vacancy && vacancy.club_id === currentUser?.id;
    });
  };

  const handlePlayerUpdate = (updatedPlayer) => {
    setCurrentUser(updatedPlayer);
    loadData();
  };

  const handleClubUpdate = (updatedClub) => {
    setCurrentUser(updatedClub);
    loadData();
  };

  const hasApplied = (vacancyId) => {
    return applications.some(app => app.player_id === currentUser?.id && app.vacancy_id === vacancyId);
  };

  const handleResendVerification = async (email, userType) => {
    try {
      await axios.post(`${API}/resend-verification`, {
        email: email,
        user_type: userType
      });
      alert("Verification email sent! Please check your inbox.");
    } catch (error) {
      alert(error.response?.data?.detail || "Failed to resend verification email");
    }
  };

  const dismissVerificationAlert = () => {
    setShowVerificationAlert(false);
    setVerificationEmail('');
  };

  const loadEnrichedApplications = async () => {
    if (!currentUser || !userType) return;
    
    try {
      if (userType === 'club') {
        const response = await axios.get(`${API}/clubs/${currentUser.id}/applications-with-profiles`);
        setEnrichedApplications(response.data);
      } else if (userType === 'player') {
        const response = await axios.get(`${API}/players/${currentUser.id}/applications-with-clubs`);
        setEnrichedApplications(response.data);
      }
    } catch (error) {
      console.error('Error loading enriched applications:', error);
    }
  };

  useEffect(() => {
    if (currentUser && userType) {
      loadEnrichedApplications();
    }
  }, [currentUser, userType]);

  return (
    <div className="App">
      <nav className="navbar">
        <div className="nav-container">
          <h1 className="nav-title" onClick={() => setCurrentView("home")}>
            Field Hockey Connect
          </h1>
          <div className="nav-buttons">
            {!currentUser ? (
              <>
                <button 
                  className="nav-btn primary" 
                  onClick={() => setCurrentView("player-login")}
                >
                  Player Login
                </button>
                <button 
                  className="nav-btn secondary" 
                  onClick={() => setCurrentView("club-login")}
                >
                  Club Login
                </button>
                <div className="nav-divider">|</div>
                <button 
                  className="nav-btn tertiary" 
                  onClick={() => setCurrentView("player-register")}
                >
                  Register as Player
                </button>
                <button 
                  className="nav-btn tertiary" 
                  onClick={() => setCurrentView("club-register")}
                >
                  Register as Club
                </button>
              </>
            ) : (
              <>
                <span className="user-greeting">
                  Welcome, {currentUser.name}!
                </span>
                <button 
                  className="nav-btn primary" 
                  onClick={() => setCurrentView(userType === 'player' ? 'player-dashboard' : 'club-dashboard')}
                >
                  Dashboard
                </button>
                <button 
                  className="nav-btn secondary" 
                  onClick={() => {
                    setCurrentUser(null);
                    setUserType(null);
                    setCurrentView("home");
                  }}
                >
                  Logout
                </button>
              </>
            )}
            <button 
              className="nav-btn prominent" 
              onClick={() => setCurrentView("vacancies")}
            >
              View Opportunities
            </button>
            <button 
              className="nav-btn secondary" 
              onClick={() => navigate("/browse/players")}
            >
              Browse Players
            </button>
            <button 
              className="nav-btn secondary" 
              onClick={() => navigate("/browse/clubs")}
            >
              Browse Clubs
            </button>
          </div>
        </div>
      </nav>

      {/* Email Verification Alert */}
      {showVerificationAlert && (
        <div className="verification-alert">
          <div className="alert-content">
            <div className="alert-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                <polyline points="22,6 12,13 2,6"></polyline>
              </svg>
            </div>
            <div className="alert-message">
              <h4>Email Verification Required</h4>
              <p>We've sent a verification email to <strong>{verificationEmail}</strong>. Please check your inbox and click the verification link to complete your registration.</p>
            </div>
            <div className="alert-actions">
              <button 
                className="resend-btn-alert"
                onClick={() => {
                  const userType = currentView.includes('player') ? 'player' : 'club';
                  handleResendVerification(verificationEmail, userType);
                }}
              >
                Resend Email
              </button>
              <button 
                className="dismiss-btn-alert"
                onClick={dismissVerificationAlert}
              >
                ✕
              </button>
            </div>
          </div>
        </div>
      )}

      <main className="main-content">
        {currentView === "home" && <HomeView />}
        {currentView === "player-register" && <PlayerRegister onRegister={handlePlayerRegister} />}
        {currentView === "club-register" && <ClubRegister onRegister={handleClubRegister} />}
        {currentView === "player-login" && <PlayerLogin onLogin={handlePlayerLogin} />}
        {currentView === "club-login" && <ClubLogin onLogin={handleClubLogin} />}
        {currentView === "vacancies" && <VacanciesList vacancies={vacancies} currentUser={currentUser} userType={userType} onApply={handleApplication} hasApplied={hasApplied} clubs={clubs} onViewClubProfile={(clubId) => setViewingClubProfile(clubId)} />}
        {currentView === "player-dashboard" && <PlayerDashboard player={currentUser} applications={enrichedApplications} onPlayerUpdate={handlePlayerUpdate} onViewClubProfile={(clubId) => setViewingClubProfile(clubId)} />}
        {currentView === "club-dashboard" && <ClubDashboard club={currentUser} vacancies={vacancies.filter(v => v.club_id === currentUser?.id)} applications={enrichedApplications} onCreateVacancy={() => setCurrentView("create-vacancy")} onClubUpdate={handleClubUpdate} onEditVacancy={(vacancy) => { setEditingVacancy(vacancy); setCurrentView("edit-vacancy"); }} onDeleteVacancy={handleVacancyDelete} onViewPlayerProfile={(playerId) => setViewingPlayerProfile(playerId)} />}
        {currentView === "create-vacancy" && <CreateVacancy onSubmit={handleVacancyCreate} />}
        {currentView === "edit-vacancy" && editingVacancy && <EditVacancy vacancy={editingVacancy} onSubmit={handleVacancyEdit} onCancel={() => { setEditingVacancy(null); setCurrentView("club-dashboard"); }} />}
      </main>

      {/* Profile View Modals */}
      {viewingPlayerProfile && (
        <PlayerProfileView 
          playerId={viewingPlayerProfile} 
          onClose={() => setViewingPlayerProfile(null)} 
        />
      )}
      
      {viewingClubProfile && (
        <ClubProfileView 
          clubId={viewingClubProfile} 
          onClose={() => setViewingClubProfile(null)} 
        />
      )}
    </div>
  );
}

const HomeView = () => (
  <div className="home-container">
    <section className="hero">
      <div className="hero-content">
        <h1 className="hero-title">
          Connect Field Hockey Players with Clubs
        </h1>
        <p className="hero-subtitle">
          The premier platform bridging the gap between talented field hockey players and clubs seeking new talent. 
          Discover opportunities, apply with one click, and build your field hockey career.
        </p>
        <img 
          src="https://images.pexels.com/photos/9093874/pexels-photo-9093874.jpeg"
          alt="Field Hockey Sport"
          className="hero-image"
        />
      </div>
    </section>

    <section className="features">
      <div className="features-grid">
        <div className="feature-card">
          <h3>For Players</h3>
          <p>Create your profile, showcase your skills, and discover opportunities with top field hockey clubs.</p>
        </div>
        <div className="feature-card">
          <h3>For Clubs</h3>
          <p>Post opportunities, find talented players, and build your dream team from a pool of skilled athletes.</p>
        </div>
        <div className="feature-card">
          <h3>One-Click Apply</h3>
          <p>Streamlined application process makes it easy for players to apply and clubs to review applications.</p>
        </div>
      </div>
    </section>
  </div>
);

const PlayerRegister = ({ onRegister }) => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    country: "",
    position: "",
    experience_level: "",
    location: "",
    bio: "",
    age: ""
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    const submitData = { ...formData };
    if (submitData.age) submitData.age = parseInt(submitData.age);
    onRegister(submitData);
  };

  return (
    <div className="form-container">
      <h2>Join as Player</h2>
      <form onSubmit={handleSubmit} className="registration-form">
        <input
          type="text"
          placeholder="Full Name"
          value={formData.name}
          onChange={(e) => setFormData({...formData, name: e.target.value})}
          required
        />
        <input
          type="email"
          placeholder="Email"
          value={formData.email}
          onChange={(e) => setFormData({...formData, email: e.target.value})}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={formData.password}
          onChange={(e) => setFormData({...formData, password: e.target.value})}
          required
        />
        <input
          type="text"
          placeholder="Country"
          value={formData.country}
          onChange={(e) => setFormData({...formData, country: e.target.value})}
        />
        <select
          value={formData.position}
          onChange={(e) => setFormData({...formData, position: e.target.value})}
          required
        >
          <option value="">Select Position</option>
          <option value="Forward">Forward</option>
          <option value="Midfielder">Midfielder</option>
          <option value="Defender">Defender</option>
          <option value="Goalkeeper">Goalkeeper</option>
        </select>
        <select
          value={formData.experience_level}
          onChange={(e) => setFormData({...formData, experience_level: e.target.value})}
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
          value={formData.location}
          onChange={(e) => setFormData({...formData, location: e.target.value})}
          required
        />
        <input
          type="number"
          placeholder="Age (optional)"
          value={formData.age}
          onChange={(e) => setFormData({...formData, age: e.target.value})}
        />
        <textarea
          placeholder="Bio (optional)"
          value={formData.bio}
          onChange={(e) => setFormData({...formData, bio: e.target.value})}
        />
        <button type="submit" className="submit-btn">Register as Player</button>
      </form>
    </div>
  );
};

const ClubRegister = ({ onRegister }) => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    location: "",
    description: "",
    contact_info: "",
    established_year: ""
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    const submitData = { ...formData };
    if (submitData.established_year) submitData.established_year = parseInt(submitData.established_year);
    onRegister(submitData);
  };

  return (
    <div className="form-container">
      <h2>Join as Club</h2>
      <form onSubmit={handleSubmit} className="registration-form">
        <input
          type="text"
          placeholder="Club Name"
          value={formData.name}
          onChange={(e) => setFormData({...formData, name: e.target.value})}
          required
        />
        <input
          type="email"
          placeholder="Email"
          value={formData.email}
          onChange={(e) => setFormData({...formData, email: e.target.value})}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={formData.password}
          onChange={(e) => setFormData({...formData, password: e.target.value})}
          required
        />
        <input
          type="text"
          placeholder="Location"
          value={formData.location}
          onChange={(e) => setFormData({...formData, location: e.target.value})}
          required
        />
        <input
          type="number"
          placeholder="Established Year (optional)"
          value={formData.established_year}
          onChange={(e) => setFormData({...formData, established_year: e.target.value})}
        />
        <textarea
          placeholder="Club Description (optional)"
          value={formData.description}
          onChange={(e) => setFormData({...formData, description: e.target.value})}
        />
        <input
          type="text"
          placeholder="Contact Information (optional)"
          value={formData.contact_info}
          onChange={(e) => setFormData({...formData, contact_info: e.target.value})}
        />
        <button type="submit" className="submit-btn">Register as Club</button>
      </form>
    </div>
  );
};

const VacanciesList = ({ vacancies, currentUser, userType, onApply, hasApplied, clubs, onViewClubProfile }) => (
  <div className="vacancies-container">
    <h2>Available Opportunities</h2>
    <div className="vacancies-grid">
      {vacancies.map(vacancy => {
        // Find the club for this vacancy to get the logo
        const club = clubs.find(c => c.id === vacancy.club_id);
        
        return (
          <div key={vacancy.id} className="vacancy-card">
            <div className="vacancy-header">
              <div className="club-logo-small">
                {club?.logo ? (
                  <img 
                    src={`${BACKEND_URL}/api/uploads/logos/${club.logo}`} 
                    alt={`${vacancy.club_name} logo`}
                    className="club-logo-image"
                  />
                ) : (
                  <div className="club-logo-placeholder">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                      <circle cx="8.5" cy="8.5" r="1.5"></circle>
                      <polyline points="21,15 16,10 5,21"></polyline>
                    </svg>
                  </div>
                )}
              </div>
              <div className="vacancy-title-section">
                <h3>{vacancy.title || vacancy.position}</h3>
                <p className="club-name">{vacancy.club_name}</p>
              </div>
            </div>
            <p className="location">{vacancy.location}</p>
            <p className="experience">{vacancy.experience_level} level</p>
            <p className="description">{vacancy.description}</p>
            {vacancy.requirements && (
              <p className="requirements">Requirements: {vacancy.requirements}</p>
            )}
            <p className="posted-date">Posted: {new Date(vacancy.created_at).toLocaleDateString()}</p>
            
            <div className="vacancy-actions">
              {onViewClubProfile && (
                <button 
                  className="view-profile-btn"
                  onClick={() => onViewClubProfile(vacancy.club_id)}
                >
                  View Club Profile
                </button>
              )}
              {currentUser && userType === 'player' && (
                <button 
                  className={`apply-btn ${hasApplied(vacancy.id) ? 'applied' : ''}`}
                  onClick={() => onApply(vacancy.id)}
                  disabled={hasApplied(vacancy.id)}
                >
                  {hasApplied(vacancy.id) ? 'Applied' : 'Apply Now'}
                </button>
              )}
            </div>
          </div>
        );
      })}
    </div>
  </div>
);

const PlayerDashboard = ({ player, applications, onPlayerUpdate, onViewClubProfile }) => (
  <div className="dashboard-container">
    <h2>Player Dashboard</h2>
    <div className="dashboard-grid">
      <div className="full-width-section">
        <PlayerProfile player={player} onPlayerUpdate={onPlayerUpdate} />
      </div>
      
      <div className="applications-card">
        <h3>Your Applications</h3>
        {applications.length === 0 ? (
          <p>No applications yet. Browse opportunities to apply!</p>
        ) : (
          <div className="applications-list">
            {applications.map(app => (
              <div key={app.id} className="application-item">
                <div className="application-header">
                  <p><strong>{app.vacancy_details?.position || app.vacancy_position}</strong> at {app.club_profile?.name || app.club_name}</p>
                  <p className={`status ${app.status}`}>Status: {app.status}</p>
                </div>
                <p>Applied: {new Date(app.applied_at).toLocaleDateString()}</p>
                {app.club_profile && onViewClubProfile && (
                  <button 
                    className="view-profile-btn"
                    onClick={() => onViewClubProfile(app.club_profile.id)}
                  >
                    View Club Profile
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  </div>
);

const ClubDashboard = ({ club, vacancies, applications, onCreateVacancy, onClubUpdate, onEditVacancy, onDeleteVacancy, onViewPlayerProfile }) => (
  <div className="dashboard-container">
    <h2>Club Dashboard</h2>
    <div className="dashboard-grid">
      <div className="full-width-section">
        <ClubProfile club={club} onClubUpdate={onClubUpdate} />
      </div>
      
      <div className="vacancies-card">
        <h3>Your Vacancies</h3>
        <button className="create-vacancy-btn" onClick={onCreateVacancy}>
          Create New Vacancy
        </button>
        {vacancies.length === 0 ? (
          <p>No vacancies posted yet.</p>
        ) : (
          <div className="vacancies-list">
            {vacancies.map(vacancy => (
              <div key={vacancy.id} className="vacancy-item-enhanced">
                <div className="vacancy-info">
                  <p><strong>{vacancy.title || vacancy.position}</strong></p>
                  <p>{vacancy.experience_level} level • {vacancy.location}</p>
                  <p>Posted: {new Date(vacancy.created_at).toLocaleDateString()}</p>
                  <p className={`vacancy-status ${vacancy.status}`}>Status: {vacancy.status}</p>
                </div>
                <div className="vacancy-actions">
                  <button 
                    className="edit-vacancy-btn"
                    onClick={() => onEditVacancy(vacancy)}
                    title="Edit vacancy"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                  </button>
                  <button 
                    className="delete-vacancy-btn"
                    onClick={() => onDeleteVacancy(vacancy.id)}
                    title="Delete vacancy"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="3,6 5,6 21,6"></polyline>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      <div className="applications-card">
        <h3>Applications Received</h3>
        {applications.length === 0 ? (
          <p>No applications received yet.</p>
        ) : (
          <div className="applications-list">
            {applications.map(app => (
              <div key={app.id} className="application-item">
                <div className="application-header">
                  <p><strong>{app.player_profile?.name || app.player_name}</strong> applied for {app.vacancy_details?.position || app.vacancy_position}</p>
                  <p className={`status ${app.status}`}>Status: {app.status}</p>
                </div>
                <p>Applied: {new Date(app.applied_at).toLocaleDateString()}</p>
                {app.player_profile && (
                  <div className="player-preview">
                    <p><strong>Position:</strong> {app.player_profile.position}</p>
                    <p><strong>Experience:</strong> {app.player_profile.experience_level}</p>
                    <p><strong>Location:</strong> {app.player_profile.location}</p>
                    {onViewPlayerProfile && (
                      <button 
                        className="view-profile-btn"
                        onClick={() => onViewPlayerProfile(app.player_profile.id)}
                      >
                        View Full Profile
                      </button>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  </div>
);

const CreateVacancy = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    position: "",
    title: "",
    description: "",
    requirements: "",
    experience_level: "",
    location: ""
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="form-container">
      <h2>Create New Vacancy</h2>
      <form onSubmit={handleSubmit} className="registration-form">
        <input
          type="text"
          placeholder="Job Title"
          value={formData.title}
          onChange={(e) => setFormData({...formData, title: e.target.value})}
          required
        />
        <select
          value={formData.position}
          onChange={(e) => setFormData({...formData, position: e.target.value})}
          required
        >
          <option value="">Select Position</option>
          <option value="Forward">Forward</option>
          <option value="Midfielder">Midfielder</option>
          <option value="Defender">Defender</option>
          <option value="Goalkeeper">Goalkeeper</option>
        </select>
        <select
          value={formData.experience_level}
          onChange={(e) => setFormData({...formData, experience_level: e.target.value})}
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
          value={formData.location}
          onChange={(e) => setFormData({...formData, location: e.target.value})}
          required
        />
        <textarea
          placeholder="Position Description"
          value={formData.description}
          onChange={(e) => setFormData({...formData, description: e.target.value})}
          required
        />
        <textarea
          placeholder="Requirements (optional)"
          value={formData.requirements}
          onChange={(e) => setFormData({...formData, requirements: e.target.value})}
        />
        <button type="submit" className="submit-btn">Create Vacancy</button>
      </form>
    </div>
  );
};

const PlayerLogin = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    email: "",
    password: ""
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onLogin(formData);
  };

  return (
    <div className="form-container">
      <h2>Player Login</h2>
      <form onSubmit={handleSubmit} className="registration-form">
        <input
          type="email"
          placeholder="Email"
          value={formData.email}
          onChange={(e) => setFormData({...formData, email: e.target.value})}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={formData.password}
          onChange={(e) => setFormData({...formData, password: e.target.value})}
          required
        />
        <button type="submit" className="submit-btn">Login</button>
      </form>
    </div>
  );
};

const ClubLogin = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    email: "",
    password: ""
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onLogin(formData);
  };

  return (
    <div className="form-container">
      <h2>Club Login</h2>
      <form onSubmit={handleSubmit} className="registration-form">
        <input
          type="email"
          placeholder="Email"
          value={formData.email}
          onChange={(e) => setFormData({...formData, email: e.target.value})}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={formData.password}
          onChange={(e) => setFormData({...formData, password: e.target.value})}
          required
        />
        <button type="submit" className="submit-btn">Login</button>
      </form>
    </div>
  );
};

const EditVacancy = ({ vacancy, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    position: vacancy.position || "",
    title: vacancy.title || "",
    description: vacancy.description || "",
    requirements: vacancy.requirements || "",
    experience_level: vacancy.experience_level || "",
    location: vacancy.location || "",
    status: vacancy.status || "active"
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="form-container">
      <h2>Edit Vacancy</h2>
      <form onSubmit={handleSubmit} className="registration-form">
        <input
          type="text"
          placeholder="Job Title"
          value={formData.title}
          onChange={(e) => setFormData({...formData, title: e.target.value})}
          required
        />
        <select
          value={formData.position}
          onChange={(e) => setFormData({...formData, position: e.target.value})}
          required
        >
          <option value="">Select Position</option>
          <option value="Forward">Forward</option>
          <option value="Midfielder">Midfielder</option>
          <option value="Defender">Defender</option>
          <option value="Goalkeeper">Goalkeeper</option>
        </select>
        <select
          value={formData.experience_level}
          onChange={(e) => setFormData({...formData, experience_level: e.target.value})}
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
          value={formData.location}
          onChange={(e) => setFormData({...formData, location: e.target.value})}
          required
        />
        <select
          value={formData.status}
          onChange={(e) => setFormData({...formData, status: e.target.value})}
          required
        >
          <option value="active">Active</option>
          <option value="paused">Paused</option>
          <option value="draft">Draft</option>
          <option value="closed">Closed</option>
        </select>
        <textarea
          placeholder="Position Description"
          value={formData.description}
          onChange={(e) => setFormData({...formData, description: e.target.value})}
          required
        />
        <textarea
          placeholder="Requirements (optional)"
          value={formData.requirements}
          onChange={(e) => setFormData({...formData, requirements: e.target.value})}
        />
        <div className="form-actions">
          <button type="button" className="cancel-btn" onClick={onCancel}>
            Cancel
          </button>
          <button type="submit" className="submit-btn">Update Vacancy</button>
        </div>
      </form>
    </div>
  );
};

export default App;