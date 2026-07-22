// Gemelo TS del motor de reglas del backend (app/services/rule_engine.py). MISMA semántica: una
// regla debe evaluarse idéntico en el cliente (reglas de formulario en vivo) y en el backend
// (reglas de validación al guardar). Si cambias uno, cambia el otro y sus tests.

export type ConditionOp =
  | 'igual'
  | 'distinto'
  | 'mayor'
  | 'menor'
  | 'mayor_igual'
  | 'menor_igual'
  | 'en_lista'
  | 'contiene'
  | 'vacio'
  | 'no_vacio'

export interface RuleConditionItem {
  field: string
  op: ConditionOp
  value?: unknown
}

export interface RuleCondition {
  match: 'all' | 'any'
  conditions: RuleConditionItem[]
}

export type RuleContext = Record<string, unknown>

function asNumber(value: unknown): number | null {
  if (value === '' || value === null || value === undefined) return null
  const n = Number(value)
  return Number.isNaN(n) ? null : n
}

function isBlank(value: unknown): boolean {
  return value === null || value === undefined || (typeof value === 'string' && value.trim() === '')
}

function evalSingle(fieldValue: unknown, op: ConditionOp, target: unknown): boolean {
  switch (op) {
    case 'vacio':
      return isBlank(fieldValue)
    case 'no_vacio':
      return !isBlank(fieldValue)
    case 'igual':
      return String(fieldValue) === String(target)
    case 'distinto':
      return String(fieldValue) !== String(target)
    case 'contiene':
      return target != null && String(fieldValue ?? '').includes(String(target))
    case 'en_lista': {
      const options = Array.isArray(target) ? target : String(target).split(',')
      return options.map((o) => String(o).trim()).includes(String(fieldValue))
    }
    default: {
      const a = asNumber(fieldValue)
      const b = asNumber(target)
      if (a === null || b === null) return false
      if (op === 'mayor') return a > b
      if (op === 'menor') return a < b
      if (op === 'mayor_igual') return a >= b
      if (op === 'menor_igual') return a <= b
      return false
    }
  }
}

export function evaluateCondition(condition: RuleCondition | null | undefined, context: RuleContext): boolean {
  if (!condition) return true
  const conditions = condition.conditions ?? []
  if (conditions.length === 0) return true
  const results = conditions.map((c) => evalSingle(context[c.field], c.op, c.value))
  return condition.match === 'any' ? results.some(Boolean) : results.every(Boolean)
}

// --- Evaluador de fórmulas aritméticas seguro (acción "calcular"), sin eval ---

const TOKEN_RE = /\s*(?:(\d+\.?\d*)|([A-Za-z_][A-Za-z0-9_.]*)|([-+*/()]))/y
const PRECEDENCE: Record<string, number> = { '+': 1, '-': 1, '*': 2, '/': 2 }

type Token = { kind: 'num' | 'ref' | 'op'; val: string }

function tokenize(expr: string): Token[] {
  const tokens: Token[] = []
  let pos = 0
  while (pos < expr.length) {
    if (/\s/.test(expr[pos])) {
      pos += 1
      continue
    }
    TOKEN_RE.lastIndex = pos
    const m = TOKEN_RE.exec(expr)
    if (!m || m.index !== pos || m[0].length === 0) return [] // token inválido -> fórmula vacía
    if (m[1] !== undefined) tokens.push({ kind: 'num', val: m[1] })
    else if (m[2] !== undefined) tokens.push({ kind: 'ref', val: m[2] })
    else tokens.push({ kind: 'op', val: m[3] })
    pos = TOKEN_RE.lastIndex
  }
  return tokens
}

/** Evalúa `campoA * 2 + campoB` resolviendo referencias desde `context`. Devuelve null si alguna
 *  referencia no es numérica o la fórmula es inválida (la acción "calcular" no autocompleta). */
export function evaluateFormula(expr: string, context: RuleContext): number | null {
  if (!expr || !expr.trim()) return null
  const tokens = tokenize(expr)
  if (tokens.length === 0) return null

  const output: number[] = []
  const ops: string[] = []

  const applyOp = (): boolean => {
    const op = ops.pop()!
    if (output.length < 2) return false
    const b = output.pop()!
    const a = output.pop()!
    if (op === '+') output.push(a + b)
    else if (op === '-') output.push(a - b)
    else if (op === '*') output.push(a * b)
    else if (op === '/') output.push(b !== 0 ? a / b : 0)
    return true
  }

  for (const t of tokens) {
    if (t.kind === 'num') output.push(Number(t.val))
    else if (t.kind === 'ref') {
      const ref = asNumber(context[t.val])
      if (ref === null) return null
      output.push(ref)
    } else if (t.val === '(') ops.push(t.val)
    else if (t.val === ')') {
      while (ops.length && ops[ops.length - 1] !== '(') if (!applyOp()) return null
      if (!ops.length) return null
      ops.pop()
    } else {
      while (ops.length && PRECEDENCE[ops[ops.length - 1]] >= PRECEDENCE[t.val]) if (!applyOp()) return null
      ops.push(t.val)
    }
  }
  while (ops.length) {
    if (ops[ops.length - 1] === '(' || ops[ops.length - 1] === ')') return null
    if (!applyOp()) return null
  }
  if (output.length !== 1) return null
  return Math.round(output[0] * 1e6) / 1e6
}
