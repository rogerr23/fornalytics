# 0001 — Backend em camadas e frontend por funcionalidade

- **Data:** 2026-11-05
- **Status:** aceita

## Contexto

O projeto tem várias funcionalidades que compartilham a mesma base (lentes, "Isso faz?", Ideia × Código, fluxos), usa dois provedores de IA intercambiáveis e precisa ser testável sem chamar a API real. O código precisa continuar organizado à medida que as fases avançam.

## Opções consideradas

1. **Tudo nos routers** — rápido no começo, mas mistura HTTP, banco e IA; difícil de testar e de trocar o provedor.
2. **Camadas (api → serviços → domain / repositories / llm)** — mais arquivos, mas cada parte tem um papel único e as dependências podem ser trocadas nos testes.
3. **Arquitetura hexagonal completa** (portas e adaptadores para tudo) — muito isolamento, cerimônia demais para um protótipo.

No frontend: organizar por **tipo** (`components/`, `hooks/`, `services/`) ou por **funcionalidade** (`features/chat`, `features/idea-vs-code`…).

## Decisão

Backend em camadas (opção 2), usando só os padrões listados na seção 8.2 do `CLAUDE.md`. Frontend organizado por funcionalidade, com `shared/` para o que é comum.

## Consequências

- Trocar Gemini por Ollama (ou Claude no futuro) não mexe em serviço nenhum.
- Testes usam `FakeProvider` injetado, sem rede.
- Cada funcionalidade nova do frontend é uma pasta isolada.
- Custo: mais arquivos e algumas camadas finas; aceitável pelo ganho de clareza.
