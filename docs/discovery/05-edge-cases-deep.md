# Stage 5 — Edge Case Taxonomy

> Versão: 2.0 | Data: 2026-03-16 | Agente líder: Engineer + Researcher
> Expande: `docs/edge-cases.md` (45 casos) → taxonomia completa com frequência, impacto, resolução e implicação arquitetural.

---

## Overview

Este artefato transforma a lista de edge cases em um mapa de decisão de produto. Para cada caso: o que acontece hoje, por que é problemático, com que frequência estimamos que ocorre, qual o impacto se não tratado, como deve ser resolvido, e o que isso implica arquiteturalmente.

**Premissa de prioridade:** Frequência × Impacto = Prioridade de resolução. Casos de alto impacto E alta frequência bloqueiam o piloto. Casos de alto impacto E baixa frequência devem ter fallback para human intervention. Casos de baixo impacto podem aguardar.

**Novidades na v2.0:** Expansão de 12 para 45 edge cases. Incorpora decisões arquiteturais do Stage 6: Motor de Negociação (vai-e-vem), EscalationService, Delegação de Contato no trigger, MAX_NEGOTIATION_ROUNDS configurável.

---

## 1. Deep-Dive: Edge Cases Originais (EC-01 a EC-12)

### Legenda
- **Frequência:** Raro (<5% das interações) / Ocasional (5–20%) / Frequente (>20%)
- **Impacto:** Baixo (conversa degradada) / Médio (agendamento atrasado) / Alto (agendamento perdido) / Crítico (dano relacional ou de dados)
- **Status atual:** 🔴 Sem solução / 🟡 Solução definida, não implementada / 🟢 Implementado

---

### Mentor-side

#### EC-01 — Mentor tem assistente executivo

| Campo | Detalhe |
|---|---|
| **Descrição** | O mentor delega WhatsApp a um assistente, que recebe e responde a mensagem em nome do mentor |
| **Frequência estimada** | Ocasional (mentores seniores / C-level tendem a delegar) |
| **Impacto se não tratado** | Alto — slots propostos pelo assistente podem não refletir a disponibilidade real do mentor; calendário pode ser criado com horário errado |
| **Status atual** | 🟡 Solução definida, não implementada |
| **O que acontece hoje** | O agente não sabe que está falando com um assistente. Se a resposta for válida (2+ slots), o fluxo continua normalmente |
| **Resolução proposta** | Curto prazo (MVP): aceitar a resposta como válida — assistente fala pelo mentor. Solução real (Phase 2): pré-trigger com campo `contact_type = "assistant"` e `assistant_phone` no payload do trigger (ver Delegação de Contato em `docs/architecture.md`). O agente já sabe desde o início que está falando com um assistente e usa linguagem adaptada |
| **Hipótese relacionada** | H1 (engajamento), H10 (número correto no Connect) |
| **Implicação arquitetural** | MVP: nenhuma. Phase 2: campo `contact_type` e `assistant_phone` no trigger payload; WhatsApp trigger envia para `assistant_phone` quando `contact_type = "assistant"` |

---

#### EC-02 — Founder tem múltiplos sócios

| Campo | Detalhe |
|---|---|
| **Descrição** | A empresa tem mais de um sócio no Connect; o agente não sabe qual deles deve receber a mensagem |
| **Frequência estimada** | Ocasional (startups de early stage frequentemente têm 2–3 co-fundadores) |
| **Impacto se não tratado** | Alto — mensagem enviada para o sócio errado; fundador certo não confirma; agendamento perdido |
| **Status atual** | 🔴 Sem solução |
| **O que acontece hoje** | O trigger do agente (Connect) provavelmente passa um número específico. A questão é se esse número é sempre o correto |
| **Resolução proposta** | Definir regra no Connect: qual campo determina o "contato primário" para agendamento. AEE deve garantir que o campo está preenchido corretamente antes de triggerar o agente |
| **Hipótese relacionada** | H16 (contato correto identificável no Connect) |
| **Implicação arquitetural** | Nenhuma no agente. Requer acordo com equipe Connect sobre campo de contato primário |

---

#### EC-03 — Mentor não responde (timeout)

| Campo | Detalhe |
|---|---|
| **Descrição** | O mentor recebe a mensagem mas não responde dentro de um prazo razoável |
| **Frequência estimada** | Ocasional — mentores ocupados, viagens, férias |
| **Impacto se não tratado** | Crítico — conversa fica em aberto indefinidamente; AEE não sabe; agendamento nunca acontece |
| **Status atual** | 🔴 Sem solução |
| **O que acontece hoje** | Conversa some silenciosamente. Sem timeout, sem notificação, sem follow-up |
| **Resolução proposta** | 1. SLA de resposta: 48h (configurável via `NO_RESPONSE_TIMEOUT_SECONDS`). 2. Após SLA: enviar 1 mensagem de follow-up. 3. Após follow-up sem resposta (+24h): mover para `aguardando_intervencao_humana` + notificar AEE via EscalationService (WhatsApp ou Slack conforme `ESCALATION_CHANNEL`) |
| **Hipótese relacionada** | H11 (janela 24h), H15 (edge cases infrequentes) |
| **Implicação arquitetural** | Novo estado: `aguardando_resposta_mentor_followup`. Celery Beat para verificação de timeout. EscalationService para notificação ao AEE |

