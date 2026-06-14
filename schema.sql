-- BiFinance — Schema Supabase (PostgreSQL)
-- Execute este script no SQL Editor do seu projeto Supabase.

-- ── Transações ────────────────────────────────────────────────────────────────
create table if not exists transactions (
    id          text primary key,
    type        text not null,
    description text not null,
    amount      double precision not null,
    date        text not null,
    category    text,
    is_recurring boolean not null default false,
    ticker      text,
    asset_type  text,
    quantity    double precision,
    notes       text
);

-- ── Compras de Dólar ──────────────────────────────────────────────────────────
create table if not exists dollar_entries (
    id            text primary key,
    date          text not null,
    amount_usd    double precision not null,
    exchange_rate double precision not null,
    iof_pct       double precision not null default 1.1,
    spread_pct    double precision not null default 0.0,
    description   text not null default 'Compra de dólar'
);

-- ── Metas Financeiras ─────────────────────────────────────────────────────────
create table if not exists goals (
    id       text primary key,
    name     text not null,
    target   double precision not null,
    current  double precision not null default 0.0,
    deadline text,
    color    text not null default '#3b82f6'
);

-- ── Configurações (linha única, id fixo = 1) ──────────────────────────────────
create table if not exists settings (
    id              integer primary key default 1,
    cdi_rate        double precision not null default 10.75,
    default_iof_pct double precision not null default 1.1,
    constraint settings_single_row check (id = 1)
);

-- ── Preços Atuais dos Ativos ──────────────────────────────────────────────────
create table if not exists current_prices (
    ticker text primary key,
    price  double precision not null
);

-- ── PIN de Bloqueio (linha única, id fixo = 1) ────────────────────────────────
create table if not exists pin (
    id       integer primary key default 1,
    pin_hash text not null default '',
    constraint pin_single_row check (id = 1)
);
