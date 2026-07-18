import 'leaflet/dist/leaflet.css'
import '../../lib/leafletIcons'
import { MapContainer, Marker, Polyline, Popup, TileLayer } from 'react-leaflet'
import type { VehiclePosition } from '../../types/gps'

const DARK_TILES_URL = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
const DARK_TILES_ATTRIBUTION =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'

interface RouteReplayMapProps {
  positions: VehiclePosition[]
}

export function RouteReplayMap({ positions }: RouteReplayMapProps) {
  if (positions.length === 0) {
    return (
      <div className="flex h-[70vh] items-center justify-center rounded-lg border border-border text-text-muted">
        No hay posiciones en el rango de fechas seleccionado.
      </div>
    )
  }

  const path: [number, number][] = positions.map((p) => [p.lat, p.lng])
  const first = positions[0]
  const last = positions[positions.length - 1]

  return (
    <div className="h-[70vh] overflow-hidden rounded-lg border border-border">
      <MapContainer center={path[0]} zoom={10} style={{ height: '100%', width: '100%' }}>
        <TileLayer url={DARK_TILES_URL} attribution={DARK_TILES_ATTRIBUTION} />
        <Polyline positions={path} pathOptions={{ color: '#d4af37', weight: 3 }} />
        <Marker position={[first.lat, first.lng]}>
          <Popup>Inicio · {new Date(first.timestamp).toLocaleString()}</Popup>
        </Marker>
        <Marker position={[last.lat, last.lng]}>
          <Popup>Fin · {new Date(last.timestamp).toLocaleString()}</Popup>
        </Marker>
      </MapContainer>
    </div>
  )
}
