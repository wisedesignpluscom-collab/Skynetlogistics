import 'leaflet/dist/leaflet.css'
import '../../lib/leafletIcons'
import { MapContainer, Marker, Popup, TileLayer } from 'react-leaflet'
import type { Vehicle } from '../../types/vehicle'
import type { VehiclePosition } from '../../types/gps'

const DARK_TILES_URL = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
const DARK_TILES_ATTRIBUTION =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'

interface FleetMapProps {
  positions: VehiclePosition[]
  vehiclesById: Record<string, Vehicle>
}

export function FleetMap({ positions, vehiclesById }: FleetMapProps) {
  const center: [number, number] =
    positions.length > 0 ? [positions[0].lat, positions[0].lng] : [10.4806, -66.9036]

  return (
    <div className="h-[70vh] overflow-hidden rounded-lg border border-border">
      <MapContainer center={center} zoom={6} style={{ height: '100%', width: '100%' }}>
        <TileLayer url={DARK_TILES_URL} attribution={DARK_TILES_ATTRIBUTION} />
        {positions.map((pos) => {
          const vehicle = vehiclesById[pos.vehicle_id]
          return (
            <Marker key={pos.vehicle_id} position={[pos.lat, pos.lng]}>
              <Popup>
                <div className="text-sm">
                  <p className="font-semibold">{vehicle?.plate ?? pos.vehicle_id}</p>
                  {vehicle && (
                    <p>
                      {vehicle.brand} {vehicle.model}
                    </p>
                  )}
                  <p>Velocidad: {pos.speed_kmh ?? '—'} km/h</p>
                  <p>Odómetro: {pos.odometer_km?.toLocaleString() ?? '—'} km</p>
                  <p>Ignición: {pos.ignition_status === null ? '—' : pos.ignition_status ? 'encendida' : 'apagada'}</p>
                  <p>{new Date(pos.timestamp).toLocaleString()}</p>
                </div>
              </Popup>
            </Marker>
          )
        })}
      </MapContainer>
    </div>
  )
}
