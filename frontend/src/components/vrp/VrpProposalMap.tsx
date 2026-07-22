import { Fragment } from 'react'
import 'leaflet/dist/leaflet.css'
import '../../lib/leafletIcons'
import { CircleMarker, MapContainer, Marker, Polyline, Popup, TileLayer } from 'react-leaflet'
import type { VrpProposedVehicle } from '../../types/vrp'

const DARK_TILES_URL = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
const DARK_TILES_ATTRIBUTION =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'

const VEHICLE_COLORS = ['#d4af37', '#3b82f6', '#10b981', '#ef4444', '#a855f7', '#f97316']

interface VrpProposalMapProps {
  proposal: VrpProposedVehicle[]
  vehicleStarts: Record<string, { lat: number; lng: number }>
  vehicleLabels: Record<string, string>
}

export function VrpProposalMap({ proposal, vehicleStarts, vehicleLabels }: VrpProposalMapProps) {
  const allStops = proposal.flatMap((p) => p.stops.map((s) => [s.lat, s.lng] as [number, number]))
  const center: [number, number] = allStops[0] ?? [10.5, -66.9]

  return (
    <div className="h-[60vh] overflow-hidden rounded-lg border border-border">
      <MapContainer center={center} zoom={8} style={{ height: '100%', width: '100%' }}>
        <TileLayer url={DARK_TILES_URL} attribution={DARK_TILES_ATTRIBUTION} />
        {proposal.map((p, i) => {
          const color = VEHICLE_COLORS[i % VEHICLE_COLORS.length]
          const start = vehicleStarts[p.vehicle_id]
          const path: [number, number][] = [
            ...(start ? [[start.lat, start.lng] as [number, number]] : []),
            ...p.stops.map((s) => [s.lat, s.lng] as [number, number]),
          ]
          return (
            <Fragment key={p.vehicle_id}>
              {path.length > 1 && <Polyline positions={path} pathOptions={{ color, weight: 4 }} />}
              {start && (
                <CircleMarker
                  center={[start.lat, start.lng]}
                  radius={8}
                  pathOptions={{ color, fillColor: color, fillOpacity: 0.9 }}
                >
                  <Popup>{vehicleLabels[p.vehicle_id] ?? 'Vehículo'} — posición actual</Popup>
                </CircleMarker>
              )}
              {p.stops.map((s, idx) => (
                <Marker key={idx} position={[s.lat, s.lng]}>
                  <Popup>
                    {vehicleLabels[p.vehicle_id] ?? 'Vehículo'} — parada {idx + 1}: {s.label}
                  </Popup>
                </Marker>
              ))}
            </Fragment>
          )
        })}
      </MapContainer>
    </div>
  )
}
