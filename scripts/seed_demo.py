"""Popula o banco Supabase com dados de demonstração.

Uso:
    python scripts/seed_demo.py

Lê SUPABASE_URL / SUPABASE_KEY do ambiente ou do arquivo .env na raiz.
Limpa as tabelas e insere um conjunto coerente de transações, dólar,
metas, preços, configurações e orçamentos — para que o deploy exiba
dados reais (não os de demonstração embutidos).
"""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

# Permite importar o pacote a partir de src/ sem instalação
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from bifinance.models import Budget, DollarEntry, Goal, Settings, Transaction  # noqa: E402
from bifinance.storage import Storage  # noqa: E402


def _load_env() -> None:
    """Carrega SUPABASE_URL/KEY do .env se ainda não estiverem no ambiente."""
    if os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_KEY"):
        return
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _uid() -> str:
    return str(uuid.uuid4())


# ── Dados de demonstração ──────────────────────────────────────────────────────

TRANSACTIONS = [
    # Abril 2026
    {"type": "income",  "description": "Salário",      "amount": 8500.00, "date": "2026-04-05", "category": "Salário"},
    {"type": "expense", "description": "Supermercado", "amount": 745.00,  "date": "2026-04-07", "category": "Alimentação"},
    {"type": "expense", "description": "Aluguel",      "amount": 1600.00, "date": "2026-04-10", "category": "Moradia"},
    {"type": "dividend","description": "Provento KNRI11","amount": 84.00, "date": "2026-04-10", "ticker": "KNRI11"},
    # Maio 2026
    {"type": "income",  "description": "Salário",      "amount": 8500.00, "date": "2026-05-05", "category": "Salário"},
    {"type": "expense", "description": "Supermercado", "amount": 820.00,  "date": "2026-05-08", "category": "Alimentação"},
    {"type": "expense", "description": "Aluguel",      "amount": 1600.00, "date": "2026-05-10", "category": "Moradia"},
    {"type": "expense", "description": "Uber",         "amount": 95.00,   "date": "2026-05-18", "category": "Transporte"},
    # Junho 2026 (mês atual — alimenta a seção Orçamento)
    {"type": "income",  "description": "Salário",        "amount": 8500.00, "date": "2026-06-05", "category": "Salário"},
    {"type": "income",  "description": "Freelance Design","amount": 1800.00,"date": "2026-06-09", "category": "Freelance"},
    {"type": "expense", "description": "Supermercado",   "amount": 690.00,  "date": "2026-06-06", "category": "Alimentação"},
    {"type": "expense", "description": "Restaurante",    "amount": 180.00,  "date": "2026-06-08", "category": "Alimentação"},
    {"type": "expense", "description": "Café",           "amount": 48.00,   "date": "2026-06-11", "category": "Alimentação"},
    {"type": "expense", "description": "Aluguel",        "amount": 1600.00, "date": "2026-06-10", "category": "Moradia"},
    {"type": "expense", "description": "Netflix",        "amount": 39.90,   "date": "2026-06-12", "category": "Assinaturas"},
    {"type": "expense", "description": "Spotify",        "amount": 21.90,   "date": "2026-06-12", "category": "Assinaturas"},
    {"type": "expense", "description": "Uber",           "amount": 112.00,  "date": "2026-06-09", "category": "Transporte"},
    {"type": "expense", "description": "Gasolina",       "amount": 250.00,  "date": "2026-06-13", "category": "Transporte"},
    {"type": "expense", "description": "Academia",       "amount": 89.90,   "date": "2026-06-07", "category": "Saúde"},
    {"type": "expense", "description": "Cinema",         "amount": 120.00,  "date": "2026-06-13", "category": "Lazer"},
    {"type": "dividend","description": "Provento KNRI11","amount": 84.00,   "date": "2026-06-10", "ticker": "KNRI11"},
    # Investimentos (carteira)
    {"type": "investment_buy", "description": "Compra KNRI11", "amount": 2100.00, "date": "2026-03-20", "ticker": "KNRI11", "asset_type": "FII",  "quantity": 20.0},
    {"type": "investment_buy", "description": "Compra ITUB4",  "amount": 2880.00, "date": "2026-03-26", "ticker": "ITUB4",  "asset_type": "Ação", "quantity": 120.0},
    {"type": "investment_buy", "description": "Compra XPML11", "amount": 3120.00, "date": "2026-04-18", "ticker": "XPML11", "asset_type": "FII",  "quantity": 30.0},
]

DOLLAR_ENTRIES = [
    {"date": "2026-02-18", "amount_usd": 800.0, "exchange_rate": 5.95, "iof_pct": 1.1, "spread_pct": 1.2, "description": "Dólar reserva"},
    {"date": "2026-03-25", "amount_usd": 300.0, "exchange_rate": 5.90, "iof_pct": 1.1, "spread_pct": 1.0, "description": "Dólar ETF"},
]

GOALS = [
    {"name": "Viagem Europa",       "target": 18000.0, "current": 7200.0,  "deadline": "2026-12-31", "color": "#3b82f6"},
    {"name": "Fundo de Emergência", "target": 25000.0, "current": 14500.0, "deadline": None,         "color": "#22c55e"},
    {"name": "MacBook Pro",         "target": 9000.0,  "current": 3800.0,  "deadline": "2026-08-01", "color": "#8b5cf6"},
]

# Orçamentos mensais por categoria (feature v2.1.0)
BUDGETS = [
    {"category": "Alimentação", "limit": 1000.0},   # gasto jun: 918  → alerta
    {"category": "Moradia",     "limit": 1600.0},   # gasto jun: 1600 → alerta/estourado
    {"category": "Transporte",  "limit": 300.0},    # gasto jun: 362  → estourado
    {"category": "Assinaturas", "limit": 100.0},    # gasto jun: 61.8 → ok
    {"category": "Lazer",       "limit": 400.0},    # gasto jun: 120  → ok
]

PRICES = {"ITUB4": 28.40, "KNRI11": 108.50, "XPML11": 107.20}


def main() -> None:
    _load_env()
    if not os.environ.get("SUPABASE_URL") or not os.environ.get("SUPABASE_KEY"):
        sys.exit("ERRO: defina SUPABASE_URL e SUPABASE_KEY (ou crie um .env).")

    s = Storage()

    # Transações e preços têm save_* que já limpam a tabela antes de inserir
    txs = [Transaction(id=_uid(), **t) for t in TRANSACTIONS]
    s.save_transactions(txs)
    s.save_prices(PRICES)
    s.save_settings(Settings())

    # Dólar, metas e orçamentos: limpa e reinsere para idempotência
    s._db.table("dollar_entries").delete().neq("id", "").execute()
    for e in DOLLAR_ENTRIES:
        s.add_dollar_entry(DollarEntry(id=_uid(), **e))

    s._db.table("goals").delete().neq("id", "").execute()
    for g in GOALS:
        s.add_goal(Goal(id=_uid(), **g))

    s._db.table("budgets").delete().neq("id", "").execute()
    for b in BUDGETS:
        s.add_budget(Budget(id=_uid(), **b))

    print(
        f"OK — {len(txs)} transações, {len(DOLLAR_ENTRIES)} dólar, "
        f"{len(GOALS)} metas, {len(BUDGETS)} orçamentos inseridos no Supabase."
    )


if __name__ == "__main__":
    main()
