import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { garageApi } from '../api/endpoints'
import StatusBadge from '../components/StatusBadge'

export default function RepairOrderList() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    garageApi.repairOrders(statusFilter ? { status: statusFilter } : {})
      .then(r => { setOrders(r.data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [statusFilter])

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Ordres de réparation</h1>
        <Link to="/garage/repair-orders/new" className="btn-primary">Nouvel ordre</Link>
      </div>

      <div className="card mb-6">
        <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)} className="w-full max-w-xs">
          <option value="">Tous les statuts</option>
          <option value="quote">Devis</option>
          <option value="in_progress">En cours</option>
          <option value="waiting_parts">Attente pièces</option>
          <option value="invoiced">Facturé</option>
          <option value="cancelled">Annulé</option>
        </select>
      </div>

      {loading ? (
        <div className="text-center py-8 text-gray-500">Chargement...</div>
      ) : orders.length === 0 ? (
        <div className="card text-center py-12 text-gray-500">Aucun ordre de réparation</div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr className="text-left text-sm text-gray-500">
                <th className="p-3">Référence</th><th className="p-3">Véhicule</th><th className="p-3">Client</th><th className="p-3">Statut</th><th className="p-3">Créé le</th><th className="p-3">Total</th><th className="p-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {orders.map(o => (
                <tr key={o.id} className="hover:bg-gray-50">
                  <td className="p-3"><Link to={`/garage/repair-orders/${o.id}`} className="font-medium text-primary-600 hover:underline">RO-{o.id}</Link></td>
                  <td className="p-3 text-sm">{o.vehicle_label}</td>
                  <td className="p-3 text-sm">{o.customer_name}</td>
                  <td className="p-3"><StatusBadge status={o.status} /></td>
                  <td className="p-3 text-sm">{new Date(o.created_at).toLocaleDateString('fr-FR')}</td>
                  <td className="p-3 text-sm font-medium">{o.total_cost ? `${new Intl.NumberFormat('fr-FR').format(o.total_cost)} €` : '—'}</td>
                  <td className="p-3 text-right"><Link to={`/garage/repair-orders/${o.id}`} className="text-primary-600 hover:underline text-sm">Voir</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}