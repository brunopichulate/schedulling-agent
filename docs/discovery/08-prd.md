# Stage 8 — PRD: Scheduling Agent MVP

> Versão: 1.0 | Data: 2026-03-16 | Ciclo: Low/Tech-Touch 2026.1
> **Audiência:** Bruno PM + Arua (Seções 1–4, 7) · Brunão + Paulo + Pedro G. (Seções 5–6, 8)

---

## 0. Como ler este documento

Este PRD é **misto por design**. As primeiras seções (contexto, personas, escopo) são legíveis por qualquer stakeholder sem background técnico. As seções de features e arquitetura (5–6) assumem familiaridade com a stack e com os artefatos da discovery. Decisões de negócio e de engenharia estão separadas mas colocadas no mesmo documento para manter alinhamento.

**Discovery completa:** todos os artefatos de base estão em `docs/discovery/`. Este PRD é o artefato de fechamento — não duplica, referencia.

---

## 1. Contexto do Produto

### Problema

O AEE (Apoio a Empreendedores Endeavor) gasta tempo significativo coordenando manualmente o agendamento de mentorias entre mentores e founders via WhatsApp. Esse back-and-forth manual é lento, não escalável, e ocupa capacidade de uma equipe cujo valor está no relacionamento estratégico, não na logística.

**Fonte:** Stage 1 (Problem Framing) + Stage 2 (Current Journey).

### Iniciativa

**Low/Tech-Touch Business Models 2026.1:** validar se a Endeavor consegue apoiar founders em escala sem crescer o headcount do AEE. O agente cobre a etapa de agendamento no pipeline de mentorias:

```
Checkpoint → Priorities → RecSys → My List → Book Meeting → [Scheduling Agent] → Calendar Invite
```

O agente substitui o AEE na logística de coordenação de horários, sem remover o AEE da relação de mentoria em si.

### Prazo

**Piloto antes de 31/05/2026.** Pré-requisito: Concierge Test com ≥5 mentores reais executado antes do piloto automatizado.

---

## 2. Personas

Extraídas do Stage 3 (JTBD Map). Resumo orientado ao produto:

### AEE — Ana (coordenadora de mentorias)

**Job funcional:** garantir que a mentoria aconteça, no horário certo, com os dois lados confirmados.
**Job emocional:** sentir que está cumprindo seu papel sem se afogar em mensagens operacionais.
**Definição de sucesso:** GCal invite criado sem nenhuma intervenção sua.
**Risco principal:** se o agente falha silenciosamente, Ana não sabe — e a mentoria não acontece.

> **Implicação de produto:** o EscalationService (notificação ao AEE) é tão crítico quanto o happy path. Um agente que falha sem avisar é pior do que o processo manual.

### Mentor — Ricardo (executivo sênior)

**Job funcional:** confirmar presença numa mentoria em <1 interação, sem burocracia.
**Job emocional:** sentir que o Endeavor respeita seu tempo.
**Risco:** indiferença e não resposta — não é rejeição hostil, é simplesmente ignorar uma mensagem de robô.
**Dado:** mentores B2B estão acostumados com automações; o risco real é a mensagem parecer spam.

> **Implicação de produto:** o primeiro contato com o mentor (template WhatsApp) é o momento de maior risco de abandono. Tom, timing, e personalização importam.

### Founder — Lucas (empreendedor em crescimento)

**Job funcional:** confirmar o slot rapidamente após aprovar o mentor no Connect.
**Job emocional:** sentir que o processo fluiu — que a mentoria vai acontecer de verdade.
**Latência:** se o agente demora a chegar ao founder (esperando resposta do mentor), o job fica sem fazer por horas.

> **Implicação de produto:** o tempo total trigger → GCal é a North Star porque capta o job do founder: "já está agendado de verdade?"

---

## 3. Escopo

### MVP — In

Estas features entram no MVP. Justificativas são funcionais, não de preferência.