---

#### EC-04 — Founder rejeita todos os slots propostos

| Campo | Detalhe |
|---|---|
| **Descrição** | O founder responde que nenhum dos horários propostos pelo mentor funciona para ele (sem oferecer contra-disponibilidade) |
| **Frequência estimada** | Raro (agendamentos costumam ter flexibilidade suficiente) |
| **Impacto se não tratado** | Alto — fluxo trava; sem regra sobre o que fazer a seguir |
| **Status atual** | 🔴 Sem solução (MVP: HI) |
| **O que acontece hoje** | ConfirmationExtractorAgent não consegue extrair confirmação → `aguardando_intervencao_humana` |
| **Resolução proposta** | MVP: notifica AEE para mediar. Phase 2: Motor de Negociação — agente volta ao mentor pedindo novos horários (dentro do limite de `MAX_NEGOTIATION_ROUNDS`). Ver também EC-24 (founder que rejeita E oferece contra-disponibilidade) |
| **Hipótese relacionada** | H17 (founders aceitam ao menos 1 slot) |
| **Implicação arquitetural** | Novo estado: `founder_rejeitou_todos_slots`. EscalationService com contexto completo (quais slots foram propostos, o que founder respondeu). Motor de Negociação para roteamento de volta ao mentor |

---

#### EC-05 — Resposta ambígua do mentor ou founder

| Campo | Detalhe |
|---|---|
| **Descrição** | O ator responde com algo que não pode ser extraído como slot ou confirmação ("qualquer dia", "pode ser de manhã", "semana que vem tá bom") |
| **Frequência estimada** | Frequente — português conversacional no WhatsApp é naturalmente vago |
| **Impacto se não tratado** | Alto — extração falha; conversa para em `aguardando_intervencao_humana` sem que o usuário saiba |
| **Status atual** | 🟡 Solução definida, não implementada |
| **O que acontece hoje** | SlotExtractorAgent retorna erro de extração → `aguardando_intervencao_humana` sem resposta ao usuário |
| **Resolução proposta** | 1. Agente responde pedindo esclarecimento com exemplo concreto ("Pode me dizer o dia e horário específico? Ex: quinta-feira, 14h"). 2. Limite de 2 pedidos de clarificação por round (decidido no Stage 6). 3. Após 2 tentativas sem sucesso: `aguardando_intervencao_humana` + notificação AEE via EscalationService |
| **Hipótese relacionada** | H9 (taxa de ambiguidade aceitável), H7/H8 (acurácia LLM) |
| **Implicação arquitetural** | AmbiguityResolverAgent (ou lógica dentro dos agentes existentes). Contador de tentativas no estado da conversa (`clarification_attempts`). Estados: `aguardando_clarificacao_mentor` / `aguardando_clarificacao_founder` |

---

#### EC-06 — Mentor responde com mídia (áudio, imagem, sticker, documento)

| Campo | Detalhe |
|---|---|
| **Descrição** | Em vez de texto, o mentor envia uma mensagem de voz, foto, sticker ou arquivo |
| **Frequência estimada** | Ocasional — áudios são muito comuns no WhatsApp brasileiro |
| **Impacto se não tratado** | Médio — conversa trava no estado atual; mentor fica sem resposta sobre o que fazer |
| **Status atual** | 🟡 Solução definida, não implementada — fallback reply existe mas estado da máquina não é atualizado (bug ativo) |
| **O que acontece hoje** | Fallback: "suporto apenas mensagens de texto". Mas o estado da máquina não avança nem registra que a resposta foi recebida → próxima mensagem de texto do mentor será processada normalmente |
| **Resolução proposta** | Implementar: ao receber mídia, responder com fallback E manter estado atual (não transitar). A próxima mensagem de texto retoma o fluxo no estado correto. Correção simples no handler de mensagens: preservar estado ao receber mídia |
| **Hipótese relacionada** | H2 (mentores respondem em texto) |
| **Implicação arquitetural** | Correção no handler de mensagens: preservar estado ao receber mídia. ~1h de dev. Sem novos agentes ou estados |

---

#### EC-07 — Número de WhatsApp do mentor desatualizado no Connect

| Campo | Detalhe |
|---|---|
| **Descrição** | O número registrado no Connect não pertence mais ao mentor (mudou de número, número errado no cadastro) |
| **Frequência estimada** | Raro — mas indetectável sem mecanismo de bounce |
| **Impacto se não tratado** | Crítico — mensagem entregue para pessoa errada; dados pessoais de agendamento expostos; agendamento perdido |
| **Status atual** | 🔴 Sem solução técnica possível no agente |
| **O que acontece hoje** | WhatsApp entrega a mensagem sem erro (número existe, só não é do mentor). O agente não tem como saber |
| **Resolução proposta** | Curto prazo: AEE deve validar número do mentor antes de triggerar o agente (checklist manual). Longo prazo: Connect deve ter campo "número WhatsApp validado" com data de verificação. Também: validar `email` do mentor no trigger (EC-38) cobre parte do risco |
| **Hipótese relacionada** | H10 (números corretos no Connect) |
| **Implicação arquitetural** | Nenhuma no agente MVP. Requer processo de higiene de dados no Connect |

