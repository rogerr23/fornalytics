# Fornalytics — Um produto, várias explicações

> Projeto do Programa de Estágio Extreme Group · Desafio de IA com Claude
> Autor: Roger Santos · Documento de produto · v2 (05/11/2026)
>
> Este é o documento de **produto** (problema, solução, jornada, impacto). As decisões técnicas e o plano de construção ficam no `CLAUDE.md`.

---

## 1. Visão geral

O **Fornalytics** é uma ferramenta que entende um produto digital a partir do que já existe sobre ele (código, documento da ideia ou transcrição de reunião) e explica esse produto de formas diferentes, conforme quem está perguntando: **cliente**, **pessoa não técnica** ou **desenvolvedor**.

Tudo parte de uma **base do produto** única, montada uma vez a partir do material enviado. As lentes mudam a forma da explicação, nunca a essência.

---

## 2. O problema

Hoje, o mesmo produto é explicado várias vezes, por pessoas diferentes e de jeitos diferentes, e algo sempre se perde nessa tradução.

| Quem sofre | Dor do dia a dia |
|---|---|
| **Devs / Tech Lead** | Perdem tempo explicando o produto para não técnicos; são interrompidos o tempo todo com "isso o sistema faz?" |
| **Dev novo no projeto** | Leva dias para entender a arquitetura, o código e as regras de negócio |
| **PO / PM** | Precisa traduzir entregas técnicas para o cliente e para a diretoria |
| **Comercial / Atendimento** | Não sabe com segurança o que o produto faz e corre o risco de prometer o que não existe |
| **Cliente** | Não entende o que está pagando nem o que foi entregue |

**Consequências:** retrabalho, reuniões de alinhamento em excesso, ruído entre as áreas, onboarding lento e documentação que ninguém mantém.

---

## 3. A solução

Um sistema em três etapas:

```
┌──────────────┐      ┌──────────────────┐      ┌─────────────────────────┐
│   ENTRADA    │ ───▶ │   ENTENDIMENTO   │ ───▶ │   SAÍDA (por lente)     │
│              │      │                  │      │                         │
│ • Repositório│      │ Base do produto: │      │ • Cliente               │
│ • Doc da     │      │ • o que faz      │      │ • Não técnico           │
│   ideia/PDF  │      │ • fluxos         │      │ • Técnico (dev)         │
│ • Transcrição│      │ • regras         │      │                         │
│ • Texto livre│      │ • arquitetura    │      │ + chat, lado a lado,    │
│              │      │ • integrações    │      │   "Isso faz?", fluxos   │
└──────────────┘      └──────────────────┘      └─────────────────────────┘
```

### 3.1 Entradas aceitas

- **Repositório de código:** um `.zip` do projeto
- **Documento da ideia:** PDF, `.docx`, `.md` ou `.txt` (escopo, proposta, briefing)
- **Transcrição:** de uma reunião de kickoff ou de discovery
- **Texto livre:** descrição colada direto no sistema

As entradas podem ser **combinadas** (por exemplo, ideia + código), o que habilita a comparação entre o que foi prometido e o que foi feito.

### 3.2 As lentes

| Lente | Para quem | Tom e conteúdo |
|---|---|---|
| 👔 **Cliente** | Cliente final, stakeholders | Valor, problema resolvido, benefícios. Sem jargão. Frases curtas, tom confiante. |
| 🙋 **Não técnico** | Comercial, atendimento, gestão, RH | Como funciona na prática, fluxos simples, analogias do dia a dia. |
| 💻 **Técnico** | Devs, Tech Lead | Arquitetura, stack, pastas, endpoints, banco, onde mexer. **Sempre** citando arquivo e linhas. |

**A regra de ouro:** a mesma pergunta tem respostas diferentes em cada lente, mas a **essência é sempre a mesma**.

**Exemplo — "Como funciona o pagamento?"**

