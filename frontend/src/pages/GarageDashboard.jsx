import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { garageApi } from '../api/endpoints'
import StatCard from '../components/StatCard'
import StatusBadge from '../components/StatusBadge'

export default function GarageDashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [orders, setOrders] = useState([])

  useEffect(() => {
    Promise.all([garageApi.dashboard(), garageApi.repairOrders()])
      .then(([d, o]) => { setData(d.data); setOrders(o.data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  const formatNumber = (n) => new Intl.NumberFormat('fr-FR').format(n)

  if (loading) return <div className="flex items-center justify-center h-64">Chargement...</div>
  if (!data) return <div className="card text-red-600">Accès refusé : compte garage requis</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Tableau de bord — {data.garage.name}</h1>
          <p className="text-gray-500">{data.garage.address}</p>
        </div>
        <Link to="/garage/repair-orders/new" className="btn-primary">Nouvel ordre</Link>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Ordres du mois" value={data.orders_month} />
        <StatCard title="Chiffre d'affaires" value={`${formatNumber(data.revenue_month)} €`} />
        <StatCard title="Impayés" value={`${formatNumber(data.unpaid_total)} €`} trend={data.unpaid_total > 0 ? 1 : 0} />
        <StatCard title="Ticket moyen" value={`${formatNumber(data.avg_ticket)} €`} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card">
          <h3 className="font-semibold mb-4">Ordres par statut</h3>
          <div className="space-y-2">
            {Object.entries(data.by_status).map(([status, count]) => (
              <div key={status} className="flex items-center justify-between">
                <span className="flex items-center space-x-2">
                  <StatusBadge status={status} />
                  <span>{status.replace('_', ' ')}</span>
                </span>
                <span className="font-medium">{count}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="card">
          <h3 className="font-semibold mb-4">Derniers ordres</h3>
          <div className="space-y-2">
            {orders.slice(0, 5).map(o => (
              <Link key={o.id} to={`/garage/repair-orders/${o.id}`} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 block">
                <div>
                  <p className="font-medium">{o.title}</p>
                  <p className="text-sm text-gray-500">{o.vehicle_label} • {new Date(o.created_at).toLocaleDateString('fr-FR')}</p>
                </div>
                <div className="text-right">
                  <StatusBadge status={o.status} />
                  <p className="text-sm font-medium mt-1">{o.total_cost ? `${new Intl.NumberFormat('fr-FR').format(o.total_cost)} €` : '—'}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}