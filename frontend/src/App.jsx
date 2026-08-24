import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import { ProtectedRoute } from './hooks/useAuth'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import VehicleList from './pages/VehicleList'
import VehicleForm from './pages/VehicleForm'
import VehicleDetail from './pages/VehicleDetail'
import PartsCatalog from './pages/PartsCatalog'
import ReferenceList from './pages/ReferenceList'
import ReferenceDetail from './pages/ReferenceDetail'
import GarageDashboard from './pages/GarageDashboard'
import RepairOrderList from './pages/RepairOrderList'
import RepairOrderForm from './pages/RepairOrderForm'

function PublicRoute({ children }) {
  const { loading, isAuthenticated } = useAuth()
  if (loading) return <div className="min-h-screen flex items-center justify-center">Chargement...</div>
  if (isAuthenticated) return <Navigate to="/vehicles" replace />
  return children
}

function GarageRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="min-h-screen flex items-center justify-center">Chargement...</div>
  if (!user?.garage) return <Navigate to="/vehicles" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
      <Route element={<Layout />}>
        <Route path="/vehicles" element={<ProtectedRoute><VehicleList /></ProtectedRoute>} />
        <Route path="/vehicles/new" element={<ProtectedRoute><VehicleForm /></ProtectedRoute>} />
        <Route path="/vehicles/:id" element={<ProtectedRoute><VehicleDetail /></ProtectedRoute>} />
        <Route path="/vehicles/:id/edit" element={<ProtectedRoute><VehicleForm /></ProtectedRoute>} />
        <Route path="/parts" element={<ProtectedRoute><PartsCatalog /></ProtectedRoute>} />
        <Route path="/reference" element={<ProtectedRoute><ReferenceList /></ProtectedRoute>} />
        <Route path="/reference/:id" element={<ProtectedRoute><ReferenceDetail /></ProtectedRoute>} />
        <Route path="/garage" element={<GarageRoute><ProtectedRoute><GarageDashboard /></ProtectedRoute></GarageRoute>} />
        <Route path="/garage/repair-orders" element={<GarageRoute><ProtectedRoute><RepairOrderList /></ProtectedRoute></GarageRoute>} />
        <Route path="/garage/repair-orders/new" element={<GarageRoute><ProtectedRoute><RepairOrderForm /></ProtectedRoute></GarageRoute>} />
        <Route path="/garage/repair-orders/:id" element={<GarageRoute><ProtectedRoute><RepairOrderForm /></ProtectedRoute></GarageRoute>} />
        <Route path="/" element={<Navigate to="/vehicles" replace />} />
        <Route path="*" element={<Navigate to="/vehicles" replace />} />
      </Route>
    </Routes>
  )
}