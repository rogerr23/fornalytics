# Runbook

Problemas que já aconteceram e como resolver. Entra aqui todo problema que tomou mais de 10 minutos.

## A IA responde "O limite gratuito da IA foi atingido"

O plano gratuito do Gemini tem dois limites. A mensagem mostra qual dos dois foi atingido:

| Mensagem | O que é | O que fazer |
|---|---|---|
| "Tente de novo em 30 segundos" (ou poucos minutos) | Limite **por minuto** (requisições ou tokens). Comum ao processar um repositório grande logo depois de outra chamada | Esperar o tempo indicado e clicar em **Tentar de novo**. As novas tentativas automáticas (até 3, no máximo 30s de espera) já cobrem a maioria dos casos |
| "É o limite diário do plano gratuito: tente de novo em cerca de N horas" | Limite **diário**: acabaram as chamadas do dia para aquele modelo | Esperar a virada do dia (horário do Pacífico) ou trocar o `GEMINI_MODEL` por outro modelo Flash com cota própria (`npm run llm:models` lista os disponíveis). Não repetir o botão: cada clique gasta uma tentativa |

**Como economizar cota durante o desenvolvimento:**
- Testes automáticos nunca chamam a IA (`FakeProvider`).
- Processar um projeto custa 1 ou 2 chamadas; cada visão geral, 1 na primeira abertura de cada lente; cada pergunta do chat, 1.
- Em 06/11/2026, um dia de desenvolvimento das Fases 4 a 6 (vários processamentos reais com cerca de 56 a 87 mil tokens de código cada, mais visões gerais e perguntas) esgotou a cota diária do `gemini-3.5-flash`.

## A IA responde "alta demanda ou instável" (503)

É comum no plano gratuito e costuma passar em segundos. O backend já tenta de novo sozinho; se mesmo assim falhar, clique em **Tentar de novo**.

## Testar a tela sem gastar cota

Para conferir a interface (streaming, citações, chat) sem a IA real, dá para subir a API com um provedor simulado num script local, fora do repositório: `create_app()` + `app.dependency_overrides[get_llm_provider] = lambda: FakeProvider([...])` + `uvicorn.run(app, port=8000)`, com o frontend rodando à parte (`npm --prefix frontend run dev`). Foi assim que a Fase 6 foi conferida depois que a cota diária acabou.
