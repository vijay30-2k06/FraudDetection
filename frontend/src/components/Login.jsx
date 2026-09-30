import { useState } from 'react';
import { ArrowRight, ShieldCheck } from 'lucide-react';

export default function Login({ onLogin }) {
  const [credentials, setCredentials] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    setIsSubmitting(true);
    try {
      await onLogin(credentials);
    } catch (loginError) {
      setError(loginError.response?.data?.detail || 'Unable to sign in. Check your connection and try again.');
    } finally {
      setIsSubmitting(false);
    }
  }

  function updateField(event) {
    setCredentials((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  return (
    <main className="login-page">
      <section className="login-panel" aria-labelledby="login-title">
        <div className="login-brand">
          <div className="login-brand-top">
            <span className="brand-mark brand-mark-light"><ShieldCheck size={21} /></span>
            <span className="brand-name brand-name-light">Fraud<span>Desk</span></span>
          </div>
          <div className="login-brand-bottom">
            <span className="eyebrow">SECURE OPERATIONS</span>
            <p>Transaction review<br />and risk operations</p>
            <div className="brand-rule" />
            <span className="brand-meta">FINANCIAL INTEGRITY OFFICE</span>
          </div>
        </div>

        <div className="login-form-wrap">
          <span className="eyebrow login-eyebrow">ACCOUNT ACCESS</span>
          <h1 id="login-title">Sign in</h1>
          <p className="login-description">Use your assigned workspace credentials.</p>
          <form onSubmit={handleSubmit} className="login-form">
            <label htmlFor="email" className="form-label">Email address</label>
            <input
              autoComplete="email"
              autoFocus
              className="form-control input-field"
              id="email"
              name="email"
              onChange={updateField}
              required
              type="email"
              value={credentials.email}
            />
            <label htmlFor="password" className="form-label mt-3">Password</label>
            <input
              autoComplete="current-password"
              className="form-control input-field"
              id="password"
              name="password"
              onChange={updateField}
              required
              type="password"
              value={credentials.password}
            />
            {error && <div className="alert alert-danger login-error" role="alert">{error}</div>}
            <button className="btn primary-button login-submit" disabled={isSubmitting} type="submit">
              {isSubmitting ? 'Signing in...' : 'Continue'}
              {!isSubmitting && <ArrowRight size={17} />}
            </button>
          </form>
        </div>
      </section>
      <footer className="login-footer"><span>FRAUD DESK</span><span>AUTHORIZED USERS ONLY</span></footer>
    </main>
  );
}