import React, { useState, useEffect } from 'react';
import { ApiService } from '../api';
import type { League, Team, Player, Schedule, Location, Game } from '../api';
import { useAuth } from '../context/AuthContext';

const Admin = () => {
  const { role, teamId } = useAuth();
  const [activeTab, setActiveTab] = useState('teams');
  const [errorMsg, setErrorMsg] = useState('');

  // Data
  const [users, setUsers] = useState<any[]>([]);
  const [leagues, setLeagues] = useState<League[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [players, setPlayers] = useState<Player[]>([]);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [games, setGames] = useState<Game[]>([]);

  // Editing State
  const [editingLeague, setEditingLeague] = useState<League | null>(null);
  const [editingTeam, setEditingTeam] = useState<Team | null>(null);
  const [editingPlayer, setEditingPlayer] = useState<Player | null>(null);

  // Forms State
  const [newUser, setNewUser] = useState({ username: '', password: '', role: 'user', team_id: '' });
  const [newLeague, setNewLeague] = useState('');
  const [newTeam, setNewTeam] = useState({ name: '', league_id: '' });
  const [newPlayer, setNewPlayer] = useState({ first_name: '', last_name: '', number: '', team_id: '' });
  const [newLocation, setNewLocation] = useState({ name: '', time_zone_id: '' });
  const [newGame, setNewGame] = useState({ schedule_id: '', home_team_id: '', visitor_team_id: '', location_id: '', name: '', date_and_time: '' });
  const [scoreForm, setScoreForm] = useState({ game_id: '', home_score: 0, visitor_score: 0 });
  const [goalForm, setGoalForm] = useState({ game_id: '', player_id: '', team_id: '', minute: '' });

  const fetchData = async () => {
    try {
      const [l, t, p, s, loc, g] = await Promise.all([
        ApiService.getLeagues(),
        ApiService.getTeams(),
        ApiService.getPlayers(),
        ApiService.getSchedules(),
        ApiService.getLocations(),
        ApiService.getGames()
      ]);
      setLeagues(l.data);
      setTeams(t.data);
      setPlayers(p.data);
      setSchedules(s.data);
      setLocations(loc.data);
      setGames(g.data);

      if (role === 'admin') {
        const u = await ApiService.getUsers();
        setUsers(u.data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchData();
  }, [role]);

  const handleError = (e: any) => {
    if (e.response && e.response.data && e.response.data.detail) {
      setErrorMsg(e.response.data.detail);
    } else {
      setErrorMsg("An unexpected error occurred.");
    }
    setTimeout(() => setErrorMsg(''), 5000);
  };

  const handleConfirmDelete = (message: string, callback: () => void) => {
    if (window.confirm(message)) {
      callback();
    }
  };

  // --- Users ---
  const handleAddUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = { ...newUser, team_id: newUser.team_id ? Number(newUser.team_id) : null };
      await ApiService.createUser(payload);
      setNewUser({ username: '', password: '', role: 'user', team_id: '' });
      fetchData();
    } catch (e) { handleError(e); }
  };

  const handleDeleteUser = async (id: number) => {
    try {
      await ApiService.deleteUser(id);
      fetchData();
    } catch (e) { handleError(e); }
  };

  // --- Leagues ---
  const handleSaveLeague = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingLeague) {
        await ApiService.updateLeague(editingLeague.id, { name: newLeague });
        setEditingLeague(null);
      } else {
        await ApiService.createLeague({ name: newLeague });
      }
      setNewLeague('');
      fetchData();
    } catch (e) { handleError(e); }
  };

  const handleDeleteLeague = async (id: number) => {
    try {
      await ApiService.deleteLeague(id);
      fetchData();
    } catch (e) { handleError(e); }
  };

  // --- Teams ---
  const handleSaveTeam = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingTeam) {
        await ApiService.updateTeam(editingTeam.id, { name: newTeam.name, league_id: Number(newTeam.league_id) });
        setEditingTeam(null);
      } else {
        await ApiService.createTeam({ name: newTeam.name, league_id: Number(newTeam.league_id) });
      }
      setNewTeam({ name: '', league_id: '' });
      fetchData();
    } catch (e) { handleError(e); }
  };

  const handleDeleteTeam = async (id: number) => {
    try {
      await ApiService.deleteTeam(id);
      fetchData();
    } catch (e) { handleError(e); }
  };

  // --- Players ---
  const handleSavePlayer = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingPlayer) {
        await ApiService.updatePlayer(editingPlayer.id, { ...newPlayer, number: Number(newPlayer.number), team_id: Number(newPlayer.team_id) });
        setEditingPlayer(null);
      } else {
        await ApiService.createPlayer({ ...newPlayer, number: Number(newPlayer.number), team_id: Number(newPlayer.team_id) });
      }
      setNewPlayer({ first_name: '', last_name: '', number: '', team_id: '' });
      fetchData();
    } catch (e) { handleError(e); }
  };

  const handleDeletePlayer = async (id: number) => {
    try {
      await ApiService.deletePlayer(id);
      fetchData();
    } catch (e) { handleError(e); }
  };

  // --- Others ---
  const handleAddLocation = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await ApiService.createLocation({ name: newLocation.name, time_zone_id: newLocation.time_zone_id });
      setNewLocation({ name: '', time_zone_id: '' });
      fetchData();
    } catch (e) { handleError(e); }
  };

  const handleDeleteLocation = async (id: number) => {
    try {
      await ApiService.deleteLocation(id);
      fetchData();
    } catch (e) { handleError(e); }
  };

  const handleAddGame = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      let schedId = Number(newGame.schedule_id);
      if (!schedId) {
        if (schedules.length === 0) {
          const res = await ApiService.createSchedule({ name: "Default Season", league_id: leagues[0]?.id || 1 });
          schedId = res.data.id;
        } else {
          schedId = schedules[0].id;
        }
      }

      await ApiService.createGame({ 
        schedule_id: schedId,
        home_team_id: Number(newGame.home_team_id),
        visitor_team_id: Number(newGame.visitor_team_id),
        location_id: Number(newGame.location_id),
        name: newGame.name,
        date_and_time: newGame.date_and_time || null
      });
      alert('Game created successfully!');
      fetchData();
    } catch (e) { handleError(e); }
  };

  const handleDeleteGame = async (id: number) => {
    try {
      await ApiService.deleteGame(id);
      fetchData();
    } catch (e) { handleError(e); }
  };

  const handleSetScore = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await ApiService.setScore(Number(scoreForm.game_id), { home_score: scoreForm.home_score, visitor_score: scoreForm.visitor_score });
      alert('Score updated!');
      fetchData();
    } catch (e) { handleError(e); }
  };

  const handleAddGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await ApiService.addGoal({
        game_id: Number(goalForm.game_id),
        player_id: Number(goalForm.player_id),
        team_id: Number(goalForm.team_id),
        minute: Number(goalForm.minute)
      });
      alert('Goal registered!');
    } catch (e) { handleError(e); }
  };

  // Filter teams for Coach
  const availableTeams = role === 'coach' ? teams.filter(t => t.id === teamId) : teams;

  const tabs = [
    { id: 'users', label: 'Users', adminOnly: true },
    { id: 'leagues', label: 'Leagues', adminOnly: true },
    { id: 'teams', label: 'Teams', adminOnly: true },
    { id: 'players', label: 'Players', adminOnly: false },
    { id: 'locations', label: 'Locations', adminOnly: true },
    { id: 'games', label: 'Games', adminOnly: false },
    { id: 'match_data', label: 'Scores & Goals', adminOnly: false }
  ];

  return (
    <div className="admin-panel">
      <h1>Management Panel</h1>
      
      {errorMsg && (
        <div style={{ padding: '1rem', background: 'rgba(239,68,68,0.2)', border: '1px solid #ef4444', color: '#fca5a5', borderRadius: '8px', marginBottom: '1rem' }}>
          <strong>Error: </strong> {errorMsg}
        </div>
      )}

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem', overflowX: 'auto' }}>
        {tabs.map(tab => {
          if (tab.adminOnly && role !== 'admin') return null;
          return (
            <button 
              key={tab.id}
              className={`btn ${activeTab === tab.id ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => { setActiveTab(tab.id); setEditingLeague(null); setEditingTeam(null); setEditingPlayer(null); }}
            >
              {tab.label}
            </button>
          );
        })}
      </div>

      <div className="grid grid-cols-2">
        {activeTab === 'users' && (
          <div className="glass-panel" style={{ gridColumn: 'span 2' }}>
            <h2>Create User</h2>
            <form onSubmit={handleAddUser} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Username</label>
                <input type="text" className="form-control" value={newUser.username} onChange={e => setNewUser({ ...newUser, username: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Password</label>
                <input type="password" className="form-control" value={newUser.password} onChange={e => setNewUser({ ...newUser, password: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Role</label>
                <select className="form-control" value={newUser.role} onChange={e => setNewUser({ ...newUser, role: e.target.value })} required>
                  <option value="user">User (Viewer)</option>
                  <option value="coach">Coach</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              {newUser.role === 'coach' && (
                <div className="form-group">
                  <label className="form-label">Assign Team</label>
                  <select className="form-control" value={newUser.team_id} onChange={e => setNewUser({ ...newUser, team_id: e.target.value })} required>
                    <option value="">Select...</option>
                    {teams.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                  </select>
                </div>
              )}
              <div style={{ gridColumn: 'span 2' }}>
                <button type="submit" className="btn btn-primary">Create User</button>
              </div>
            </form>

            <h3 style={{ marginTop: '2rem' }}>Registered Users</h3>
            <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <th style={{ padding: '0.5rem' }}>ID</th>
                  <th style={{ padding: '0.5rem' }}>Username</th>
                  <th style={{ padding: '0.5rem' }}>Role</th>
                  <th style={{ padding: '0.5rem' }}>Assigned Team</th>
                  <th style={{ padding: '0.5rem' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <td style={{ padding: '0.5rem' }}>{u.id}</td>
                    <td style={{ padding: '0.5rem' }}>{u.username}</td>
                    <td style={{ padding: '0.5rem' }}>{u.role}</td>
                    <td style={{ padding: '0.5rem' }}>{u.team_id ? teams.find(t => t.id === u.team_id)?.name : '-'}</td>
                    <td style={{ padding: '0.5rem' }}>
                      <button className="btn" style={{ padding: '0.2rem 0.5rem', fontSize: '0.8rem', background: '#ef4444', color: 'white' }} 
                        onClick={() => handleConfirmDelete(`Delete user ${u.username}?`, () => handleDeleteUser(u.id))}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'leagues' && (
          <div className="glass-panel">
            <h2>{editingLeague ? 'Edit' : 'Add'} League</h2>
            <form onSubmit={handleSaveLeague}>
              <div className="form-group">
                <label className="form-label">League Name</label>
                <input type="text" className="form-control" value={newLeague} onChange={e => setNewLeague(e.target.value)} required />
              </div>
              <button type="submit" className="btn btn-primary">{editingLeague ? 'Update' : 'Add'}</button>
              {editingLeague && <button type="button" className="btn btn-secondary" onClick={() => {setEditingLeague(null); setNewLeague('');}} style={{marginLeft: '0.5rem'}}>Cancel</button>}
            </form>
            <ul style={{ marginTop: '1.5rem' }}>{leagues.map(l => (
              <li key={l.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                {l.name}
                <div>
                  <button className="btn btn-secondary" style={{ padding: '0.2rem 0.5rem', fontSize: '0.8rem', marginRight: '0.5rem' }} onClick={() => { setEditingLeague(l); setNewLeague(l.name); }}>Edit</button>
                  <button className="btn" style={{ padding: '0.2rem 0.5rem', fontSize: '0.8rem', background: '#ef4444', color: 'white' }} onClick={() => handleConfirmDelete(`Delete league ${l.name}?`, () => handleDeleteLeague(l.id))}>Delete</button>
                </div>
              </li>
            ))}</ul>
          </div>
        )}

        {activeTab === 'teams' && (
          <div className="glass-panel">
            <h2>{editingTeam ? 'Edit' : 'Add'} Team</h2>
            <form onSubmit={handleSaveTeam}>
              <div className="form-group">
                <label className="form-label">Team Name</label>
                <input type="text" className="form-control" value={newTeam.name} onChange={e => setNewTeam({ ...newTeam, name: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">League</label>
                <select className="form-control" value={newTeam.league_id} onChange={e => setNewTeam({ ...newTeam, league_id: e.target.value })} required>
                  <option value="">Select...</option>
                  {leagues.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}
                </select>
              </div>
              <button type="submit" className="btn btn-primary">{editingTeam ? 'Update' : 'Add'}</button>
              {editingTeam && <button type="button" className="btn btn-secondary" onClick={() => {setEditingTeam(null); setNewTeam({name:'', league_id:''});}} style={{marginLeft: '0.5rem'}}>Cancel</button>}
            </form>
            <ul style={{ marginTop: '1.5rem' }}>{teams.map(t => (
              <li key={t.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                {t.name}
                <div>
                  <button className="btn btn-secondary" style={{ padding: '0.2rem 0.5rem', fontSize: '0.8rem', marginRight: '0.5rem' }} onClick={() => { setEditingTeam(t); setNewTeam({name: t.name, league_id: t.league_id.toString()}); }}>Edit</button>
                  <button className="btn" style={{ padding: '0.2rem 0.5rem', fontSize: '0.8rem', background: '#ef4444', color: 'white' }} onClick={() => handleConfirmDelete(`Delete team ${t.name}?`, () => handleDeleteTeam(t.id))}>Delete</button>
                </div>
              </li>
            ))}</ul>
          </div>
        )}

        {activeTab === 'players' && (
          <div className="glass-panel" style={{ gridColumn: 'span 2' }}>
            <h2>{editingPlayer ? 'Edit' : 'Add'} Player</h2>
            <form onSubmit={handleSavePlayer} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">First Name</label>
                <input type="text" className="form-control" value={newPlayer.first_name} onChange={e => setNewPlayer({ ...newPlayer, first_name: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Last Name</label>
                <input type="text" className="form-control" value={newPlayer.last_name} onChange={e => setNewPlayer({ ...newPlayer, last_name: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Number</label>
                <input type="number" className="form-control" value={newPlayer.number} onChange={e => setNewPlayer({ ...newPlayer, number: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Team</label>
                <select className="form-control" value={newPlayer.team_id} onChange={e => setNewPlayer({ ...newPlayer, team_id: e.target.value })} required>
                  <option value="">Select...</option>
                  {availableTeams.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                </select>
              </div>
              <div style={{ gridColumn: 'span 2' }}>
                <button type="submit" className="btn btn-primary">{editingPlayer ? 'Update' : 'Add'}</button>
                {editingPlayer && <button type="button" className="btn btn-secondary" onClick={() => {setEditingPlayer(null); setNewPlayer({first_name:'', last_name:'', number:'', team_id:''});}} style={{marginLeft: '0.5rem'}}>Cancel</button>}
              </div>
            </form>
            
            <div style={{ marginTop: '2rem', overflowX: 'auto' }}>
              <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <th style={{ padding: '0.5rem' }}>Name</th>
                    <th style={{ padding: '0.5rem' }}>Number</th>
                    <th style={{ padding: '0.5rem' }}>Team</th>
                    <th style={{ padding: '0.5rem' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {players
                    .filter(p => availableTeams.some(t => t.id === p.team_id))
                    .sort((a, b) => a.team_id - b.team_id || a.number - b.number)
                    .map(p => {
                      const teamName = teams.find(t => t.id === p.team_id)?.name || 'Unknown';
                      return (
                      <tr key={p.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                        <td style={{ padding: '0.5rem' }}>{p.first_name} {p.last_name}</td>
                        <td style={{ padding: '0.5rem' }}>{p.number}</td>
                        <td style={{ padding: '0.5rem', color: 'var(--text-secondary)' }}>{teamName}</td>
                        <td style={{ padding: '0.5rem' }}>
                          <button className="btn btn-secondary" style={{ padding: '0.2rem 0.5rem', fontSize: '0.8rem', marginRight: '0.5rem' }} onClick={() => { 
                            setEditingPlayer(p); 
                            setNewPlayer({first_name: p.first_name, last_name: p.last_name, number: p.number.toString(), team_id: p.team_id.toString()}); 
                          }}>Edit</button>
                          <button className="btn" style={{ padding: '0.2rem 0.5rem', fontSize: '0.8rem', background: '#ef4444', color: 'white' }} onClick={() => handleConfirmDelete(`Delete player ${p.first_name}?`, () => handleDeletePlayer(p.id))}>Delete</button>
                        </td>
                      </tr>
                    )})}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'locations' && (
           <div className="glass-panel">
            <h2>Manage Locations</h2>
            <form onSubmit={handleAddLocation}>
              <div className="form-group">
                <label className="form-label">Location Name</label>
                <input type="text" className="form-control" value={newLocation.name} onChange={e => setNewLocation({ ...newLocation, name: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Time Zone</label>
                <input type="text" className="form-control" value={newLocation.time_zone_id} onChange={e => setNewLocation({ ...newLocation, time_zone_id: e.target.value })} required />
              </div>
              <button type="submit" className="btn btn-primary">Add Location</button>
            </form>
            <ul style={{ marginTop: '1.5rem' }}>{locations.map(l => (
              <li key={l.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                <span>{l.name} ({l.time_zone_id})</span>
                <button className="btn" style={{ padding: '0.2rem 0.5rem', fontSize: '0.8rem', background: '#ef4444', color: 'white' }} onClick={() => handleConfirmDelete(`Delete location ${l.name}?`, () => handleDeleteLocation(l.id))}>Delete</button>
              </li>
            ))}</ul>
          </div>
        )}

        {activeTab === 'games' && (
           <div className="glass-panel" style={{ gridColumn: 'span 2' }}>
            <h2>Create Game Matchup</h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>Schedules will be automatically applied. Both teams must have at least 11 registered players to create a game.</p>
            <form onSubmit={handleAddGame} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Game Name / Description</label>
                <input type="text" className="form-control" value={newGame.name} onChange={e => setNewGame({ ...newGame, name: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Location</label>
                <select className="form-control" value={newGame.location_id} onChange={e => setNewGame({ ...newGame, location_id: e.target.value })} required>
                  <option value="">Select...</option>
                  {locations.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Home Team</label>
                <select className="form-control" value={newGame.home_team_id} onChange={e => setNewGame({ ...newGame, home_team_id: e.target.value })} required>
                  <option value="">Select...</option>
                  {role === 'coach' ? (
                    availableTeams.map(t => <option key={t.id} value={t.id}>{t.name}</option>)
                  ) : (
                    teams.map(t => <option key={t.id} value={t.id}>{t.name}</option>)
                  )}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Visitor Team</label>
                <select className="form-control" value={newGame.visitor_team_id} onChange={e => setNewGame({ ...newGame, visitor_team_id: e.target.value })} required>
                  <option value="">Select...</option>
                  {teams.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Schedule Filter (Optional)</label>
                <select className="form-control" value={newGame.schedule_id} onChange={e => setNewGame({ ...newGame, schedule_id: e.target.value })}>
                  <option value="">Auto-Assign (Default Season)</option>
                  {schedules.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                </select>
              </div>
              <div style={{ gridColumn: 'span 2' }}>
                <button type="submit" className="btn btn-primary">Create Game</button>
              </div>
            </form>

            <h3 style={{ marginTop: '2rem' }}>Existing Games</h3>
            <ul style={{ marginTop: '1.5rem' }}>{games.map(g => {
              if (role === 'coach' && g.home_team_id !== teamId && g.visitor_team_id !== teamId) return null;
              return (
              <li key={g.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                <span>{g.name}</span>
                <button className="btn" style={{ padding: '0.2rem 0.5rem', fontSize: '0.8rem', background: '#ef4444', color: 'white' }} onClick={() => handleConfirmDelete(`Delete game ${g.name}?`, () => handleDeleteGame(g.id))}>Delete</button>
              </li>
            )})}</ul>
          </div>
        )}

        {activeTab === 'match_data' && (
           <>
           <div className="glass-panel">
            <h2>Set Final Score</h2>
            <form onSubmit={handleSetScore}>
              <div className="form-group">
                <label className="form-label">Game</label>
                <select className="form-control" value={scoreForm.game_id} onChange={e => setScoreForm({ ...scoreForm, game_id: e.target.value })} required>
                  <option value="">Select...</option>
                  {games.map(g => {
                    if (role === 'coach' && g.home_team_id !== teamId && g.visitor_team_id !== teamId) return null;
                    return <option key={g.id} value={g.id}>{g.name}</option>
                  })}
                </select>
              </div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <div className="form-group">
                  <label className="form-label">Home Score</label>
                  <input type="number" className="form-control" value={scoreForm.home_score} onChange={e => setScoreForm({ ...scoreForm, home_score: Number(e.target.value) })} required />
                </div>
                <div className="form-group">
                  <label className="form-label">Visitor Score</label>
                  <input type="number" className="form-control" value={scoreForm.visitor_score} onChange={e => setScoreForm({ ...scoreForm, visitor_score: Number(e.target.value) })} required />
                </div>
              </div>
              <button type="submit" className="btn btn-primary">Save Score</button>
            </form>
          </div>

          <div className="glass-panel">
            <h2>Add Goal Scorer</h2>
            <form onSubmit={handleAddGoal}>
              <div className="form-group">
                <label className="form-label">Game</label>
                <select className="form-control" value={goalForm.game_id} onChange={e => setGoalForm({ ...goalForm, game_id: e.target.value })} required>
                  <option value="">Select...</option>
                  {games.map(g => {
                    if (role === 'coach' && g.home_team_id !== teamId && g.visitor_team_id !== teamId) return null;
                    return <option key={g.id} value={g.id}>{g.name}</option>
                  })}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Player</label>
                <select className="form-control" value={goalForm.player_id} onChange={e => setGoalForm({ ...goalForm, player_id: e.target.value })} required>
                  <option value="">Select...</option>
                  {players.filter(p => availableTeams.some(t => t.id === p.team_id)).map(p => <option key={p.id} value={p.id}>{p.first_name} {p.last_name}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Team Scored For</label>
                <select className="form-control" value={goalForm.team_id} onChange={e => setGoalForm({ ...goalForm, team_id: e.target.value })} required>
                  <option value="">Select...</option>
                  {availableTeams.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Minute</label>
                <input type="number" className="form-control" value={goalForm.minute} onChange={e => setGoalForm({ ...goalForm, minute: e.target.value })} required />
              </div>
              <button type="submit" className="btn btn-primary">Add Goal</button>
            </form>
          </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Admin;
