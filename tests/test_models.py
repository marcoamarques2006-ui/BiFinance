"""Testes para os modelos de dados."""

import pytest

from bifinance.models import (
    ASSET_TYPES,
    EXPENSE_CATEGORIES,
    INCOME_CATEGORIES,
    DollarEntry,
    Goal,
    Settings,
    Transaction,
)

# ── Transaction ───────────────────────────────────────────────────────────────


def _tx(**kwargs) -> Transaction:
    defaults = dict(type="expense", description="Mercado", amount=100.0, date="2026-04-10")
    return Transaction(**{**defaults, **kwargs})


def _buy(**kwargs) -> Transaction:
    defaults = dict(
        type="investment_buy", description="Compra ITUB4", amount=10_000.0,
        date="2026-01-10", ticker="ITUB4", quantity=100.0,
    )
    return Transaction(**{**defaults, **kwargs})


def test_transaction_creation():
    t = _tx()
    assert t.description == "Mercado"
    assert t.amount == 100.0
    assert t.type == "expense"
    assert t.date == "2026-04-10"
    assert t.id  # UUID gerado automaticamente


def test_transaction_unique_ids():
    assert _tx().id != _tx().id


def test_transaction_to_dict():
    t = _tx(id="fixed-id", category="Alimentação")
    d = t.to_dict()
    assert d["id"] == "fixed-id"
    assert d["type"] == "expense"
    assert d["description"] == "Mercado"
    assert d["amount"] == 100.0
    assert d["category"] == "Alimentação"


def test_transaction_from_dict():
    data = {
        "id": "abc", "type": "income", "description": "Salário",
        "amount": 5000.0, "date": "2026-04-05",
    }
    t = Transaction.from_dict(data)
    assert t.id == "abc"
    assert t.type == "income"
    assert t.description == "Salário"
    assert t.amount == 5000.0


def test_transaction_roundtrip():
    original = _buy(id="fixed")
    restored = Transaction.from_dict(original.to_dict())
    assert restored.id == original.id
    assert restored.type == original.type
    assert restored.ticker == original.ticker
    assert restored.quantity == original.quantity
    assert restored.amount == original.amount


def test_transaction_validate_ok():
    _tx().validate()  # não deve lançar


def test_transaction_validate_investment_ok():
    _buy().validate()  # não deve lançar


def test_transaction_validate_empty_description():
    with pytest.raises(ValueError, match="Descrição"):
        _tx(description="").validate()


def test_transaction_validate_zero_amount():
    with pytest.raises(ValueError, match="Valor"):
        _tx(amount=0.0).validate()


def test_transaction_validate_negative_amount():
    with pytest.raises(ValueError, match="Valor"):
        _tx(amount=-10.0).validate()


def test_transaction_validate_investment_requires_ticker():
    with pytest.raises(ValueError, match="Ticker"):
        Transaction(
            type="investment_buy", description="X", amount=100.0, date="2026-01-01",
            ticker=None, quantity=10.0,
        ).validate()


def test_transaction_validate_investment_requires_quantity():
    with pytest.raises(ValueError, match="Quantidade"):
        Transaction(
            type="investment_buy", description="X", amount=100.0, date="2026-01-01",
            ticker="ITUB4", quantity=0.0,
        ).validate()


def test_expense_categories_not_empty():
    assert len(EXPENSE_CATEGORIES) > 0


def test_income_categories_not_empty():
    assert len(INCOME_CATEGORIES) > 0


def test_asset_types_not_empty():
    assert len(ASSET_TYPES) > 0


# ── DollarEntry ───────────────────────────────────────────────────────────────


def _dollar(**kwargs) -> DollarEntry:
    defaults = dict(date="2026-04-10", amount_usd=1000.0, exchange_rate=5.0)
    return DollarEntry(**{**defaults, **kwargs})


def test_dollar_total_cost_brl_no_fees():
    """Sem IOF e spread: custo = usd * taxa."""
    entry = _dollar(iof_pct=0.0, spread_pct=0.0)
    assert entry.total_cost_brl == pytest.approx(5000.0)


def test_dollar_total_cost_brl_with_iof():
    """Com IOF 1.1%: custo = usd * taxa * 1.011."""
    entry = _dollar(iof_pct=1.1, spread_pct=0.0)
    assert entry.total_cost_brl == pytest.approx(5000.0 * 1.011)