| Feature | Justificativa de inclusão |
|---|---|
| **Happy path completo** (mentor → slots → founder → confirm → GCal) | Core do produto. Fluxo já implementado parcialmente, mas sem GCal o produto não existe: confirmação sem invite é falsa |
| **Google Calendar invite** (Service Account) | Sem isso, nenhum valor é entregue. Decisão de arquitetura já fechada: @endeavor como organizer, mentor + founder como guests |
| **EscalationService** (notificação AEE via WhatsApp ou Slack) | Sem isso, todas as falhas são silenciosas. AEE não sabe quando intervir — pior que o processo manual |
| **Timeout 48h + 1 follow-up** (Celery Beat) | Timeout atual = 30s fixo, sem verificação proativa. Sem Celery Beat, o agente trava silenciosamente em fluxos sem resposta |
| **Refusal detection → HI imediato** | H1 (chatbot aversion) é a hipótese mais arriscada da discovery. Recusa não detectada = loop infinito ou contexto ignorado |
| **Ambiguity counter** (máx 2x por round) | Sem limite, agente pode pedir clarificação indefinidamente. Experiência degradada para ambos os lados |
| **Fix EC-06: mídia preserva estado** | Bug ativo e reproduzível: áudio/imagem/sticker trava a conversa. Impacto real no piloto |
| **Deduplicação por meeting_id no trigger** | EC-12: dois triggers do mesmo meeting_id criam dois fluxos paralelos que corrompem o estado |
| **Janela 24h para founder** (template EC-09) | WhatsApp Business API requer template para mensagens fora da janela 24h. Sem isso, founder não é alcançado se demorar a responder ao mentor |
| **Validação de email do mentor no trigger** (EC-38) | Sem email, não é possível criar o GCal invite. Falhar cedo (no trigger) é melhor do que falhar após toda a negociação |

### Phase 2 — Out (com justificativa)

Estas features foram avaliadas e excluídas do MVP com razão explícita.

| Feature | Razão de exclusão |
|---|---|
| **Cancellation/rescheduling detection** (EC-39–44) | Cenário raro no contexto de piloto com 3–10 mentorias. Priorizar após validar que o fluxo base funciona |
| **Delegação de contato** (`contact_type` + `assistant_phone`) | Frequência desconhecida — o Concierge Test vai revelar se é raro ou comum. Implementar com dados reais |
| **Idempotência por message_id** (EC-31) | Duplicação de mensagens no WhatsApp é rara. Prioridade após o happy path estar estável |
| **Celery retry + DLQ** (EC-32) | Infraestrutura de resiliência importante, mas não bloqueia o piloto. Prioridade após aprendizados do piloto |

### Phase 3 — Later

- Atualização de status no Connect via API (hoje é manual)
- UI de intervenções no Connect para o AEE
- Agendamento com múltiplos founders por reunião (EC-02)
- Integração com Amplitude para rastreamento de eventos no Connect

---

## 4. Fluxo Completo

Os fluxos estão documentados nos diagramas vivos. Este PRD não os duplica.

| Diagrama | Conteúdo | Link |
|---|---|---|
| Diagrama 1 — Happy Path | Fluxo ideal: mentor responde, founder confirma, GCal criado | [`flow-diagram.md` → Diagrama 1](flow-diagram.md) |
| Diagrama 2 — Edge Cases | Todos os desvios: timeout, recusa, ambiguidade, mídia, deduplicação | [`flow-diagram.md` → Diagrama 2](flow-diagram.md) |
| Diagrama 3 — Orquestração de Agentes | Qual agente é ativado em cada ponto do fluxo | [`flow-diagram.md` → Diagrama 3](flow-diagram.md) |
| Agent Journey | Visão simplificada para PM e stakeholders | [`agent-journey.md`](agent-journey.md) |

**Referência de stage cases:** os 45 edge cases catalogados estão em [`05-edge-cases-deep.md`](05-edge-cases-deep.md) e em `docs/edge-cases.md`.

---

## 5. Features e Acceptance Criteria

> **Convenção:** cada AC começa com "Dado... → agente..." para ser testável sem ambiguidade.

---

### F1 — Happy Path + Google Calendar Invite

**Descrição:** fluxo principal end-to-end: trigger → contato com mentor → extração de slots → contato com founder → confirmação → criação do GCal invite.

**Acceptance Criteria:**