---

### Founder-side

#### EC-08 — AEE esquece de atualizar status no Connect após agendar

| Campo | Detalhe |
|---|---|
| **Descrição** | Após o GCal invite ser criado pelo agente, o status da reunião no Connect permanece como "Potential Meeting" ao invés de "Scheduled" |
| **Frequência estimada** | Frequente no modelo atual (processo manual); Raro se o agente automatizar |
| **Impacto se não tratado** | Médio — relatórios de pipeline incorretos; risco de o próximo passo (Briefing) não disparar automaticamente |
| **Status atual** | 🔴 Sem solução |
| **O que acontece hoje** | O agente não tem integração com Connect para atualizar status. AEE deve fazer manualmente e frequentemente esquece |
| **Resolução proposta** | O agente deve chamar a API do Connect para atualizar status após criar o GCal invite. Alternativa MVP: notificação de sucesso ao AEE via EscalationService com lembrete explícito de atualizar o Connect manualmente |
| **Hipótese relacionada** | H13 (Connect update não bloqueia Briefing no MVP) |
| **Implicação arquitetural** | Novo serviço: `ConnectService` com método `update_meeting_status`. Ou: mensagem de notificação ao AEE como workaround MVP |

---

#### EC-09 — Janela de 24h do WhatsApp expira no meio do fluxo

| Campo | Detalhe |
|---|---|
| **Descrição** | O mentor demora mais de 24h para responder. Quando o agente tenta contactar o founder após receber a resposta do mentor, a janela de 24h já fechou para o founder |
| **Frequência estimada** | Ocasional — depende da velocidade de resposta do mentor |
| **Impacto se não tratado** | Alto — o agente não pode enviar mensagem livre ao founder sem janela aberta; tenta enviar e falha |
| **Status atual** | 🟡 Solução definida — WhatsApp Window Service cobre este cenário: envia template `hello_world` antes da mensagem principal quando janela está fechada |
| **O que acontece hoje** | `WhatsAppWindowService` verifica janela antes de enviar. Se fechada, envia template primeiro para reabrir a janela, depois segue com a mensagem normal |
| **Resolução proposta** | Solução já definida e implementada para o contato inicial com o founder. Validar cobertura também para edge cases de multi-round (Motor de Negociação) onde o gap entre mensagens pode ultrapassar 24h em rounds subsequentes |
| **Hipótese relacionada** | H11 (janela 24h suficiente) |
| **Implicação arquitetural** | Window Service deve ser invocado em cada etapa de contato no Motor de Negociação, não apenas no primeiro contato com o founder |

---

#### EC-10 — Mentor ou founder se recusa a interagir com o agente (chatbot aversion)

| Campo | Detalhe |
|---|---|
| **Descrição** | O ator ignora a mensagem, responde explicitamente que não quer interagir com um robô, ou expressa ceticismo/desconfiança |
| **Frequência estimada** | Desconhecida — hipótese de alto risco (H1). Pode ser Raro ou Ocasional dependendo do perfil do mentor |
| **Impacto se não tratado** | Crítico — se Frequente, invalida o modelo inteiro |
| **Status atual** | 🔴 Sem solução |
| **O que acontece hoje** | Uma recusa explicitamente escrita pode ser interpretada pelo LLM como resposta ambígua → `aguardando_intervencao_humana`. Sem notificação ao AEE, a recusa fica invisível |
| **Resolução proposta** | 1. Detecção de intenção de recusa no pipeline de extração. 2. Se detectado: mensagem humanizante ("Entendido. Vou avisar o time da Endeavor para entrar em contato.") + notificação imediata ao AEE via EscalationService + estado `mentor_recusou_agente` / `founder_recusou_agente` |
| **Hipótese relacionada** | H1 (premissa zero do projeto) |
| **Implicação arquitetural** | Intent classifier: `RefusalDetectorAgent` ou intent detection dentro dos agentes existentes. EscalationService imediato. Estados dedicados: `mentor_recusou_agente` / `founder_recusou_agente` |

---

### System-side

#### EC-11 — Founder não reconhece o número do agente (phishing fear)

| Campo | Detalhe |
|---|---|
| **Descrição** | O founder recebe uma mensagem de um número desconhecido (número virtual Salvy) falando sobre agendamento de mentoria, sem ter sido avisado previamente |
| **Frequência estimada** | Ocasional — founders não têm contexto de que receberão essa mensagem |
| **Impacto se não tratado** | Alto — agendamento perdido; founder pode bloquear o número; reputação do processo comprometida |
| **Status atual** | 🔴 Sem solução técnica no agente |
| **O que acontece hoje** | AEE hoje prepara as partes manualmente antes do contato. O agente não faz isso |
| **Resolução proposta** | MVP: AEE envia aviso prévio manual ao founder antes do agente entrar em contato (sem novo código). Futuro: etapa de notificação por e-mail ao founder antes do primeiro WhatsApp (usando e-mail do Connect) |
| **Hipótese relacionada** | H6 (founder não confunde com phishing) |
| **Implicação arquitetural** | MVP: nenhuma. Futuro: etapa de notificação no pipeline de trigger antes de enviar o primeiro WhatsApp |

