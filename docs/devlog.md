# Diário de construção

Registro de como o Fornalytics está sendo construído com o Claude Code e o Cowork.
Uma entrada por sessão de trabalho: o que foi pedido, o que saiu, o que precisou de correção e o que se aprendeu.

---

## 2026-11-05 — Planejamento técnico

- **Pedido:** revisar o `CLAUDE.md`, levantar pontos em aberto, definir estrutura de código e documentação.
- **Resultado:** estrutura em camadas no backend e por funcionalidade no frontend (seção 8 do `CLAUDE.md`), plano de documentação viva (seção 14), 12 pontos técnicos em aberto com recomendação (seção 15) e documento de produto atualizado para a v2.
- **Próximo passo:** Roger decidir os pontos em aberto e iniciar a Fase 0.

## 2026-11-05 — Fechamento dos pontos em aberto

- **Pedido:** debater os 12 pontos técnicos da seção 15 do `CLAUDE.md`.
- **Resultado:** todos decididos e registrados na seção 13. Ajustes do Roger em relação às recomendações: limitar a quantidade de arquivos enviados no chat (`CHAT_MAX_FILES`) e manter os testes enxutos, só no essencial, cuidando para não sobrecarregar o Neon.
- **Próximo passo:** Fase 0 (base do projeto).