- AC1: Dado `meeting_id` + `donated_phone` (mentor) + `received_phone` (founder) + `donated_email` válidos no trigger → agente envia mensagem de abertura ao mentor dentro de 30s
- AC2: Dado resposta do mentor com ≥2 slots → SlotExtractorAgent extrai os slots e agente encaminha opções ao founder na mesma sessão Celery
- AC3: Dado founder confirmando um slot → ConfirmationExtractorAgent extrai o slot confirmado e estado transiciona para `RECEIVED_CONFIRMED`
- AC4: Dado estado `RECEIVED_CONFIRMED` → agente cria GCal invite com: mentor (e-mail pessoal) + founder (e-mail pessoal) como guests, conta @endeavor como organizer, título e descrição incluindo nome da empresa e nome do mentor
- AC5: Dado GCal invite criado com sucesso → ambos os participantes recebem o convite no calendário em <5 min
- AC6: Dado GCal invite criado → agente envia mensagem de confirmação ao mentor E ao founder com data/hora confirmada
- AC7: Dado qualquer falha na criação do GCal (API error, e-mail inválido) → agente não entra em loop; EscalationService é chamado com reason=`gcal_creation_failed`

**Arquivos envolvidos:** novo `src/services/gcal_service.py`, `src/workflows/meeting_shared/handlers.py`, `src/workflows/meeting_shared/models.py`

---

### F2 — EscalationService (Notificação ao AEE)

**Descrição:** serviço transversal — qualquer transição para `HUMAN_INTERVITION_REQUIRED` dispara uma notificação estruturada ao AEE com contexto suficiente para intervir sem precisar consultar outros sistemas.

**Acceptance Criteria:**

- AC1: Dado qualquer transição para `HUMAN_INTERVITION_REQUIRED` → EscalationService é chamado com: `reason` (tipo de escalada), nome do mentor, nome do founder, empresa, `meeting_id`, último estado anterior, histórico resumido de rounds
- AC2: Dado `ESCALATION_CHANNEL=whatsapp` configurado → mensagem WhatsApp enviada para `ESCALATION_WHATSAPP_PHONE` dentro de 60s da transição
- AC3: Dado `ESCALATION_CHANNEL=slack` configurado → thread criado no canal `SLACK_TAKEOVER_CHANNEL` (ver F10)
- AC4: Dado variáveis de escalada não configuradas → EscalationService loga `WARNING` mas não lança exceção e não interrompe o fluxo
- AC5: Dado múltiplos fluxos simultâneos em HI → cada um gera notificação independente, sem colapso

**Arquivos envolvidos:** novo `src/services/escalation_service.py`, `src/core/config.py` (novas vars: `ESCALATION_CHANNEL`, `ESCALATION_WHATSAPP_PHONE`)

---

### F3 — Timeout + Follow-up Proativo (Celery Beat)

**Descrição:** verificação periódica de fluxos sem resposta. Diferente do timeout atual (passivo, só ativo quando o usuário envia mensagem), o Celery Beat verifica ativamente todos os fluxos abertos.

**Acceptance Criteria:**

- AC1: Dado fluxo em estado de espera (mentor ou founder) sem nova mensagem por `NO_RESPONSE_TIMEOUT_SECONDS` (default 48h) → agente envia 1 mensagem de follow-up personalizada ao destinatário correto
- AC2: Dado follow-up enviado e nenhuma resposta por mais `NO_RESPONSE_TIMEOUT_SECONDS` → agente transiciona para HI + EscalationService com reason=`timeout_after_followup`
- AC3: Dado Celery Beat rodando → verificação ocorre a cada 15 min (configurável via `TIMEOUT_CHECK_INTERVAL_MINUTES`)
- AC4: Dado fluxo já concluído (GCal criado ou HI) → Celery Beat não processa nem envia mensagens para aquele fluxo
- AC5: Dado `NO_RESPONSE_TIMEOUT_SECONDS` não configurado → default de 172800s (48h) aplicado sem erro

**Arquivos envolvidos:** `src/tasks/whatsapp/` (novo periodic task `check_timeouts`), `src/core/celery.py` (Celery Beat schedule), `src/core/config.py`

---

### F4 — Refusal Detection

**Descrição:** detecção de intenção de recusa explícita ao agente. Ativa HI imediato sem tentar extrair slots ou confirmação.

**Acceptance Criteria:**

