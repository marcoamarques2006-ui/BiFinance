"""Testes para a lógica de negócio (finance.py)."""

import pytest

from bifinance.finance import (
    available_cash,
    dollar_summary,
    expenses_by_category,
    fmt_brl,
    fmt_pct,
    monthly_expenses,
    monthly_history,
    monthly_income,
    portfolio_positions,
    small_vices,
    total_dividends,
    total_invested_cost,
    total_real_expenses,
    total_real_income,
    with_pnl,
)
from bifinance.models import DollarEntry, Transaction

# ── Helpers ───────────────────────────────────────────────────────────────────


def _tx(type_, amount, date="2026-01-15", **kwargs) -> Transaction:
    return Transaction(type=type_, description=kwargs.pop("description", type_),
                       amount=amount, date=date, **kwargs)


def _income(amount, date="2026-01-05") -> Transaction:
    return _tx("income", amount, date, description="Salário")


def _expense(amount, date="2026-01-10", category="Alimentação", description="Mercado") -> Transaction:
    return _tx("expense", amount, date, description=description, category=category)


def _buy(ticker, amount, qty, date="2026-01-20") -> Transaction:
    return _tx("investment_buy", amount, date, description=f"Compra {ticker}",
               ticker=ticker, quantity=qty, asset_type="Ação")


def _sell(ticker, amount, qty, date="2026-02-10") -> Transaction:
    return _tx("investment_sell", amount, date, description=f"Venda {ticker}",
               ticker=ticker, quantity=qty, asset_type="Ação")


def _dividend(ticker, amount, date="2026-02-20") -> Transaction:
    return _tx("dividend", amount, date, description=f"Provento {ticker}", ticker=ticker)


# ── Regra de negócio central: investimento ≠ despesa ─────────────────────────


def test_investment_not_counted_as_expense():
    """
    Usuário gasta R$10k em ações, vende por R$15k, compra R$10k em FIIs.
    Despesas reais devem ser R$0 — não R$20k.
    """
    txs = [
        _buy("ITUB4", 10_000, 100),
        _sell("ITUB4", 15_000, 100),
        _buy("KNRI11", 10_000, 50),
    ]
    assert total_real_expenses(txs) == 0.0
    assert total_real_expenses(txs) != 20_000.0


def test_expense_only_counts_type_expense():
    txs = [
        _income(5000),
        _expense(200),
        _buy("PETR4", 3000, 50),
        _dividend("PETR4", 100),
    ]
    assert total_real_expenses(txs) == pytest.approx(200.0)


def test_income_only_counts_real_income():
    txs = [
        _income(5000),
        _expense(200),
        _buy("PETR4", 3000, 50),
        _dividend("PETR4", 100),
    ]
    assert total_real_income(txs) == pytest.approx(5100.0)  # income + dividend


def test_dividends_counted_separately():
    txs = [_income(5000), _dividend("KNRI11", 300), _dividend("XPML11", 150)]
    assert total_dividends(txs) == pytest.approx(450.0)


# ── Caixa disponível ──────────────────────────────────────────────────────────


def test_available_cash_income_minus_expense():
    txs = [_income(5000), _expense(500)]
    assert available_cash(txs) == pytest.approx(4500.0)


def test_available_cash_buy_reduces_cash():
    txs = [_income(10_000), _buy("ITUB4", 3000, 100)]
    assert available_cash(txs) == pytest.approx(7000.0)


def test_available_cash_sell_increases_cash():
    txs = [_income(10_000), _buy("ITUB4", 3000, 100), _sell("ITUB4", 4000, 100)]
    assert available_cash(txs) == pytest.approx(11_000.0)


def test_available_cash_dividend_increases_cash():
    txs = [_income(5000), _dividend("FII", 300)]
    assert available_cash(txs) == pytest.approx(5300.0)


def test_available_cash_empty():
    assert available_cash([]) == 0.0


# ── Resumos mensais ───────────────────────────────────────────────────────────


def test_monthly_income_correct_month():
    txs = [
        Transaction(type="income", description="Jan", amount=3000.0, date="2026-01-05"),
        Transaction(type="income", description="Feb", amount=4000.0, date="2026-02-05"),
    ]
    assert monthly_income(txs, 2026, 1) == pytest.approx(3000.0)
    assert monthly_income(txs, 2026, 2) == pytest.approx(4000.0)