---

#### EC-12 — Trigger duplicado (mesma mentoria triggerada duas vezes)

| Campo | Detalhe |
|---|---|
| **Descrição** | O Connect ou o AEE triggerou o agente duas vezes para a mesma mentoria — por erro, double-click, ou retry automático |
| **Frequência estimada** | Raro, mas tecnicamente possível |
| **Impacto se não tratado** | Crítico — mentor recebe duas mensagens idênticas; dois fluxos paralelos para o mesmo número; estado da máquina pode corromper |
| **Status atual** | 🟡 Solução definida — deduplicação por `meeting_id` na trigger endpoint |
| **O que acontece hoje** | Solução definida: se workflow já ativo para aquele `meeting_id`, o segundo trigger é rejeitado. Requer `meeting_id` como chave primária do estado (não `phone_number`) |
| **Resolução proposta** | Verificação de idempotência no state machine service: `if state_exists(meeting_id): skip`. O `meeting_id` deve ser a chave primária do estado da conversa |
| **Hipótese relacionada** | N/A — falha operacional, não de adoção |
| **Implicação arquitetural** | `StateMachineService`: verificar existência por `meeting_id` antes de criar novo estado. Mudança de chave primária de `phone_number` para `meeting_id` se ainda não implementado |

---

## 2. Novos Edge Cases Identificados (EC-13 a EC-45)

### Grupo A — Comportamental: Mentor Side (EC-13 a EC-22)

| # | Caso | Frequência | Impacto | Status | Agente resolve? | Resolução proposta |
|---|---|---|---|---|---|---|
| EC-13 | Redis TTL expira silenciosamente após 24h de conversa ativa | Raro | Crítico | 🔴 Sem solução | ❌ | TTL refresh em cada mensagem recebida. Alerta de expiração iminente para AEE via EscalationService. Sem refresh: ao expirar, notificar AEE em vez de resetar silenciosamente |
| EC-14 | Mentor envia slots em mensagens separadas ("terça 14h" ... "ou quinta 10h") | Ocasional | Crítico | 🔴 Sem solução | ❌ | Agente processa apenas a última mensagem recebida. Necessário: agregação de mensagens dentro de uma janela de tempo (ex: 30s) OU sinal de encerramento ("pode ser isso") como trigger de processamento |
| EC-15 | Mentor envia slots no passado ("semana passada às 14h") | Raro | Alto | 🟡 Solução definida | ✅ | SlotExtractorAgent detecta datas passadas e pede explicitamente datas futuras. Já coberto pelo prompt do agente |
| EC-16 | Horário sem data ("às 14h ou às 16h") | Ocasional | Alto | 🟡 Solução definida | ✅ | SlotExtractorAgent detecta ausência de data e pede especificação do dia. Já coberto pelo prompt do agente |
| EC-17 | Slot condicional ("só se for videochamada", "só presencial") | Ocasional | Médio | 🟡 Solução definida | ✅ | Agente extrai horário normalmente + anota condição como campo `slot_condition` no contexto. AEE é informado da condição na notificação de sucesso |
| EC-18 | Mentor e founder já combinaram diretamente antes do agente iniciar | Ocasional | Crítico | 🔴 Sem solução | ❌ | Não verificável pelo agente. Se mentor menciona isso, agente vai para HI imediatamente + EscalationService notifica AEE para confirmar e criar GCal manualmente |
| EC-19 | Mentor faz pergunta fora de escopo antes de dar slots | Ocasional | Médio | 🟡 Solução definida | ✅ | Agente redireciona educadamente ("sou assistente de agendamento, pode me enviar 2 horários?"). Limite 2x → HI com EscalationService |
| EC-20 | Mentor muda disponibilidade enquanto founder ainda está escolhendo | Raro | Alto | 🔴 Sem solução | ❌ | Estado atual não suporta. Motor de Negociação: se mentor envia nova mensagem quando estado é `aguardando_confirmacao_founder`, agente suspende escolha do founder, notifica AEE, e reinicia ciclo com novos slots |
| EC-21 | Resposta emocional ou agressiva do mentor | Raro | Alto | 🔴 Sem solução | ❌ | HI imediato. Agente responde com mensagem neutra e empática + EscalationService notifica AEE com contexto completo. Não tenta resolver o conflito |
| EC-22 | Mentor responde DEPOIS de já estar em HI (resposta tardia) | Ocasional | Médio | 🔴 Sem solução | ❌ | Agente detecta estado HI e avisa: "Esse atendimento já foi encaminhado para o time da Endeavor. Eles entrarão em contato." AEE decide se reabre o fluxo |

