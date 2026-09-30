const statusStyles = {
  Safe: 'status-safe',
  Review: 'status-review',
  Fraud: 'status-fraud',
  Reviewed: 'status-reviewed',
  Cleared: 'status-cleared',
};

export default function StatusBadge({ status }) {
  return <span className={`status-badge ${statusStyles[status] || ''}`}>{status}</span>;
}