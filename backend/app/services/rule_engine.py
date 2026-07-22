"""Motor de reglas sin código (Config-B).

Dos funciones puras (sin DB, sin red) — mismo criterio que `custom_fields.py` y las fórmulas de
nómina/fatiga: se testean con datos fijos y tienen una gemela en TS (`frontend/src/features/config/
ruleEngine.ts`) con la MISMA semántica, para que una regla se evalúe idéntico en el cliente (reglas
de formulario en vivo) y en el backend (reglas de validación al guardar).

- `evaluate_condition(condition, context)` -> bool
- `evaluate_formula(expr, context)` -> float | None   (aritmética segura, sin `eval`)
"""

from typing import Any

CONDITION_OPS = (
    "igual",
    "distinto",
    "mayor",
    "menor",
    "mayor_igual",
    "menor_igual",
    "en_lista",
    "contiene",
    "vacio",
    "no_vacio",
)


def _as_number(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and value.strip() == "")


def _eval_single(field_value: Any, op: str, target: Any) -> bool:
    if op == "vacio":
        return _is_blank(field_value)
    if op == "no_vacio":
        return not _is_blank(field_value)
    if op == "igual":
        return str(field_value) == str(target)
    if op == "distinto":
        return str(field_value) != str(target)
    if op == "contiene":
        return target is not None and str(target) in str(field_value or "")
    if op == "en_lista":
        options = target if isinstance(target, list) else str(target).split(",")
        return str(field_value) in [str(o).strip() for o in options]
    # operadores numéricos
    a, b = _as_number(field_value), _as_number(target)
    if a is None or b is None:
        return False
    if op == "mayor":
        return a > b
    if op == "menor":
        return a < b
    if op == "mayor_igual":
        return a >= b
    if op == "menor_igual":
        return a <= b
    return False  # pragma: no cover - operador desconocido


def evaluate_condition(condition: dict[str, Any] | None, context: dict[str, Any]) -> bool:
    """Evalúa `{match: "all"|"any", conditions: [{field, op, value}]}` contra `context`
    (dict campo->valor, con los custom aplanados como `custom.<key>`). Una condición vacía o sin
    sub-condiciones se considera SIEMPRE verdadera (la regla aplica incondicionalmente)."""
    if not condition:
        return True
    conditions = condition.get("conditions") or []
    if not conditions:
        return True
    match = condition.get("match", "all")

    results = (
        _eval_single(context.get(c["field"]), c["op"], c.get("value"))
        for c in conditions
    )
    return all(results) if match == "all" else any(results)


# --- Evaluador de fórmulas aritméticas seguro (para la acción "calcular") ---
# Gramática mínima: números, referencias a campos (identificadores, incl. `custom.x`), + - * / y
# paréntesis. Se tokeniza y evalúa con shunting-yard — NUNCA `eval`, así "calcular" no ejecuta
# código arbitrario del usuario.

import re

_TOKEN_RE = re.compile(r"\s*(?:(\d+\.?\d*)|([A-Za-z_][A-Za-z0-9_.]*)|([-+*/()]))")
_PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2}


class FormulaError(ValueError):
    pass


def _tokenize(expr: str) -> list[tuple[str, str]]:
    tokens: list[tuple[str, str]] = []
    pos = 0
    while pos < len(expr):
        if expr[pos].isspace():
            pos += 1
            continue
        m = _TOKEN_RE.match(expr, pos)
        if not m or m.start() == m.end():
            raise FormulaError(f"Token inválido en la fórmula: {expr[pos:]}")
        num, ident, opsym = m.groups()
        if num is not None:
            tokens.append(("num", num))
        elif ident is not None:
            tokens.append(("ref", ident))
        else:
            tokens.append(("op", opsym))
        pos = m.end()
    return tokens


def evaluate_formula(expr: str, context: dict[str, Any]) -> float | None:
    """Evalúa una fórmula aritmética (`campoA * 2 + campoB`) resolviendo referencias desde
    `context`. Devuelve None si alguna referencia no es numérica (campo vacío) — la acción
    "calcular" simplemente no autocompleta en ese caso."""
    if not expr or not expr.strip():
        return None
    tokens = _tokenize(expr)

    output: list[float] = []
    ops: list[str] = []

    def apply_op() -> None:
        op = ops.pop()
        if len(output) < 2:
            raise FormulaError("Fórmula mal formada")
        b = output.pop()
        a = output.pop()
        if op == "+":
            output.append(a + b)
        elif op == "-":
            output.append(a - b)
        elif op == "*":
            output.append(a * b)
        elif op == "/":
            output.append(a / b if b != 0 else 0.0)

    for kind, val in tokens:
        if kind == "num":
            output.append(float(val))
        elif kind == "ref":
            ref = _as_number(context.get(val))
            if ref is None:
                return None
            output.append(ref)
        elif val == "(":
            ops.append(val)
        elif val == ")":
            while ops and ops[-1] != "(":
                apply_op()
            if not ops:
                raise FormulaError("Paréntesis desbalanceados")
            ops.pop()
        else:  # operador binario
            while ops and ops[-1] in _PRECEDENCE and _PRECEDENCE[ops[-1]] >= _PRECEDENCE[val]:
                apply_op()
            ops.append(val)

    while ops:
        if ops[-1] in "()":
            raise FormulaError("Paréntesis desbalanceados")
        apply_op()

    if len(output) != 1:
        raise FormulaError("Fórmula mal formada")
    return round(output[0], 6)