- AC1: Dado mensagem com intenção de recusa ao agente ("não quero falar com robô", "prefiro uma pessoa", "para de me mandar mensagem", "não quero usar esse sistema") → RefusalDetectorAgent classifica como `refusal=true` com confiança ≥0.85
- AC2: Dado `refusal=true` → agente responde ao usuário com mensagem humanizante antes de transicionar para HI ("Entendido, vou conectar você com alguém do time Endeavor.")
- AC3: Dado `refusal=true` → estado transiciona para `HUMAN_INTERVITION_REQUIRED` e EscalationService é chamado com reason=`agent_refused`
- AC4: Dado mensagem negativa sobre o horário proposto (não sobre o agente) → RefusalDetectorAgent classifica como `refusal=false` e fluxo continua normalmente
- AC5: RefusalDetectorAgent é verificado antes dos outros agentes (SlotExtractor, ConfirmationExtractor) na ordem de processamento

**Arquivos envolvidos:** novo `src/agents/main/refusal_detector_agent.py`, `src/workflows/meeting_shared/handlers.py`

---

### F5 — Ambiguity Counter

**Descrição:** limite de pedidos de clarificação por round. Previne que o agente fique em loop infinito tentando extrair informação de uma mensagem ambígua.

**Acceptance Criteria:**

- AC1: Dado extração falha (resposta ambígua ou incompleta) → agente pede clarificação e incrementa `clarification_count` no estado
- AC2: Dado `clarification_count` atinge 2 no mesmo ponto do fluxo → agente transiciona para HI + EscalationService com reason=`max_clarifications_reached`
- AC3: Dado início de novo round de negociação (mentor recebe contra-proposta) → `clarification_count` é resetado para 0
- AC4: `clarification_count` é persistido no estado da conversa (MongoDB), não apenas em memória de sessão

**Arquivos envolvidos:** `src/services/state_machine_service.py` (campo `clarification_count`), `src/workflows/meeting_shared/handlers.py`

---

### F6 — Fix EC-06: Mídia Preserva Estado

**Descrição:** bug ativo — mensagem de mídia (áudio, imagem, sticker, documento) causa transição de estado indevida ou trava a conversa.

**Acceptance Criteria:**

- AC1: Dado mentor ou founder envia áudio, imagem, sticker ou documento → agente responde pedindo que o usuário envie apenas texto ("Por favor, responda com texto para eu conseguir processar sua resposta.")
- AC2: Dado resposta com mídia recebida → estado da conversa permanece no mesmo estado que estava antes da mensagem (sem transição)
- AC3: Dado próxima mensagem de texto após a mídia → processada normalmente no estado correto, como se a mídia nunca tivesse ocorrido
- AC4: AC1–3 aplicam para todos os estados da máquina de estados onde mensagem de texto é esperada

**Arquivos envolvidos:** `src/workflows/whatsapp_workflow.py` ou `src/workflows/meeting_shared/handlers.py` (handler de tipo de mensagem)

---

### F7 — Deduplicação de Trigger (EC-12)

**Descrição:** proteção contra dois triggers simultâneos para o mesmo fluxo, que causariam dois processos paralelos corrompendo o estado da conversa.

**Acceptance Criteria:**

- AC1: Dado trigger recebido para `meeting_id` que já tem fluxo ativo → endpoint retorna HTTP 409 com body `{"error": "flow_already_active", "meeting_id": "..."}`
- AC2: Dado trigger recebido para `donated_phone` que já está em fluxo ativo (mesmo que `meeting_id` diferente) → endpoint retorna HTTP 409
- AC3: Dado fluxo concluído (GCal criado, HI confirmado, ou cancelado) → novo trigger para o mesmo `meeting_id` é aceito (200) e inicia novo fluxo
- AC4: Verificação de deduplicação ocorre antes de qualquer processamento ou envio de mensagem

**Arquivos envolvidos:** `src/api/v1/schedule.py`, `src/services/state_machine_service.py`

---

### F8 — Validação de E-mail no Trigger (EC-38)

**Descrição:** falha rápida se dados necessários para criação do GCal invite estão ausentes no momento do trigger, antes de iniciar qualquer interação.

**Acceptance Criteria:**

