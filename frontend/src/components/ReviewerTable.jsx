import { Check, CircleAlert, LoaderCircle, ShieldCheck, X } from 'lucide-react';
import StatusBadge from './StatusBadge';

function formatAmount(amount) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(Number(amount));
}

export default function ReviewerTable({ transactions, isLoading, busyId, onDecision }) {
  if (isLoading) return <div className="table-state"><span className="loading-indicator" />Loading review queue</div>;
  if (!transactions.length) {
    return <div className="empty-state empty-state-clear"><ShieldCheck size={22} /><div><strong>Queue is clear</strong><span>No transactions are waiting for review.</span></div></div>;
  }

  return (
    <div className="table-responsive">
      <table className="table transaction-table reviewer-table align-middle mb-0">
        <thead><tr><th>Transaction</th><th>Customer</th><th>Account</th><th>Amount</th><th>Country</th><th>Risk</th><th>Status</th><th>Decision</th></tr></thead>
        <tbody>
          {transactions.map((transaction) => (
            <tr key={transaction.id}>
              <td><span className="transaction-id">TX-{String(transaction.id).padStart(5, '0')}</span></td>
              <td>
                <details className="customer-details">
                  <summary>
                    <span className="customer-id">CUS-{String(transaction.customer_id).padStart(5, '0')}</span>
                    <strong>{transaction.customer_name}</strong>
                  </summary>
                  <div className="customer-history-panel">
                    <div className="customer-contact">{transaction.customer_email}</div>
                    <div className="history-list">
                      {transaction.customer_history.map((historyItem) => (
                        <article className="history-item" key={historyItem.id}>
                          <div className="history-item-heading">
                            <span className="transaction-id">TX-{String(historyItem.id).padStart(5, '0')}</span>
                            <StatusBadge status={historyItem.status} />
                          </div>
                          <div className="history-item-meta">
                            <span>{formatAmount(historyItem.amount)}</span>
                            <span>{historyItem.country}</span>
                            <span>Risk {historyItem.risk_score}</span>
                          </div>
                          <time>{new Date(historyItem.created_at).toLocaleString()}</time>
                          {!!historyItem.reasons?.length && <div className="history-reasons">{historyItem.reasons.join(' · ')}</div>}
                        </article>
                      ))}
                    </div>
                  </div>
                </details>
              </td>
              <td className="account-cell">{transaction.account_id}</td>
              <td className="amount-cell">{formatAmount(transaction.amount)}</td>
              <td>{transaction.country}</td>
              <td><span className="risk-score score-high"><CircleAlert size={14} />{transaction.risk_score}</span></td>
              <td><StatusBadge status={transaction.status} /></td>
              <td>
                <div className="decision-buttons">
                  <button className="btn decision-button decision-review" disabled={busyId === transaction.id} onClick={() => onDecision(transaction.id, 'review')} title="Mark reviewed" type="button">
                    {busyId === transaction.id ? <LoaderCircle className="spin" size={15} /> : <Check size={15} />}<span>Reviewed</span>
                  </button>
                  <button className="btn decision-button decision-clear" disabled={busyId === transaction.id} onClick={() => onDecision(transaction.id, 'clear')} title="Clear transaction" type="button">
                    {busyId === transaction.id ? <LoaderCircle className="spin" size={15} /> : <X size={15} />}<span>Cleared</span>
                  </button>
                </div>
                {!!transaction.reasons?.length && <div className="reason-list">{transaction.reasons.map((reason) => <span key={reason}>{reason}</span>)}</div>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}