def test_monthly_expenses_correct_month():
    txs = [
        _expense(100, date="2026-01-10"),
        _expense(200, date="2026-02-10"),
    ]
    assert monthly_expenses(txs, 2026, 1) == pytest.approx(100.0)
    assert monthly_expenses(txs, 2026, 2) == pytest.approx(200.0)


def test_monthly_history_returns_n_months():
    history = monthly_history([], n=6)
    assert len(history) == 6


def test_monthly_history_has_required_keys():
    history = monthly_history([], n=3)
    for entry in history:
        assert "month" in entry
        assert "income" in entry
        assert "expenses" in entry


def test_expenses_by_category():
    txs = [
        _expense(100, category="Alimentação"),
        _expense(200, category="Alimentação"),
        _expense(150, category="Transporte"),
    ]
    by_cat = expenses_by_category(txs, 2026, 1)
    assert by_cat["Alimentação"] == pytest.approx(300.0)
    assert by_cat["Transporte"] == pytest.approx(150.0)


def test_expenses_by_category_excludes_investments():
    txs = [
        _expense(100, category="Alimentação"),
        _buy("ITUB4", 5000, 100),
    ]
    by_cat = expenses_by_category(txs, 2026, 1)
    assert "Alimentação" in by_cat
    assert len(by_cat) == 1


# ── Portfolio: custo médio ponderado ─────────────────────────────────────────


def test_portfolio_buy_creates_position():
    txs = [_buy("ITUB4", 10_000, 100)]
    pos = portfolio_positions(txs)
    assert "ITUB4" in pos
    assert pos["ITUB4"]["quantity"] == pytest.approx(100.0)
    assert pos["ITUB4"]["total_cost"] == pytest.approx(10_000.0)
    assert pos["ITUB4"]["avg_cost"] == pytest.approx(100.0)


def test_portfolio_buy_twice_averages_cost():
    txs = [
        _buy("ITUB4", 10_000, 100, date="2026-01-10"),  # R$100/un
        _buy("ITUB4", 5_000, 25, date="2026-02-10"),    # R$200/un
    ]
    pos = portfolio_positions(txs)
    assert pos["ITUB4"]["quantity"] == pytest.approx(125.0)
    assert pos["ITUB4"]["total_cost"] == pytest.approx(15_000.0)
    assert pos["ITUB4"]["avg_cost"] == pytest.approx(120.0)


def test_portfolio_sell_reduces_position():
    txs = [
        _buy("ITUB4", 10_000, 100),
        _sell("ITUB4", 6_000, 50),   # vende metade pelo preço atual
    ]
    pos = portfolio_positions(txs)
    assert "ITUB4" in pos
    assert pos["ITUB4"]["quantity"] == pytest.approx(50.0)
    assert pos["ITUB4"]["total_cost"] == pytest.approx(5_000.0)  # metade do custo


def test_portfolio_full_sell_removes_position():
    txs = [_buy("ITUB4", 10_000, 100), _sell("ITUB4", 12_000, 100)]
    pos = portfolio_positions(txs)
    assert "ITUB4" not in pos


def test_portfolio_multiple_tickers():
    txs = [_buy("ITUB4", 5000, 100), _buy("VALE3", 8000, 50)]
    pos = portfolio_positions(txs)
    assert "ITUB4" in pos
    assert "VALE3" in pos


def test_total_invested_cost():
    txs = [_buy("ITUB4", 10_000, 100), _buy("VALE3", 8_000, 50)]
    assert total_invested_cost(txs) == pytest.approx(18_000.0)


def test_total_invested_cost_after_sell():
    """Custo total deve refletir apenas posição remanescente."""
    txs = [
        _buy("ITUB4", 10_000, 100),
        _sell("ITUB4", 6_000, 50),  # vende metade
    ]
    assert total_invested_cost(txs) == pytest.approx(5_000.0)


# ── P&L com preços ────────────────────────────────────────────────────────────