- AC1: Dado trigger sem `donated_email` (e-mail do mentor) → endpoint retorna HTTP 422 com body `{"error": "missing_mentor_email", "field": "donated_email"}`
- AC2: Dado trigger com `donated_email` em formato inválido → endpoint retorna HTTP 422 com body descritivo
- AC3: Dado `donated_email` ausente no Connect (não vem no payload do trigger) → `meetings_service` tenta buscar pelo `meeting_id`; se não encontrado, retorna erro antes de iniciar o fluxo
- AC4: Validação de e-mail do founder (`received_email`) é igualmente verificada; ausência → HTTP 422

**Arquivos envolvidos:** `src/api/v1/schedule.py`, `src/services/meetings_service.py`

---

### F9 — Motor de Negociação Multi-Round

**Descrição:** quando founder rejeita todos os slots mas oferece disponibilidade própria, o agente inicia um vai-e-vem: extrai a disponibilidade do founder, volta ao mentor com contra-proposta, e repete até convergência ou `MAX_NEGOTIATION_ROUNDS`.

**Acceptance Criteria:**

- AC1: Dado founder rejeita todos os slots E menciona disponibilidade própria ("só posso na quinta ou sexta") → CounterAvailabilityExtractorAgent extrai os horários propostos pelo founder
- AC2: Dado disponibilidade do founder extraída → agente envia mensagem ao mentor com contra-proposta: "O founder pode [horários do founder]. Você tem disponibilidade em algum desses?"
- AC3: Dado mentor responde com novo(s) slot(s) compatível(is) → agente envia opções ao founder para confirmação final
- AC4: Dado `current_round` < `MAX_NEGOTIATION_ROUNDS` (default 2) → novo round iniciado; `current_round` incrementado
- AC5: Dado `current_round` == `MAX_NEGOTIATION_ROUNDS` sem convergência → HI + EscalationService com reason=`max_rounds_reached`, incluindo histórico completo de todos os rounds
- AC6: Dado founder rejeita slots SEM oferecer alternativa ("esses horários não funcionam", sem mais informação) → HI imediato com reason=`founder_rejected_no_alternative`; motor não é iniciado
- AC7: `current_round` e `max_rounds` são campos no `MeetingContext` (não estados separados na máquina de estados)
- AC8: Cada round é persistido como `NegotiationRound` no histórico do contexto, contendo: slots oferecidos, resposta recebida, timestamp

**Arquivos envolvidos:** `src/workflows/meeting_shared/models.py` (dataclass `NegotiationRound`, campos no `MeetingContext`), `src/workflows/meeting_shared/handlers.py`, novo `src/agents/main/counter_availability_extractor_agent.py`

---

### F10 — Conversation Takeover via Slack (Relay Bidirecional)

**Descrição:** ao escalar para `HUMAN_INTERVITION_REQUIRED`, o AEE recebe um thread no Slack com todo o histórico da conversa. A partir dali, pode continuar interagindo com mentor e founder diretamente do Slack — sem trocar de canal. Mentor e founder continuam no WhatsApp e não sabem da troca de operador.

**Acceptance Criteria:**

- AC1: Dado `ESCALATION_CHANNEL=slack` e HI disparado → EscalationService cria thread no canal `SLACK_TAKEOVER_CHANNEL` com:
  - Bloco de contexto: nome do mentor, nome do founder, empresa, `meeting_id`, motivo da escalada
  - Histórico completo da conversa (todas as mensagens trocadas até aquele ponto)
  - Instruções de uso: "`@mentor <texto>` envia ao mentor · `@founder <texto>` envia ao founder · `/concluir slot="YYYY-MM-DDTHH:MM"` retoma o fluxo automático"
- AC2: Dado AEE responde no thread Slack com `@mentor Olá, você tem horário na quinta?` → Slack bot detecta o prefix, extrai o texto, e envia mensagem WhatsApp ao número do mentor em <30s
- AC3: Dado mentor responde no WhatsApp → mensagem é relay-ada de volta ao thread Slack como mensagem do bot com identificação: `[Mentor respondeu]: "quinta às 14h"`
- AC4: Dado AEE responde com `@founder` → mesma lógica, enviado ao número do founder
- AC5: Dado AEE envia `/concluir slot="2026-04-10T14:00"` no thread → agente extrai o slot, transiciona estado para `RECEIVED_CONFIRMED`, cria GCal invite, e notifica mentor e founder via WhatsApp
- AC6: Durante o takeover, estado permanece `HUMAN_INTERVITION_REQUIRED`; só transiciona após `/concluir` bem-sucedido
- AC7: Endpoint `POST /v1/channels/slack/events` valida `SLACK_SIGNING_SECRET` antes de processar qualquer evento; requisição inválida → 403