- 👔 **Cliente:** "Seu cliente paga com cartão ou Pix em poucos cliques, com segurança, e recebe a confirmação na hora por e-mail."
- 🙋 **Não técnico:** "Quando a pessoa finaliza a compra, o sistema envia os dados para a empresa de pagamento (como uma maquininha online). Se aprovado, o pedido muda para 'pago' e um e-mail é disparado."
- 💻 **Técnico:** "O `CheckoutController` chama o `PaymentService.process()` (`src/services/payment.ts:12-40`), que integra com o gateway via REST. O webhook em `/api/webhooks/payment` atualiza o status do `Order` e enfileira o e-mail no `NotificationQueue`."

### 3.3 Confiança nas respostas

O maior risco de uma ferramenta assim é inventar funcionalidades. O Fornalytics combate isso de três formas:

1. A IA só responde com base no material e diz "não encontrei no material" quando falta base.
2. Toda citação (arquivo + linhas + trecho) é **conferida pelo sistema** antes de aparecer na tela. Citação que não bate com o arquivo é descartada ou marcada como não verificada.
3. Na interface, cada citação válida é um link que abre o trecho real do arquivo.

---

## 4. Funcionalidades

### 4.1 Núcleo (MVP, o que precisa funcionar no protótipo)

- [ ] **Entrada de conteúdo:** upload de arquivo e/ou texto colado
- [ ] **Três lentes** alternáveis a qualquer momento
- [ ] **Visão geral automática:** ao terminar o processamento, mostra um resumo do produto na lente ativa
- [ ] **Chat com o produto:** perguntar qualquer coisa na lente escolhida, com resposta em tempo real

### 4.2 Diferenciais (entram no protótipo)

- [ ] **Ideia × Código** (diferencial principal): compara o documento da ideia com o repositório
  - ✅ Prometido e implementado
  - ⚠️ Prometido e **não** implementado
  - 🔍 Implementado e **não** documentado
- [ ] **"Isso o produto faz?":** responde sim, não ou parcialmente, com justificativa e evidências (pensado para o comercial)
- [ ] **Lado a lado:** a mesma pergunta respondida nas três lentes ao mesmo tempo (o momento "uau" da demo)
- [ ] **Explicador de fluxo com diagrama:** "o que acontece quando o usuário clica em X?" gera um passo a passo e um diagrama (Mermaid)

### 4.3 Futuro (vai para o slide de "próximos passos")

- Onboarding com trilha de leitura do código e quiz no final
- Tour guiado do produto
- Mapa de impacto ("se eu mudar X, o que é afetado?")
- "Onde eu mexo?", que aponta arquivos a partir de uma mudança desejada
- Glossário vivo (termo técnico → explicação por lente)
- Explicador de entrega/changelog para o cliente
- Saúde do projeto (partes sem documentação, complexidade, riscos)
- Documentos prontos por público (one-pager, guia de uso, README)
- Lentes personalizadas (investidor, jurídico, QA…)
- Linha do tempo do produto (comparação entre versões)
- Compartilhar uma lente por link
- Integração direta com GitHub/GitLab e atualização automática a cada commit
- Uso do Claude como IA em execução (a arquitetura já está pronta para trocar o provedor)

---

## 5. Jornada de uso (cenário da demo)

Material da demo: uma loja simples criada para isso (`demo/`), com um documento de escopo que tem lacunas propositais.

1. **Ana (PO)** cria um projeto no Fornalytics e envia o PDF do escopo e o `.zip` do repositório.
2. O Fornalytics processa os arquivos, mostrando cada etapa, e abre a **visão geral** na lente *Não técnico*.
3. Ana troca para a lente **Cliente** e copia o resumo para enviar ao cliente.
4. **Bruno (comercial)** abre a aba **Isso faz?** e pergunta: *"O sistema gera nota fiscal?"* → **Não.** A emissão de nota fiscal está no escopo, mas não foi encontrada no código.
5. **Carla (dev nova)** abre a lente **Técnico** e pergunta *"como funciona o login?"*, recebendo a explicação com links para os arquivos e linhas exatas.
6. Na aba **Lado a lado**, a mesma pergunta aparece nas três lentes, mostrando que a essência não muda.
7. Ana abre a aba **Ideia × Código** e descobre que 2 funcionalidades do escopo ainda não existem e 1 foi feita sem estar documentada. O risco é identificado antes da entrega.

