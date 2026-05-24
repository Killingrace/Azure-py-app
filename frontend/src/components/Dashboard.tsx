import { useEffect, useState } from 'react';
import { ApiService } from '../api';
import type { Team } from '../api';
import { Trophy, Star, ShieldAlert } from 'lucide-react';

const Dashboard = () => {
  const [topTeams, setTopTeams] = useState<any[]>([]);
  const [topPlayers, setTopPlayers] = useState<any[]>([]);
  const [allTeams, setAllTeams] = useState<Team[]>([]);
  
  const [nemesisTeamId, setNemesisTeamId] = useState<number | ''>('');
  const [nemesisData, setNemesisData] = useState<any>(null);
  const [nemesisTeamData, setNemesisTeamData] = useState<any>(null);

  const fetchStats = async () => {
    try {
      const [teamsRes, playersRes, allTeamsRes] = await Promise.all([
        ApiService.getBestTeams(),
        ApiService.getBestPlayers(),
        ApiService.getTeams()
      ]);
      setTopTeams(teamsRes.data);
      setTopPlayers(playersRes.data);
      setAllTeams(allTeamsRes.data);
      if (allTeamsRes.data.length > 0) {
        setNemesisTeamId(allTeamsRes.data[0].id);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchNemesis = async () => {
    if (!nemesisTeamId) return;
    try {
      const resPlayer = await ApiService.getBestPlayerVsTeam(Number(nemesisTeamId));
      setNemesisData(resPlayer.data);
    } catch (e) {
      setNemesisData(null);
    }

    try {
      const resTeam = await ApiService.getBestTeamVsTeam(Number(nemesisTeamId));
      setNemesisTeamData(resTeam.data);
    } catch (e) {
      setNemesisTeamData(null);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return (
    <div>
      <h1 style={{ marginBottom: '2rem' }}>Liga Analytics</h1>

      <div className="grid grid-cols-2" style={{ marginBottom: '2rem' }}>
        <div className="glass-panel">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
            <div className="icon-wrapper"><Trophy size={24} color="var(--primary)" /></div>
            <h2 style={{ margin: 0 }}>Top Teams Leaderboard</h2>
          </div>
          
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <th style={{ padding: '0.5rem' }}>Rank</th>
                  <th style={{ padding: '0.5rem' }}>Team</th>
                  <th style={{ padding: '0.5rem' }}>Pts</th>
                  <th style={{ padding: '0.5rem' }}>W</th>
                  <th style={{ padding: '0.5rem' }}>D</th>
                  <th style={{ padding: '0.5rem' }}>L</th>
                  <th style={{ padding: '0.5rem' }}>GD</th>
                </tr>
              </thead>
              <tbody>
                {topTeams.length > 0 ? topTeams.map((t, idx) => (
                  <tr key={t.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <td style={{ padding: '0.5rem' }}>{idx + 1}</td>
                    <td style={{ padding: '0.5rem', fontWeight: 'bold' }}>{t.name}</td>
                    <td style={{ padding: '0.5rem', color: 'var(--primary)', fontWeight: 'bold' }}>{t.points}</td>
                    <td style={{ padding: '0.5rem' }}>{t.wins}</td>
                    <td style={{ padding: '0.5rem' }}>{t.draws}</td>
                    <td style={{ padding: '0.5rem' }}>{t.losses}</td>
                    <td style={{ padding: '0.5rem' }}>{t.goal_diff > 0 ? `+${t.goal_diff}` : t.goal_diff}</td>
                  </tr>
                )) : <tr><td colSpan={7} style={{ padding: '1rem', textAlign: 'center' }}>No data available</td></tr>}
              </tbody>
            </table>
          </div>
        </div>

        <div className="glass-panel">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
            <div className="icon-wrapper"><Star size={24} color="#eab308" /></div>
            <h2 style={{ margin: 0 }}>Top Players Leaderboard</h2>
          </div>
          
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <th style={{ padding: '0.5rem' }}>Rank</th>
                  <th style={{ padding: '0.5rem' }}>Player</th>
                  <th style={{ padding: '0.5rem' }}>Team</th>
                  <th style={{ padding: '0.5rem' }}>Goals</th>
                  <th style={{ padding: '0.5rem' }}>Avg / Game</th>
                </tr>
              </thead>
              <tbody>
                {topPlayers.length > 0 ? topPlayers.map((p, idx) => (
                  <tr key={p.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <td style={{ padding: '0.5rem' }}>{idx + 1}</td>
                    <td style={{ padding: '0.5rem', fontWeight: 'bold' }}>{p.first_name} {p.last_name}</td>
                    <td style={{ padding: '0.5rem', fontSize: '0.9em', color: 'var(--text-secondary)' }}>{p.team_name}</td>
                    <td style={{ padding: '0.5rem', color: '#eab308', fontWeight: 'bold' }}>{p.total_goals}</td>
                    <td style={{ padding: '0.5rem' }}>{p.avg_goals}</td>
                  </tr>
                )) : <tr><td colSpan={5} style={{ padding: '1rem', textAlign: 'center' }}>No data available</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="glass-panel" style={{ maxWidth: '800px', margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
          <div className="icon-wrapper"><ShieldAlert size={24} color="#ef4444" /></div>
          <h2 style={{ margin: 0 }}>Nemesis Analysis</h2>
        </div>
        
        <div className="form-group" style={{ maxWidth: '400px' }}>
          <label className="form-label">Select Team to analyze</label>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <select 
              className="form-control" 
              value={nemesisTeamId} 
              onChange={e => setNemesisTeamId(e.target.value ? Number(e.target.value) : '')}
            >
              <option value="">Select a team...</option>
              {allTeams.map(t => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
            <button onClick={fetchNemesis} className="btn btn-primary">Analyze</button>
          </div>
        </div>

        <div className="grid grid-cols-2" style={{ marginTop: '2rem', gap: '1rem' }}>
          {nemesisData ? (
            <div style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
              <h3 style={{ margin: '0 0 0.5rem 0', color: '#ef4444', fontSize: '1rem' }}>Most Dangerous Player</h3>
              <h2 style={{ margin: '0 0 0.5rem 0' }}>{nemesisData.player.first_name} {nemesisData.player.last_name}</h2>
              <p style={{ margin: 0 }}>Has scored <strong>{nemesisData.goals} goals</strong> against this team!</p>
            </div>
          ) : (
            <div style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '8px' }}>
              <p style={{ color: 'var(--text-secondary)', margin: 0 }}>No player nemesis data available.</p>
            </div>
          )}

          {nemesisTeamData ? (
            <div style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
              <h3 style={{ margin: '0 0 0.5rem 0', color: '#ef4444', fontSize: '1rem' }}>Most Dangerous Opponent Team</h3>
              <h2 style={{ margin: '0 0 0.5rem 0' }}>{nemesisTeamData.team.name}</h2>
              <p style={{ margin: 0 }}>Won <strong>{nemesisTeamData.stats.points} points</strong> against this team.</p>
            </div>
          ) : (
            <div style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '8px' }}>
              <p style={{ color: 'var(--text-secondary)', margin: 0 }}>No team nemesis data available.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
