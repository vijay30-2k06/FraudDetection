import { CircleCheck } from 'lucide-react';

function formatAmount(amount) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(Number(amount));
}

function formatDate(date) {
  return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }).format(new Date(date));
}

export default function TransactionTable({ transactions, isLoading }) {
  if (isLoading) return <div className="table-state"><span className="loading-indicator" />Loading transactions</div>;
  if (!transactions.length) {
    return <div className="empty-state"><CircleCheck size={21} /><div><strong>No transactions yet</strong><span>Your submitted activity will appear here.</span></div></div>;
  }

  return (
    <div className="table-responsive">
      <table className="table transaction-table align-middle mb-0">
        <thead><tr><th>Transaction</th><th>Amount</th><th>Country</th><th>Submitted</th></tr></thead>
        <tbody>
          {transactions.map((transaction) => (
            <tr key={transaction.id}>
              <td><span className="transaction-id">TX-{String(transaction.id).padStart(5, '0')}</span></td>
              <td className="amount-cell">{formatAmount(transaction.amount)}</td>
              <td>{transaction.country}</td>
              <td className="date-cell">{formatDate(transaction.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}