"""Gráficos matplotlib — design system serene-finance-hub."""

from __future__ import annotations

import matplotlib.ticker as mticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# ── Design tokens ─────────────────────────────────────────────────────────────
BG         = "#ffffff"
GRID       = "#f3f4f6"
SPINE      = "#e5e7eb"
TEXT       = "#6b7280"
C_GREEN    = "#22c55e"
C_RED      = "#ef4444"
C_BLUE     = "#3b82f6"
C_PURPLE   = "#8b5cf6"
PALETTE    = ["#3b82f6", "#8b5cf6", "#ec4899", "#10b981",
              "#f59e0b", "#06b6d4", "#f97316", "#94a3b8",
              "#22c55e", "#ef4444"]


def _fig(w: float, h: float) -> tuple[Figure, object]:
    fig = Figure(figsize=(w, h), dpi=96)
    fig.patch.set_facecolor(BG)
    ax = fig.add_subplot(111)
    ax.set_facecolor(BG)
    ax.tick_params(colors=TEXT, labelsize=8.5)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color(SPINE)
    ax.spines["bottom"].set_color(SPINE)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    return fig, ax


def embed(fig: Figure, parent) -> FigureCanvasTkAgg:
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    w = canvas.get_tk_widget()
    w.configure(background=BG, highlightthickness=0)
    return canvas


# ── Chart builders ────────────────────────────────────────────────────────────

def bar_income_expenses(history: list[dict]) -> Figure:
    """Barras agrupadas: receita vs despesa real por mês."""
    fig, ax = _fig(6.5, 2.6)
    months   = [h["month"][5:] for h in history]
    incomes  = [h["income"]   for h in history]
    expenses = [h["expenses"] for h in history]
    x, bw = range(len(months)), 0.35
    ax.bar([i - bw / 2 for i in x], incomes,  width=bw, color=C_GREEN,  label="Receitas",
           zorder=3, alpha=0.88, linewidth=0)
    ax.bar([i + bw / 2 for i in x], expenses, width=bw, color=C_RED,    label="Despesas",
           zorder=3, alpha=0.88, linewidth=0)
    ax.set_xticks(list(x))
    ax.set_xticklabels(months, fontsize=8.5)
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: f"R${v/1000:.0f}k" if v >= 1000 else f"R${v:.0f}")
    )
    ax.legend(fontsize=8, framealpha=0, labelcolor=TEXT)
    fig.tight_layout(pad=1.0)
    return fig


def donut_categories(by_cat: dict[str, float]) -> Figure:
    """Rosca de gastos por categoria."""
    fig = Figure(figsize=(3.4, 2.6), dpi=96)
    fig.patch.set_facecolor(BG)
    ax = fig.add_subplot(111)
    ax.set_facecolor(BG)
    if not by_cat:
        ax.text(0.5, 0.5, "Sem dados", ha="center", va="center",
                transform=ax.transAxes, color=TEXT, fontsize=10)
        ax.axis("off")
        fig.tight_layout()
        return fig
    labels = list(by_cat.keys())
    values = list(by_cat.values())
    total  = sum(values)
    colors = PALETTE[:len(labels)]
    wedges, _ = ax.pie(values, colors=colors, startangle=90,
                        wedgeprops={"width": 0.5, "linewidth": 0})
    legend_labels = [f"{lb} {v / total * 100:.0f}%" for lb, v in zip(labels, values)]
    ax.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1, 0.5),
               fontsize=7.5, framealpha=0, labelcolor=TEXT)
    fig.tight_layout(pad=0.4)
    return fig


def area_portfolio_cdi(data: list[dict], cdi_rate: float) -> Figure:
    """Área: custo do portfólio vs simulação CDI."""
    fig, ax = _fig(7, 2.6)
    months   = [d["month"][5:] for d in data]
    invested = [d["invested"]  for d in data]
    cdi      = [d["cdi"]       for d in data]
    x = list(range(len(months)))
    ax.fill_between(x, invested, alpha=0.16, color=C_BLUE)
    ax.plot(x, invested, color=C_BLUE,   linewidth=2, label="Custo Portfólio", zorder=3)
    ax.fill_between(x, cdi,      alpha=0.10, color=C_PURPLE)
    ax.plot(x, cdi, color=C_PURPLE, linewidth=2, linestyle="--",
            label=f"CDI {cdi_rate:.1f}% a.a.", zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(months, fontsize=8.5)
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: f"R${v/1000:.1f}k" if v >= 1000 else f"R${v:.0f}")
    )
    ax.legend(fontsize=8, framealpha=0, labelcolor=TEXT)
    fig.tight_layout(pad=1.0)
    return fig


def line_balance(history: list[dict]) -> Figure:
    """Linha de saldo acumulado (receitas - despesas reais)."""
    fig, ax = _fig(7, 2.0)
    months = [h["month"][5:] for h in history]
    acc, values = 0.0, []
    for h in history:
        acc += h["income"] - h["expenses"]
        values.append(acc)
    x = list(range(len(months)))
    color = C_GREEN if (values[-1] if values else 0) >= 0 else C_RED
    ax.fill_between(x, values, alpha=0.14, color=color)
    ax.plot(x, values, color=color, linewidth=2.5, zorder=3)
    ax.axhline(0, color=SPINE, linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(months, fontsize=8.5)
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: f"R${v/1000:.1f}k" if abs(v) >= 1000 else f"R${v:.0f}")
    )
    fig.tight_layout(pad=1.0)
    return fig