---

## 6. Como construir

### 6.1 Abordagem escolhida: Opção C (híbrida)

Foram avaliados três caminhos:

| Opção | Ideia | Prós | Contras |
|---|---|---|---|
| A | Projeto no Claude com instruções e arquivos | Rápido, sem código | Pouco visual, parece "só um chat" |
| B | Aplicação web própria | Visual, demo forte, parece produto | Exige mais tempo |
| **C** ✅ | Validar os prompts primeiro e depois levá-los para a aplicação web | O "cérebro" chega testado na interface | — |

### 6.2 Como fica na prática

- **Construção:** todo o projeto é construído com o **Claude Code** e o **Cowork**. É aqui que entra o Claude no desafio.
- **IA dentro do app:** **Gemini** no plano gratuito do Google AI Studio, com **Ollama** (modelo local) como reserva. Custo zero.
- **Aplicação:** backend em Python (FastAPI), frontend em React, banco PostgreSQL na nuvem (Neon, plano gratuito).
- **Portabilidade:** roda em qualquer computador com `git clone`, um arquivo `.env` e um comando.
- Os detalhes técnicos estão no `CLAUDE.md`.

### 6.3 Pontos técnicos e como foram resolvidos

| Tema | Desafio | Abordagem adotada |
|---|---|---|
| **Repositórios grandes** | O código inteiro pode não caber no contexto ou gastar a cota | Ignorar `node_modules`, builds, assets e arquivos grandes; priorizar README, rotas, models e services; avisar quando passar do limite |
| **Formatos de arquivo** | PDF, docx, zip | Extrair o texto antes de enviar ao modelo; guardar só o texto |
| **Consistência entre lentes** | Respostas não podem se contradizer | Base do produto única; todas as lentes derivam dela |
| **Alucinação** | A IA pode inventar funcionalidades | Responder "não encontrei" quando faltar base; validação automática de citações |
| **Diagramas** | Visualizar os fluxos | Saída em Mermaid renderizada na interface |
| **Limite do plano gratuito** | A cota de chamadas é pequena | Base e visões gerais salvas no banco; nova tentativa automática; aviso amigável |
| **Confidencialidade** | O plano gratuito pode usar o conteúdo enviado | Usar apenas o repositório de demo próprio ou projetos open source |

### 6.4 Esboço dos prompts por lente

Ponto de partida dos arquivos em `backend/app/prompts/`.

```
[BASE — sempre]
Você é o Fornalytics. Explique o produto com base APENAS no material fornecido.
Se algo não estiver no material, diga claramente: "não encontrei no material".

[LENTE CLIENTE]
Público: cliente final, sem conhecimento técnico.
Foque em valor, benefícios e problema resolvido. Sem jargão. Frases curtas.

[LENTE NÃO TÉCNICO]
Público: colaboradores de áreas como comercial, atendimento e gestão.
Explique como funciona na prática, use analogias do dia a dia e fluxos simples.

[LENTE TÉCNICO]
Público: desenvolvedores.
Detalhe arquitetura, stack, arquivos, funções e integrações.
SEMPRE cite o arquivo e as linhas de onde tirou a informação.
```

---

## 7. Impacto esperado

