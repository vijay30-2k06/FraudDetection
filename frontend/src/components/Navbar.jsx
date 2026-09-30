import { LogOut, ShieldCheck } from 'lucide-react';

export default function Navbar({ user, onLogout }) {
  const roleLabel = user.role === 'REVIEWER' ? 'Fraud reviewer' : 'Customer';

  return (
    <header className="topbar">
      <a className="brand" href="#top" aria-label="Fraud Desk home">
        <span className="brand-mark"><ShieldCheck size={19} strokeWidth={2.2} /></span>
        <span className="brand-name">Fraud<span>Desk</span></span>
      </a>
      <div className="topbar-session">
        <div className="session-identity">
          <span className="session-role">{roleLabel}</span>
          <span className="session-name">{user.email}</span>
        </div>
        <button className="icon-button logout-button" onClick={onLogout} title="Sign out" aria-label="Sign out">
          <LogOut size={17} />
        </button>
      </div>
    </header>
  );
}