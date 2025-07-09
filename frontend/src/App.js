import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";
import PlayerProfile from "./PlayerProfile";
import ClubProfile from "./ClubProfile";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [currentView, setCurrentView] = useState("home");
  const [players, setPlayers] = useState([]);
  const [clubs, setClubs] = useState([]);
  const [vacancies, setVacancies] = useState([]);
  const [applications, setApplications] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [userType, setUserType] = useState(null); // 'player' or 'club'

  useEffect(() => {
    loadData();
  }, []);

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

  const handlePlayerRegister = async (playerData) => {
    try {
      const response = await axios.post(`${API}/players`, playerData);
      setCurrentUser(response.data);
      setUserType('player');
      loadData();
      setCurrentView('player-dashboard');
    } catch (error) {
      alert(error.response?.data?.detail || "Error registering player");
    }
  };

  const handleClubRegister = async (clubData) => {
    try {
      const response = await axios.post(`${API}/clubs`, clubData);
      setCurrentUser(response.data);
      setUserType('club');
      loadData();
      setCurrentView('club-dashboard');
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
      alert(error.response?.data?.detail || "Invalid email or password");
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
      alert(error.response?.data?.detail || "Invalid email or password");
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
              className="nav-btn tertiary" 
              onClick={() => setCurrentView("vacancies")}
            >
              View Opportunities
            </button>
          </div>
        </div>
      </nav>

      <main className="main-content">
        {currentView === "home" && <HomeView />}
        {currentView === "player-register" && <PlayerRegister onRegister={handlePlayerRegister} />}
        {currentView === "club-register" && <ClubRegister onRegister={handleClubRegister} />}
        {currentView === "player-login" && <PlayerLogin onLogin={handlePlayerLogin} />}
        {currentView === "club-login" && <ClubLogin onLogin={handleClubLogin} />}
        {currentView === "vacancies" && <VacanciesList vacancies={vacancies} currentUser={currentUser} userType={userType} onApply={handleApplication} hasApplied={hasApplied} />}
        {currentView === "player-dashboard" && <PlayerDashboard player={currentUser} applications={getPlayerApplications()} onPlayerUpdate={handlePlayerUpdate} />}
        {currentView === "club-dashboard" && <ClubDashboard club={currentUser} vacancies={vacancies.filter(v => v.club_id === currentUser?.id)} applications={getClubApplications()} onCreateVacancy={() => setCurrentView("create-vacancy")} onClubUpdate={handleClubUpdate} />}
        {currentView === "create-vacancy" && <CreateVacancy onSubmit={handleVacancyCreate} />}
      </main>
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

const VacanciesList = ({ vacancies, currentUser, userType, onApply, hasApplied }) => (
  <div className="vacancies-container">
    <h2>Available Opportunities</h2>
    <div className="vacancies-grid">
      {vacancies.map(vacancy => (
        <div key={vacancy.id} className="vacancy-card">
          <h3>{vacancy.position}</h3>
          <p className="club-name">{vacancy.club_name}</p>
          <p className="location">{vacancy.location}</p>
          <p className="experience">{vacancy.experience_level} level</p>
          <p className="description">{vacancy.description}</p>
          {vacancy.requirements && (
            <p className="requirements">Requirements: {vacancy.requirements}</p>
          )}
          <p className="posted-date">Posted: {new Date(vacancy.created_at).toLocaleDateString()}</p>
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
      ))}
    </div>
  </div>
);

const PlayerDashboard = ({ player, applications, onPlayerUpdate }) => (
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
                <p><strong>{app.vacancy_position}</strong> at {app.club_name}</p>
                <p className={`status ${app.status}`}>Status: {app.status}</p>
                <p>Applied: {new Date(app.applied_at).toLocaleDateString()}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  </div>
);

const ClubDashboard = ({ club, vacancies, applications, onCreateVacancy, onClubUpdate }) => (
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
              <div key={vacancy.id} className="vacancy-item">
                <p><strong>{vacancy.position}</strong></p>
                <p>{vacancy.experience_level} level</p>
                <p>Posted: {new Date(vacancy.created_at).toLocaleDateString()}</p>
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
                <p><strong>{app.player_name}</strong> applied for {app.vacancy_position}</p>
                <p className={`status ${app.status}`}>Status: {app.status}</p>
                <p>Applied: {new Date(app.applied_at).toLocaleDateString()}</p>
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

export default App;