---

### Grupo B — Comportamental: Founder Side (EC-23 a EC-30)

| # | Caso | Frequência | Impacto | Status | Agente resolve? | Resolução proposta |
|---|---|---|---|---|---|---|
| EC-23 | Founder responde "sim", "ok", "pode ser" sem especificar qual opção | Frequente | Crítico | 🟡 Solução definida | ✅ | Extremamente comum no WhatsApp brasileiro. ConfirmationExtractorAgent detecta ausência de índice/horário específico e pede: "Qual das opções você prefere? (1, 2 ou 3)" |
| EC-24 | Founder rejeita todos os slots E oferece contra-disponibilidade | Ocasional | Crítico | 🟡 Solução definida | ✅ | Aciona Motor de Negociação: ConfirmationExtractorAgent extrai disponibilidade do founder → agente retorna ao mentor com contra-proposta formatada → novo ciclo. Limitado a `MAX_NEGOTIATION_ROUNDS` rounds |
| EC-25 | Founder delega ao assistente mid-flow ("confirma com minha secretária, número X") | Raro | Alto | 🔴 Sem solução | ❌ | HI imediato + EscalationService notifica AEE para reconfigurar contato. Solução estrutural: Delegação de Contato no trigger (campo `contact_type` + `assistant_phone`) |
| EC-26 | Founder confirma com modificação ("opção 2 mas 30 min antes", "pode ser às 15h em vez de 14h?") | Ocasional | Médio | 🔴 Sem solução | ❌ | HI imediato + EscalationService para AEE mediar a negociação de horário exato. Agente não tenta renegociar horário interno ao slot |
| EC-27 | Founder escolhe por descrição em vez de número ("a reunião de quinta", "o horário da tarde") | Frequente | Médio | 🟡 Solução definida | ✅ | ConfirmationExtractorAgent com prompt adequado mapeia descrição semântica → índice da lista. Ex: "a de quinta" → identifica qual slot cai na quinta-feira |
| EC-28 | Founder envia disponibilidade genérica em vez de escolher da lista ("posso segunda ou terça") | Ocasional | Médio | 🟡 Solução definida | ✅ | Motor de Negociação: agente extrai disponibilidade do founder → verifica sobreposição com slots do mentor → se houver match, confirma; se não, leva ao mentor como contra-proposta |
| EC-29 | Resposta emocional ou agressiva do founder | Raro | Alto | 🔴 Sem solução | ❌ | HI imediato. Agente responde com mensagem neutra e empática + EscalationService notifica AEE imediatamente. Não tenta resolver o conflito |
| EC-30 | Founder responde DEPOIS de já estar em HI (resposta tardia) | Ocasional | Médio | 🔴 Sem solução | ❌ | Mesmo tratamento de EC-22: agente detecta estado HI e avisa que o time da Endeavor foi acionado. AEE decide se reabre |

---

### Grupo C — Cancelamento e Remarcação (EC-39 a EC-45)

| # | Caso | Frequência | Impacto | Status | Agente resolve? | Resolução proposta |
|---|---|---|---|---|---|---|
| EC-39 | Mentor cancela ANTES da confirmação (durante negociação) | Raro | Alto | 🔴 Sem solução | ❌ | Agente notifica founder + AEE via EscalationService. Motor de Negociação: inicia novo ciclo solicitando novos slots ao mentor, ou encerra e notifica AEE para mediar manualmente |
| EC-40 | Founder cancela ANTES da confirmação | Raro | Alto | 🔴 Sem solução | ❌ | Agente notifica mentor + AEE via EscalationService. Mesmo tratamento de EC-39. AEE decide se encerra ou reinicia |
| EC-41 | Mentor cancela APÓS confirmação (reunião já agendada no GCal) | Raro | Crítico | 🔴 Sem solução | ❌ | EscalationService notifica founder + AEE imediatamente com contexto. GCal invite deve ser cancelado. Novo ciclo de negociação disparado ou AEE assume controle total |
| EC-42 | Founder cancela APÓS confirmação | Raro | Crítico | 🔴 Sem solução | ❌ | Mesmo tratamento de EC-41: notificação imediata, cancelamento do GCal, novo ciclo ou HI |
| EC-43 | Mentor pede remarcação ("preciso mudar o horário, pode ser outra data?") | Ocasional | Crítico | 🔴 Sem solução | ❌ | HI + novo ciclo de negociação completo. GCal invite deve ser cancelado e recriado. Estado `RESCHEDULING_REQUESTED` necessário para rastrear remarcações |
| EC-44 | Founder pede remarcação | Ocasional | Crítico | 🔴 Sem solução | ❌ | Mesmo tratamento de EC-43. Estado `RESCHEDULING_REQUESTED` unifica o fluxo de remarcação independente de quem pediu |
| EC-45 | N rounds sem convergência (nenhum slot em comum encontrado após máx rounds) | Raro | Alto | 🟡 Solução definida | ❌ | Após `MAX_NEGOTIATION_ROUNDS` (padrão: 2, configurável), agente encerra negociação automática e envia para HI com resumo completo: todos os slots propostos pelo mentor + todas as disponibilidades do founder |

