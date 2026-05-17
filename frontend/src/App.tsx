import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import { Activity, ShieldCheck, LogOut, LogIn } from 'lucide-react';
import Dashboard from './components/Dashboard';
import Admin from './components/Admin';
import Login from './components/Login';
import { AuthProvider, useAuth } from './context/AuthContext';

const NavBar = () => {
  const location = useLocation();
  const { token, logout, role } = useAuth();
  
  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">LIGA</Link>
      <div className="nav-links">
        <Link 
          to="/" 
          className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
        >
          <Activity size={18} style={{ display: 'inline', marginRight: '5px' }} />
          Dashboard
        </Link>
        {(role === 'admin' || role === 'coach') && (
          <Link 
            to="/admin" 
            className={`nav-link ${location.pathname.startsWith('/admin') ? 'active' : ''}`}
          >
            <ShieldCheck size={18} style={{ display: 'inline', marginRight: '5px' }} />
            Management Panel ({role})
          </Link>
        )}
        {token ? (
          <button onClick={logout} className="btn btn-secondary" style={{ padding: '0.5rem 1rem' }}>
            <LogOut size={16} /> Logout
          </button>
        ) : (
          <Link to="/login" className="btn btn-primary" style={{ padding: '0.5rem 1rem', textDecoration: 'none' }}>
            <LogIn size={16} /> Login
          </Link>
        )}
      </div>
    </nav>
  );
};

const ProtectedRoute = ({ children, allowedRoles }: { children: React.ReactNode, allowedRoles: string[] }) => {
  const { token, role } = useAuth();
  if (!token) return <Navigate to="/login" />;
  if (role && !allowedRoles.includes(role)) return <Navigate to="/" />;
  return <>{children}</>;
};

function AppContent() {
  return (
    <div className="app-container">
      <NavBar />
      <main className="container animate-fade-in">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/login" element={<Login />} />
          <Route 
            path="/admin/*" 
            element={
              <ProtectedRoute allowedRoles={['admin', 'coach']}>
                <Admin />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

export default App;
