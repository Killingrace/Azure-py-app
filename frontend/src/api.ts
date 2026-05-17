import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface League { id: number; name: string; }
export interface Team { id: number; name: string; league_id: number; }
export interface Player { id: number; first_name: string; last_name: string; number: number; team_id: number; }
export interface Schedule { id: number; name: string; league_id: number; }
export interface Location { id: number; name: string; time_zone_id: string; }
export interface Game { id: number; schedule_id: number; home_team_id: number; visitor_team_id: number; location_id: number; name: string; score?: any; }

export const ApiService = {
  // Users
  getUsers: () => api.get('/users'),
  createUser: (data: any) => api.post('/users', data),
  deleteUser: (id: number) => api.delete(`/users/${id}`),

  // Stats
  getBestTeams: () => api.get('/stats/teams'),
  getBestPlayers: () => api.get('/stats/players'),
  getBestPlayerVsTeam: (teamId: number) => api.get(`/stats/best-player-vs-team/${teamId}`),
  getBestTeamVsTeam: (teamId: number) => api.get(`/stats/best-team-vs-team/${teamId}`),

  // Leagues
  getLeagues: () => api.get('/leagues'),
  createLeague: (data: any) => api.post('/leagues', data),
  updateLeague: (id: number, data: any) => api.put(`/leagues/${id}`, data),
  deleteLeague: (id: number) => api.delete(`/leagues/${id}`),

  // Teams
  getTeams: () => api.get('/teams'),
  createTeam: (data: any) => api.post('/teams', data),
  updateTeam: (id: number, data: any) => api.put(`/teams/${id}`, data),
  deleteTeam: (id: number) => api.delete(`/teams/${id}`),

  // Players
  getPlayers: () => api.get('/players'),
  createPlayer: (data: any) => api.post('/players', data),
  updatePlayer: (id: number, data: any) => api.put(`/players/${id}`, data),
  deletePlayer: (id: number) => api.delete(`/players/${id}`),

  // Schedules
  getSchedules: () => api.get('/schedules'),
  createSchedule: (data: any) => api.post('/schedules', data),

  // Locations
  getLocations: () => api.get('/locations'),
  createLocation: (data: any) => api.post('/locations', data),
  deleteLocation: (id: number) => api.delete(`/locations/${id}`),

  // Games
  getGames: () => api.get('/games'),
  createGame: (data: any) => api.post('/games', data),
  deleteGame: (id: number) => api.delete(`/games/${id}`),
  setScore: (gameId: number, data: any) => api.post(`/games/${gameId}/score`, data),

  // Goals
  addGoal: (data: any) => api.post('/goals', data),
};
