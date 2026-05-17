# BiFinance 💰

![CI](https://github.com/marcoamarques2006-ui/BiFinance/actions/workflows/ci.yml/badge.svg)
![Versão](https://img.shields.io/badge/versão-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![Licença](https://img.shields.io/badge/licença-MIT-orange)

**🌐 Deploy (versão web):** [bifinance.streamlit.app](https://bifinance.streamlit.app)

**Gerenciador de finanças pessoais com interface gráfica moderna.**

---

## Problema

Milhões de brasileiros têm dificuldade de acompanhar para onde vai o dinheiro todo mês. Sem um registro simples e acessível, é fácil perder o controle dos gastos, acumular dívidas e não conseguir poupar. Aplicativos existentes costumam ser complexos demais ou exigir cadastro em nuvem.

## Solução

O **BiFinance** é uma aplicação desktop leve que permite registrar, categorizar e visualizar receitas, despesas e investimentos em segundos — sem internet, sem cadastro, com dados armazenados localmente.

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
- Dados persistidos localmente em JSON (`~/.bifinance/data.json`)

## Tecnologias

| Ferramenta       | Uso                          |
|------------------|------------------------------|
| Python 3.11+     | Linguagem principal          |
| customtkinter    | Interface gráfica moderna    |
| matplotlib       | Gráficos e visualizações     |
| requests         | Consumo de API (cotação USD) |
| streamlit        | Dashboard web (deploy)       |
| pytest           | Testes automatizados         |
| ruff             | Linting e análise estática   |
| GitHub Actions   | Integração contínua (CI)     |

---

## Instalação

### Pré-requisitos

- Python 3.11 ou superior
- pip

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

---

## Execução

```bash
# Via comando instalado
bifinance

# Ou diretamente como módulo
python -m bifinance
```

---

## Testes

```bash
# Instale as dependências de desenvolvimento
pip install -e ".[dev]"

# Execute os testes
pytest
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

Para corrigir automaticamente problemas de formatação:

```bash
ruff check . --fix
```

---

## Deploy

A versão web do BiFinance está publicada em:

**[bifinance.streamlit.app](https://bifinance.streamlit.app)**

Exibe a cotação USD/BRL em tempo real (via [AwesomeAPI](https://economia.awesomeapi.com.br)) e o resumo financeiro. Para rodar o dashboard localmente:

```bash
pip install -r requirements-web.txt
streamlit run streamlit_app.py
```

---

## Estrutura do Projeto

```
BiFinance/
├── .github/
│   └── workflows/
│       └── ci.yml              # Pipeline de CI
├── scripts/
│   └── seed_demo.py            # Script de dados de demonstração
├── src/
│   └── bifinance/
│       ├── __init__.py         # Versão do pacote
│       ├── __main__.py         # Ponto de entrada
│       ├── api_client.py       # Consumo da API de cotações (AwesomeAPI)
│       ├── app.py              # Interface gráfica (7 views)
│       ├── charts.py           # Gráficos matplotlib
│       ├── finance.py          # Lógica de negócio e cálculos
│       ├── models.py           # Modelos de dados
│       └── storage.py          # Persistência JSON
├── tests/
│   ├── test_finance.py         # 41 testes de lógica financeira
│   ├── test_integration.py     # 3 testes de integração (API)
│   ├── test_models.py          # 35 testes de modelos
│   └── test_storage.py         # 22 testes de persistência
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── VERSION
├── pyproject.toml
├── requirements.txt
├── requirements-web.txt        # Dependências para deploy web
└── streamlit_app.py            # Dashboard web (Streamlit)
```

---

## Versão

**1.0.0** — ver [CHANGELOG.md](CHANGELOG.md)

## Autor

Marco Antonio Marques Monte — [marcoamarques2006@gmail.com](mailto:marcoamarques2006@gmail.com)

## Repositório

[https://github.com/marcoamarques2006-ui/BiFinance](https://github.com/marcoamarques2006-ui/BiFinance)

## Licença

Distribuído sob a licença MIT. Ver [LICENSE](LICENSE) para detalhes.
