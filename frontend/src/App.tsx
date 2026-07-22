import type { ReactElement } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from './features/auth/AuthContext'
import { LoginPage } from './routes/LoginPage'
import { IncidentsPage } from './routes/IncidentsPage'
import { IncidentDetailPage } from './routes/IncidentDetailPage'
import { DeliveryGoodsPage } from './routes/DeliveryGoodsPage'
import { DeliveryGoodsDetailPage } from './routes/DeliveryGoodsDetailPage'
import { DeliveryOrdersPage } from './routes/DeliveryOrdersPage'
import { ConfigPage } from './routes/ConfigPage'
import { DriverHomePage } from './routes/driver/DriverHomePage'
import { DriverDeliveriesPage } from './routes/driver/DriverDeliveriesPage'
import { DriverChatPage } from './routes/driver/DriverChatPage'
import { DriverIncidentDetailPage } from './routes/driver/DriverIncidentDetailPage'
import { CompaniesPage } from './routes/CompaniesPage'
import { UsersPage } from './routes/UsersPage'
import { VehiclesPage } from './routes/VehiclesPage'
import { VehicleOwnersPage } from './routes/VehicleOwnersPage'
import { VehicleDetailPage } from './routes/VehicleDetailPage'
import { VehicleRoutePage } from './routes/VehicleRoutePage'
import { DriversPage } from './routes/DriversPage'
import { DriverDetailPage } from './routes/DriverDetailPage'
import { FatigueSettingsPage } from './routes/FatigueSettingsPage'
import { AlertsPage } from './routes/AlertsPage'
import { TripsPage } from './routes/TripsPage'
import { ClientsPage } from './routes/ClientsPage'
import { TripDetailPage } from './routes/TripDetailPage'
import { TripRoutePage } from './routes/TripRoutePage'
import { TripSettingsPage } from './routes/TripSettingsPage'
import { VrpOptimizationPage } from './routes/VrpOptimizationPage'
import { FleetMapPage } from './routes/FleetMapPage'
import { GPSSettingsPage } from './routes/GPSSettingsPage'
import { TiresPage } from './routes/TiresPage'
import { TireDetailPage } from './routes/TireDetailPage'
import { TireSettingsPage } from './routes/TireSettingsPage'
import { TirePerformancePage } from './routes/TirePerformancePage'
import { WarehousesPage } from './routes/WarehousesPage'
import { VehicleTiresPage } from './routes/VehicleTiresPage'
import { InventoryPage } from './routes/InventoryPage'
import { InventoryItemDetailPage } from './routes/InventoryItemDetailPage'

function ProtectedRoute({ children }: { children: ReactElement }) {
  const { user, driverId, isLoading } = useAuth()
  if (isLoading) return null
  if (!user) return <Navigate to="/login" replace />
  if (driverId) return <Navigate to="/driver" replace />
  return children
}

function DriverProtectedRoute({ children }: { children: ReactElement }) {
  const { user, driverId, isLoading } = useAuth()
  if (isLoading) return null
  if (!user) return <Navigate to="/login" replace />
  if (!driverId) return <Navigate to="/users" replace />
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
        path="/companies"
        element={
          <ProtectedRoute>
            <CompaniesPage />
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
        path="/vehicle-owners"
        element={
          <ProtectedRoute>
            <VehicleOwnersPage />
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
        path="/drivers/:driverId"
        element={
          <ProtectedRoute>
            <DriverDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/fatigue-settings"
        element={
          <ProtectedRoute>
            <FatigueSettingsPage />
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
        path="/clients"
        element={
          <ProtectedRoute>
            <ClientsPage />
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
        path="/trips/:tripId/route"
        element={
          <ProtectedRoute>
            <TripRoutePage />
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
        path="/trips-vrp"
        element={
          <ProtectedRoute>
            <VrpOptimizationPage />
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
      <Route
        path="/tires"
        element={
          <ProtectedRoute>
            <TiresPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/tires/:tireId"
        element={
          <ProtectedRoute>
            <TireDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/tire-settings"
        element={
          <ProtectedRoute>
            <TireSettingsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/tire-performance"
        element={
          <ProtectedRoute>
            <TirePerformancePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/warehouses"
        element={
          <ProtectedRoute>
            <WarehousesPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/vehicles/:vehicleId/tires"
        element={
          <ProtectedRoute>
            <VehicleTiresPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/inventory"
        element={
          <ProtectedRoute>
            <InventoryPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/inventory/:itemId"
        element={
          <ProtectedRoute>
            <InventoryItemDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/delivery-orders"
        element={
          <ProtectedRoute>
            <DeliveryOrdersPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/config"
        element={
          <ProtectedRoute>
            <ConfigPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/delivery-goods"
        element={
          <ProtectedRoute>
            <DeliveryGoodsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/delivery-goods/:goodsId"
        element={
          <ProtectedRoute>
            <DeliveryGoodsDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/incidents"
        element={
          <ProtectedRoute>
            <IncidentsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/incidents/:incidentId"
        element={
          <ProtectedRoute>
            <IncidentDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/driver"
        element={
          <DriverProtectedRoute>
            <DriverHomePage />
          </DriverProtectedRoute>
        }
      />
      <Route
        path="/driver/chat"
        element={
          <DriverProtectedRoute>
            <DriverChatPage />
          </DriverProtectedRoute>
        }
      />
      <Route
        path="/driver/deliveries"
        element={
          <DriverProtectedRoute>
            <DriverDeliveriesPage />
          </DriverProtectedRoute>
        }
      />
      <Route
        path="/driver/incidents/:incidentId"
        element={
          <DriverProtectedRoute>
            <DriverIncidentDetailPage />
          </DriverProtectedRoute>
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
