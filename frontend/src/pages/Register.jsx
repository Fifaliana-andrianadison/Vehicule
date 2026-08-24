import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { LogoIcon, UserIcon, EmailIcon, LockIcon, LoadingSpinner } from '../components/Icons'

const checkPasswordStrength = (pwd) => {
  let strength = 0
  if (pwd.length >= 8) strength++
  if (new RegExp('[A-Z]').test(pwd)) strength++
  if (new RegExp('[0-9]').test(pwd)) strength++
  if (new RegExp('[^A-Za-z0-9]').test(pwd)) strength++
  return strength
}

export default function Register() {
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    username: '',
    email: '',
    password: '',
    password2: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [passwordStrength, setPasswordStrength] = useState(0)
  const { register } = useAuth()
  const navigate = useNavigate()

  const handlePasswordChange = (e) => {
    const value = e.target.value
    setForm({...form, password: value})
    setPasswordStrength(checkPasswordStrength(value))
  }

  const getStrengthColor = () => {
    if (passwordStrength <= 1) return 'bg-red-500'
    if (passwordStrength <= 2) return 'bg-yellow-500'
    if (passwordStrength <= 3) return 'bg-blue-500'
    return 'bg-green-500'
  }

  const getStrengthLabel = () => {
    if (passwordStrength <= 1) return 'Très faible'
    if (passwordStrength <= 2) return 'Faible'
    if (passwordStrength <= 3) return 'Moyen'
    return 'Fort'
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (form.password !== form.password2) return setError('Les mots de passe ne correspondent pas')
    if (form.password.length < 8) return setError('Le mot de passe doit contenir au moins 8 caractères')
    setLoading(true)
    try {
      await register({
        username: form.username,
        email: form.email,
        password: form.password,
        first_name: form.first_name,
        last_name: form.last_name,
      })
      navigate('/vehicles')
    } catch (err) {
      setError(err.response?.data?.username?.[0] || err.response?.data?.email?.[0] || 'Erreur lors de l\'inscription')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-gray-50 px-4 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 mb-4">
            <LogoIcon />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Carnet</h1>
          <p className="text-gray-500 mt-1">Créez votre compte gratuit</p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-2 text-center">Inscription</h2>
          <p className="text-gray-500 text-center mb-6">Remplissez le formulaire pour créer votre compte</p>

          {error && (
            <div className="mb-6 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm flex items-center gap-2">
              <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 101.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-1.5">
                  Prénom <span className="text-red-500">*</span>
                </label>
                <input
                  id="first_name"
                  type="text"
                  value={form.first_name}
                  onChange={e => setForm({...form, first_name: e.target.value})}
                  required
                  autoComplete="given-name"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                  placeholder="Jean"
                />
              </div>
              <div>
                <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-1.5">
                  Nom <span className="text-red-500">*</span>
                </label>
                <input
                  id="last_name"
                  type="text"
                  value={form.last_name}
                  onChange={e => setForm({...form, last_name: e.target.value})}
                  required
                  autoComplete="family-name"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                  placeholder="Dupont"
                />
              </div>
            </div>

            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1.5">
                Nom d'utilisateur <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                  <UserIcon />
                </div>
                <input
                  id="username"
                  type="text"
                  value={form.username}
                  onChange={e => setForm({...form, username: e.target.value})}
                  required
                  autoComplete="username"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                  placeholder="monpseudo"
                />
              </div>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1.5">
                Email <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                  <EmailIcon />
                </div>
                <input
                  id="email"
                  type="email"
                  value={form.email}
                  onChange={e => setForm({...form, email: e.target.value})}
                  required
                  autoComplete="email"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                  placeholder="vous@email.com"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1.5">
                Mot de passe <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                  <LockIcon />
                </div>
                <input
                  id="password"
                  type="password"
                  value={form.password}
                  onChange={handlePasswordChange}
                  required
                  autoComplete="new-password"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                  placeholder="Min. 8 caractères"
                  minLength={8}
                />
              </div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                  <LockIcon />
                </div>
                <input
                  id="password"
                  type="password"
                  value={form.password}
                  onChange={handlePasswordChange}
                  required
                  autoComplete="new-password"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                  placeholder="Min. 8 caractères"
                  minLength={8}
                />
              </div>
              <p className="mt-2 text-xs text-gray-400">
                8+ caractères, majuscule, chiffre, caractère spécial recommandés
              </p>
            </div>
            </div>

            <div>
              <label htmlFor="password2" className="block text-sm font-medium text-gray-700 mb-1.5">
                Confirmer le mot de passe <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                  <LockIcon />
                </div>
                <input
                  id="password2"
                  type="password"
                  value={form.password2}
                  onChange={e => setForm({...form, password2: e.target.value})}
                  required
                  autoComplete="new-password"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                  placeholder="Confirmez votre mot de passe"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary py-3 text-base font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:shadow-lg"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <LoadingSpinner />
                  Création du compte...
                </span>
              ) : (
                'Créer mon compte'
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-600">
              Déjà un compte ?{' '}
              <Link to="/login" className="text-primary-600 font-medium hover:text-primary-700 hover:underline">
                Se connecter
              </Link>
            </p>
          </div>

          <div className="mt-6 pt-6 border-t border-gray-100">
            <p className="text-xs text-gray-400 text-center mb-3">En créant un compte, vous acceptez nos</p>
            <div className="flex justify-center gap-4 text-xs">
              <Link to="/terms" className="text-primary-600 hover:underline">Conditions d'utilisation</Link>
              <Link to="/privacy" className="text-primary-600 hover:underline">Politique de confidentialité</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

const getStrengthColor = () => {
  if (passwordStrength <= 1) return 'bg-red-500'
  if (passwordStrength <= 2) return 'bg-yellow-500'
  if (passwordStrength <= 3) return 'bg-blue-500'
  return 'bg-green-500'
}

const getStrengthLabel = () => {
  if (passwordStrength <= 1) return 'Très faible'
  if (passwordStrength <= 2) return 'Faible'
  if (passwordStrength <= 3) return 'Moyen'
  return 'Fort'
}

const handlePasswordChange = (e) => {
  const value = e.target.value
  setForm({...form, password: value})
  setPasswordStrength(checkPasswordStrength(value))
}

const handleSubmit = async (e) => {
  e.preventDefault()
  setError('')
  if (form.password !== form.password2) return setError('Les mots de passe ne correspondent pas')
  if (form.password.length < 8) return setError('Le mot de passe doit contenir au moins 8 caractères')
  setLoading(true)
  try {
    await register({
      username: form.username,
      email: form.email,
      password: form.password,
      first_name: form.first_name,
      last_name: form.last_name,
    })
    navigate('/vehicles')
  } catch (err) {
    setError(err.response?.data?.username?.[0] || err.response?.data?.email?.[0] || 'Erreur lors de l\'inscription')
  } finally {
    setLoading(false)
  }
}