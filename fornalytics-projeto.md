# Fornalytics — Um produto, várias explicações

> Projeto do Programa de Estágio Extreme Group · Desafio de IA com Claude
> Autor: Roger Santos · Documento de trabalho (versão inicial)

---

## 1. Visão geral

O **Fornalytics** é uma ferramenta que entende um produto digital a partir do que já existe sobre ele (código, documento da ideia ou transcrição de reunião) e explica esse produto de formas diferentes, conforme quem está perguntando: **cliente**, **pessoa não técnica** ou **desenvolvedor**.

**A metáfora:** um prisma recebe uma única luz e a divide em várias cores. Aqui, a luz é o produto e as cores são as explicações para cada público. A fonte de verdade é uma só, então todos ouvem a mesma coisa, só que em linguagens diferentes.

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

> 📌 **A validar:** conversar com 3 a 5 Extremers (dev, PO, comercial) para levantar evidências e números reais da dor. Isso alimenta o Canvas.

---

## 3. A solução

Um sistema em três etapas:

```
┌──────────────┐      ┌──────────────────┐      ┌─────────────────────────┐
│   ENTRADA    │ ───▶ │   ENTENDIMENTO   │ ───▶ │   SAÍDA (por lente)     │
│              │      │                  │      │                         │
│ • Repositório│      │ Base do produto: │      │ 👔 Cliente              │
│ • Doc da     │      │ • o que faz      │      │ 🙋 Não técnico          │
│   ideia/PDF  │      │ • fluxos         │      │ 💻 Técnico (dev)        │
│ • Transcrição│      │ • regras         │      │                         │
│ • Texto livre│      │ • arquitetura    │      │ + chat, diagramas,      │
│              │      │ • integrações    │      │   documentos prontos    │
└──────────────┘      └──────────────────┘      └─────────────────────────┘
```

### 3.1 Entradas aceitas

- **Repositório de código:** um .zip ou os arquivos principais
- **Documento da ideia:** PDF, .docx, .md (escopo, proposta, briefing)
- **Transcrição:** de uma reunião de kickoff ou de discovery
- **Texto livre:** descrição colada direto no sistema

As entradas podem ser **combinadas** (por exemplo, ideia + código), o que habilita a comparação entre o que foi prometido e o que foi feito.

### 3.2 As lentes

| Lente | Para quem | Tom e conteúdo |
|---|---|---|
| 👔 **Cliente** | Cliente final, stakeholders | Valor, problema resolvido, benefícios. Sem jargão. Tom comercial e confiante. |
| 🙋 **Não técnico** | Comercial, atendimento, gestão, RH | Como funciona na prática, fluxos simples, analogias do dia a dia. |
| 💻 **Técnico** | Devs, Tech Lead | Arquitetura, stack, pastas, endpoints, banco, onde mexer. Sempre citando arquivo e trecho. |

**A regra de ouro:** a mesma pergunta tem respostas diferentes em cada lente, mas a **essência é sempre a mesma**.

**Exemplo — "Como funciona o pagamento?"**

- 👔 **Cliente:** "Seu cliente paga com cartão ou Pix em poucos cliques, com segurança, e recebe a confirmação na hora por e-mail."
- 🙋 **Não técnico:** "Quando a pessoa finaliza a compra, o sistema envia os dados para a empresa de pagamento (como uma maquininha online). Se aprovado, o pedido muda para 'pago' e um e-mail é disparado."
- 💻 **Técnico:** "O `CheckoutController` chama o `PaymentService.process()` (`src/services/payment.ts`), que integra com o gateway via REST. O webhook em `/api/webhooks/payment` atualiza o status do `Order` e enfileira o e-mail no `NotificationQueue`."

---

## 4. Funcionalidades

### 4.1 Núcleo (MVP, o que precisa funcionar no protótipo)

- [ ] **Entrada de conteúdo:** upload de arquivo e/ou texto colado
- [ ] **Três lentes** alternáveis a qualquer momento
- [ ] **Chat com o produto:** perguntar qualquer coisa na lente escolhida
- [ ] **Visão geral automática:** ao carregar, gera um resumo do produto na lente ativa

### 4.2 Diferenciais (prioridade alta, se der tempo)

- [ ] **Ideia × Código:** compara o documento da ideia com o repositório
  - ✅ Prometido e implementado
  - ⚠️ Prometido e **não** implementado
  - 🔍 Implementado e **não** documentado
- [ ] **Explicador de fluxo com diagrama:** "o que acontece quando o usuário clica em X?" gera um fluxo passo a passo e um diagrama (Mermaid)
- [ ] **"Isso o produto faz?":** responde sim, não ou parcialmente, com justificativa (pensado para o comercial)
- [ ] **Onboarding com trilha:** roteiro de leitura do código para o dev novo, com um quiz no final

### 4.3 Futuro (vai para o slide de "próximos passos")

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

---

## 5. Jornada de uso (cenário da demo)

1. **Ana (PO)** cria um projeto no Prisma e envia o PDF do escopo e o .zip do repositório.
2. O Prisma processa os arquivos e mostra a **visão geral** na lente *Não técnico*.
3. Ana troca para a lente **Cliente** e copia o resumo para enviar ao cliente.
4. **Bruno (comercial)** pergunta: *"O sistema gera nota fiscal?"* → resposta: **Parcialmente.** Gera o recibo, mas a emissão da NF não está implementada.
5. **Carla (dev nova)** abre a lente **Técnico**, segue a trilha de onboarding e pergunta *"como funciona a autenticação?"*, recebendo arquivos e trechos de código.
6. Ana abre a aba **Ideia × Código** e descobre que 2 funcionalidades do escopo ainda não existem. O risco é identificado antes da entrega.

---

