# Contribuindo com o BiFinance

Obrigado pelo interesse em contribuir!

## Configuração do ambiente

```bash
git clone https://github.com/marcoamarques2006-ui/BiFinance.git
cd BiFinance
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows
pip install -e ".[dev]" supabase
```

Copie `.env.example` para `.env` e preencha com suas credenciais Supabase:

```bash
cp .env.example .env
```

## Fluxo de trabalho (obrigatório para PRs)

1. **Crie uma issue** descrevendo o que será feito:
   - Acesse **Issues → New issue** no GitHub
   - Use um título claro: `feat: adicionar filtro por data`, `fix: erro ao remover meta`

2. **Crie uma branch** a partir de `main`:
   ```bash
   git checkout main && git pull
   git checkout -b feature/nome-da-feature
   ```
   Convenções de nome: `feature/`, `fix/`, `docs/`, `refactor/`

3. **Desenvolva e teste**:
   ```bash
   ruff check .          # lint
   pytest                # testes (usa banco in-memory, não precisa de credenciais)
   ```

4. **Abra o Pull Request**:
   - Faça push da branch: `git push -u origin feature/nome-da-feature`
   - Vá ao GitHub e clique em **Compare & pull request**
   - Preencha título, descrição e mencione a issue (`Closes #N`)
   - Aguarde o CI ficar verde (Lint + Testes)

5. **Code Review**:
   - Outro integrante deve revisar e aprovar o PR
   - Após aprovação e CI verde, faça o **Merge** para `main`

## Padrões de código

- Formatação verificada por **ruff** (linha-limite: 100 chars)
- Tipos declarados com anotações (`from __future__ import annotations`)
- Novos comportamentos devem ter testes correspondentes
- Nenhum segredo (senhas, chaves de API) deve ser commitado

## Reportando bugs

Abra uma *issue* descrevendo:
- Comportamento esperado
- Comportamento atual
- Passos para reproduzir
- Print do erro (se houver)
