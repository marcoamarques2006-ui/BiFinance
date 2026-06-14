# BiFinance 💰

![CI](https://github.com/marcoamarques2006-ui/BiFinance/actions/workflows/ci.yml/badge.svg)
![Versão](https://img.shields.io/badge/versão-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![Licença](https://img.shields.io/badge/licença-MIT-orange)
![Banco](https://img.shields.io/badge/banco-Supabase-3ECF8E)
![Cobertura](https://img.shields.io/badge/cobertura-≥70%25-brightgreen)

**🌐 Deploy (versão web):** [bifinance-nahy8rhsn9xstsgzzdmdup.streamlit.app](https://bifinance-nahy8rhsn9xstsgzzdmdup.streamlit.app)

**Gerenciador de finanças pessoais com interface gráfica moderna e banco de dados na nuvem.**

---

## Problema

Milhões de brasileiros têm dificuldade de acompanhar para onde vai o dinheiro todo mês. Sem um registro simples e acessível, é fácil perder o controle dos gastos, acumular dívidas e não conseguir poupar. Aplicativos existentes costumam ser complexos demais ou exigir cadastro em nuvem.

## Solução

O **BiFinance** é uma aplicação que permite registrar, categorizar e visualizar receitas, despesas e investimentos em segundos. Os dados ficam persistidos em um banco de dados PostgreSQL na nuvem (Supabase), acessíveis de qualquer dispositivo.

## Público-alvo

Jovens adultos, estudantes e famílias que querem controlar gastos, investimentos e metas financeiras de forma simples e rápida.

## Funcionalidades

- **Dashboard** com KPIs de patrimônio, receita, gastos e proventos, além de gráficos de barras, rosca e comparativo com CDI
- **Transações** — registro de receitas, despesas, compras/vendas de ativos e dividendos com validação de dados
- **Investimentos** — carteira com custo médio ponderado, P&L não realizado e atualização de preço por ativo
- **Dólar** — registro de compras em USD com IOF + spread, custo médio efetivo e P&L vs. taxa atual
- **Metas** — criação e acompanhamento de metas financeiras com barra de progresso
- **Relatórios** — saldo acumulado, histórico mensal e análise de "pequenos vícios" com projeção anual
- **Configurações** — taxa CDI e IOF padrão configuráveis
- Dados persistidos em **Supabase (PostgreSQL na nuvem)**

## Tecnologias

| Ferramenta       | Versão mínima | Uso                               |
|------------------|---------------|-----------------------------------|
| Python           | 3.11+         | Linguagem principal               |
| customtkinter    | 5.2.2+        | Interface gráfica moderna         |
| matplotlib       | 3.8+          | Gráficos e visualizações          |
| requests         | 2.31+         | Consumo de API (cotação USD)      |
| supabase-py      | 2.0+          | Banco de dados PostgreSQL (nuvem) |
| streamlit        | —             | Dashboard web (deploy)            |
| pytest           | 8.0+          | Testes automatizados              |
| pytest-cov       | 5.0+          | Relatório de cobertura            |
| ruff             | 0.4+          | Linting e análise estática        |
| GitHub Actions   | —             | Integração contínua (CI)          |

---

## Instalação

### Pré-requisitos

- Python 3.11 ou superior
- pip
- Conta no [Supabase](https://supabase.com) com projeto configurado

### Passos

```bash
# Clone o repositório
git clone https://github.com/marcoamarques2006-ui/BiFinance.git
cd BiFinance

# (Opcional) Crie um ambiente virtual
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows

# Instale as dependências
pip install -e .
```

### Configuração do Banco de Dados

1. Crie um projeto no [Supabase](https://supabase.com)
2. No SQL Editor do Supabase, execute o script `schema.sql`
3. Em seguida, execute o script `schema_rls.sql` para configurar as políticas de acesso (RLS)
4. Copie `.env.example` para `.env` e preencha com suas credenciais:

```bash
cp .env.example .env
```

```env
SUPABASE_URL=https://<seu-projeto>.supabase.co
SUPABASE_KEY=<sua-anon-key>
```

> **Segurança:** nunca commite o arquivo `.env`. Ele já está no `.gitignore`.

---

## Execução

```bash
# Exportar variáveis de ambiente (Windows PowerShell)
$env:SUPABASE_URL="https://seu-projeto.supabase.co"
$env:SUPABASE_KEY="sua-anon-key"

# Via comando instalado
bifinance

# Ou diretamente como módulo
python -m bifinance
```

---

## Testes

Os testes usam um cliente Supabase **in-memory** — nenhuma credencial real é necessária.

```bash
# Instale as dependências de desenvolvimento
pip install -e ".[dev]" supabase

# Execute os testes com relatório de cobertura
pytest --cov=src/bifinance --cov-report=term-missing
```

Saída esperada:

```
101 passed in 0.60s
```

---

## Linting

```bash
ruff check .
```

---

## Deploy

A versão web do BiFinance está publicada em:

**[bifinance-nahy8rhsn9xstsgzzdmdup.streamlit.app](https://bifinance-nahy8rhsn9xstsgzzdmdup.streamlit.app)**

Exibe cotação USD/BRL em tempo real e o resumo financeiro com dados reais do Supabase.

Para rodar o dashboard localmente:

```bash
pip install -r requirements-web.txt
streamlit run streamlit_app.py
```

---

## Pipeline de CI/CD

O repositório usa **GitHub Actions** com dois jobs em sequência:

1. **Lint** — executa `ruff check .` para garantir qualidade de código
2. **Testes** — executa `pytest` com `pytest-cov` e publica o relatório de cobertura no Step Summary

A branch `main` está protegida: o CI precisa estar verde **e** pelo menos 1 aprovação de revisor é exigida antes de qualquer merge.

---

## Estrutura do Projeto

```
BiFinance/
├── .github/
│   └── workflows/
│       └── ci.yml              # Pipeline CI (Lint + Testes)
├── src/
│   └── bifinance/
│       ├── __init__.py         # Versão do pacote
│       ├── __main__.py         # Ponto de entrada
│       ├── api_client.py       # API de cotações USD/BRL (AwesomeAPI + fallback)
│       ├── app.py              # Interface gráfica customtkinter (7 views)
│       ├── charts.py           # Gráficos matplotlib
│       ├── finance.py          # Lógica de negócio e cálculos financeiros
│       ├── models.py           # Modelos de dados (Transaction, Goal, Settings…)
│       ├── storage.py          # Persistência Supabase (PostgreSQL)
│       ├── theme.py            # Design tokens e estrutura de navegação
│       └── views/              # Módulos de interface (dashboard, transações…)
├── tests/
│   ├── fake_supabase.py        # Cliente Supabase in-memory para testes
│   ├── test_finance.py         # 41 testes de lógica financeira
│   ├── test_integration.py     # 3 testes de integração (API externa)
│   ├── test_models.py          # 35 testes de modelos de dados
│   └── test_storage.py         # 22 testes de persistência
├── .env.example                # Template de variáveis de ambiente
├── schema.sql                  # Schema do banco de dados Supabase
├── schema_rls.sql              # Políticas de acesso Row Level Security
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── VERSION
├── pyproject.toml
├── requirements.txt
├── requirements-web.txt
└── streamlit_app.py            # Dashboard web (Streamlit Cloud)
```

---

## Versão

**2.0.0** — ver [CHANGELOG.md](CHANGELOG.md)

## Equipe

| Nome | Matrícula |
|------|-----------|
| Marco Antonio Marques Monte | 22503865 |

## Repositório

[https://github.com/marcoamarques2006-ui/BiFinance](https://github.com/marcoamarques2006-ui/BiFinance)

## Licença

Distribuído sob a licença MIT. Ver [LICENSE](LICENSE) para detalhes.
