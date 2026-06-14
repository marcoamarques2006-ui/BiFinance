# Contribuindo com o BiFinance

Obrigado pelo interesse em contribuir! Siga as orientações abaixo.

## Configuração do ambiente

```bash
git clone https://github.com/SEU_USUARIO/bifinance.git
cd bifinance
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Fluxo de trabalho

1. Crie uma branch a partir de `main`:
   ```bash
   git checkout -b feature/nome-da-feature
   ```
2. Faça suas alterações e adicione testes quando necessário.
3. Verifique lint e testes antes de abrir o PR:
   ```bash
   ruff check .
   pytest
   ```
4. Abra um Pull Request descrevendo o que foi alterado e por quê.

## Padrões de código

- Formatação verificada por **ruff** (linha-limite: 100 chars)
- Tipos declarados com anotações (`from __future__ import annotations`)
- Novos comportamentos devem ter testes correspondentes

## Reportando bugs

Abra uma *issue* descrevendo: comportamento esperado, comportamento atual e passos para reproduzir.
