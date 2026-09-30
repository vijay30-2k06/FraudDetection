import { useEffect, useRef, useState } from 'react';
import { ArrowUpRight, LoaderCircle, MapPin } from 'lucide-react';

const initialForm = { account_id: '', amount: '', country: '' };

export default function TransactionForm({ onCreated }) {
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);
  const [locationMessage, setLocationMessage] = useState('Detecting your country...');
  const didRequestLocation = useRef(false);

  useEffect(() => {
    if (didRequestLocation.current) return;
    didRequestLocation.current = true;
    detectCountry();
  }, []);

  function detectCountry() {
    if (!navigator.geolocation) {
      setLocationMessage('Location is unavailable. Enter your country manually.');
      return;
    }

    setIsDetecting(true);
    setLocationMessage('Waiting for location permission...');
    navigator.geolocation.getCurrentPosition(
      async ({ coords }) => {
        try {
          const query = new URLSearchParams({
            latitude: String(coords.latitude),
            longitude: String(coords.longitude),
            localityLanguage: 'en',
          });
          const response = await fetch(
            `https://api.bigdatacloud.net/data/reverse-geocode-client?${query}`,
          );
          if (!response.ok) throw new Error('Location lookup failed');
          const location = await response.json();
          const country = location.countryName;
          if (!country) throw new Error('Country was not returned');

          setForm((current) => current.country ? current : { ...current, country });
          setLocationMessage(`Location detected: ${country}. Confirm or edit as needed.`);
        } catch {
          setLocationMessage('Could not detect your country. Enter it manually.');
        } finally {
          setIsDetecting(false);
        }
      },
      (locationError) => {
        setIsDetecting(false);
        setLocationMessage(
          locationError.code === 1
            ? 'Location permission denied. Enter your country manually.'
            : 'Could not detect your country. Enter it manually.',
        );
      },
      { enableHighAccuracy: false, maximumAge: 300000, timeout: 10000 },
    );
  }

  function updateField(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    setIsSubmitting(true);
    try {
      const transaction = await onCreated({ ...form, amount: Number(form.amount) });
      if (transaction) setForm(initialForm);
    } catch (submitError) {
      setError(submitError.response?.data?.detail || 'Transaction could not be submitted. Try again.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="transaction-form" onSubmit={handleSubmit}>
      <div className="form-grid">
        <div>
          <label className="form-label" htmlFor="account_id">Account ID</label>
          <input className="form-control input-field" id="account_id" name="account_id" onChange={updateField} required value={form.account_id} />
        </div>
        <div>
          <label className="form-label" htmlFor="amount">Amount</label>
          <div className="input-with-prefix"><span>$</span><input className="form-control input-field" id="amount" min="0.01" name="amount" onChange={updateField} required step="0.01" type="number" value={form.amount} /></div>
        </div>
        <div>
          <label className="form-label" htmlFor="country">Country</label>
          <div className="country-entry-row">
            <input autoComplete="country-name" className="form-control input-field" id="country" name="country" onChange={updateField} required value={form.country} />
            <button aria-label="Detect country from location" className="icon-button location-retry" disabled={isDetecting} onClick={detectCountry} title="Detect country from location" type="button">
              {isDetecting ? <LoaderCircle className="spin" size={17} /> : <MapPin size={17} />}
            </button>
          </div>
          <p aria-live="polite" className="location-message">{locationMessage}</p>
        </div>
      </div>
      {error && <div className="alert alert-danger form-error" role="alert">{error}</div>}
      <div className="form-actions">
        <span className="form-footnote">All fields are required</span>
        <button className="btn primary-button" disabled={isSubmitting} type="submit">
          {isSubmitting ? <LoaderCircle className="spin" size={16} /> : <ArrowUpRight size={16} />}
          {isSubmitting ? 'Assessing...' : 'Submit transaction'}
        </button>
      </div>
    </form>
  );
}