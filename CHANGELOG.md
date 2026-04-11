# Changelog

Todas as mudanças notáveis neste projeto serão documentadas aqui.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adota [Versionamento Semântico](https://semver.org/lang/pt-BR/).

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
