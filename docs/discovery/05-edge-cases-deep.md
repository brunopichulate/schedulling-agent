# Stage 5 — Edge Case Taxonomy

> Versão: 1.0 | Data: 2026-03-13 | Agente líder: Engineer + Researcher
> Expande: `docs/edge-cases.md` (lista de 10 casos) → taxonomia completa com frequência, impacto, resolução e implicação arquitetural.

---

## Overview

Este artefato transforma a lista de edge cases em um mapa de decisão de produto. Para cada caso: o que acontece hoje, por que é problemático, com que frequência estimamos que ocorre, qual o impacto se não tratado, como deve ser resolvido, e o que isso implica arquiteturalmente.

**Premissa de prioridade:** Frequência × Impacto = Prioridade de resolução. Casos de alto impacto E alta frequência bloqueiam o piloto. Casos de alto impacto E baixa frequência devem ter fallback para human intervention. Casos de baixo impacto podem aguardar.

---

## 1. Taxonomia Completa

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
| **Status atual** | 🔴 Sem solução |
| **O que acontece hoje** | O agente não sabe que está falando com um assistente. Se a resposta for válida (2+ slots), o fluxo continua normalmente. O problema emerge depois: data confirmada pode ser incorreta |
| **Resolução proposta** | Curto prazo: aceitar a resposta como válida (assistente fala pelo mentor). Longo prazo: o AEE deve ser notificado quando o número respondente difere do número registrado no Connect (se possível detectar via nome no perfil WhatsApp) |
| **Hipótese relacionada** | H1 (engajamento), H10 (número correto no Connect) |
| **Implicação arquitetural** | Nenhuma para MVP. Futuro: signal de "assistente detectado" para notificação ao AEE |

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
| **Resolução proposta** | 1. Definir SLA de resposta (ex: 48h úteis). 2. Após SLA: enviar 1 mensagem de follow-up. 3. Após follow-up sem resposta (ex: +24h): mover para `aguardando_intervencao_humana` + notificar AEE via Slack/WhatsApp |
| **Hipótese relacionada** | H11 (janela 24h), H15 (edge cases infrequentes) |
| **Implicação arquitetural** | Novo estado: `aguardando_resposta_mentor_followup`. Celery Beat para verificação de timeout. Serviço de notificação ao AEE |

---

#### EC-04 — Founder rejeita todos os slots propostos

| Campo | Detalhe |
|---|---|
| **Descrição** | O founder responde que nenhum dos horários propostos pelo mentor funciona para ele |
| **Frequência estimada** | Raro (agendamentos costumam ter flexibilidade suficiente) |
| **Impacto se não tratado** | Alto — fluxo trava; sem regra sobre o que fazer a seguir |
| **Status atual** | 🔴 Sem solução |
| **O que acontece hoje** | ConfirmationExtractorAgent não consegue extrair confirmação → `aguardando_intervencao_humana` |
| **Resolução proposta** | Opção A: agente volta ao mentor pedindo novos horários (loop). Opção B: notifica AEE para mediar. Recomendação MVP: Opção B (mais seguro; não criar loops automáticos sem limite) |
| **Hipótese relacionada** | H17 (founders aceitam ao menos 1 slot) |
| **Implicação arquitetural** | Novo estado: `founder_rejeitou_todos_slots`. Notificação ao AEE com contexto completo (quais slots foram propostos, o que founder respondeu) |

---

#### EC-05 — Resposta ambígua do mentor ou founder

| Campo | Detalhe |
|---|---|
| **Descrição** | O ator responde com algo que não pode ser extraído como slot ou confirmação ("qualquer dia", "pode ser de manhã", "semana que vem tá bom") |
| **Frequência estimada** | Frequente — português conversacional no WhatsApp é naturalmente vago |
| **Impacto se não tratado** | Alto — extração falha; conversa para em `aguardando_intervencao_humana` sem que o usuário saiba |
| **Status atual** | 🔴 Sem solução |
| **O que acontece hoje** | SlotExtractorAgent retorna erro de extração → `aguardando_intervencao_humana` sem resposta ao usuário |
| **Resolução proposta** | 1. Agente responde pedindo esclarecimento com exemplo concreto ("Pode me dizer o dia e horário específico? Ex: quinta-feira, 14h"). 2. Após 2 tentativas sem sucesso: `aguardando_intervencao_humana` + notificação AEE |
| **Hipótese relacionada** | H9 (taxa de ambiguidade aceitável), H7/H8 (acurácia LLM) |
| **Implicação arquitetural** | Novo agente: AmbiguityResolverAgent. Contador de tentativas no estado da conversa. Novo estado: `aguardando_clarificacao_mentor` / `aguardando_clarificacao_founder` |

