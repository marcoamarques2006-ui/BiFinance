-- BiFinance — Migração: tabela de Orçamentos Mensais (feature v2.1.0)
-- Execute APENAS este script no SQL Editor do Supabase em bancos já existentes.
-- É idempotente: pode rodar mais de uma vez sem erro.

create table if not exists budgets (
    id            text primary key,
    category      text not null unique,
    monthly_limit double precision not null
);

alter table budgets enable row level security;

drop policy if exists "allow_all" on budgets;
create policy "allow_all" on budgets for all using (true) with check (true);
