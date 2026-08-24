import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { vehiclesApi, partsApi } from '../api/endpoints'
import StatusBadge from '../components/StatusBadge'
import StatCard from '../components/StatCard'
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell
} from 'recharts'

const COLORS = ['#0ea5e9', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

function AlertsSection({ alerts, trackedItems }) {
  if (alerts.length === 0 && trackedItems.length === 0) {
    return (
      <div className="card text-center py-8">
        <p className="text-gray-500">Aucune alerte</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {alerts.length > 0 && (
        <div className="card space-y-3">
          <h3 className="font-semibold">Alertes</h3>
          {alerts.map(a => (
            <div key={`${a.type}-${a.item_id || a.title}`} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <StatusBadge status={a.severity} />
                <div>
                  <p className="font-medium">{a.title}</p>
                  <p className="text-sm text-gray-500">{a.message}</p>
                </div>
              </div>
              {a.progress !== undefined && (
                <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div className={`h-full ${a.severity === 'critical' ? 'bg-red-500' : a.severity === 'warning' ? 'bg-yellow-500' : 'bg-green-500'}`}
                       style={{ width: `${Math.min(a.progress, 100)}%` }} />
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {trackedItems.length > 0 && (
        <div className="card">
          <h3 className="font-semibold mb-4">Éléments suivis</h3>
          <div className="space-y-2">
            {trackedItems.map(t => (
              <div key={t.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <StatusBadge status={t.status} />
                  <div>
                    <p className="font-medium">{t.name}</p>
                    <p className="text-sm text-gray-500">
                      {t.interval_km ? `Km: ${t.interval_km.toLocaleString()}` : ''} {t.interval_months ? `• Mois: ${t.interval_months}` : ''}
                      {t.last_service_km ? ` • Dernier: ${t.last_service_km.toLocaleString()} km` : ''}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default function VehicleDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('dashboard')
  const [vehicle, setVehicle] = useState(null)
  const [dashboard, setDashboard] = useState(null)
  const [maintenances, setMaintenances] = useState([])
  const [expenses, setExpenses] = useState([])
  const [expensesSummary, setExpensesSummary] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [trackedItems, setTrackedItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchAll = async () => {
    try {
      setLoading(true)
      const [v, d, m, e, es, a, t] = await Promise.all([
        vehiclesApi.get(id),
        vehiclesApi.dashboard(id),
        vehiclesApi.maintenances(id),
        vehiclesApi.expenses(id),
        vehiclesApi.expensesSummary(id),
        vehiclesApi.alerts(id),
        vehiclesApi.trackedItems(id),
      ])
      setVehicle(v.data)
      setDashboard(d.data)
      setMaintenances(m.data)
      setExpenses(e.data)
      setExpensesSummary(es.data)
      setAlerts(a.data)
      setTrackedItems(t.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur de chargement')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchAll() }, [id])

  const deleteVehicle = async () => {
    if (confirm('Supprimer ce véhicule ?')) {
      try {
        await vehiclesApi.delete(id)
        navigate('/vehicles')
      } catch (err) {
        alert('Erreur lors de la suppression')
      }
    }
  }

  if (loading) return <div className="flex items-center justify-center h-64">Chargement...</div>
  if (error) return <div className="card text-red-600">{error}</div>
  if (!vehicle) return null

  const formatNumber = (n) => new Intl.NumberFormat('fr-FR').format(n)

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <Link to="/vehicles" className="text-primary-600 hover:underline text-sm mb-2 inline-block">← Mes véhicules</Link>
          <h1 className="text-2xl font-bold">{vehicle.brand} {vehicle.model}</h1>
          <p className="text-gray-500">{vehicle.name} • {vehicle.year} • {vehicle.registration_number || 'Sans plaque'} • {vehicle.mileage.toLocaleString()} km</p>
        </div>
        <div className="flex items-center space-x-3">
          <StatusBadge status={vehicle.health?.overall_status || 'up_to_date'} />
          <Link to={`/vehicles/${id}/edit`} className="btn-secondary text-sm">Modifier</Link>
          <button onClick={deleteVehicle} className="btn-danger text-sm">Supprimer</button>
        </div>
      </div>

      <div className="border-b border-gray-200 mb-6">
        <nav className="flex space-x-4" aria-label="Onglets véhicule">
          {[
            { id: 'dashboard', label: 'Tableau de bord' },
            { id: 'maintenance', label: 'Entretiens' },
            { id: 'expenses', label: 'Dépenses' },
            { id: 'alerts', label: 'Alertes' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-3 px-4 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.id ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {activeTab === 'dashboard' && dashboard && (
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard title="Total véhicules" value={dashboard.totals.count_maintenance + 1} />
            <StatCard title="Entretiens" value={dashboard.totals.count_maintenance} />
            <StatCard title="Coût total" value={`${formatNumber(dashboard.totals.total_cost)} €`} />
            <StatCard title="Alertes critiques" value={dashboard.health.is_critical ? 'OUI' : 'NON'} />
          </div>
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="card">
              <h3 className="font-semibold mb-4">Répartition des coûts</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={Object.entries(dashboard.by_category).map(([name, value]) => ({ name, value }))}
                      cx="50%" cy="50%" innerRadius={60} outerRadius={100}
                      paddingAngle={2} dataKey="value"
                    >
                      {Object.keys(dashboard.by_category).map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Pie>
                    <Tooltip formatter={(v) => [`${formatNumber(v)} €`, '']} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="card">
              <h3 className="font-semibold mb-4">Évolution mensuelle</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={dashboard.by_month.labels.map((label, i) => ({ label, value: dashboard.by_month.values[i] }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                    <YAxis />
                    <Tooltip formatter={(v) => [`${formatNumber(v)} €`, '']} />
                    <Bar dataKey="value" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="card">
              <h3 className="font-semibold mb-4">Derniers entretiens</h3>
              <div className="space-y-2">
                {dashboard.recent_maintenance.slice(0, 5).map(m => (
                  <div key={m.id} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium">{m.maintenance_type_display}</p>
                      <p className="text-sm text-gray-500">{new Date(m.date).toLocaleDateString('fr-FR')} • {m.mileage_at_service.toLocaleString()} km</p>
                    </div>
                    <span className="font-medium">{m.cost ? `${formatNumber(m.cost)} €` : '—'}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="card">
              <h3 className="font-semibold mb-4">Dernières dépenses</h3>
              <div className="space-y-2">
                {dashboard.recent_expenses.slice(0, 5).map(e => (
                  <div key={e.id} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium">{e.category_name}</p>
                      <p className="text-sm text-gray-500">{new Date(e.date).toLocaleDateString('fr-FR')}</p>
                    </div>
                    <span className="font-medium">{formatNumber(e.amount)} €</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'maintenance' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Historique des entretiens</h2>
            <Link to={`/vehicles/${id}/maintenances/new`} className="btn-primary">Ajouter</Link>
          </div>
          <div className="card overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr className="text-left text-sm text-gray-500">
                  <th className="p-3">Date</th><th className="p-3">Type</th><th className="p-3">Km</th><th className="p-3">Coût</th><th className="p-3">Garage</th><th className="p-3">Prochaine échéance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {maintenances.map(m => (
                  <tr key={m.id} className="hover:bg-gray-50">
                    <td className="p-3 text-sm">{new Date(m.date).toLocaleDateString('fr-FR')}</td>
                    <td className="p-3 text-sm">{m.maintenance_type_display}</td>
                    <td className="p-3 text-sm">{m.mileage_at_service.toLocaleString()}</td>
                    <td className="p-3 text-sm">{m.cost ? `${formatNumber(m.cost)} €` : '—'}</td>
                    <td className="p-3 text-sm">{m.garage_name || '—'}</td>
                    <td className="p-3 text-sm">
                      {m.next_due_date && (
                        <StatusBadge status={new Date(m.next_due_date) < new Date() ? 'critical' : 'warning'} />
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'expenses' && expensesSummary && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Dépenses</h2>
            <Link to={`/vehicles/${id}/expenses/new`} className="btn-primary">Ajouter</Link>
          </div>
          <div className="grid gap-4 sm:grid-cols-4">
            <StatCard title="Total" value={`${formatNumber(expensesSummary.total)} €`} />
            <StatCard title="Ce mois" value={`${formatNumber(expensesSummary.current_month_total)} €`} />
            <StatCard title="Nombre" value={expensesSummary.count} />
            <StatCard title="Moyenne" value={`${formatNumber(expensesSummary.total / (expensesSummary.count || 1))} €`} />
          </div>
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="card">
              <h3 className="font-semibold mb-4">Par catégorie</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={Object.entries(expensesSummary.by_category).map(([name, value]) => ({ name, value }))} cx="50%" cy="50%" innerRadius={60} outerRadius={100} dataKey="value">
                      {Object.keys(expensesSummary.by_category).map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Pie>
                    <Tooltip formatter={(v) => [`${formatNumber(v)} €`, '']} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="card">
              <h3 className="font-semibold mb-4">Évolution mensuelle</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={Object.entries(expensesSummary.by_month).map(([month, value]) => ({ month, value }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                    <YAxis />
                    <Tooltip formatter={(v) => [`${formatNumber(v)} €`, '']} />
                    <Line type="monotone" dataKey="value" stroke="#0ea5e9" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
          <div className="card overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50"><tr className="text-left text-sm text-gray-500"><th className="p-3">Date</th><th className="p-3">Catégorie</th><th className="p-3">Description</th><th className="p-3 text-right">Montant</th></tr></thead>
              <tbody className="divide-y divide-gray-100">
                {expenses.map(e => (
                  <tr key={e.id} className="hover:bg-gray-50">
                    <td className="p-3 text-sm">{new Date(e.date).toLocaleDateString('fr-FR')}</td>
                    <td className="p-3 text-sm">{e.category_name}</td>
                    <td className="p-3 text-sm">{e.description || '—'}</td>
                    <td className="p-3 text-sm text-right font-medium">{formatNumber(e.amount)} €</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'alerts' && (
        <AlertsSection alerts={alerts} trackedItems={trackedItems} />
      )}
    </div>
  )
}

function formatNumber(n) {
  return new Intl.NumberFormat('fr-FR').format(n)
}