---

#### EC-06 — Mentor responde com mídia (áudio, imagem, sticker, documento)

| Campo | Detalhe |
|---|---|
| **Descrição** | Em vez de texto, o mentor envia uma mensagem de voz, foto, sticker ou arquivo |
| **Frequência estimada** | Ocasional — áudios são muito comuns no WhatsApp brasileiro |
| **Impacto se não tratado** | Médio — conversa trava no estado atual; mentor fica sem resposta sobre o que fazer |
| **Status atual** | 🟡 Solução definida, não implementada — fallback reply existe mas estado da máquina não é atualizado |
| **O que acontece hoje** | Fallback: "suporto apenas mensagens de texto". Mas o estado da máquina não avança nem registra que a resposta foi recebida → próxima mensagem de texto do mentor será processada normalmente |
| **Resolução proposta** | Implementar: ao receber mídia, responder com fallback E manter estado atual (não transitar). A próxima mensagem de texto retoma o fluxo no estado correto. Isso já está definido — só falta implementar |
| **Hipótese relacionada** | H2 (mentores respondem em texto) |
| **Implicação arquitetural** | Correção simples no handler de mensagens: preservar estado ao receber mídia. ~1h de dev |

---

#### EC-07 — Número de WhatsApp do mentor desatualizado no Connect

| Campo | Detalhe |
|---|---|
| **Descrição** | O número registrado no Connect não pertence mais ao mentor (mudou de número, número errado no cadastro) |
| **Frequência estimada** | Raro — mas indetectável sem mecanismo de bounce |
| **Impacto se não tratado** | Crítico — mensagem entregue para pessoa errada; dados pessoais de agendamento expostos; agendamento perdido |
| **Status atual** | 🔴 Sem solução |
| **O que acontece hoje** | WhatsApp entrega a mensagem sem erro (número existe, só não é do mentor). O agente não tem como saber |
| **Resolução proposta** | Curto prazo: AEE deve validar número do mentor antes de triggerar o agente (checklist manual). Longo prazo: o Connect deve ter campo de "número WhatsApp validado" com data de verificação. Não há solução técnica no agente para este caso |
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
| **Resolução proposta** | O agente deve chamar a API do Connect para atualizar status após criar o GCal invite. Depende de: API do Connect disponível para escrita; credenciais. Alternativa MVP: notificar AEE via mensagem para atualizar manualmente |
| **Hipótese relacionada** | H13 (Connect update não bloqueia Briefing no MVP) |
| **Implicação arquitetural** | Novo serviço: ConnectService com método `update_meeting_status`. Ou: mensagem de notificação ao AEE como workaround |

---

#### EC-09 — Janela de 24h do WhatsApp expira no meio do fluxo

| Campo | Detalhe |
|---|---|
| **Descrição** | O mentor demora mais de 24h para responder. Quando o agente tenta contactar o founder após receber a resposta do mentor, a janela de 24h já fechou para o founder (que nunca foi contactado) — e pode também ter fechado para o mentor |
| **Frequência estimada** | Ocasional — depende da velocidade de resposta do mentor |
| **Impacto se não tratado** | Alto — o agente não pode enviar mensagem livre ao founder sem janela aberta; tenta enviar e falha ou envia template indevido |
| **Status atual** | 🔴 Sem solução |
| **O que acontece hoje** | WhatsApp Window Service existe mas não cobre este cenário (verifica janela do remetente, não do destinatário seguinte no fluxo) |
| **Resolução proposta** | Antes de contactar o founder, verificar se há janela aberta. Se não: usar template de primeiro contato para o founder também. Requer template aprovado pela Meta para primeiro contato com founder |
| **Hipótese relacionada** | H11 (janela 24h suficiente) |
| **Implicação arquitetural** | Extensão do WhatsApp Window Service para cobrir múltiplos destinatários no mesmo fluxo. Template adicional para founder (requer aprovação Meta) |

---

#### EC-10 — Mentor ou founder se recusa a interagir com o agente (chatbot aversion)

