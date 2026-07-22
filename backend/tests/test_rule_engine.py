"""Tests del motor de reglas puro (Config-B) — sin DB, mismos casos que la gemela TS."""

from app.services.rule_engine import FormulaError, evaluate_condition, evaluate_formula

import pytest


CTX = {"type": "camion", "custom.categoria": "urbano", "year": 2015, "vacio_field": ""}


def test_condition_all_true() -> None:
    cond = {"match": "all", "conditions": [
        {"field": "type", "op": "igual", "value": "camion"},
        {"field": "custom.categoria", "op": "igual", "value": "urbano"},
    ]}
    assert evaluate_condition(cond, CTX) is True


def test_condition_all_one_false() -> None:
    cond = {"match": "all", "conditions": [
        {"field": "type", "op": "igual", "value": "camion"},
        {"field": "year", "op": "mayor", "value": 2020},
    ]}
    assert evaluate_condition(cond, CTX) is False


def test_condition_any() -> None:
    cond = {"match": "any", "conditions": [
        {"field": "type", "op": "igual", "value": "remolque"},
        {"field": "year", "op": "menor", "value": 2020},
    ]}
    assert evaluate_condition(cond, CTX) is True


def test_condition_operators() -> None:
    assert evaluate_condition({"conditions": [{"field": "vacio_field", "op": "vacio"}]}, CTX)
    assert evaluate_condition({"conditions": [{"field": "type", "op": "no_vacio"}]}, CTX)
    assert evaluate_condition({"conditions": [{"field": "type", "op": "en_lista", "value": "camion,cabezal"}]}, CTX)
    assert evaluate_condition({"conditions": [{"field": "type", "op": "contiene", "value": "cam"}]}, CTX)
    assert evaluate_condition({"conditions": [{"field": "year", "op": "menor_igual", "value": 2015}]}, CTX)
    assert not evaluate_condition({"conditions": [{"field": "year", "op": "mayor", "value": 2015}]}, CTX)


def test_empty_condition_is_true() -> None:
    assert evaluate_condition({}, CTX) is True
    assert evaluate_condition(None, CTX) is True
    assert evaluate_condition({"match": "all", "conditions": []}, CTX) is True


def test_numeric_op_with_non_numeric_is_false() -> None:
    assert evaluate_condition({"conditions": [{"field": "type", "op": "mayor", "value": 5}]}, CTX) is False


def test_formula_precedence_and_parens() -> None:
    ctx = {"a": 10, "b": 3, "custom.peso": "2.5"}
    assert evaluate_formula("a * b + 1", ctx) == 31.0
    assert evaluate_formula("(a + b) / 2", ctx) == 6.5
    assert evaluate_formula("custom.peso * 4", ctx) == 10.0


def test_formula_missing_ref_returns_none() -> None:
    assert evaluate_formula("missing + 1", {"a": 1}) is None


def test_formula_div_by_zero_is_zero() -> None:
    assert evaluate_formula("a / 0", {"a": 5}) == 0.0


def test_formula_empty_returns_none() -> None:
    assert evaluate_formula("", {}) is None
    assert evaluate_formula("   ", {}) is None


def test_formula_invalid_token_raises() -> None:
    with pytest.raises(FormulaError):
        evaluate_formula("a % b", {"a": 1, "b": 2})
