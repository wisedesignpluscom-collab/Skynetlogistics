import type { AxleDualPosition, AxleSide, Tire } from '../../types/tire'
import type { VehicleType } from '../../types/vehicle'

export interface AxleSlot {
  axleNumber: number
  side: AxleSide
  dualPosition: AxleDualPosition
  tire: Tire | null
}

// Heurística de layout por defecto cuando el vehículo no tiene neumáticos instalados
// todavía: eje 1 direccional (una llanta por lado), resto doble rodado. Una vez que hay
// neumáticos instalados en un eje mayor al sugerido, el diagrama se extiende para mostrarlo.
const DEFAULT_AXLE_COUNT: Record<VehicleType, number> = { camion: 2, remolque: 2, cabezal: 2 }

export function buildAxleSlots(vehicleType: VehicleType, tires: Tire[]): AxleSlot[] {
  const maxInstalledAxle = tires.reduce((max, t) => Math.max(max, t.axle_number ?? 0), 0)
  const axleCount = Math.max(maxInstalledAxle, DEFAULT_AXLE_COUNT[vehicleType])

  const slots: AxleSlot[] = []
  for (let axleNumber = 1; axleNumber <= axleCount; axleNumber++) {
    const isDual = axleNumber > 1
    const sides: AxleSide[] = ['izquierdo', 'derecho']
    for (const side of sides) {
      const dualPositions: AxleDualPosition[] = isDual ? ['interior', 'exterior'] : ['unico']
      for (const dualPosition of dualPositions) {
        const tire =
          tires.find(
            (t) => t.axle_number === axleNumber && t.axle_side === side && t.axle_dual_position === dualPosition,
          ) ?? null
        slots.push({ axleNumber, side, dualPosition, tire })
      }
    }
  }
  return slots
}

interface VehicleAxleDiagramProps {
  vehicleType: VehicleType
  tires: Tire[]
  disparityThresholdMm: number
  onSlotClick: (slot: AxleSlot) => void
}

export function VehicleAxleDiagram({ vehicleType, tires, disparityThresholdMm, onSlotClick }: VehicleAxleDiagramProps) {
  const slots = buildAxleSlots(vehicleType, tires)
  const axleNumbers = [...new Set(slots.map((s) => s.axleNumber))].sort((a, b) => a - b)

  function isDisparate(slot: AxleSlot): boolean {
    if (!slot.tire) return false
    const partner = slots.find(
      (s) =>
        s.axleNumber === slot.axleNumber &&
        s.side === slot.side &&
        s.dualPosition !== slot.dualPosition &&
        s.tire !== null,
    )
    if (!partner?.tire) return false
    return Math.abs(slot.tire.current_thickness_mm - partner.tire.current_thickness_mm) > disparityThresholdMm
  }

  return (
    <div className="flex flex-col items-center gap-6 rounded-lg border border-border bg-background/40 p-6">
      {axleNumbers.map((axleNumber) => {
        const axleSlots = slots.filter((s) => s.axleNumber === axleNumber)
        const left = axleSlots.filter((s) => s.side === 'izquierdo')
        const right = axleSlots.filter((s) => s.side === 'derecho')
        return (
          <div key={axleNumber} className="flex w-full items-center justify-center gap-8">
            <div className="flex gap-1">
              {left.map((slot) => (
                <TireSlotButton
                  key={`${slot.side}-${slot.dualPosition}`}
                  slot={slot}
                  disparate={isDisparate(slot)}
                  onClick={() => onSlotClick(slot)}
                />
              ))}
            </div>
            <div className="flex h-8 w-16 items-center justify-center rounded bg-surface-hover text-[10px] text-text-muted">
              Eje {axleNumber}
            </div>
            <div className="flex gap-1">
              {right.map((slot) => (
                <TireSlotButton
                  key={`${slot.side}-${slot.dualPosition}`}
                  slot={slot}
                  disparate={isDisparate(slot)}
                  onClick={() => onSlotClick(slot)}
                />
              ))}
            </div>
          </div>
        )
      })}
      <p className="text-xs text-text-muted">Clic en una posición para instalar, desinstalar o enviar a reparación.</p>
    </div>
  )
}

function TireSlotButton({ slot, disparate, onClick }: { slot: AxleSlot; disparate: boolean; onClick: () => void }) {
  const base = 'flex h-16 w-14 flex-col items-center justify-center rounded border text-[10px] transition-colors'
  const stateClasses = slot.tire
    ? disparate
      ? 'border-danger bg-danger/15 text-danger'
      : 'border-gold/40 bg-gold/10 text-text hover:border-gold'
    : 'border-dashed border-border text-text-muted hover:border-gold hover:text-gold'
  return (
    <button
      type="button"
      onClick={onClick}
      className={`${base} ${stateClasses}`}
      title={slot.tire ? `${slot.tire.unique_code} · ${slot.tire.current_thickness_mm}mm` : 'Posición vacía'}
    >
      {slot.tire ? (
        <>
          <span className="max-w-full truncate px-1 font-medium">{slot.tire.unique_code}</span>
          <span>{slot.tire.current_thickness_mm}mm</span>
        </>
      ) : (
        <span className="text-lg leading-none">+</span>
      )}
    </button>
  )
}