---

### Grupo D — Técnico / Infraestrutura (EC-31 a EC-35)

| # | Caso | Frequência | Impacto | Status | Agente resolve? | Resolução proposta |
|---|---|---|---|---|---|---|
| EC-31 | Webhook entregue 2x pelo Meta (retry automático do Meta) | Ocasional | Alto | 🔴 Sem solução | ❌ | Sem idempotência por `message_id`. Mesma mensagem processada 2x pode duplicar transições de estado. Solução: verificar `message_id` antes de processar; se já processado, ignorar (Redis com TTL) |
| EC-32 | Tarefa Celery perdida (broker down, crash mid-task, sem retry strategy) | Raro | Crítico | 🔴 Sem solução | ❌ | `ignore_result=True` sem DLQ. Mensagem do usuário some silenciosamente. Solução: configurar retry strategy no Celery task + Dead Letter Queue para tarefas falhas + alerta ao AEE |
| EC-33 | OpenAI indisponível ou rate limit durante execução do agente | Raro | Alto | 🔴 Sem solução | ❌ | Agente falha sem fallback. Conversa trava no estado atual indefinidamente. Solução: retry com backoff exponencial (3x); se persistir, mover para HI e notificar AEE |
| EC-34 | Mensagem WhatsApp falha APÓS update de estado (stale state) | Raro | Alto | 🔴 Sem solução | ❌ | Estado avançou mas usuário nunca recebeu a mensagem — sem atomicidade entre send e state write. Solução: write-after-send (escrever estado apenas após confirmação de entrega); ou mecanismo de reconciliação |
| EC-35 | Google Calendar não implementado — confirmação enviada sem criar evento | — | Crítico | 🔴 Gap de implementação ativo | ❌ | Confirmação é enviada a mentor e founder mas GCal invite não é criado. Bloqueia produção. Implementação do `GoogleCalendarService` é pré-requisito para go-live |

---

### Grupo E — Processo (EC-36 a EC-38)

| # | Caso | Frequência | Impacto | Status | Agente resolve? | Resolução proposta |
|---|---|---|---|---|---|---|
| EC-36 | Nenhuma notificação chega ao AEE quando conversa vai para HI | Frequente | Crítico | 🔴 Sem solução | ❌ | Casos acumulam silenciosamente; AEE só descobre por reclamação. `EscalationService` deve notificar AEE em qualquer transição para `aguardando_intervencao_humana` via WhatsApp (MVP) ou Slack, configurável via `ESCALATION_CHANNEL` |
| EC-37 | Reunião cancelada no Connect enquanto fluxo está ativo | Raro | Médio | 🔴 Sem solução | ❌ | Agente continua negociando uma reunião que não existe mais. Solução: webhook do Connect para o agente, ou polling de status do `meeting_id` antes de cada etapa do fluxo |
| EC-38 | Email do mentor ausente no Connect — GCal invite não pode ser criado | Ocasional | Médio | 🔴 Sem solução | ❌ | Descoberto tarde, após toda a negociação. Solução: validar presença do `mentor_email` no trigger, antes de iniciar o fluxo. Se ausente: bloquear trigger e notificar AEE imediatamente |

---

## 3. Matriz de Prioridade

### P0 — Bloqueia piloto (deve ser resolvido antes do primeiro teste real)

| Edge Case | Frequência | Impacto | Ação |
|---|---|---|---|
| EC-05 (resposta ambígua) | Frequente | Alto | Contador de tentativas + AmbiguityResolver |
| EC-06 (mídia não-texto) | Ocasional | Médio | Corrigir bug de preservação de estado (~1h) |
| EC-10 (chatbot aversion) | Desconhecida | Crítico | Validar com Concierge Test antes do piloto |
| EC-14 (slots em mensagens separadas) | Ocasional | Crítico | Agregação de mensagens ou sinal de encerramento |
| EC-23 (sim/ok sem opção) | Frequente | Crítico | ConfirmationExtractorAgent já cobre — validar no teste |
| EC-35 (GCal não implementado) | — | Crítico | Implementar GoogleCalendarService (pré-requisito go-live) |
| EC-36 (sem notificação AEE no HI) | Frequente | Crítico | Implementar EscalationService básico |

### P1 — Resolver durante o piloto

| Edge Case | Frequência | Impacto | Ação |
|---|---|---|---|
| EC-03 (timeout mentor) | Ocasional | Crítico | Celery Beat + timeout state + EscalationService |
| EC-09 (janela 24h expira) | Ocasional | Alto | Extensão do Window Service para multi-round |
| EC-11 (phishing fear founder) | Ocasional | Alto | Aviso prévio manual pelo AEE (sem código) |
| EC-12 (trigger duplicado) | Raro | Crítico | Deduplicação por meeting_id |
| EC-24 (motor de negociação) | Ocasional | Crítico | Implementar Motor de Negociação com MAX_NEGOTIATION_ROUNDS |
| EC-31 (webhook duplicado Meta) | Ocasional | Alto | Idempotência por message_id |
| EC-32 (Celery retry) | Raro | Crítico | DLQ + retry strategy |
| EC-38 (email mentor ausente) | Ocasional | Médio | Validação no trigger antes de iniciar fluxo |

