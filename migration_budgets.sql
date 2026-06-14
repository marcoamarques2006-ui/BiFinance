-- BiFinance — Migração: tabela de Orçamentos Mensais (feature v2.1.0)
-- Execute no SQL Editor do Supabase em bancos já existentes.

create table if not exists budgets (
    id            text primary key,
    category      text not null unique,
    monthly_limit double precision not null
);

alter table budgets disable row level security;
