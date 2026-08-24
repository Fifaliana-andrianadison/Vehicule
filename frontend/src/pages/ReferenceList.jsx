import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { referenceApi } from '../api/endpoints'

export default function ReferenceList() {
  const [refs, setRefs] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({ type: '', brand: '', q: '' })

  useEffect(() => { fetchRefs() }, [filters])

  const fetchRefs = async () => {
    setLoading(true)
    try {
      const { data } = await referenceApi.list(filters)
      setRefs(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Encyclopédie mécanique</h1>
      </div>

      <div className="card mb-6">
        <div className="grid gap-4 sm:grid-cols-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select value={filters.type} onChange={e => { setFilters({...filters, type: e.target.value}); fetchRefs() }}>
              <option value="">Tous</option>
              <option value="car">Voiture</option>
              <option value="motorcycle">Moto</option>
              <option value="truck">Camion</option>
              <option value="van">Utilitaire</option>
              <option value="bus">Bus</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Marque</label>
            <input type="text" placeholder="Renault, Peugeot..." value={filters.brand} onChange={e => { setFilters({...filters, brand: e.target.value}); fetchRefs() }} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Recherche</label>
            <input type="text" placeholder="Modèle..." value={filters.q} onChange={e => { setFilters({...filters, q: e.target.value}); fetchRefs() }} />
          </div>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-8 text-gray-500">Chargement...</div>
      ) : refs.length === 0 ? (
        <div className="card text-center py-12 text-gray-500">Aucune fiche trouvée</div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {refs.map(r => (
            <Link key={r.id} to={`/reference/${r.id}`} className="card hover:shadow-md transition-shadow block">
              <h3 className="font-semibold text-lg">{r.brand} {r.model}</h3>
              <p className="text-gray-500 text-sm capitalize">{r.type_display} • {r.year_start || ''}{r.year_end ? ` - ${r.year_end}` : ''}</p>
              <p className="text-gray-400 text-sm mt-1">{r.body_type || ''} {r.engine_info || ''}</p>
              <div className="mt-3 flex items-center justify-between text-sm text-gray-500">
                <span>{r.schedule_count} interventions</span>
                <span className="text-primary-600">Voir fiche →</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}