def test_dollar_total_cost_brl_with_spread():
    """Com spread 2%: custo = usd * taxa * 1.02."""
    entry = _dollar(iof_pct=0.0, spread_pct=2.0)
    assert entry.total_cost_brl == pytest.approx(5000.0 * 1.02)


def test_dollar_total_cost_brl_combined():
    """IOF 1.1% + spread 2%: custo = usd * taxa * 1.031."""
    entry = _dollar(iof_pct=1.1, spread_pct=2.0)
    assert entry.total_cost_brl == pytest.approx(5000.0 * 1.031)


def test_dollar_effective_rate():
    entry = _dollar(iof_pct=1.1, spread_pct=0.0)
    expected = entry.total_cost_brl / entry.amount_usd
    assert entry.effective_rate == pytest.approx(expected)


def test_dollar_effective_rate_zero_amount():
    entry = _dollar(amount_usd=0.0)
    assert entry.effective_rate == 0.0


def test_dollar_roundtrip():
    original = _dollar(id="fixed", description="Dólar viagem")
    restored = DollarEntry.from_dict(original.to_dict())
    assert restored.id == original.id
    assert restored.amount_usd == original.amount_usd
    assert restored.exchange_rate == original.exchange_rate
    assert restored.iof_pct == original.iof_pct


def test_dollar_validate_ok():
    _dollar().validate()


def test_dollar_validate_zero_usd():
    with pytest.raises(ValueError, match="USD"):
        _dollar(amount_usd=0.0).validate()


def test_dollar_validate_zero_rate():
    with pytest.raises(ValueError, match="câmbio"):
        _dollar(exchange_rate=0.0).validate()


def test_dollar_validate_negative_iof():
    with pytest.raises(ValueError, match="IOF"):
        _dollar(iof_pct=-1.0).validate()


# ── Goal ──────────────────────────────────────────────────────────────────────


def _goal(**kwargs) -> Goal:
    defaults = dict(name="Viagem", target=5000.0, current=2500.0)
    return Goal(**{**defaults, **kwargs})


def test_goal_progress_half():
    g = _goal(target=5000.0, current=2500.0)
    assert g.progress == pytest.approx(0.5)


def test_goal_progress_complete():
    g = _goal(target=5000.0, current=6000.0)
    assert g.progress == 1.0  # capped at 1.0


def test_goal_progress_zero():
    g = _goal(target=5000.0, current=0.0)
    assert g.progress == 0.0


def test_goal_remaining():
    g = _goal(target=5000.0, current=2000.0)
    assert g.remaining == pytest.approx(3000.0)


def test_goal_remaining_complete():
    g = _goal(target=5000.0, current=6000.0)
    assert g.remaining == 0.0  # capped at 0


def test_goal_roundtrip():
    original = _goal(id="fixed", deadline="2026-12-31", color="#22c55e")
    restored = Goal.from_dict(original.to_dict())
    assert restored.id == original.id
    assert restored.name == original.name
    assert restored.target == original.target
    assert restored.current == original.current
    assert restored.deadline == original.deadline
    assert restored.color == original.color


def test_goal_validate_ok():
    _goal().validate()


def test_goal_validate_empty_name():
    with pytest.raises(ValueError, match="Nome"):
        _goal(name="").validate()


def test_goal_validate_zero_target():
    with pytest.raises(ValueError, match="alvo"):
        _goal(target=0.0).validate()


def test_goal_validate_negative_current():
    with pytest.raises(ValueError, match="negativo"):
        _goal(current=-1.0).validate()


# ── Settings ──────────────────────────────────────────────────────────────────


def test_settings_defaults():
    s = Settings()
    assert s.cdi_rate == pytest.approx(10.75)
    assert s.default_iof_pct == pytest.approx(1.1)


def test_settings_roundtrip():
    original = Settings(cdi_rate=12.0, default_iof_pct=2.0)
    restored = Settings.from_dict(original.to_dict())
    assert restored.cdi_rate == pytest.approx(12.0)
    assert restored.default_iof_pct == pytest.approx(2.0)


def test_settings_from_empty_dict_uses_defaults():
    s = Settings.from_dict({})
    assert s.cdi_rate == pytest.approx(10.75)
