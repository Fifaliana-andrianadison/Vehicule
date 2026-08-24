import { Link, useLocation, NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth()
  const location = useLocation()

  if (!isAuthenticated) return null

  const isGarage = user?.garage
  const navItems = isGarage
    ? [
        { to: '/garage', label: 'Tableau de bord' },
        { to: '/garage/repair-orders', label: 'Ordres de réparation' },
      ]
    : [
        { to: '/vehicles', label: 'Mes véhicules' },
        { to: '/parts', label: 'Catalogue pièces' },
        { to: '/reference', label: 'Encyclopédie' },
      ]

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to={isGarage ? '/garage' : '/vehicles'} className="text-xl font-bold text-primary-700">Carnet</Link>
          <div className="hidden md:flex space-x-4">
            {navItems.map(item => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive ? 'bg-primary-50 text-primary-700' : 'text-gray-600 hover:bg-gray-50'
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">{user?.first_name || user?.username}</span>
            <button onClick={logout} className="text-sm text-gray-600 hover:text-gray-900">Déconnexion</button>
          </div>
        </div>
      </div>
    </nav>
  )
}