**Arquitetura Slack:**
- `SLACK_BOT_TOKEN`, `SLACK_TAKEOVER_CHANNEL`, `SLACK_SIGNING_SECRET` em `src/core/config.py`
- EscalationService usa Slack Web API (`chat.postMessage`) para criar thread
- Novo endpoint `POST /v1/channels/slack/events` recebe eventos do Slack Events API
- Endpoint detecta prefixos `@mentor`/`@founder` e relaya via WhatsApp service existente
- Webhook WhatsApp existente relaya respostas de volta ao Slack thread via `chat.postMessage` com `thread_ts` armazenado no contexto

**Arquivos envolvidos:** novo `src/api/v1/slack.py`, `src/services/escalation_service.py` (lógica de thread creation), `src/services/whatsapp.py` (relay de mensagens), `src/core/config.py`

---

## 6. Arquitetura de Agentes — Target MVP

| Agente / Serviço | Tipo | Status | Prioridade MVP |
|---|---|---|---|
| `SlotExtractorAgent` | LLM (Agno + GPT-4o-mini) | ✅ Implementado | — |
| `ConfirmationExtractorAgent` | LLM (Agno + GPT-4o-mini) | ✅ Implementado | — |
| `RefusalDetectorAgent` | LLM (Agno + GPT-4o-mini) | ❌ Novo | P0 |
| `EscalationService` | Serviço (não LLM) | ❌ Novo | P0 |
| `GCalService` | Serviço (não LLM, Google API) | ❌ Novo | P0 |
| `CounterAvailabilityExtractorAgent` | LLM (Agno + GPT-4o-mini) | ❌ Novo | P1 |
| `AmbiguityResolverAgent` | LLM (Agno + GPT-4o-mini) | ❌ Novo | P1 |
| `TimeoutHandlerAgent` | LLM ou regra (a definir) | ❌ Novo | P1 |
| Slack Relay (takeover bidirecional) | Serviço (Slack API + WhatsApp) | ❌ Novo | P1 |

**Phase 2 (fora do MVP):**

| Agente | Razão de adiamento |
|---|---|
| `DetectCancellationAgent` | Cobre EC-39–44 (cancelamento/remarcação pós-confirmação). Raro no piloto; priorizar após validar fluxo base |

### Ordem de implementação recomendada

1. **P0 bloqueadores do produto:** GCalService → F1 fecha o happy path
2. **P0 bloqueadores de operação:** EscalationService → F2 garante visibilidade do AEE
3. **P0 guardrail crítico:** RefusalDetectorAgent → F4 valida H1
4. **P1 — resiliência do fluxo:** Timeout + Celery Beat (F3), Ambiguity Counter (F5), Fix EC-06 (F6)
5. **P1 — integridade de dados:** Deduplicação (F7), Validação e-mail (F8)
6. **P1 — negociação e takeover:** Motor de Negociação (F9), Slack Relay (F10)

---

## 7. Métricas de Sucesso

As métricas completas estão definidas em [`07-metrics.md`](07-metrics.md). Resumo orientado ao piloto:

### North Star

**Tempo médio entre trigger e GCal invite criado.** Meta: <24h no happy path.

### Critérios formais de aprovação do piloto (3–5 mentorias)

Para declarar o piloto bem-sucedido e avançar para escala, **todos os critérios abaixo devem ser atendidos:**

| Critério | Métrica | Limite |
|---|---|---|
| AEE não interveio na maioria dos fluxos | G3 — % de mentorias sem intervenção | ≥60% |
| Taxa de intervenção humana dentro do esperado | R1 — % de fluxos → HI | <30% |
| Nenhuma rejeição explícita ao agente | R2 — chatbot aversion | <10% |
| Mentores não reclamaram da experiência | R4 — reclamações explícitas | 0 |

### Pré-requisito do piloto automatizado

- Concierge Test executado com ≥5 mentores reais antes do piloto
- Resultado Concierge Test: ≥70% respondem cooperativamente à abordagem do agente
- Instrumentação P0 ativa: timestamps de trigger + GCal criados, snapshots de estado persistidos antes do reset

