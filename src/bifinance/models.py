"""Modelos de dados do BiFinance."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Literal

# ── Constantes ────────────────────────────────────────────────────────────────

EXPENSE_CATEGORIES: list[str] = [
    "Alimentação", "Transporte", "Moradia", "Saúde", "Educação",
    "Lazer", "Vestuário", "Assinaturas", "Pets", "Outros",
]

INCOME_CATEGORIES: list[str] = [
    "Salário", "Freelance", "Bônus", "Aluguel Recebido", "Outros",
]

ASSET_TYPES: list[str] = [
    "Ação", "FII", "ETF", "BDR", "Tesouro Direto", "CDB/LCI/LCA", "Cripto", "Outro",
]

TxType = Literal["income", "expense", "investment_buy", "investment_sell", "dividend"]

# Regras de negócio: classificação de fluxo de caixa
CASH_INFLOWS: set[str] = {"income", "dividend", "investment_sell"}
CASH_OUTFLOWS: set[str] = {"expense", "investment_buy"}
REAL_INCOME: set[str] = {"income", "dividend"}
REAL_EXPENSE: set[str] = {"expense"}
INVESTMENT_MOVES: set[str] = {"investment_buy", "investment_sell"}

TX_LABELS: dict[str, str] = {
    "income":          "Receita",
    "expense":         "Despesa",
    "investment_buy":  "Compra de Ativo",
    "investment_sell": "Venda de Ativo",
    "dividend":        "Provento",
}

TX_COLORS: dict[str, str] = {
    "income":          "#22c55e",
    "expense":         "#ef4444",
    "investment_buy":  "#3b82f6",
    "investment_sell": "#8b5cf6",
    "dividend":        "#06b6d4",
}

TX_ICONS: dict[str, str] = {
    "income":          "💰",
    "expense":         "🛒",
    "investment_buy":  "📈",
    "investment_sell": "📉",
    "dividend":        "💎",
}

GOAL_COLORS: list[str] = [
    "#3b82f6", "#22c55e", "#8b5cf6", "#f59e0b",
    "#ef4444", "#06b6d4", "#f97316", "#ec4899",
]


# ── Modelos ───────────────────────────────────────────────────────────────────

@dataclass
class Transaction:
    type: TxType
    description: str
    amount: float            # BRL
    date: str                # YYYY-MM-DD
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    category: str | None = None
    is_recurring: bool = False
    ticker: str | None = None       # compra/venda de ativo ou dividendo
    asset_type: str | None = None
    quantity: float | None = None   # quantidade de cotas/ações
    notes: str | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id, "type": self.type, "description": self.description,
            "amount": self.amount, "date": self.date, "category": self.category,
            "is_recurring": self.is_recurring, "ticker": self.ticker,
            "asset_type": self.asset_type, "quantity": self.quantity, "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, d: dict) -> Transaction:
        return cls(
            id=str(d["id"]), type=d["type"],
            description=str(d["description"]), amount=float(d["amount"]),
            date=str(d["date"]), category=d.get("category"),
            is_recurring=bool(d.get("is_recurring", False)),
            ticker=d.get("ticker"), asset_type=d.get("asset_type"),
            quantity=float(d["quantity"]) if d.get("quantity") is not None else None,
            notes=d.get("notes"),
        )

    def validate(self) -> None:
        if not self.description.strip():
            raise ValueError("Descrição não pode ser vazia.")
        if self.amount <= 0:
            raise ValueError("Valor deve ser maior que zero.")
        if self.type not in TX_LABELS:
            raise ValueError(f"Tipo inválido: {self.type}")
        if self.type in INVESTMENT_MOVES:
            if not self.ticker or not self.ticker.strip():
                raise ValueError("Ticker é obrigatório para operações de ativo.")
            if not self.quantity or self.quantity <= 0:
                raise ValueError("Quantidade deve ser maior que zero.")


@dataclass
class DollarEntry:
    date: str
    amount_usd: float
    exchange_rate: float      # taxa base BRL/USD
    iof_pct: float = 1.1      # IOF (%)
    spread_pct: float = 0.0   # spread bancário (%)
    description: str = "Compra de dólar"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def total_cost_brl(self) -> float:
        base = self.amount_usd * self.exchange_rate
        return base * (1 + (self.iof_pct + self.spread_pct) / 100)

    @property
    def effective_rate(self) -> float:
        return self.total_cost_brl / self.amount_usd if self.amount_usd > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "id": self.id, "date": self.date, "amount_usd": self.amount_usd,
            "exchange_rate": self.exchange_rate, "iof_pct": self.iof_pct,
            "spread_pct": self.spread_pct, "description": self.description,
        }

    @classmethod
    def from_dict(cls, d: dict) -> DollarEntry:
        return cls(
            id=str(d["id"]), date=str(d["date"]),
            amount_usd=float(d["amount_usd"]),
            exchange_rate=float(d["exchange_rate"]),
            iof_pct=float(d.get("iof_pct", 1.1)),
            spread_pct=float(d.get("spread_pct", 0.0)),
            description=str(d.get("description", "Compra de dólar")),
        )

    def validate(self) -> None:
        if self.amount_usd <= 0:
            raise ValueError("Quantidade em USD deve ser maior que zero.")
        if self.exchange_rate <= 0:
            raise ValueError("Taxa de câmbio deve ser maior que zero.")
        if self.iof_pct < 0:
            raise ValueError("IOF não pode ser negativo.")
        if self.spread_pct < 0:
            raise ValueError("Spread não pode ser negativo.")


@dataclass
class Goal:
    name: str
    target: float
    current: float = 0.0
    deadline: str | None = None
    color: str = "#3b82f6"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def progress(self) -> float:
        return min(1.0, self.current / self.target) if self.target > 0 else 0.0

    @property
    def remaining(self) -> float:
        return max(0.0, self.target - self.current)

    def to_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name, "target": self.target,
            "current": self.current, "deadline": self.deadline, "color": self.color,
        }

    @classmethod
    def from_dict(cls, d: dict) -> Goal:
        return cls(
            id=str(d["id"]), name=str(d["name"]),
            target=float(d["target"]), current=float(d.get("current", 0.0)),
            deadline=d.get("deadline"), color=str(d.get("color", "#3b82f6")),
        )

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("Nome da meta não pode ser vazio.")
        if self.target <= 0:
            raise ValueError("Valor alvo deve ser maior que zero.")
        if self.current < 0:
            raise ValueError("Valor atual não pode ser negativo.")


@dataclass
class Budget:
    """Orçamento mensal de gasto para uma categoria de despesa."""

    category: str
    limit: float             # teto de gasto mensal (BRL)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict:
        # Coluna do banco é "monthly_limit" — "limit" é palavra reservada no SQL/PostgREST.
        return {"id": self.id, "category": self.category, "monthly_limit": self.limit}

    @classmethod
    def from_dict(cls, d: dict) -> Budget:
        return cls(
            id=str(d["id"]),
            category=str(d["category"]),
            limit=float(d["monthly_limit"]),
        )

    def validate(self) -> None:
        if not self.category.strip():
            raise ValueError("Categoria não pode ser vazia.")
        if self.category not in EXPENSE_CATEGORIES:
            raise ValueError(f"Categoria inválida: {self.category}")
        if self.limit <= 0:
            raise ValueError("Limite do orçamento deve ser maior que zero.")


@dataclass
class Settings:
    cdi_rate: float = 10.75
    default_iof_pct: float = 1.1

    def to_dict(self) -> dict:
        return {"cdi_rate": self.cdi_rate, "default_iof_pct": self.default_iof_pct}

    @classmethod
    def from_dict(cls, d: dict) -> Settings:
        return cls(
            cdi_rate=float(d.get("cdi_rate", 10.75)),
            default_iof_pct=float(d.get("default_iof_pct", 1.1)),
        )
