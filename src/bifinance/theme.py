"""Tokens de design — cores, paleta e utilitários visuais."""

from __future__ import annotations

C: dict[str, str] = {
    "bg":          "#f5f6fa",
    "sidebar":     "#111827",
    "sidebar_tx":  "#9ca3af",
    "sidebar_act": "#1f2937",
    "sidebar_lbl": "#4b5563",
    "header":      "#ffffff",
    "card":        "#ffffff",
    "border":      "#e5e7eb",
    "text":        "#111827",
    "muted":       "#6b7280",
    "blue":        "#3b82f6",
    "green":       "#22c55e",
    "red":         "#ef4444",
    "muted_bg":    "#f3f4f6",
}

NAV = [
    ("GERAL", [
        ("dashboard",    "📊  Dashboard"),
        ("transactions", "💸  Transações"),
    ]),
    ("PATRIMÔNIO", [
        ("investments", "📈  Investimentos"),
        ("dollar",      "💵  Dólar"),
    ]),
    ("PLANEJAMENTO", [
        ("goals",    "🎯  Metas"),
        ("reports",  "📋  Relatórios"),
    ]),
    ("SISTEMA", [
        ("settings", "⚙️  Configurações"),
    ]),
]


def _tint(hex_color: str, f: float = 0.88) -> str:
    """Clareia uma cor hex misturando com branco na proporção f."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return "#{:02x}{:02x}{:02x}".format(
        int(r + (255 - r) * f),
        int(g + (255 - g) * f),
        int(b + (255 - b) * f),
    )