### Leading indicators monitorados durante o piloto

| Métrica | Meta conservadora (piloto) | Meta final |
|---|---|---|
| L1 — taxa de resposta do mentor | ≥70% | ≥80% |
| L3 — acurácia do SlotExtractorAgent | ≥85% | ≥90% |

**Para medição completa de todas as métricas, gaps de instrumentação e estratégia de coleta:** ver [`07-metrics.md`](07-metrics.md).

---

## 8. Decisões em Aberto

Estas decisões precisam ser resolvidas **antes do início da implementação**. O PRD não pode ser executado sem elas.

| # | Decisão | Owner | Impacto se não resolvida |
|---|---|---|---|
| D1 | **Redis vs MongoDB para estado de conversa?** CLAUDE.md documenta MongoDB, código atual usa Redis. Qual é a fonte de verdade? | Brunão | Afeta TTL, histórico pós-piloto, análise de dados. EscalationService precisa saber onde ler o histórico |
| D2 | **Corrigir typo `HUMAN_INTERVITION_REQUIRED` → `HUMAN_INTERVENTION_REQUIRED` antes do piloto?** | Brunão | Breaking change em Redis keys + todos os handlers. Requer migração ou deploy coordenado. Se não corrigir agora, fica mais difícil depois |
| D3 | **`WAITING_FOR_TEMPLATE_REPLY` — implementar handler ou remover o estado?** Estado existe na máquina mas sem handler. | Brunão | Lacuna de cobertura: fluxos que chegam nesse estado ficam presos silenciosamente |
| D4 | **Timeout do founder = mesmo que mentor (48h) ou menor?** Founders tendem a responder mais rápido. | Bruno PM | Afeta `NO_RESPONSE_TIMEOUT_SECONDS` por destinatário vs. valor único global |
| D5 | **EC-11 — aviso prévio ao founder: processo manual (AEE avisa antes do agente contatar) ou o agente inclui essa comunicação?** | Bruno PM | Se manual, afeta H6 (adoção do founder). Se automatizado, adiciona complexidade ao trigger |
| D6 | **Quem é responsável por coletar e analisar as métricas durante o piloto?** | Bruno PM + Brunão | Sem responsável definido, instrumentação P0 pode não ser feita antes do piloto |
| D7 | **Shadow mode antes do piloto — viável?** Agente roda sem enviar mensagens, só analisa. Valida acurácia do LLM sem risco ao relacionamento com mentores. | Bruno PM + Brunão | Se não feito, piloto é o primeiro teste real. Risco maior em R4 |

---

## Apêndice — Referências Cruzadas da Discovery

| Artefato | O que contém | Link |
|---|---|---|
| Stage 1 — Problem Framing | Problema canônico, anti-goals, evidências de dor | [`01-problem-framing.md`](01-problem-framing.md) |
| Stage 2 — Current Journey | Fluxo atual sem agente, friction points, contexto emocional | [`02-current-journey.md`](02-current-journey.md) |
| Stage 3 — JTBD Map | Jobs funcionais/emocionais/sociais, Switch Diagram | [`03-jtbd.md`](03-jtbd.md) |
| Stage 4 — Assumption Map | H1–H15, risk × evidence 2×2, roadmap de validação | [`04-assumption-map.md`](04-assumption-map.md) |
| Stage 5 — Edge Case Taxonomy | 45 edge cases catalogados, prioridade, implicações arquiteturais | [`05-edge-cases-deep.md`](05-edge-cases-deep.md) |
| Stage 6 — Flow Mapping | 11 fluxos mapeados, 6 gaps críticos, máquina de estados expandida | [`06-flow-map.md`](06-flow-map.md) |
| Stage 7 — Success Metrics | North Star, 10 indicadores, 4 guardrails, instrumentação, piloto | [`07-metrics.md`](07-metrics.md) |
| Edge Cases (catálogo) | Lista viva de todos os edge cases com status | [`../../edge-cases.md`](../../edge-cases.md) |
| Business Rules | Regras de negócio do ciclo atual | [`../../business-rules.md`](../../business-rules.md) |
| Architecture Deep-dive | Data flow, componentes, máquina de estados completa | [`../../architecture.md`](../../architecture.md) |
