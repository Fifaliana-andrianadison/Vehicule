import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export function ProtectedRoute({ children, roles }) {
  const { user, loading } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  if (loading) return <div className="min-h-screen flex items-center justify-center">Chargement...</div>
  if (!user) return navigate('/login', { state: { from: location }, replace: true })
  if (roles && !roles.includes(user.role)) return navigate('/', { replace: true })
  return children
}

export function useGarage() {
  const { user } = useAuth()
  return user?.garage || null
}