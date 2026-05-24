import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';

interface AuthContextType {
  token: string | null;
  role: string | null;
  teamId: number | null;
  login: (token: string, role: string, teamId?: number) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  token: null,
  role: null,
  teamId: null,
  login: () => {},
  logout: () => {},
});

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [role, setRole] = useState<string | null>(localStorage.getItem('role'));
  const [teamId, setTeamId] = useState<number | null>(localStorage.getItem('teamId') ? Number(localStorage.getItem('teamId')) : null);

  const login = (newToken: string, newRole: string, newTeamId?: number) => {
    localStorage.setItem('token', newToken);
    localStorage.setItem('role', newRole);
    if (newTeamId) {
      localStorage.setItem('teamId', newTeamId.toString());
      setTeamId(newTeamId);
    } else {
      localStorage.removeItem('teamId');
      setTeamId(null);
    }
    setToken(newToken);
    setRole(newRole);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('teamId');
    setToken(null);
    setRole(null);
    setTeamId(null);
  };

  return (
    <AuthContext.Provider value={{ token, role, teamId, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