| Campo | Detalhe |
|---|---|
| **Descrição** | O ator ignora a mensagem, responde explicitamente que não quer interagir com um robô, ou expressa ceticismo/desconfiança sobre a automação |
| **Frequência estimada** | Desconhecida — hipótese de alto risco (H1). Pode ser Raro ou Ocasional dependendo do perfil do mentor |
| **Impacto se não tratado** | Crítico — se Frequente, invalida o modelo inteiro. Se Raro, é tratável como fallback para human intervention |
| **Status atual** | 🔴 Sem solução |
| **O que acontece hoje** | Uma recusa explicitamente escrita pode ser interpretada pelo LLM como resposta ambígua → `aguardando_intervencao_humana`. Mas sem notificação ao AEE, a recusa fica invisível |
| **Resolução proposta** | 1. Adicionar detecção de intenção de recusa no pipeline de extração. 2. Se detectado: responder com mensagem humanizante ("Entendido. Vou avisar o time da Endeavor para entrar em contato.") + notificar AEE imediatamente + mover para `aguardando_intervencao_humana`. 3. AEE assume o contato manual |
| **Hipótese relacionada** | H1 (premissa zero do projeto) |
| **Implicação arquitetural** | Novo agente ou intent classifier: RefusalDetectorAgent. Notificação imediata ao AEE (Slack ou WhatsApp). Estado dedicado: `mentor_recusou_agente` / `founder_recusou_agente` |

---

### System-side (novos, identificados no Stage 5)

#### EC-11 — Founder não reconhece o número do agente (phishing fear)

| Campo | Detalhe |
|---|---|
| **Descrição** | O founder recebe uma mensagem de um número desconhecido (número virtual Salvy) falando sobre agendamento de mentoria, sem ter sido avisado previamente. Ignora ou bloqueia por suspeita de fraude |
| **Frequência estimada** | Ocasional — founders não têm contexto de que receberão essa mensagem |
| **Impacto se não tratado** | Alto — agendamento perdido; founder pode bloquear o número; reputação do processo comprometida |
| **Status atual** | 🔴 Sem solução |
| **O que acontece hoje** | AEE hoje prepara as partes manualmente antes do contato. O agente não faz isso |
| **Resolução proposta** | Opção A: AEE envia aviso prévio manual ao founder antes do agente entrar em contato. Opção B: o próprio trigger do agente inclui um passo de "aviso ao founder" via e-mail (Connect já tem o e-mail). Recomendação MVP: Opção A (sem novo código) |
| **Hipótese relacionada** | H6 (founder não confunde com phishing) |
| **Implicação arquitetural** | MVP: nenhuma. Futuro: etapa de notificação por e-mail ao founder antes do primeiro WhatsApp |

---

#### EC-12 — Trigger duplicado (mesma mentoria triggerada duas vezes)

| Campo | Detalhe |
|---|---|
| **Descrição** | O Connect ou o AEE triggerou o agente duas vezes para a mesma mentoria — por erro, double-click, ou retry automático |
| **Frequência estimada** | Raro, mas tecnicamente possível |
| **Impacto se não tratado** | Crítico — mentor recebe duas mensagens idênticas; dois fluxos paralelos para o mesmo número; estado da máquina pode corromper |
| **Status atual** | 🔴 Sem solução |
| **O que acontece hoje** | Não há deduplicação no trigger. O Celery task pode ser invocado múltiplas vezes para o mesmo `meeting_id` |
| **Resolução proposta** | Deduplicação por `meeting_id` antes de iniciar o fluxo. Se já existir estado para aquele meeting, ignorar o segundo trigger (ou notificar AEE) |
| **Hipótese relacionada** | N/A — falha operacional, não de adoção |
| **Implicação arquitetural** | Verificação de idempotência no state machine service: `if state_exists(meeting_id): skip`. Requer `meeting_id` como chave primária do estado (hoje provavelmente usa `phone_number`) |

---

## 2. Matriz de Prioridade

