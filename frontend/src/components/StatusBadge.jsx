export default function StatusBadge({ status }) {
  const map = {
    critical: 'badge-critical',
    warning: 'badge-warning',
    up_to_date: 'badge-up_to_date',
    quote: 'badge-quote',
    in_progress: 'badge-in_progress',
    waiting_parts: 'badge-waiting_parts',
    invoiced: 'badge-invoiced',
    cancelled: 'badge-cancelled',
  }
  const labels = {
    critical: 'Critique',
    warning: 'À surveiller',
    up_to_date: 'À jour',
    quote: 'Devis',
    in_progress: 'En cours',
    waiting_parts: 'Attente pièces',
    invoiced: 'Facturé',
    cancelled: 'Annulé',
  }
  return <span className={`badge ${map[status] || 'badge-critical'}`}>{labels[status] || status}</span>
}