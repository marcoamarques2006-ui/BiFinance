"""Persistência multi-coleção em JSON."""

from __future__ import annotations

import json
from pathlib import Path

from bifinance.models import DollarEntry, Goal, Settings, Transaction


def _empty() -> dict:
    return {
        "transactions": [],
        "dollar_entries": [],
        "goals": [],
        "settings": {},
        "current_prices": {},
    }


class Storage:
    def __init__(self, path: Path | None = None) -> None:
        if path is None:
            path = Path.home() / ".bifinance" / "data.json"
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write(_empty())

    # ── Internal ──────────────────────────────────────────────────────────────

    def _read(self) -> dict:
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            # migrate from legacy format (plain list of expenses)
            migrated = _empty()
            self._write(migrated)
            return migrated
        return raw

    def _write(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # ── Transactions ──────────────────────────────────────────────────────────

    def load_transactions(self) -> list[Transaction]:
        return [Transaction.from_dict(d) for d in self._read().get("transactions", [])]

    def save_transactions(self, items: list[Transaction]) -> None:
        raw = self._read()
        raw["transactions"] = [t.to_dict() for t in items]
        self._write(raw)

    def add_transaction(self, t: Transaction) -> None:
        txs = self.load_transactions()
        txs.append(t)
        self.save_transactions(txs)

    def remove_transaction(self, tx_id: str) -> bool:
        txs = self.load_transactions()
        filtered = [t for t in txs if t.id != tx_id]
        if len(filtered) == len(txs):
            return False
        self.save_transactions(filtered)
        return True

    # ── Dollar Entries ────────────────────────────────────────────────────────

    def load_dollar_entries(self) -> list[DollarEntry]:
        return [DollarEntry.from_dict(d) for d in self._read().get("dollar_entries", [])]

    def add_dollar_entry(self, entry: DollarEntry) -> None:
        raw = self._read()
        raw.setdefault("dollar_entries", []).append(entry.to_dict())
        self._write(raw)

    def remove_dollar_entry(self, entry_id: str) -> bool:
        raw = self._read()
        lst = raw.get("dollar_entries", [])
        filtered = [e for e in lst if e["id"] != entry_id]
        if len(filtered) == len(lst):
            return False
        raw["dollar_entries"] = filtered
        self._write(raw)
        return True

    # ── Goals ─────────────────────────────────────────────────────────────────

    def load_goals(self) -> list[Goal]:
        return [Goal.from_dict(d) for d in self._read().get("goals", [])]

    def add_goal(self, goal: Goal) -> None:
        raw = self._read()
        raw.setdefault("goals", []).append(goal.to_dict())
        self._write(raw)

    def update_goal(self, goal: Goal) -> None:
        raw = self._read()
        raw["goals"] = [
            goal.to_dict() if g["id"] == goal.id else g
            for g in raw.get("goals", [])
        ]
        self._write(raw)

    def remove_goal(self, goal_id: str) -> bool:
        raw = self._read()
        lst = raw.get("goals", [])
        filtered = [g for g in lst if g["id"] != goal_id]
        if len(filtered) == len(lst):
            return False
        raw["goals"] = filtered
        self._write(raw)
        return True

    # ── Settings ──────────────────────────────────────────────────────────────

    def load_settings(self) -> Settings:
        return Settings.from_dict(self._read().get("settings", {}))

    def save_settings(self, s: Settings) -> None:
        raw = self._read()
        raw["settings"] = s.to_dict()
        self._write(raw)

    # ── Current Prices ────────────────────────────────────────────────────────

    def load_prices(self) -> dict[str, float]:
        return {k: float(v) for k, v in self._read().get("current_prices", {}).items()}

    def save_prices(self, prices: dict[str, float]) -> None:
        raw = self._read()
        raw["current_prices"] = prices
        self._write(raw)

    # ── PIN ───────────────────────────────────────────────────────────────────

    def load_pin_hash(self) -> str:
        return self._read().get("pin_hash", "")

    def save_pin_hash(self, h: str) -> None:
        raw = self._read()
        raw["pin_hash"] = h
        self._write(raw)