## 6. Como construir (caminhos possíveis)

### Opção A — Projeto no Claude (mais simples)
- Criar um **Projeto** no Claude com instruções detalhadas (o "cérebro" das lentes).
- Subir os arquivos do produto no conhecimento do projeto.
- A troca de lente é feita por comando no chat (`/cliente`, `/leigo`, `/dev`).
- ✅ Rápido e sem código · ❌ Pouco visual, parece "só um chat"

### Opção B — Aplicação web com a API do Claude (recomendada para o protótipo)
- Uma interface própria: área de upload, um seletor de lentes (botões ou slider), o chat e abas (Visão geral, Ideia × Código, Fluxos).
- Construída com o apoio do Claude (Claude Code ou um artifact).
- A troca de lente muda o **prompt de sistema** enviado ao modelo.
- ✅ Visual, demo forte, parece produto · ❌ Exige mais tempo de desenvolvimento

### Opção C — Híbrido
- Validar os prompts das lentes primeiro na Opção A e depois levá-los para a interface da Opção B.
- ✅ Reduz o risco: o "cérebro" já chega testado na interface.

> 💡 **Sugestão:** seguir a **Opção C**. Primeiro acertar a qualidade das respostas e depois investir na interface.

### 6.1 Pontos técnicos a resolver

| Tema | Desafio | Possível abordagem |
|---|---|---|
| **Repositórios grandes** | O código inteiro pode não caber no contexto | Ignorar `node_modules`, builds e assets; priorizar README, rotas, models e services; resumir por pasta e depois responder |
| **Formatos de arquivo** | PDF, docx, zip | Extrair o texto antes de enviar ao modelo |
| **Consistência entre lentes** | Respostas não podem se contradizer | Gerar primeiro uma "base do produto" única e derivar as lentes a partir dela |
| **Alucinação** | A IA pode inventar funcionalidades | Na lente técnica, exigir a citação de arquivo e trecho; responder "não encontrei" quando não houver base |
| **Diagramas** | Visualizar os fluxos | Pedir a saída em Mermaid e renderizar na interface |
| **Confidencialidade** | Código de cliente é sensível | Usar apenas projetos próprios ou open source na demo; seguir a política de dados da empresa |

### 6.2 Esboço dos prompts por lente

```
[BASE — sempre]
Você é o Prisma. Explique o produto com base APENAS no material fornecido.
Se algo não estiver no material, diga claramente que não encontrou.

[LENTE CLIENTE]
Público: cliente final, sem conhecimento técnico.
Foque em valor, benefícios e problema resolvido. Sem jargão. Frases curtas.

[LENTE NÃO TÉCNICO]
Público: colaboradores de áreas como comercial, atendimento e gestão.
Explique como funciona na prática, use analogias do dia a dia e fluxos simples.

[LENTE TÉCNICO]
Público: desenvolvedores.
Detalhe arquitetura, stack, arquivos, funções e integrações.
SEMPRE cite o arquivo (e o trecho, quando possível) de onde tirou a informação.
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

| Entrega | O que levar do Prisma |
|---|---|
| **Canvas do processo** | Problema (seção 2), público, solução (3), funcionalidades (4), impacto (7), riscos (6.1) |
| **Protótipo no Claude** | MVP (4.1) e pelo menos 1 diferencial (4.2), de preferência o **Ideia × Código** |
| **Apresentação** | Dor → demo ao vivo (mesma pergunta, 3 lentes) → impacto → próximos passos (4.3) |

### Critérios de avaliação

| Critério | Como o Prisma atende |
|---|---|
| Problema identificado | Dor real e transversal, validada com colegas |
| Solução proposta | Fonte única de verdade, explicada por lentes |
| Impacto esperado | Métricas de tempo, onboarding e alinhamento |
| Viabilidade | Usa capacidades nativas do Claude; MVP enxuto |
| Protótipo desenvolvido | Funcional, com troca de lente ao vivo |
| Apresentação | Demo visual e de fácil entendimento |

---

## 9. Plano de trabalho sugerido

| Etapa | Atividade | Resultado |
|---|---|---|
| 1 | Validar a dor com 3 a 5 colegas | Evidências para o Canvas |
| 2 | Preencher o Canvas com base na cartilha | **Entrega 1** |
| 3 | Escolher um repositório e um documento de teste (próprio ou open source) | Material da demo |
| 4 | Criar e testar os prompts das lentes no Claude | "Cérebro" validado |
| 5 | Construir a interface (upload, lentes, chat) | MVP funcionando |
| 6 | Adicionar o diferencial Ideia × Código | Protótipo completo, **Entrega 2** |
| 7 | Testar com colegas e ajustar | Feedback real para a apresentação |
| 8 | Montar os slides e ensaiar a demo | **Entrega 3** |

---

## 10. Decisões em aberto

- [ ] Nome final do projeto (Prisma? outro?)
- [ ] Opção de construção: A, B ou C
- [ ] Três lentes fixas ou um **slider de profundidade**?
- [ ] Qual diferencial entra no protótipo: Ideia × Código, Fluxo com diagrama ou "Isso faz?"
- [ ] Qual repositório e documento usar na demo
- [ ] Quais colegas entrevistar para validar a dor
- [ ] Prazo de cada entrega do programa

---

## 11. Riscos e cuidados

- **Confidencialidade:** nunca usar código ou documento de cliente real sem autorização.
- **Respostas inventadas:** reforçar nos prompts que a IA só pode responder com base no material.
- **Escopo grande demais:** priorizar o MVP; o resto vira "próximos passos".
- **Repositório muito grande:** usar um projeto pequeno ou médio na demo.
- **Dependência da demo ao vivo:** ter um vídeo ou prints de backup na apresentação.