### P2 — Pós-piloto (após validação do MVP)

| Edge Case | Frequência | Impacto | Ação |
|---|---|---|---|
| EC-01 (assistente executivo) | Ocasional | Alto | Delegação de Contato no trigger (contact_type + assistant_phone) |
| EC-04 (founder rejeita todos sem alternativa) | Raro | Alto | Motor de Negociação Phase 2 |
| EC-08 (Connect não atualizado) | Frequente | Médio | ConnectService com update_meeting_status |
| EC-02 (multi-sócio) | Ocasional | Alto | Definir campo de contato primário no Connect |
| EC-07 (número errado) | Raro | Crítico | Processo de higiene de dados no Connect |
| EC-13 (Redis TTL) | Raro | Crítico | TTL refresh por mensagem + alerta de expiração |
| EC-33 (OpenAI indisponível) | Raro | Alto | Retry com backoff + fallback para HI |
| EC-34 (stale state) | Raro | Alto | Write-after-send ou reconciliação |

### P3 — Cancelamento e Remarcação (funcionalidade futura)

| Edge Case | Frequência | Impacto | Ação |
|---|---|---|---|
| EC-39 (mentor cancela pré-confirmação) | Raro | Alto | Novo ciclo de negociação ou HI |
| EC-40 (founder cancela pré-confirmação) | Raro | Alto | Mesmo tratamento de EC-39 |
| EC-41 (mentor cancela pós-confirmação) | Raro | Crítico | EscalationService + cancelar GCal + novo ciclo |
| EC-42 (founder cancela pós-confirmação) | Raro | Crítico | Mesmo tratamento de EC-41 |
| EC-43 (mentor pede remarcação) | Ocasional | Crítico | Estado RESCHEDULING_REQUESTED + novo ciclo |
| EC-44 (founder pede remarcação) | Ocasional | Crítico | Mesmo tratamento de EC-43 |
| EC-45 (N rounds sem convergência) | Raro | Alto | HI após MAX_NEGOTIATION_ROUNDS com resumo |

---

## 4. Implicações Arquiteturais

### Novos estados necessários

| Estado | Trigger | Quem detecta |
|---|---|---|
| `aguardando_resposta_mentor_followup` | Timeout de 48h após primeira mensagem | Celery Beat |
| `aguardando_clarificacao_mentor` | Resposta ambígua do mentor | SlotExtractorAgent |
| `aguardando_clarificacao_founder` | Resposta ambígua do founder | ConfirmationExtractorAgent |
| `founder_rejeitou_todos_slots` | Founder rejeita sem contra-disponibilidade | ConfirmationExtractorAgent |
| `mentor_recusou_agente` | Detecção de intenção de recusa | RefusalDetectorAgent |
| `founder_recusou_agente` | Detecção de intenção de recusa | RefusalDetectorAgent |
| `negociando_contra_proposta` | Founder oferece disponibilidade alternativa | Motor de Negociação |
| `RESCHEDULING_REQUESTED` | Qualquer ator pede remarcação pós-confirmação | Handler de cancelamento |

### Motor de Negociação (vai-e-vem)

Suporta múltiplos ciclos de negociação entre mentor e founder. Estrutura de dados:

```python
@dataclass
class NegotiationRound:
    round_number: int
    mentor_slots: list[Slot]
    founder_counter: list[Availability] | None
    status: Literal["pending", "accepted", "rejected", "escalated"]
```

- Campo `negotiation_rounds: list[NegotiationRound]` no contexto da conversa
- Contador `current_round` no estado da máquina
- Variável de ambiente `MAX_NEGOTIATION_ROUNDS` (padrão: 2)
- Ao atingir o limite: HI com resumo completo de todas as disponibilidades trocadas

### EscalationService

Serviço de notificação ao AEE. Não usa LLM — é operacional.

```python
class EscalationService:
    channel: Literal["whatsapp", "slack"]  # configurável via ESCALATION_CHANNEL

    def notify(
        case: str,           # ex: "timeout_mentor", "human_intervention", "gcal_failed"
        context: dict,       # meeting_id, mentor_name, founder_name, conversation_summary
        urgency: Literal["low", "high", "critical"]
    ) -> None: ...
```

- Acionado em qualquer transição para `aguardando_intervencao_humana`
- Acionado em eventos críticos: cancelamentos pós-confirmação, GCal falhou, mentor recusou agente
- Canal configurável via `ESCALATION_CHANNEL` (WhatsApp para MVP, Slack para equipe técnica)

### Delegação de Contato no Trigger

Campos adicionais no payload do trigger para suportar EC-01 e EC-25:

```python
class TriggerPayload(BaseModel):
    meeting_id: str
    mentor_phone: str
    founder_phone: str
    contact_type: Literal["direct", "assistant"] = "direct"
    assistant_phone: str | None = None  # preenchido quando contact_type = "assistant"
    mentor_email: str  # obrigatório — validado no trigger para EC-38
```

