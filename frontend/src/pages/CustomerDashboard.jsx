import { useEffect, useState } from 'react';
import { Plus } from 'lucide-react';
import api from '../services/api';
import TransactionForm from '../components/TransactionForm';
import TransactionTable from '../components/TransactionTable';

export default function CustomerDashboard() {
  const [transactions, setTransactions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState('');

  useEffect(() => {
    let isCurrent = true;
    api.get('/my-transactions')
      .then(({ data }) => { if (isCurrent) setTransactions(data); })
      .catch(() => { if (isCurrent) setLoadError('Could not load your transactions. Refresh to try again.'); })
      .finally(() => { if (isCurrent) setIsLoading(false); });
    return () => { isCurrent = false; };
  }, []);

  async function submitTransaction(payload) {
    const { data } = await api.post('/transaction', payload);
    setTransactions((current) => [data, ...current]);
    return data;
  }

  return (
    <main className="page-shell" id="top">
      <div className="page-heading">
        <div><span className="eyebrow">CUSTOMER WORKSPACE</span><h1>Transaction activity</h1></div>
        <div className="page-heading-meta"><span className="live-dot" />Secure session</div>
      </div>

      <section className="content-section entry-section" aria-labelledby="new-transaction-title">
        <div className="section-heading">
          <div className="section-icon"><Plus size={17} /></div>
          <div><h2 id="new-transaction-title">New transaction</h2><p>Submit transaction details for assessment.</p></div>
        </div>
        <TransactionForm onCreated={submitTransaction} />
      </section>

      <section className="content-section activity-section" aria-labelledby="activity-title">
        <div className="section-heading section-heading-wide">
          <div><span className="eyebrow">ACCOUNT HISTORY</span><h2 id="activity-title">My transactions</h2></div>
          <span className="record-count">{transactions.length} {transactions.length === 1 ? 'record' : 'records'}</span>
        </div>
        {loadError && <div className="alert alert-danger" role="alert">{loadError}</div>}
        <TransactionTable transactions={transactions} isLoading={isLoading} />
      </section>
    </main>
  );
}