| Indicador | Como medir | Meta (hipótese, validar) |
|---|---|---|
| Tempo de onboarding de dev | Dias até a primeira entrega | Reduzir em ~50% |
| Interrupções ao time técnico | Perguntas "isso faz X?" por semana | Reduzir significativamente |
| Tempo para preparar a explicação ao cliente | Horas por entrega/apresentação | De horas para minutos |
| Gaps de escopo detectados cedo | Itens apontados pelo Ideia × Código | Encontrar antes da entrega |
| Alinhamento entre áreas | Pesquisa rápida antes/depois | Aumentar a clareza percebida |

**Abrangência:** atinge tecnologia, produto, comercial, atendimento e o próprio cliente, ou seja, **o grupo todo**, o que conversa com o objetivo coletivo do programa.

---

## 8. Mapeamento com as entregas e os critérios

### Entregas

| Entrega | O que levar do Fornalytics |
|---|---|
| **Canvas do processo** | Problema (seção 2), público, solução (3), funcionalidades (4), impacto (7), riscos (11) |
| **Protótipo** | MVP (4.1) e os diferenciais (4.2), com destaque para o **Ideia × Código** |
| **Apresentação** | Dor → demo ao vivo (lado a lado nas 3 lentes, "Isso faz?", Ideia × Código) → impacto → próximos passos (4.3) |

### Critérios de avaliação

| Critério | Como o Fornalytics atende |
|---|---|
| Problema identificado | Dor real e transversal a várias áreas |
| Solução proposta | Fonte única de verdade, explicada por lentes |
| Impacto esperado | Métricas de tempo, onboarding e alinhamento |
| Viabilidade | Construído com Claude Code, custo zero para rodar, roda em qualquer computador |
| Protótipo desenvolvido | Funcional, com troca de lente ao vivo e citações verificadas |
| Apresentação | Demo visual, com resultado previsível graças ao repositório de demo |

---

## 9. Plano de trabalho

| Etapa | Atividade | Resultado |
|---|---|---|
| 1 | Validar a dor com colegas | Evidências para o Canvas |
| 2 | Preencher o Canvas com base na cartilha | **Entrega 1** |
| 3 | Construir a base técnica do projeto (fases 0 a 4 do `CLAUDE.md`) | Upload, processamento e base do produto |
| 4 | Criar e testar os prompts das lentes | "Cérebro" validado |
| 5 | Construir a interface do MVP (fases 5 e 6) | MVP funcionando |
| 6 | Adicionar os diferenciais (fases 7 a 9) | Protótipo completo, **Entrega 2** |
| 7 | Montar o repositório de demo e testar de ponta a ponta (fases 10 e 11) | Demo previsível |
| 8 | Testar com colegas, ajustar, montar os slides e ensaiar | **Entrega 3** |

---

## 10. Decisões

### Tomadas

- [x] Nome: **Fornalytics**
- [x] Abordagem: **Opção C** (prompts validados primeiro, depois a interface)
- [x] Três lentes fixas (sem slider de profundidade)
- [x] Diferenciais no protótipo: **Ideia × Código** (principal), "Isso faz?", lado a lado e fluxo com diagrama
- [x] Demo com repositório próprio (`demo/`) e escopo com lacunas propositais
- [x] IA em execução gratuita (Gemini + Ollama); Claude usado na construção
- [x] Onboarding com quiz fica para o futuro

### Em aberto

- [ ] Quais colegas entrevistar para validar a dor
- [ ] Prazo de cada entrega do programa

---

## 11. Riscos e cuidados

- **Confidencialidade:** nunca usar código ou documento de cliente real; o plano gratuito do Gemini pode usar o conteúdo enviado.
- **Respostas inventadas:** prompts restritos ao material + validação automática de citações.
- **Limite do plano gratuito:** cache no banco, nova tentativa automática e Ollama como reserva.
- **Escopo grande demais:** priorizar o MVP; o resto vira "próximos passos".
- **Repositório muito grande:** usar o projeto de demo, pequeno e controlado.
- **Dependência da demo ao vivo:** respostas da demo salvas como reserva, além de vídeo ou prints.
