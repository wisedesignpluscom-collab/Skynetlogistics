import 'leaflet/dist/leaflet.css'
import '../../lib/leafletIcons'
import { CircleMarker, MapContainer, Marker, Polyline, Popup, TileLayer } from 'react-leaflet'
import type { RoutePlan } from '../../types/route'
import type { VehiclePosition } from '../../types/gps'

const DARK_TILES_URL = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
const DARK_TILES_ATTRIBUTION =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'

interface TripRouteMapProps {
  plan: RoutePlan
  currentPosition: VehiclePosition | null
}

export function TripRouteMap({ plan, currentPosition }: TripRouteMapProps) {
  // geometry viene como [[lng, lat], ...] (GeoJSON); Leaflet usa [lat, lng].
  const path: [number, number][] = plan.geometry.map(([lng, lat]) => [lat, lng])
  const origin: [number, number] = [plan.origin_lat, plan.origin_lng]
  const destination: [number, number] = [plan.destination_lat, plan.destination_lng]

  return (
    <div className="h-[60vh] overflow-hidden rounded-lg border border-border">
      <MapContainer center={origin} zoom={9} style={{ height: '100%', width: '100%' }}>
        <TileLayer url={DARK_TILES_URL} attribution={DARK_TILES_ATTRIBUTION} />
        <Polyline positions={path} pathOptions={{ color: '#d4af37', weight: 4 }} />
        <Marker position={origin}>
          <Popup>Origen</Popup>
        </Marker>
        <Marker position={destination}>
          <Popup>Destino</Popup>
        </Marker>
        {currentPosition && (
          <CircleMarker
            center={[currentPosition.lat, currentPosition.lng]}
            radius={8}
            pathOptions={{ color: '#3b82f6', fillColor: '#3b82f6', fillOpacity: 0.9 }}
          >
            <Popup>
              Posición real del vehículo
              <br />
              {new Date(currentPosition.timestamp).toLocaleString()}
            </Popup>
          </CircleMarker>
        )}
      </MapContainer>
    </div>
  )
}
