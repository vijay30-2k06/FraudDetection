import { useCallback, useEffect, useState } from 'react';
import { ShieldAlert } from 'lucide-react';
import api from '../services/api';
import ReviewerTable from '../components/ReviewerTable';

export default function ReviewerDashboard() {
  const [transactions, setTransactions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [busyId, setBusyId] = useState(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const fraudCount = transactions.filter((transaction) => transaction.status === 'Fraud').length;
  const reviewCount = transactions.filter((transaction) => transaction.status === 'Review').length;

  const loadQueue = useCallback(async () => {
    setError('');
    try {
      const { data } = await api.get('/reviewer/transactions');
      setTransactions(data);
    } catch {
      setError('Could not load the review queue. Refresh to try again.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { loadQueue(); }, [loadQueue]);

  async function handleDecision(transactionId, action) {
    setBusyId(transactionId);
    setError('');
    setNotice('');
    try {
      const endpoint = action === 'review' ? 'review' : 'clear';
      await api.put(`/reviewer/${endpoint}/${transactionId}`);
      setTransactions((current) => current.filter((item) => item.id !== transactionId));
      setNotice(action === 'review' ? 'Transaction marked as reviewed.' : 'Transaction cleared from the queue.');
    } catch (decisionError) {
      setError(decisionError.response?.data?.detail || 'Could not update this transaction. Refresh the queue.');
      await loadQueue();
    } finally {
      setBusyId(null);
    }
  }

  return (
    <main className="page-shell reviewer-page" id="top">
      <div className="page-heading">
        <div><span className="eyebrow">FRAUD OPERATIONS</span><h1>Review queue</h1></div>
        <div className="queue-summary" aria-label={`${fraudCount} Fraud cases, ${reviewCount} Review cases`}>
          <div className="queue-metric queue-metric-fraud"><span>{fraudCount}</span><small>Fraud priority</small></div>
          <div className="queue-metric queue-metric-review"><span>{reviewCount}</span><small>Review</small></div>
          <div className="queue-total"><span className="queue-total-number">{transactions.length}</span><span>awaiting decision</span></div>
        </div>
      </div>

      <section className="content-section review-section" aria-labelledby="queue-title">
        <div className="section-heading section-heading-wide">
          <div className="review-heading-icon"><ShieldAlert size={18} /></div>
          <div><h2 id="queue-title">Suspicious transactions</h2><p>Rule signals and customer activity are shown for each case.</p></div>
        </div>
        {error && <div className="alert alert-danger" role="alert">{error}</div>}
        {notice && <div className="alert alert-success" role="status">{notice}</div>}
        <ReviewerTable busyId={busyId} isLoading={isLoading} onDecision={handleDecision} transactions={transactions} />
      </section>
    </main>
  );
}