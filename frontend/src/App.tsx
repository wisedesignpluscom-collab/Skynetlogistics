import type { ReactElement } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from './features/auth/AuthContext'
import { LoginPage } from './routes/LoginPage'
import { UsersPage } from './routes/UsersPage'
import { VehiclesPage } from './routes/VehiclesPage'
import { VehicleDetailPage } from './routes/VehicleDetailPage'
import { VehicleRoutePage } from './routes/VehicleRoutePage'
import { DriversPage } from './routes/DriversPage'
import { AlertsPage } from './routes/AlertsPage'
import { TripsPage } from './routes/TripsPage'
import { TripDetailPage } from './routes/TripDetailPage'
import { TripSettingsPage } from './routes/TripSettingsPage'
import { FleetMapPage } from './routes/FleetMapPage'
import { GPSSettingsPage } from './routes/GPSSettingsPage'

function ProtectedRoute({ children }: { children: ReactElement }) {
  const { user, isLoading } = useAuth()
  if (isLoading) return null
  if (!user) return <Navigate to="/login" replace />
  return children
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/users"
        element={
          <ProtectedRoute>
            <UsersPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/vehicles"
        element={
          <ProtectedRoute>
            <VehiclesPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/vehicles/:vehicleId"
        element={
          <ProtectedRoute>
            <VehicleDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/vehicles/:vehicleId/route"
        element={
          <ProtectedRoute>
            <VehicleRoutePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/drivers"
        element={
          <ProtectedRoute>
            <DriversPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/alerts"
        element={
          <ProtectedRoute>
            <AlertsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/trips"
        element={
          <ProtectedRoute>
            <TripsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/trips/:tripId"
        element={
          <ProtectedRoute>
            <TripDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/trip-settings"
        element={
          <ProtectedRoute>
            <TripSettingsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/gps-map"
        element={
          <ProtectedRoute>
            <FleetMapPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/gps-settings"
        element={
          <ProtectedRoute>
            <GPSSettingsPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/users" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  )
}
