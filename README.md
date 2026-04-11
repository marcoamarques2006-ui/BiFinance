# BiFinance 💰

![CI](https://github.com/SEU_USUARIO/bifinance/actions/workflows/ci.yml/badge.svg)
![Versão](https://img.shields.io/badge/versão-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![Licença](https://img.shields.io/badge/licença-MIT-orange)

**Gerenciador de finanças pessoais com interface gráfica moderna.**

---

## Problema

Milhões de brasileiros têm dificuldade de acompanhar para onde vai o dinheiro todo mês. Sem um registro simples e acessível, é fácil perder o controle dos gastos, acumular dívidas e não conseguir poupar. Aplicativos existentes costumam ser complexos demais ou exigir cadastro em nuvem.

## Solução

O **BiFinance** é uma aplicação desktop leve que permite registrar, categorizar e visualizar despesas em segundos — sem internet, sem cadastro, com dados armazenados localmente.

## Público-alvo

Jovens adultos, estudantes e famílias que querem controlar gastos do dia a dia de forma simples e rápida.

## Funcionalidades

- Registrar despesas com descrição, valor, categoria e data
- Dashboard com total acumulado, resumo mensal e breakdown por categoria com barras de progresso
- Listagem completa de despesas com remoção individual
- 8 categorias pré-definidas (Alimentação, Transporte, Moradia, Saúde, Educação, Lazer, Vestuário, Outros)
- Alternância entre tema Dark / Light / System
- Dados persistidos localmente em JSON (`~/.bifinance/data.json`)

## Tecnologias

| Ferramenta       | Uso                        |
|------------------|----------------------------|
| Python 3.11+     | Linguagem principal        |
| customtkinter    | Interface gráfica moderna  |
| pytest           | Testes automatizados       |
| ruff             | Linting e análise estática |
| GitHub Actions   | Integração contínua (CI)   |

---

## Instalação

### Pré-requisitos

- Python 3.11 ou superior
- pip

### Passos

```bash
# Clone o repositório
git clone https://github.com/SEU_USUARIO/bifinance.git
cd bifinance

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
========================= 20 passed in 0.12s =========================
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

## Estrutura do Projeto

```
bifinance/
├── .github/
│   └── workflows/
│       └── ci.yml          # Pipeline de CI
├── src/
│   └── bifinance/
│       ├── __init__.py     # Versão do pacote
│       ├── __main__.py     # Ponto de entrada
│       ├── app.py          # Interface gráfica
│       ├── models.py       # Modelos de dados
│       └── storage.py      # Persistência JSON
├── tests/
│   ├── test_models.py
│   └── test_storage.py
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── VERSION
├── pyproject.toml
└── requirements.txt
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