def test_with_pnl_gain():
    txs = [_buy("ITUB4", 10_000, 100)]
    pos = portfolio_positions(txs)
    result = with_pnl(pos, {"ITUB4": 120.0})  # preço subiu R$100 → R$120
    assert result["ITUB4"]["market_value"] == pytest.approx(12_000.0)
    assert result["ITUB4"]["pnl"] == pytest.approx(2_000.0)
    assert result["ITUB4"]["pnl_pct"] == pytest.approx(20.0)


def test_with_pnl_loss():
    txs = [_buy("ITUB4", 10_000, 100)]
    pos = portfolio_positions(txs)
    result = with_pnl(pos, {"ITUB4": 80.0})  # preço caiu R$100 → R$80
    assert result["ITUB4"]["pnl"] == pytest.approx(-2_000.0)


def test_with_pnl_no_price():
    txs = [_buy("ITUB4", 10_000, 100)]
    pos = portfolio_positions(txs)
    result = with_pnl(pos, {})  # sem preço informado
    assert result["ITUB4"]["pnl"] == 0.0


# ── Resumo do dólar ───────────────────────────────────────────────────────────


def test_dollar_summary_avg_rate():
    entries = [
        DollarEntry(date="2026-01-10", amount_usd=1000.0, exchange_rate=5.0, iof_pct=0.0, spread_pct=0.0),
        DollarEntry(date="2026-02-10", amount_usd=1000.0, exchange_rate=5.5, iof_pct=0.0, spread_pct=0.0),
    ]
    summary = dollar_summary(entries)
    assert summary["total_usd"] == pytest.approx(2000.0)
    assert summary["total_brl"] == pytest.approx(10_500.0)
    assert summary["avg_effective_rate"] == pytest.approx(5.25)


def test_dollar_summary_pnl():
    entries = [
        DollarEntry(date="2026-01-10", amount_usd=1000.0, exchange_rate=5.0, iof_pct=0.0, spread_pct=0.0),
    ]
    summary = dollar_summary(entries, current_rate=6.0)
    assert summary["pnl"] == pytest.approx(1000.0)  # 6000 - 5000
    assert summary["pnl_pct"] == pytest.approx(20.0)


def test_dollar_summary_empty():
    summary = dollar_summary([])
    assert summary["total_usd"] == 0.0
    assert summary["pnl"] == 0.0


# ── Pequenos vícios ───────────────────────────────────────────────────────────


def test_small_vices_identifies_recurring():
    txs = [
        _expense(15.0, date="2026-01-05", description="Café"),
        _expense(15.0, date="2026-02-05", description="Café"),
        _expense(15.0, date="2026-03-05", description="Café"),
        _expense(500.0, date="2026-01-10", description="Gasto único"),  # só aparece 1x
    ]
    vices = small_vices(txs, min_count=2)
    descs = [v["description"].lower() for v in vices]
    assert "café" in descs
    assert "gasto único" not in descs


def test_small_vices_annual_projection():
    txs = [
        _expense(30.0, date="2026-01-01", description="Netflix"),
        _expense(30.0, date="2026-02-01", description="Netflix"),
        _expense(30.0, date="2026-03-01", description="Netflix"),
    ]
    vices = small_vices(txs, min_count=2)
    assert len(vices) >= 1
    netflix = next(v for v in vices if "netflix" in v["description"].lower())
    assert netflix["annual_est"] > 0


def test_small_vices_sorted_by_impact():
    txs = [
        _expense(10.0, date="2026-01-01", description="Café"),
        _expense(10.0, date="2026-02-01", description="Café"),
        _expense(100.0, date="2026-01-05", description="Restaurante"),
        _expense(100.0, date="2026-02-05", description="Restaurante"),
    ]
    vices = small_vices(txs, min_count=2)
    assert vices[0]["annual_est"] >= vices[-1]["annual_est"]


# ── Formatação ────────────────────────────────────────────────────────────────


def test_fmt_brl_integer():
    assert fmt_brl(1000.0) == "R$ 1.000,00"


def test_fmt_brl_decimal():
    assert fmt_brl(22.90) == "R$ 22,90"


def test_fmt_brl_large():
    result = fmt_brl(1_234_567.89)
    assert "1.234.567,89" in result


def test_fmt_pct_positive():
    result = fmt_pct(5.5)
    assert result.startswith("+")
    assert "5.50" in result


def test_fmt_pct_negative():
    result = fmt_pct(-3.2)
    assert result.startswith("-")
