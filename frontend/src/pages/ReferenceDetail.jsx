import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { referenceApi, partsApi } from '../api/endpoints'
import StatusBadge from '../components/StatusBadge'

export default function ReferenceDetail() {
  const { id } = useParams()
  const [ref, setRef] = useState(null)
  const [schedule, setSchedule] = useState([])
  const [compatibleParts, setCompatibleParts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      referenceApi.get(id),
      referenceApi.schedule(id),
      referenceApi.parts(id),
    ]).then(([r, s, p]) => {
      setRef(r.data)
      setSchedule(s.data)
      setCompatibleParts(p.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [id])

  if (loading) return <div className="flex items-center justify-center h-64">Chargement...</div>
  if (!ref) return <div className="card text-red-600">Fiche introuvable</div>

  const INTERVENTION_LABELS = {
    oil_change: 'Vidange', brake: 'Freins', tire: 'Pneus', belt: 'Courroie',
    timing_belt: 'Distribution', battery: 'Batterie', filter: 'Filtres',
    clutch: 'Embrayage', suspension: 'Suspension', exhaust: 'Échappement',
    electric: 'Électrique', air_conditioning: 'Climatisation', cooling: 'Refroidissement', other: 'Autre',
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">{ref.brand} {ref.model}</h1>
      <div className="flex flex-wrap gap-2 text-sm text-gray-500">
        <span className="px-2 py-1 bg-gray-100 rounded">{ref.type_display}</span>
        {ref.year_start && <span>{ref.year_start}{ref.year_end ? ` - ${ref.year_end}` : ''}</span>}
        {ref.body_type && <span>{ref.body_type}</span>}
        {ref.engine_info && <span>{ref.engine_info}</span>}
      </div>
      {ref.description && <p className="text-gray-600">{ref.description}</p>}

      <div className="card">
        <h3 className="font-semibold mb-4">Plan d'entretien constructeur</h3>
        {schedule.length === 0 ? (
          <p className="text-gray-500">Aucun plan d'entretien défini</p>
        ) : (
          <div className="overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr className="text-left text-sm text-gray-500">
                  <th className="p-3">Intervention</th>
                  <th className="p-3">Libellé</th>
                  <th className="p-3">Intervalle km</th>
                  <th className="p-3">Intervalle mois</th>
                  <th className="p-3">Coût estimé</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {schedule.map(s => (
                  <tr key={s.id} className="hover:bg-gray-50">
                    <td className="p-3 text-sm">{INTERVENTION_LABELS[s.intervention_type] || s.intervention_type}</td>
                    <td className="p-3 text-sm">{s.label}</td>
                    <td className="p-3 text-sm">{s.interval_km ? s.interval_km.toLocaleString() : '—'}</td>
                    <td className="p-3 text-sm">{s.interval_months ? `${s.interval_months} mois` : '—'}</td>
                    <td className="p-3 text-sm">{s.cost_estimate ? `${s.cost_estimate} €` : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="card">
        <h3 className="font-semibold mb-4">Pièces compatibles (catalogue)</h3>
        {compatibleParts.length === 0 ? (
          <p className="text-gray-500">Aucune pièce dans le catalogue pour ce modèle</p>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {compatibleParts.map(p => (
              <div key={p.id} className="p-3 bg-gray-50 rounded-lg">
                <p className="font-medium">{p.name}</p>
                <p className="text-sm text-gray-500">{p.brand} • {p.reference || 'Sans réf.'}</p>
                {p.price && <p className="text-primary-600 font-semibold mt-1">{p.price} €</p>}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}