import { useEffect, useState } from 'react';
import Login from './components/Login';
import Navbar from './components/Navbar';
import CustomerDashboard from './pages/CustomerDashboard';
import ReviewerDashboard from './pages/ReviewerDashboard';
import { SESSION_EVENT, signIn, signOut } from './services/api';

function readSavedUser() {
  try {
    return JSON.parse(localStorage.getItem('frauddesk-user'));
  } catch {
    return null;
  }
}

export default function App() {
  const [user, setUser] = useState(readSavedUser);

  useEffect(() => {
    function clearSession() {
      signOut();
      setUser(null);
    }
    window.addEventListener(SESSION_EVENT, clearSession);
    return () => window.removeEventListener(SESSION_EVENT, clearSession);
  }, []);

  async function handleLogin(credentials) {
    const authenticatedUser = await signIn(credentials);
    setUser(authenticatedUser);
  }

  function handleLogout() {
    signOut();
    setUser(null);
  }

  if (!user) return <Login onLogin={handleLogin} />;

  return (
    <div className="app-frame">
      <Navbar onLogout={handleLogout} user={user} />
      {user.role === 'REVIEWER' ? <ReviewerDashboard /> : <CustomerDashboard />}
    </div>
  );
}