| Prioridade | Edge Case | Frequência | Impacto | Ação |
|---|---|---|---|---|
| 🔴 P0 — Bloqueia piloto | EC-05 (resposta ambígua) | Frequente | Alto | Resolver antes do piloto |
| 🔴 P0 — Bloqueia piloto | EC-06 (mídia não-texto) | Ocasional | Médio | Resolver antes do piloto (já definido, ~1h) |
| 🔴 P0 — Bloqueia piloto | EC-10 (chatbot aversion) | Desconhecida | Crítico | Validar com Concierge Test antes do piloto |
| 🟡 P1 — Resolver no piloto | EC-03 (timeout mentor) | Ocasional | Crítico | Implementar timeout + notificação AEE |
| 🟡 P1 — Resolver no piloto | EC-09 (janela 24h expira) | Ocasional | Alto | Extensão do Window Service |
| 🟡 P1 — Resolver no piloto | EC-11 (phishing fear founder) | Ocasional | Alto | Aviso prévio manual no MVP |
| 🟡 P1 — Resolver no piloto | EC-12 (trigger duplicado) | Raro | Crítico | Deduplicação por meeting_id |
| 🟢 P2 — Pós-piloto | EC-01 (assistente executivo) | Ocasional | Alto | Aceitar como válido no MVP; notificação futura |
| 🟢 P2 — Pós-piloto | EC-04 (founder rejeita todos) | Raro | Alto | Fallback para AEE no MVP |
| 🟢 P2 — Pós-piloto | EC-08 (Connect não atualizado) | Frequente | Médio | Notificação manual ao AEE no MVP |
| 🟢 P2 — Pós-piloto | EC-02 (multi-partner) | Ocasional | Alto | Definir campo no Connect |
| 🟢 P2 — Pós-piloto | EC-07 (número errado) | Raro | Crítico | Processo de higiene de dados |

---

## 3. Implicações Arquiteturais

### Novos estados necessários (além dos atuais)

| Estado | Trigger | Quem notifica |
|---|---|---|
| `aguardando_resposta_mentor_followup` | Timeout de 48h após primeira mensagem | Celery Beat |
| `aguardando_clarificacao_mentor` | Resposta ambígua do mentor | SlotExtractorAgent |
| `aguardando_clarificacao_founder` | Resposta ambígua do founder | ConfirmationExtractorAgent |
| `founder_rejeitou_todos_slots` | Founder rejeita explicitamente todos | ConfirmationExtractorAgent |
| `mentor_recusou_agente` | Detecção de intenção de recusa | RefusalDetectorAgent |
| `founder_recusou_agente` | Detecção de intenção de recusa | RefusalDetectorAgent |

### Novos agentes necessários

| Agente | Responsabilidade | Prioridade |
|---|---|---|
| AmbiguityResolverAgent | Detecta ambiguidade, gera pedido de clarificação | P1 (piloto) |
| RefusalDetectorAgent | Detecta intenção de recusa/aversão | P0 (pré-piloto) |
| TimeoutHandlerAgent | Gerencia follow-up e escalação por timeout | P1 (piloto) |

### Novos serviços necessários

| Serviço | Responsabilidade | Prioridade |
|---|---|---|
| Serviço de notificação ao AEE | Slack/WhatsApp com contexto do caso | P1 |
| ConnectService (escrita) | Atualiza status da reunião no Connect | P2 |
| Deduplicação por meeting_id | Idempotência no trigger do agente | P1 |

---

## 4. Casos que Invalidam Premissas MVP

| Edge Case | Hipótese em risco | Condição de invalidação |
|---|---|---|
| EC-10 (chatbot aversion) | H1 — premissa zero | Se >20% dos mentores recusarem interação |
| EC-05 (ambiguidade frequente) | H9 — taxa aceitável | Se >20% das interações exigirem intervenção humana |
| EC-07 (número errado) | H10 — números corretos | Se >10% de falhas de entrega por número errado |
| EC-09 (janela 24h) | H11 — janela suficiente | Se >30% dos mentores demorarem >24h para responder |
| EC-12 (trigger duplicado) | N/A | Qualquer ocorrência — dado o impacto crítico |

---

## 5. Open Questions

| Questão | Stage que responde |
|---|---|
| Qual é o SLA de resposta aceitável para o mentor antes do primeiro follow-up? (48h? 72h?) | Stage 6 — Flow Map (decisão de produto) |
| Quantas tentativas de clarificação antes de ir para human intervention? | Stage 6 — Flow Map |
| O aviso prévio ao founder deve ser responsabilidade do agente ou do AEE? | Stage 6 — Flow Map + Stage 8 — PRD |
| O `meeting_id` está disponível no trigger do agente hoje, ou usa apenas `phone_number`? | Verificação técnica no código (src/tasks, src/services/state_machine_service.py) |
| Qual canal para notificação ao AEE — Slack, WhatsApp, e-mail? | Stage 6 — Flow Map |
