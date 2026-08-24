import { useState, useEffect } from 'react'
import { partsApi, vehiclesApi } from '../api/endpoints'
import StatusBadge from '../components/StatusBadge'

export default function PartsCatalog() {
  const [parts, setParts] = useState([])
  const [categories, setCategories] = useState([])
  const [vehicles, setVehicles] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({ vehicle: '', category: '', q: '' })

  useEffect(() => {
    Promise.all([partsApi.categories(), vehiclesApi.list()]).then(([catRes, vehRes]) => {
      setCategories(catRes.data)
      setVehicles(vehRes.data)
      fetchParts()
    })
  }, [])

  const fetchParts = async () => {
    setLoading(true)
    try {
      const { data } = await partsApi.list(filters)
      setParts(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Catalogue de pièces</h1>
      </div>

      <div className="card mb-6">
        <div className="grid gap-4 sm:grid-cols-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Filtrer par véhicule</label>
            <select value={filters.vehicle} onChange={e => { setFilters({...filters, vehicle: e.target.value}); fetchParts() }}>
              <option value="">Tous mes véhicules</option>
              {vehicles.map(v => <option key={v.id} value={v.id}>{v.brand} {v.model} ({v.registration_number})</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Catégorie</label>
            <select value={filters.category} onChange={e => { setFilters({...filters, category: e.target.value}); fetchParts() }}>
              <option value="">Toutes</option>
              {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Recherche</label>
            <input type="text" placeholder="Nom, référence, marque..." value={filters.q} onChange={e => { setFilters({...filters, q: e.target.value}); fetchParts() }} />
          </div>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-8 text-gray-500">Chargement...</div>
      ) : parts.length === 0 ? (
        <div className="card text-center py-12 text-gray-500">Aucune pièce trouvée</div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {parts.map(p => (
            <div key={p.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold">{p.name}</h3>
                  <p className="text-sm text-gray-500">{p.brand} • {p.reference || 'Sans réf.'}</p>
                  <p className="text-sm text-gray-400">{p.category_name || 'Sans catégorie'}</p>
                  {p.price && <p className="text-lg font-bold text-primary-600 mt-1">{p.price} €</p>}
                </div>
                {filters.vehicle && (
                  <StatusBadge status={p.compatible ? 'up_to_date' : 'critical'} />
                )}
              </div>
              <p className="text-sm text-gray-500 mt-3 line-clamp-2">{p.description}</p>
              <div className="flex items-center justify-between mt-4 pt-3 border-t">
                <span className="text-xs text-gray-500">Type: {p.vehicle_type || 'Tous'}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}