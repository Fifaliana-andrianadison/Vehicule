import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { vehiclesApi } from '../api/endpoints'

const FUEL_TYPES = [
  { value: 'gasoline', label: 'Essence' },
  { value: 'diesel', label: 'Diesel' },
  { value: 'electric', label: 'Électrique' },
  { value: 'hybrid', label: 'Hybride' },
  { value: 'lpg', label: 'GPL' },
  { value: 'other', label: 'Autre' },
]
const VEHICLE_TYPES = [
  { value: 'car', label: 'Voiture' },
  { value: 'motorcycle', label: 'Moto' },
  { value: 'truck', label: 'Camion' },
  { value: 'van', label: 'Utilitaire' },
  { value: 'bus', label: 'Bus' },
  { value: 'other', label: 'Autre' },
]

export default function VehicleForm() {
  const { id } = useParams()
  const navigate = useNavigate()
  const isEdit = !!id

  const [form, setForm] = useState({
    name: '', brand: '', model: '', year: new Date().getFullYear(),
    vehicle_type: 'car', fuel_type: 'gasoline', vin: '',
    registration_number: '', mileage: 0, purchase_date: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [makes, setMakes] = useState([])
  const [models, setModels] = useState([])
  const [loadingMakes, setLoadingMakes] = useState(false)
  const [loadingModels, setLoadingModels] = useState(false)

  const loadMakes = async (type) => {
    setLoadingMakes(true)
    try {
      const { data } = await vehiclesApi.nhtsaMakes(type)
      setMakes(data.makes || [])
      if (!form.brand && data.makes?.length) {
        setForm({ ...form, brand: data.makes[0], model: '' })
      }
    } catch (err) {
      setMakes([])
    } finally {
      setLoadingMakes(false)
    }
  }

  const loadModels = async (make, type, year) => {
    if (!make || !type) { setModels([]); return }
    setLoadingModels(true)
    try {
      const { data } = await vehiclesApi.nhtsaModels(make, type, year)
      setModels(data.models || [])
      if (!form.model && data.models?.length) {
        setForm({ ...form, model: data.models[0] })
      }
    } catch (err) {
      setModels([])
    } finally {
      setLoadingModels(false)
    }
  }

  useEffect(() => {
    loadMakes(form.vehicle_type)
  }, [form.vehicle_type])

  useEffect(() => {
    if (form.brand && form.vehicle_type) {
      loadModels(form.brand, form.vehicle_type, form.year)
    }
  }, [form.brand, form.vehicle_type, form.year])

  if (isEdit) {
    useEffect(() => {
      vehiclesApi.get(id).then(r => {
        setForm(r.data)
        loadMakes(r.data.vehicle_type)
      }).catch(() => navigate('/vehicles'))
    }, [id])
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (isEdit) await vehiclesApi.update(id, form)
      else await vehiclesApi.create(form)
      navigate('/vehicles')
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la sauvegarde')
    } finally {
      setLoading(false)
    }
  }

  const handleVinDecode = async () => {
    if (!form.vin || form.vin.length < 10) return
    setLoading(true)
    try {
      const { data } = await vehiclesApi.nhtsaDecodeVin(form.vin)
      if (data?.brand) setForm(f => ({ ...f, brand: data.brand, model: data.model, year: data.year, vehicle_type: data.vehicle_type || f.vehicle_type, fuel_type: data.fuel_type || f.fuel_type }))
    } catch (err) {
      console.error('VIN decode failed:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{isEdit ? 'Modifier' : 'Ajouter'} un véhicule</h1>
        <p className="text-gray-500 mt-1">Les champs marqués <span className="text-red-500">*</span> sont obligatoires</p>
      </div>

      {error && <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">{error}</div>}

      <form onSubmit={handleSubmit} className="card space-y-6">
        {/* Section 1: Infos principales */}
        <fieldset className="space-y-4">
          <legend className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <span className="w-8 h-8 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center text-sm font-bold">1</span>
            Identification
          </legend>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nom <span className="text-red-500">*</span></label>
              <input value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="Ex: Ma Clio, Voiture de Pierre" required className="w-full" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Type <span className="text-red-500">*</span></label>
              <select value={form.vehicle_type} onChange={e => setForm({...form, vehicle_type: e.target.value, brand: '', model: ''})} required className="w-full">
                {VEHICLE_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Marque <span className="text-red-500">*</span></label>
              <select value={form.brand} onChange={e => { setForm({...form, brand: e.target.value, model: ''}) }} required disabled={loadingMakes} className="w-full">
                <option value="">-- Choisir --</option>
                {makes.map(m => <option key={m} value={m}>{m}</option>)}
              </select>
              {loadingMakes && <p className="text-xs text-gray-400 mt-1">Chargement des marques...</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Modèle <span className="text-red-500">*</span></label>
              <select value={form.model} onChange={e => setForm({...form, model: e.target.value})} required disabled={!models.length || loadingModels} className="w-full">
                <option value="">-- Choisir la marque d'abord --</option>
                {models.map(m => <option key={m} value={m}>{m}</option>)}
              </select>
              {loadingModels && <p className="text-xs text-gray-400 mt-1">Chargement des modèles...</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Année <span className="text-red-500">*</span></label>
              <input type="number" min="1900" max={new Date().getFullYear() + 1} value={form.year} onChange={e => setForm({...form, year: parseInt(e.target.value)})} required className="w-full" />
            </div>
          </div>
        </fieldset>

        {/* Section 2: Carburant & VIN */}
        <fieldset className="space-y-4">
          <legend className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <span className="w-8 h-8 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center text-sm font-bold">2</span>
            Caractéristiques techniques
          </legend>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Carburant <span className="text-red-500">*</span></label>
              <select value={form.fuel_type} onChange={e => setForm({...form, fuel_type: e.target.value})} required className="w-full">
                {FUEL_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">VIN (17 caractères)</label>
              <div className="flex gap-2">
                <input value={form.vin} onChange={e => setForm({...form, vin: e.target.value.toUpperCase()})} placeholder="VF1AAAAAA12345678" maxLength={17} className="flex-1 font-mono" />
                <button type="button" onClick={handleVinDecode} disabled={loading || !form.vin || form.vin.length < 10} className="btn-secondary whitespace-nowrap">
                  Décoder VIN
                </button>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Immatriculation</label>
              <input value={form.registration_number} onChange={e => setForm({...form, registration_number: e.target.value})} placeholder="AB-123-CD" className="w-full" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Kilométrage <span className="text-red-500">*</span></label>
              <input type="number" min="0" value={form.mileage} onChange={e => setForm({...form, mileage: parseInt(e.target.value) || 0})} required className="w-full" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date d'achat</label>
            <input type="date" value={form.purchase_date} onChange={e => setForm({...form, purchase_date: e.target.value})} className="w-full max-w-xs" />
          </div>
        </fieldset>

        {/* Actions */}
        <div className="flex justify-end space-x-3 pt-4 border-t">
          <button type="button" onClick={() => navigate(-1)} className="btn-secondary">Annuler</button>
          <button type="submit" disabled={loading} className="btn-primary px-6">
            {loading ? <span className="flex items-center gap-2"><svg className="animate-spin h-5 w-5" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>Sauvegarde...</span> : (isEdit ? 'Modifier' : 'Créer')}
          </button>
        </div>
      </form>
    </div>
  )
}