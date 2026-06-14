"""Testes para a camada de persistência (backend Supabase via cliente falso)."""

import pytest

from bifinance.models import DollarEntry, Goal, Settings, Transaction
from bifinance.storage import Storage
from tests.fake_supabase import FakeSupabaseClient


@pytest.fixture
def storage():
    return Storage(_client=FakeSupabaseClient())


def _tx(**kwargs) -> Transaction:
    defaults = dict(type="expense", description="Compra", amount=50.0, date="2026-04-10")
    return Transaction(**{**defaults, **kwargs})


def _dollar(**kwargs) -> DollarEntry:
    defaults = dict(date="2026-04-10", amount_usd=500.0, exchange_rate=5.0)
    return DollarEntry(**{**defaults, **kwargs})


def _goal(**kwargs) -> Goal:
    defaults = dict(name="Meta", target=1000.0, current=0.0)
    return Goal(**{**defaults, **kwargs})


# ── Transactions ──────────────────────────────────────────────────────────────


def test_transactions_load_empty(storage):
    assert storage.load_transactions() == []


def test_transaction_add_and_load(storage):
    t = _tx(description="Mercado", amount=120.0)
    storage.add_transaction(t)
    loaded = storage.load_transactions()
    assert len(loaded) == 1
    assert loaded[0].description == "Mercado"
    assert loaded[0].amount == 120.0


def test_transaction_add_multiple(storage):
    for i in range(4):
        storage.add_transaction(_tx(description=f"Item {i}"))
    assert len(storage.load_transactions()) == 4


def test_transaction_remove_existing(storage):
    t = _tx()
    storage.add_transaction(t)
    assert storage.remove_transaction(t.id) is True
    assert storage.load_transactions() == []


def test_transaction_remove_correct_item(storage):
    t1 = _tx(description="A")
    t2 = _tx(description="B")
    storage.add_transaction(t1)
    storage.add_transaction(t2)
    storage.remove_transaction(t1.id)
    remaining = storage.load_transactions()
    assert len(remaining) == 1
    assert remaining[0].description == "B"


def test_transaction_remove_nonexistent(storage):
    assert storage.remove_transaction("id-inexistente") is False


def test_transaction_persistence_across_instances():
    fake = FakeSupabaseClient()
    s1 = Storage(_client=fake)
    s1.add_transaction(_tx(description="Café", amount=5.50))
    s2 = Storage(_client=fake)
    loaded = s2.load_transactions()
    assert len(loaded) == 1
    assert loaded[0].description == "Café"


# ── Dollar Entries ────────────────────────────────────────────────────────────


def test_dollar_load_empty(storage):
    assert storage.load_dollar_entries() == []


def test_dollar_add_and_load(storage):
    e = _dollar(amount_usd=1000.0, exchange_rate=5.2)
    storage.add_dollar_entry(e)
    loaded = storage.load_dollar_entries()
    assert len(loaded) == 1
    assert loaded[0].amount_usd == pytest.approx(1000.0)
    assert loaded[0].exchange_rate == pytest.approx(5.2)


def test_dollar_remove_existing(storage):
    e = _dollar()
    storage.add_dollar_entry(e)
    assert storage.remove_dollar_entry(e.id) is True
    assert storage.load_dollar_entries() == []


def test_dollar_remove_nonexistent(storage):
    assert storage.remove_dollar_entry("id-inexistente") is False


def test_dollar_preserves_iof(storage):
    e = _dollar(iof_pct=1.5, spread_pct=2.0)
    storage.add_dollar_entry(e)
    loaded = storage.load_dollar_entries()[0]
    assert loaded.iof_pct == pytest.approx(1.5)
    assert loaded.spread_pct == pytest.approx(2.0)


# ── Goals ─────────────────────────────────────────────────────────────────────


def test_goals_load_empty(storage):
    assert storage.load_goals() == []


def test_goal_add_and_load(storage):
    g = _goal(name="Viagem", target=5000.0)
    storage.add_goal(g)
    loaded = storage.load_goals()
    assert len(loaded) == 1
    assert loaded[0].name == "Viagem"
    assert loaded[0].target == pytest.approx(5000.0)


def test_goal_update(storage):
    g = _goal(name="Fundo")
    storage.add_goal(g)
    g.current = 750.0
    storage.update_goal(g)
    loaded = storage.load_goals()[0]
    assert loaded.current == pytest.approx(750.0)


def test_goal_remove_existing(storage):
    g = _goal()
    storage.add_goal(g)
    assert storage.remove_goal(g.id) is True
    assert storage.load_goals() == []


def test_goal_remove_nonexistent(storage):
    assert storage.remove_goal("id-inexistente") is False


# ── Settings ──────────────────────────────────────────────────────────────────


def test_settings_defaults(storage):
    s = storage.load_settings()
    assert s.cdi_rate == pytest.approx(10.75)


def test_settings_save_and_load(storage):
    s = Settings(cdi_rate=12.5, default_iof_pct=2.0)
    storage.save_settings(s)
    loaded = storage.load_settings()
    assert loaded.cdi_rate == pytest.approx(12.5)
    assert loaded.default_iof_pct == pytest.approx(2.0)


# ── Prices ────────────────────────────────────────────────────────────────────


def test_prices_load_empty(storage):
    assert storage.load_prices() == {}


def test_prices_save_and_load(storage):
    prices = {"ITUB4": 28.50, "KNRI11": 105.0}
    storage.save_prices(prices)
    loaded = storage.load_prices()
    assert loaded["ITUB4"] == pytest.approx(28.50)
    assert loaded["KNRI11"] == pytest.approx(105.0)


def test_prices_overwrite(storage):
    storage.save_prices({"ITUB4": 28.0})
    storage.save_prices({"ITUB4": 30.0, "VALE3": 65.0})
    loaded = storage.load_prices()
    assert loaded["ITUB4"] == pytest.approx(30.0)
    assert "VALE3" in loaded


# ── Isolation: different collections don't interfere ─────────────────────────


def test_collections_isolated(storage):
    storage.add_transaction(_tx(description="TX"))
    storage.add_dollar_entry(_dollar(description="USD"))
    storage.add_goal(_goal(name="Meta"))
    assert len(storage.load_transactions()) == 1
    assert len(storage.load_dollar_entries()) == 1
    assert len(storage.load_goals()) == 1
