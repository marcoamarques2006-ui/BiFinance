"""
Lógica de negócio e cálculos financeiros.

Regra central: compra/venda de ativos é MOVIMENTAÇÃO, não despesa nem receita.
Se o usuário gasta R$10k em ações, vende por R$15k e compra R$10k em FIIs,
o app indica R$0,00 de despesas reais — apenas variação patrimonial.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date

from bifinance.models import (
    CASH_INFLOWS,
    CASH_OUTFLOWS,
    INVESTMENT_MOVES,
    REAL_EXPENSE,
    REAL_INCOME,
    DollarEntry,
    Transaction,
)

# ── Formatação ────────────────────────────────────────────────────────────────

def fmt_brl(value: float) -> str:
    s = f"{value:,.2f}"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_pct(value: float) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"


# ── Caixa e Patrimônio ────────────────────────────────────────────────────────

def available_cash(txs: list[Transaction]) -> float:
    """
    Caixa disponível real.
    Receitas e vendas entram; despesas e compras de ativos saem.
    Compra de ativo NÃO é despesa — é alocação de caixa.
    """
    cash = 0.0
    for t in txs:
        if t.type in CASH_INFLOWS:
            cash += t.amount
        elif t.type in CASH_OUTFLOWS:
            cash -= t.amount
    return cash


def total_real_expenses(txs: list[Transaction]) -> float:
    """Gastos reais de consumo — exclui qualquer movimentação de investimento."""
    return sum(t.amount for t in txs if t.type in REAL_EXPENSE)


def total_real_income(txs: list[Transaction]) -> float:
    """Receitas reais: salário, freelance, dividendos."""
    return sum(t.amount for t in txs if t.type in REAL_INCOME)


def total_dividends(txs: list[Transaction]) -> float:
    return sum(t.amount for t in txs if t.type == "dividend")


def total_invested_cost(txs: list[Transaction]) -> float:
    """Custo total aportado (soma das compras - custo proporcional das vendas)."""
    positions = portfolio_positions(txs)
    return sum(p["total_cost"] for p in positions.values())


# ── Resumos Mensais ───────────────────────────────────────────────────────────

def _pfx(year: int, month: int) -> str:
    return f"{year:04d}-{month:02d}"


def monthly_income(txs: list[Transaction], year: int, month: int) -> float:
    p = _pfx(year, month)
    return sum(t.amount for t in txs if t.type in REAL_INCOME and t.date.startswith(p))


def monthly_expenses(txs: list[Transaction], year: int, month: int) -> float:
    p = _pfx(year, month)
    return sum(t.amount for t in txs if t.type in REAL_EXPENSE and t.date.startswith(p))


def expenses_by_category(txs: list[Transaction], year: int, month: int) -> dict[str, float]:
    p = _pfx(year, month)
    result: dict[str, float] = {}
    for t in txs:
        if t.type == "expense" and t.date.startswith(p) and t.category:
            result[t.category] = result.get(t.category, 0.0) + t.amount
    return result


def monthly_history(txs: list[Transaction], n: int = 6) -> list[dict]:
    """Histórico de receita vs despesa real para N meses (mais antigo → mais recente)."""
    today = date.today()
    months: list[tuple[int, int]] = []
    y, m = today.year, today.month
    for _ in range(n):
        months.append((y, m))
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    return [
        {
            "month":    f"{y:04d}-{m:02d}",
            "income":   monthly_income(txs, y, m),
            "expenses": monthly_expenses(txs, y, m),
        }
        for y, m in reversed(months)
    ]


# ── Portfolio de Investimentos ────────────────────────────────────────────────

def portfolio_positions(txs: list[Transaction]) -> dict[str, dict]:
    """
    Custo médio ponderado por ativo.
    Retorna {TICKER: {quantity, avg_cost, total_cost, asset_type}}.
    Na venda, mantém o preço médio e reduz quantidade/custo proporcional.
    """
    positions: dict[str, dict] = {}
    for t in sorted(txs, key=lambda x: x.date):
        if t.type not in INVESTMENT_MOVES or not t.ticker:
            continue
        ticker = t.ticker.upper().strip()
        if ticker not in positions:
            positions[ticker] = {
                "quantity": 0.0, "total_cost": 0.0,
                "avg_cost": 0.0, "asset_type": t.asset_type or "Outro",
            }
        pos = positions[ticker]
        qty = t.quantity or 0.0
        if t.type == "investment_buy":
            pos["total_cost"] += t.amount
            pos["quantity"] += qty
        elif t.type == "investment_sell" and pos["quantity"] > 0:
            cost_per_unit = pos["total_cost"] / pos["quantity"]
            pos["total_cost"] -= cost_per_unit * min(qty, pos["quantity"])
            pos["quantity"] = max(0.0, pos["quantity"] - qty)
        pos["total_cost"] = max(0.0, pos["total_cost"])
        pos["avg_cost"] = pos["total_cost"] / pos["quantity"] if pos["quantity"] > 0 else 0.0
    return {k: v for k, v in positions.items() if v["quantity"] > 0.0001}


def with_pnl(positions: dict[str, dict], prices: dict[str, float]) -> dict[str, dict]:
    """Adiciona P&L não realizado a cada posição conforme preços atuais."""
    result = {}
    for ticker, pos in positions.items():
        price = prices.get(ticker, 0.0)
        mkt = price * pos["quantity"]
        cost = pos["total_cost"]
        pnl = mkt - cost if price > 0 else 0.0
        pnl_pct = pnl / cost * 100 if cost > 0 and price > 0 else 0.0
        result[ticker] = {**pos, "current_price": price,
                           "market_value": mkt, "pnl": pnl, "pnl_pct": pnl_pct}
    return result


# ── Simulação CDI ─────────────────────────────────────────────────────────────

def patrimony_vs_cdi(txs: list[Transaction], n: int, cdi_rate: float) -> list[dict]:
    """
    Compara custo total investido vs o que valeria se aplicado no CDI.
    Retorna lista com {month, invested, cdi} para N meses.
    """
    hist = monthly_history(txs, n)
    cost = total_invested_cost(txs)
    monthly_rate = (1 + cdi_rate / 100) ** (1 / 12) - 1
    result = []
    for i, h in enumerate(hist):
        cdi_val = cost * (1 + monthly_rate) ** (i + 1) if cost > 0 else 0.0
        result.append({"month": h["month"], "invested": cost, "cdi": round(cdi_val, 2)})
    return result


# ── Dólar ─────────────────────────────────────────────────────────────────────

def dollar_summary(entries: list[DollarEntry], current_rate: float = 0.0) -> dict:
    """
    Resumo da posição em dólar:
    - Custo médio efetivo (inclui IOF + spread)
    - P&L se taxa atual informada
    """
    total_usd = sum(e.amount_usd for e in entries)
    total_brl = sum(e.total_cost_brl for e in entries)
    avg_eff = total_brl / total_usd if total_usd > 0 else 0.0
    mkt = total_usd * current_rate if current_rate > 0 else 0.0
    pnl = mkt - total_brl if current_rate > 0 else 0.0
    pnl_pct = pnl / total_brl * 100 if total_brl > 0 and current_rate > 0 else 0.0
    return {
        "total_usd": total_usd,
        "total_brl": total_brl,
        "avg_effective_rate": avg_eff,
        "market_value": mkt,
        "pnl": pnl,
        "pnl_pct": pnl_pct,
    }


# ── Pequenos Vícios ───────────────────────────────────────────────────────────

def small_vices(txs: list[Transaction], min_count: int = 2) -> list[dict]:
    """
    Identifica gastos de consumo recorrentes e projeta custo anual.
    Agrupa por descrição normalizada. Ordena pelo maior impacto anual estimado.
    """
    by_desc: dict[str, list] = defaultdict(list)
    for t in txs:
        if t.type == "expense":
            by_desc[t.description.strip().lower()].append((t.amount, t.date))

    result = []
    for desc, entries in by_desc.items():
        if len(entries) < min_count:
            continue
        amounts = [a for a, _ in entries]
        dates = sorted(d for _, d in entries)
        avg = sum(amounts) / len(amounts)
        if len(dates) >= 2:
            d0 = date.fromisoformat(dates[0])
            d1 = date.fromisoformat(dates[-1])
            span_months = max(1.0, (d1 - d0).days / 30)
            monthly_freq = len(entries) / span_months
        else:
            monthly_freq = 1.0
        result.append({
            "description":  desc.title(),
            "avg":          avg,
            "count":        len(entries),
            "monthly_est":  avg * monthly_freq,
            "annual_est":   avg * monthly_freq * 12,
        })
    return sorted(result, key=lambda x: -x["annual_est"])
