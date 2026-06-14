-- BiFinance — Políticas de acesso (RLS)
-- Execute no SQL Editor do Supabase após o schema.sql.
-- É idempotente: pode rodar mais de uma vez sem erro de "policy already exists".

-- Habilita RLS em todas as tabelas
alter table transactions   enable row level security;
alter table dollar_entries enable row level security;
alter table goals          enable row level security;
alter table budgets        enable row level security;
alter table settings       enable row level security;
alter table current_prices enable row level security;
alter table pin            enable row level security;

-- Remove políticas antigas (se existirem) antes de recriar
drop policy if exists "allow_all" on transactions;
drop policy if exists "allow_all" on dollar_entries;
drop policy if exists "allow_all" on goals;
drop policy if exists "allow_all" on budgets;
drop policy if exists "allow_all" on settings;
drop policy if exists "allow_all" on current_prices;
drop policy if exists "allow_all" on pin;

-- Cria políticas abertas (app pessoal, acesso via chave anon)
create policy "allow_all" on transactions   for all using (true) with check (true);
create policy "allow_all" on dollar_entries for all using (true) with check (true);
create policy "allow_all" on goals          for all using (true) with check (true);
create policy "allow_all" on budgets        for all using (true) with check (true);
create policy "allow_all" on settings       for all using (true) with check (true);
create policy "allow_all" on current_prices for all using (true) with check (true);
create policy "allow_all" on pin            for all using (true) with check (true);
