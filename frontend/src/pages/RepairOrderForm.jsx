import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { garageApi, vehiclesApi, partsApi } from '../api/endpoints'
import StatusBadge from '../components/StatusBadge'

const STATUS_CHOICES = [
  { value: 'quote', label: 'Devis' },
  { value: 'in_progress', label: 'En cours' },
  { value: 'waiting_parts', label: 'Attente pièces' },
  { value: 'invoiced', label: 'Facturé' },
  { value: 'cancelled', label: 'Annulé' },
]

export default function RepairOrderForm() {
  const { id } = useParams()
  const navigate = useNavigate()
  const isEdit = !!id

  const [form, setForm] = useState({
    vehicle: '', title: '', description: '', status: 'quote',
    estimated_cost: '', total_cost: '',
    parts: [{ name: '', quantity: 1, unit_price: 0 }],
  })
  const [vehicles, setVehicles] = useState([])
  const [allParts, setAllParts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([vehiclesApi.list(), partsApi.list()])
      .then(([v, p]) => { setVehicles(v.data); setAllParts(p.data) })
  }, [])

  if (isEdit) {
    useEffect(() => {
      garageApi.getRepairOrder(id).then(r => {
        const o = r.data
        setForm({
          vehicle: o.vehicle, title: o.title, description: o.description, status: o.status,
          estimated_cost: o.estimated_cost || '', total_cost: o.total_cost || '',
          parts: o.parts.map(p => ({ id: p.id, part: p.part, name: p.name, quantity: p.quantity, unit_price: p.unit_price })),
        })
      })
    }, [id])
  }

  const addPart = () => setForm({ ...form, parts: [...form.parts, { name: '', quantity: 1, unit_price: 0 }] })
  const removePart = (idx) => setForm({ ...form, parts: form.parts.filter((_, i) => i !== idx) })
  const updatePart = (idx, field, value) => setForm({ ...form, parts: form.parts.map((p, i) => i === idx ? { ...p, [field]: value } : p) })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const payload = {
        vehicle: form.vehicle, title: form.title, description: form.description, status: form.status,
        estimated_cost: form.estimated_cost || null, total_cost: form.total_cost || null,
        parts: form.parts.map(p => ({ part: p.part || null, name: p.name, quantity: p.quantity, unit_price: p.unit_price })),
      }
      if (isEdit) await garageApi.updateRepairOrder(id, payload)
      else await garageApi.createRepairOrder(payload)
      navigate('/garage/repair-orders')
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur')
    } finally {
      setLoading(false)
    }
  }

  const partsTotal = form.parts.reduce((sum, p) => sum + (p.quantity * p.unit_price), 0)

  return (
    <div className="max-w-3xl">
      <h1 className="text-2xl font-bold mb-6">{isEdit ? 'Modifier' : 'Créer'} un ordre de réparation</h1>
      {error && <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">{error}</div>}
      <form onSubmit={handleSubmit} className="card space-y-6">
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Véhicule *</label>
            <select value={form.vehicle} onChange={e => setForm({...form, vehicle: e.target.value})} required>
              <option value="">-- Choisir --</option>
              {vehicles.map(v => <option key={v.id} value={v.id}>{v.brand} {v.model} ({v.registration_number})</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Statut</label>
            <select value={form.status} onChange={e => setForm({...form, status: e.target.value})}>
              {STATUS_CHOICES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
            </select>
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Titre *</label>
          <input value={form.title} onChange={e => setForm({...form, title: e.target.value})} required placeholder="Remplacement plaquettes avant" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea value={form.description} onChange={e => setForm({...form, description: e.target.value})} rows={3} />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Coût estimé (€)</label>
            <input type="number" step="0.01" min="0" value={form.estimated_cost} onChange={e => setForm({...form, estimated_cost: e.target.value})} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Coût total (€)</label>
            <input type="number" step="0.01" min="0" value={form.total_cost} onChange={e => setForm({...form, total_cost: e.target.value})} />
          </div>
        </div>

        <div className="border-t pt-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold">Pièces & main d'œuvre</h3>
            <button type="button" onClick={addPart} className="text-sm text-primary-600 hover:underline">+ Ajouter une ligne</button>
          </div>
          {form.parts.map((p, idx) => (
            <div key={idx} className="grid gap-2 sm:grid-cols-5 mb-3 p-3 bg-gray-50 rounded-lg">
              <div className="sm:col-span-2">
                <label className="block text-xs text-gray-500 mb-1">Pièce</label>
                <select value={p.part} onChange={e => updatePart(idx, 'part', e.target.value)}>
                  <option value="">— Choix libre —</option>
                  {allParts.map(part => <option key={part.id} value={part.id}>{part.name} ({part.reference})</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Nom</label>
                <input value={p.name} onChange={e => updatePart(idx, 'name', e.target.value)} placeholder="Plaquettes avant" />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Qté</label>
                <input type="number" min="1" value={p.quantity} onChange={e => updatePart(idx, 'quantity', parseInt(e.target.value) || 1)} />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Prix unitaire (€)</label>
                <input type="number" step="0.01" min="0" value={p.unit_price} onChange={e => updatePart(idx, 'unit_price', parseFloat(e.target.value) || 0)} />
              </div>
              {form.parts.length > 1 && (
                <button type="button" onClick={() => removePart(idx)} className="self-end text-red-600 hover:underline text-sm">Supprimer</button>
              )}
            </div>
          ))}
          <div className="text-right font-semibold text-lg pt-3 border-t">Total pièces : {partsTotal.toFixed(2)} €</div>
        </div>

        <div className="flex justify-end space-x-3 pt-4 border-t">
          <button type="button" onClick={() => navigate(-1)} className="btn-secondary">Annuler</button>
          <button type="submit" disabled={loading} className="btn-primary">{loading ? 'Sauvegarde...' : (isEdit ? 'Modifier' : 'Créer')}</button>
        </div>
      </form>
    </div>
  )
}