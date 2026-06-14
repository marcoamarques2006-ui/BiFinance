"""Persistência via Supabase (PostgreSQL na nuvem)."""

from __future__ import annotations

import os

from supabase import Client, create_client

from bifinance.models import Budget, DollarEntry, Goal, Settings, Transaction


class Storage:
    """Camada de persistência — todas as coleções em Supabase.

    Em testes, passe um cliente falso via _client para evitar I/O de rede.
    """

    def __init__(self, _client: Client | None = None) -> None:
        if _client is not None:
            self._db = _client
        else:
            self._db = create_client(
                os.environ["SUPABASE_URL"],
                os.environ["SUPABASE_KEY"],
            )

    # ── Transactions ──────────────────────────────────────────────────────────

    def load_transactions(self) -> list[Transaction]:
        res = self._db.table("transactions").select("*").execute()
        return [Transaction.from_dict(r) for r in res.data]

    def save_transactions(self, items: list[Transaction]) -> None:
        self._db.table("transactions").delete().neq("id", "").execute()
        if items:
            self._db.table("transactions").insert([t.to_dict() for t in items]).execute()

    def add_transaction(self, t: Transaction) -> None:
        t.validate()
        self._db.table("transactions").insert(t.to_dict()).execute()

    def remove_transaction(self, tx_id: str) -> bool:
        res = self._db.table("transactions").delete().eq("id", tx_id).execute()
        return len(res.data) > 0

    # ── Dollar Entries ────────────────────────────────────────────────────────

    def load_dollar_entries(self) -> list[DollarEntry]:
        res = self._db.table("dollar_entries").select("*").execute()
        return [DollarEntry.from_dict(r) for r in res.data]

    def add_dollar_entry(self, entry: DollarEntry) -> None:
        entry.validate()
        self._db.table("dollar_entries").insert(entry.to_dict()).execute()

    def remove_dollar_entry(self, entry_id: str) -> bool:
        res = self._db.table("dollar_entries").delete().eq("id", entry_id).execute()
        return len(res.data) > 0

    # ── Goals ─────────────────────────────────────────────────────────────────

    def load_goals(self) -> list[Goal]:
        res = self._db.table("goals").select("*").execute()
        return [Goal.from_dict(r) for r in res.data]

    def add_goal(self, goal: Goal) -> None:
        goal.validate()
        self._db.table("goals").insert(goal.to_dict()).execute()

    def update_goal(self, goal: Goal) -> None:
        self._db.table("goals").update(goal.to_dict()).eq("id", goal.id).execute()

    def remove_goal(self, goal_id: str) -> bool:
        res = self._db.table("goals").delete().eq("id", goal_id).execute()
        return len(res.data) > 0

    # ── Budgets ───────────────────────────────────────────────────────────────

    def load_budgets(self) -> list[Budget]:
        res = self._db.table("budgets").select("*").execute()
        return [Budget.from_dict(r) for r in res.data]

    def add_budget(self, budget: Budget) -> None:
        budget.validate()
        # Substitui o orçamento existente da mesma categoria (uma categoria, um teto)
        self._db.table("budgets").delete().eq("category", budget.category).execute()
        self._db.table("budgets").insert(budget.to_dict()).execute()

    def remove_budget(self, budget_id: str) -> bool:
        res = self._db.table("budgets").delete().eq("id", budget_id).execute()
        return len(res.data) > 0

    # ── Settings ──────────────────────────────────────────────────────────────

    def load_settings(self) -> Settings:
        res = self._db.table("settings").select("*").execute()
        if res.data:
            return Settings.from_dict(res.data[0])
        return Settings()

    def save_settings(self, s: Settings) -> None:
        d = s.to_dict()
        d["id"] = 1
        self._db.table("settings").upsert(d).execute()

    # ── Current Prices ────────────────────────────────────────────────────────

    def load_prices(self) -> dict[str, float]:
        res = self._db.table("current_prices").select("*").execute()
        return {r["ticker"]: float(r["price"]) for r in res.data}

    def save_prices(self, prices: dict[str, float]) -> None:
        self._db.table("current_prices").delete().neq("ticker", "").execute()
        if prices:
            rows = [{"ticker": k, "price": v} for k, v in prices.items()]
            self._db.table("current_prices").insert(rows).execute()

    # ── PIN ───────────────────────────────────────────────────────────────────

    def load_pin_hash(self) -> str:
        res = self._db.table("pin").select("*").execute()
        if res.data:
            return res.data[0].get("pin_hash", "")
        return ""

    def save_pin_hash(self, h: str) -> None:
        self._db.table("pin").upsert({"id": 1, "pin_hash": h}).execute()
