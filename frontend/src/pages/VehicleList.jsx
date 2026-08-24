import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { vehiclesApi } from '../api/endpoints'
import Navbar from '../components/Navbar'

export default function VehicleList() {
  const [vehicles, setVehicles] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const navigate = useNavigate()

  const fetch = async () => {
    try {
      const { data } = await vehiclesApi.list({ q: search })
      setVehicles(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetch() }, [search])

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Mes véhicules</h1>
        <Link to="/vehicles/new" className="btn-primary">Ajouter un véhicule</Link>
      </div>
      <div className="mb-4">
        <input
          type="text"
          placeholder="Rechercher (marque, modèle, nom)..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="w-full max-w-md"
        />
      </div>
      {loading ? (
        <div className="text-center py-8 text-gray-500">Chargement...</div>
      ) : vehicles.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500 mb-4">Aucun véhicule pour le moment</p>
          <Link to="/vehicles/new" className="btn-primary inline-block">Ajouter mon premier véhicule</Link>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {vehicles.map(v => (
            <Link key={v.id} to={`/vehicles/${v.id}`} className="card hover:shadow-md transition-shadow block">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-lg">{v.brand} {v.model}</h3>
                  <p className="text-gray-500 text-sm">{v.name} • {v.year} • {v.registration_number || 'Sans plaque'}</p>
                  <p className="text-gray-400 text-sm mt-1">{v.mileage.toLocaleString()} km</p>
                </div>
                {v.health && (
                  <StatusBadge status={v.health.overall_status} />
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

import StatusBadge from '../components/StatusBadge'