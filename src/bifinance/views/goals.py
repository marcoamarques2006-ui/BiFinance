"""View: Metas."""

from __future__ import annotations

import customtkinter as ctk

from bifinance import finance as fin
from bifinance.models import GOAL_COLORS, Goal
from bifinance.theme import C, _tint


def render(app) -> None:
    outer = ctk.CTkFrame(app._content, fg_color=C["bg"])
    outer.grid(row=0, column=0, sticky="nsew", padx=24, pady=20)
    outer.grid_columnconfigure(0, weight=1)
    outer.grid_rowconfigure(1, weight=1)

    # ── Formulário ────────────────────────────────────────────────────────────
    form_card = app._card(outer, row=0, column=0, sticky="ew", pady=(0, 16))
    form_card.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
    app._lbl(form_card, "Nova Meta", size=13, weight="bold").grid(
        row=0, column=0, columnspan=5, sticky="w", padx=16, pady=(14, 10))
    app._sep(form_card, 1)

    fields = [
        ("Nome da Meta",        "Ex: Reserva de emergência…"),
        ("Valor Alvo (R$)",     "10000"),
        ("Valor Atual (R$)",    "0"),
        ("Prazo (AAAA-MM-DD)",  "Opcional"),
    ]
    goal_entries: list[ctk.CTkEntry] = []
    for col, (lbl, ph) in enumerate(fields):
        app._lbl(form_card, lbl, size=11, weight="bold").grid(
            row=2, column=col, sticky="w",
            padx=(16 if col == 0 else 8, 8), pady=(10, 3))
        e = ctk.CTkEntry(form_card, height=36, corner_radius=6,
                          border_color=C["border"], fg_color=C["card"],
                          text_color=C["text"], placeholder_text=ph)
        e.grid(row=3, column=col, sticky="ew", padx=(16 if col == 0 else 8, 8))
        goal_entries.append(e)

    app._lbl(form_card, "Cor", size=11, weight="bold").grid(
        row=2, column=4, sticky="w", padx=8, pady=(10, 3))
    color_var = ctk.StringVar(value=GOAL_COLORS[0])
    ctk.CTkOptionMenu(
        form_card, values=GOAL_COLORS, variable=color_var,
        height=36, corner_radius=6, fg_color=C["card"],
        button_color=C["border"], text_color=C["text"],
        dropdown_fg_color=C["card"], dropdown_text_color=C["text"],
    ).grid(row=3, column=4, padx=8)

    gmsg = ctk.CTkLabel(form_card, text="", font=ctk.CTkFont(size=11), text_color=C["red"])
    gmsg.grid(row=4, column=0, columnspan=5, padx=16, pady=(6, 10))

    def _add_goal() -> None:
        gmsg.configure(text="")
        try:
            name, target_s, current_s, deadline_s = [e.get().strip() for e in goal_entries]
            goal = Goal(
                name=name,
                target=float(target_s.replace(",", ".")),
                current=float(current_s.replace(",", ".")) if current_s else 0.0,
                deadline=deadline_s or None,
                color=color_var.get(),
            )
            goal.validate()
            app._s.add_goal(goal)
            app._nav_to("goals")
        except ValueError as exc:
            gmsg.configure(text=str(exc), text_color=C["red"])

    form_card.grid_columnconfigure(5, weight=0)
    ctk.CTkButton(
        form_card, text="Criar Meta", height=36, corner_radius=6,
        font=ctk.CTkFont(size=12, weight="bold"),
        fg_color=C["text"], hover_color="#374151", text_color="#ffffff",
        command=_add_goal,
    ).grid(row=3, column=5, padx=(8, 16), sticky="e")

    # ── Lista de metas ────────────────────────────────────────────────────────
    goals = app._s.load_goals()
    goals_frame = ctk.CTkScrollableFrame(outer, fg_color=C["bg"],
                                          scrollbar_button_color=C["border"])
    goals_frame.grid(row=1, column=0, sticky="nsew")
    goals_frame.grid_columnconfigure((0, 1), weight=1, uniform="gcol")

    if not goals:
        app._lbl(goals_frame, "Nenhuma meta cadastrada ainda.", color=C["muted"]).grid(
            row=0, column=0, columnspan=2, pady=40)
        return

    for i, g in enumerate(goals):
        col  = i % 2
        row  = i // 2
        card = ctk.CTkFrame(goals_frame, fg_color=C["card"],
                             border_color=C["border"], border_width=1, corner_radius=8)
        card.grid(row=row, column=col, sticky="nsew",
                   padx=(0, 8) if col == 0 else (8, 0), pady=8)
        card.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 4))
        top.grid_columnconfigure(0, weight=1)
        app._lbl(top, g.name, size=14, weight="bold").grid(row=0, column=0, sticky="w")
        if g.deadline:
            app._lbl(top, f"Prazo: {g.deadline}", size=11, color=C["muted"]).grid(
                row=0, column=1, sticky="e")

        app._lbl(card, fin.fmt_brl(g.current), size=22, weight="bold", mono=True).grid(
            row=1, column=0, sticky="w", padx=16, pady=(4, 2))
        app._lbl(card, f"de {fin.fmt_brl(g.target)} — faltam {fin.fmt_brl(g.remaining)}",
                  size=11, color=C["muted"]).grid(row=2, column=0, sticky="w", padx=16, pady=(0, 8))

        bar = ctk.CTkProgressBar(card, height=6, corner_radius=3,
                                  progress_color=g.color, fg_color=C["muted_bg"])
        bar.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 4))
        bar.set(g.progress)
        app._lbl(card, f"{g.progress * 100:.0f}% concluído", size=11, color=g.color).grid(
            row=4, column=0, sticky="w", padx=16, pady=(0, 8))

        upd_frame = ctk.CTkFrame(card, fg_color="transparent")
        upd_frame.grid(row=5, column=0, sticky="ew", padx=16, pady=(0, 16))
        upd_frame.grid_columnconfigure(0, weight=1)
        upd_e = ctk.CTkEntry(upd_frame, height=32, corner_radius=6,
                              border_color=C["border"], fg_color=C["muted_bg"],
                              text_color=C["text"], placeholder_text="Novo valor atual…")
        upd_e.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        def _upd(goal=g, entry=upd_e) -> None:
            try:
                v = float(entry.get().strip().replace(",", "."))
                goal.current = v
                app._s.update_goal(goal)
                app._nav_to("goals")
            except ValueError:
                pass

        ctk.CTkButton(
            upd_frame, text="Atualizar", height=32, corner_radius=6,
            fg_color=g.color, hover_color=_tint(g.color, 0.2),
            text_color="#ffffff", font=ctk.CTkFont(size=11),
            command=_upd,
        ).grid(row=0, column=1)
        ctk.CTkButton(
            upd_frame, text="✕", width=28, height=32, corner_radius=6,
            fg_color="transparent", border_color=C["border"], border_width=1,
            text_color=C["muted"], hover_color="#fef2f2",
            command=lambda gid=g.id: (app._s.remove_goal(gid), app._nav_to("goals")),
        ).grid(row=0, column=2, padx=(6, 0))
