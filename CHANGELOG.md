# Changelog

Todas as mudanças notáveis neste projeto serão documentadas aqui.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adota [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [2.1.0] — 2026-06-14

### Adicionado
- **Orçamento Mensal por Categoria** — defina um teto de gasto para cada categoria de despesa
- Nova tabela `budgets` no Supabase (script `migration_budgets.sql` para bancos existentes)
- Modelo `Budget` com validação (categoria válida + limite positivo)
- `finance.budget_status()` — compara gasto real do mês vs. limite, com status `ok` / `alerta` / `estourado`
- `finance.total_budgeted()` — soma de todos os limites definidos
- CRUD de orçamentos no `Storage` (`load_budgets`, `add_budget`, `remove_budget`) — um teto por categoria
- Nova view "🧮 Orçamento" na navegação, com barras de progresso coloridas por status
- Seção de Orçamento no dashboard web (Streamlit)
- 23 novos testes (124 no total); cobertura subiu para ~94%

---

## [2.0.0] — 2026-06-14

### Adicionado
- Integração completa com **Supabase (PostgreSQL na nuvem)** — sem mais JSON local
- Script `schema.sql` para criação das tabelas no banco
- Script `schema_rls.sql` com políticas de acesso Row Level Security
- `FakeSupabaseClient` in-memory para testes sem I/O de rede
- Suporte a variáveis de ambiente `SUPABASE_URL` / `SUPABASE_KEY` via `.env`
- Arquivo `.env.example` como template para novas instalações
- Dashboard web publicado via **Streamlit Cloud** com dados reais do Supabase
- Relatório de cobertura de testes no CI (pytest-cov)
- Upload automático do resumo de cobertura no GitHub Actions Step Summary
- Dois jobs separados no CI: `Lint` e `Testes` (test depende de lint passar)
- Branch protection na `main` exigindo CI verde + 1 aprovação antes do merge

### Alterado
- `Storage` migrado de JSON local para tabelas Supabase (`transactions`, `dollar_entries`, `goals`, `settings`, `current_prices`, `pin`)
- `Storage.__init__` aceita `_client` para injeção de dependência em testes
- Suíte de testes ampliada de 20 para **101 testes** (4 módulos: models, finance, storage, integration)
- `pyproject.toml` atualizado: `supabase>=2.0` em `dependencies`, `pytest-cov>=5.0` em `dev`
- Versão bumpeada de 1.0.0 → 2.0.0 (breaking change: sem retrocompatibilidade com JSON local)
- LICENSE corrigido com nome real do autor

### Removido
- Persistência local em JSON (`~/.bifinance/data.json`) removida completamente

---

## [1.0.0] — 2026-04-11

### Adicionado
- Interface gráfica com customtkinter (tema dark/light/system)
- Sidebar com navegação entre Dashboard, Despesas e Adicionar
- Dashboard com total acumulado, resumo mensal e breakdown por categoria
- Barras de progresso coloridas por categoria no Dashboard
- Listagem de despesas ordenada por data com remoção individual
- Formulário de cadastro de despesas com validação de entrada
- 8 categorias pré-definidas com cores distintas
- Persistência local em JSON (`~/.bifinance/data.json`)
- Modelos de dados com validação (`Expense.validate()`)
- Testes automatizados com pytest (20 testes cobrindo models e storage)
- Linting configurado com ruff
- Pipeline de CI com GitHub Actions (lint + testes)
- Versionamento semântico 1.0.0