- Quando `contact_type = "assistant"`: WhatsApp é enviado para `assistant_phone`; linguagem adaptada ("estou entrando em contato para agendar em nome do [mentor]")
- `mentor_email` validado antes de iniciar o fluxo (EC-38)

### Novos agentes necessários

| Agente | Responsabilidade | Prioridade |
|---|---|---|
| AmbiguityResolverAgent | Detecta ambiguidade, gera pedido de clarificação contextualizado | P0 |
| RefusalDetectorAgent | Detecta intenção de recusa ou aversão a chatbot | P0 |
| TimeoutHandlerAgent | Gerencia follow-up e escalação por timeout | P1 |
| CounterProposalExtractorAgent | Extrai disponibilidade do founder para o Motor de Negociação | P1 |
| CancellationDetectorAgent | Detecta intenção de cancelamento ou remarcação | P3 |

### Novos serviços necessários

| Serviço | Responsabilidade | Prioridade |
|---|---|---|
| EscalationService | Notificação ao AEE (WhatsApp/Slack) com contexto estruturado | P0 |
| GoogleCalendarService | Criação de GCal invites (gap ativo no MVP) | P0 |
| DeduplicationService | Idempotência por meeting_id (trigger) e message_id (webhook) | P1 |
| ConnectService (escrita) | Atualiza status da reunião no Connect após confirmação | P2 |
| CancellationService | Cancela GCal e inicia novo ciclo pós-cancelamento | P3 |

### Mudanças de infraestrutura necessárias

| Mudança | Motivo | Prioridade |
|---|---|---|
| Chave primária do estado: `meeting_id` em vez de `phone_number` | Suporta deduplicação (EC-12) e múltiplos participantes | P1 |
| Celery Beat scheduler | Verificação periódica de timeouts (EC-03) | P1 |
| Celery DLQ + retry strategy | Tarefas perdidas (EC-32) | P1 |
| Idempotência de webhook por `message_id` | Webhooks duplicados do Meta (EC-31) | P1 |
| TTL refresh no Redis por mensagem recebida | Reset silencioso de estado (EC-13) | P2 |

---

## 5. Casos que Invalidam Premissas MVP

| Edge Case | Hipótese em risco | Condição de invalidação |
|---|---|---|
| EC-10 (chatbot aversion) | H1 — premissa zero | Se >20% dos mentores recusarem interação |
| EC-05 (ambiguidade frequente) | H9 — taxa aceitável | Se >20% das interações exigirem intervenção humana |
| EC-07 (número errado) | H10 — números corretos | Se >10% de falhas de entrega por número errado |
| EC-09 (janela 24h) | H11 — janela suficiente | Se >30% dos mentores demorarem >24h para responder |
| EC-12 (trigger duplicado) | N/A | Qualquer ocorrência — dado o impacto crítico |
| EC-14 (slots separados) | H7/H8 — acurácia LLM | Se >15% dos mentores enviarem slots em múltiplas mensagens |
| EC-23 (sim/ok sem opção) | H9 — taxa aceitável | Frequente por definição — validar que o agente trata corretamente no Concierge Test |

---

## 6. Open Questions

| Questão | Status |
|---|---|
| Qual é o SLA de resposta aceitável para o mentor antes do primeiro follow-up? | **DECIDIDO** — 48h, configurável via `NO_RESPONSE_TIMEOUT_SECONDS` |
| Quantas tentativas de clarificação antes de ir para human intervention? | **DECIDIDO** — 2x por round, configurável |
| Rounds de negociação antes de escalar para HI? | **DECIDIDO** — `MAX_NEGOTIATION_ROUNDS = 2`, configurável |
| Canal de notificação ao AEE — Slack, WhatsApp, e-mail? | **DECIDIDO** — WhatsApp (MVP) ou Slack, configurável via `ESCALATION_CHANNEL` |
| O aviso prévio ao founder deve ser responsabilidade do agente ou do AEE? | **DECIDIDO (MVP)** — responsabilidade do AEE; sem código. Futuro: etapa de e-mail no trigger |
| O `meeting_id` está disponível no trigger do agente hoje, ou usa apenas `phone_number`? | **ABERTA** — verificar em `src/tasks/whatsapp/schemas.py` e `src/services/state_machine_service.py` |
| Como tratar aggregação de mensagens separadas (EC-14) — janela de tempo ou sinal explícito? | **ABERTA** — decisão de UX/produto: janela de 30s vs instrução ao mentor no prompt inicial |
| GCal invite: cancelar e recriar (EC-41/43) ou usar update? | **ABERTA** — depende da API do Google Calendar e da experiência do convidado |
| EscalationService deve incluir UI para o AEE gerenciar casos em HI, ou apenas mensagem? | **ABERTA** — MVP: apenas mensagem. Futuro: dashboard de gestão de casos |
| Webhook do Connect para notificar cancelamento de reunião (EC-37) — viável? | **ABERTA** — depende da capacidade da equipe Connect de expor webhooks de status |
