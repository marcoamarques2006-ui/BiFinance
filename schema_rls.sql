-- BiFinance — Políticas de acesso (RLS)
-- Execute no SQL Editor do Supabase após o schema.sql

-- Desabilita RLS nas tabelas (app pessoal, sem multiusuário)
alter table transactions   disable row level security;
alter table dollar_entries disable row level security;
alter table goals          disable row level security;
alter table budgets        disable row level security;
alter table settings       disable row level security;
alter table current_prices disable row level security;
alter table pin            disable row level security;
