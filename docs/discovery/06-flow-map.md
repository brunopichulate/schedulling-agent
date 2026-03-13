# Stage 6 — Flow Mapping & Multi-Agent Routing

> Versão: 1.0 | Data: 2026-03-13 | Agente líder: Engineer + PM
> Baseado em: leitura direta de `src/workflows/meeting_shared/handlers.py` e `src/services/state_machine_service.py`

---

## Overview

Este artefato mapeia todos os fluxos possíveis do agente — o happy path já implementado e todos os branches alternativos identificados nos Stages 4 e 5. Também documenta o estado atual da implementação versus o que precisa ser construído, e define critérios exatos de handoff para intervenção humana.

---

## Descobertas Técnicas (leitura do código)

Antes do mapeamento de fluxos, as seguintes descobertas diretas do código são relevantes para o design:

| Achado | Impacto |
|---|---|
| **Estado em Redis, não MongoDB** — `state_machine_service.py` usa `redis.from_url`. CLAUDE.md diz MongoDB. | Divergência doc/código. Redis tem TTL de 24h — estado expira automaticamente. MongoDB teria persistência duradoura. Decisão a confirmar |
| **Chave de estado = `user_id` = phone number** — não há `meeting_id` como chave | EC-12 (trigger duplicado) se torna crítico: dois triggers para o mesmo mentor criariam conflito de estado |
| **Timeout hardcoded = 30 segundos** (`NO_RESPONSE_TIMEOUT_SECONDS = 30` em `handlers.py:38`) | Valor de desenvolvimento. Em produção precisa ser dias (ex: 48h úteis) |
| **Terminal states resetam o estado completamente** — após CONFIRMED/REJECTED/HUMAN_INTERVENTION, estado é apagado | Sem histórico de conversas para análise pós-piloto. Problema para métricas (Stage 7) |
| **Terminologia código vs. docs diverge** — código usa `donated`/`received`; docs usam `mentor`/`founder` | Confusão para novos devs. `donated` = mentor (quem doa o tempo); `received` = founder |
| **Typo em estado crítico** — `HUMAN_INTERVITION_REQUIRED` (deveria ser INTERVENTION) | Presente em `state_machine_service.py:43` e `handlers.py:62,84,114,177` |

---

## 1. Estado Atual da Máquina de Estados

### Estados existentes (implementados)

```
INIT
WAITING_FOR_TEMPLATE_REPLY      ← definido mas sem handler no STATE_HANDLERS
WAITING_DONATED_RESPONSE        ← donated = mentor
DONATED_REJECTED_SLOTS          ← terminal → reseta estado
DONATED_NO_RESPONSE             ← terminal → reseta estado
DONATED_SELECTED_SLOT           ← intermediário, não tem handler próprio
WAITING_RECEIVED_RESPONSE       ← received = founder
RECEIVED_REJECTED               ← terminal → reseta estado
RECEIVED_NO_RESPONSE            ← terminal → reseta estado
RECEIVED_CONFIRMED              ← terminal → reseta estado
HUMAN_INTERVITION_REQUIRED      ← terminal → reseta estado (typo)
```

### Handlers implementados (STATE_HANDLERS)

```python
INIT                        → handle_init
WAITING_DONATED_RESPONSE    → handle_waiting_donated
WAITING_RECEIVED_RESPONSE   → handle_waiting_received
HUMAN_INTERVITION_REQUIRED  → handle_human_intervention_required
RECEIVED_CONFIRMED          → handle_received_confirmed
```

> ⚠️ `WAITING_FOR_TEMPLATE_REPLY` está na lista de estados válidos mas não tem handler. Lacuna de implementação.

---

## 2. Happy Path (implementado)

```mermaid
flowchart TD
    A([Trigger: Connect envia meeting_id + phone]) --> B[INIT]
    B --> C[Envia template WhatsApp ao mentor\nbuild_initial_message]
    C --> D[WAITING_DONATED_RESPONSE]
    D --> E{Mentor responde}
    E -->|2+ slots válidos| F[DONATED_SELECTED_SLOT]
    F --> G[Envia opções ao founder\nbuild_slot_selection_message]
    G --> H[WAITING_RECEIVED_RESPONSE]
    H --> I{Founder responde}
    I -->|Slot confirmado| J[RECEIVED_CONFIRMED]
    J --> K[Envia confirmação para mentor + founder\nbuild_confirmation_message]
    K --> L([Estado resetado → fim])
```

**Notas de implementação:**
- Mentor = `donated`; Founder = `received` (terminologia do código)
- Confirmação enviada para ambos (`donated_phone` e `received_phone`)
- Após RECEIVED_CONFIRMED: estado é apagado do Redis

---

## 3. Flows Alternativos (parcialmente implementados ou não implementados)

### Flow 3A — Mentor fornece apenas 1 slot

```mermaid
flowchart TD
    D[WAITING_DONATED_RESPONSE] --> E{SlotExtractorAgent}
    E -->|1 slot extraído| F[Envia pedido de mais opções\nbuild_need_more_options_message]
    F --> D
```

**Status:** ✅ Implementado (`handlers.py:105–107`). Estado não avança — mentor recebe pedido e pode responder novamente.

---

### Flow 3B — Mentor fornece resposta não reconhecida / ambígua

```mermaid
flowchart TD
    D[WAITING_DONATED_RESPONSE] --> E{SlotExtractorAgent}
    E -->|0 slots, não é rejeição| F[Envia mensagem genérica\nbuild_unrecognized_options_message]
    F --> D
```

**Status:** ✅ Implementado (`handlers.py:109`). Estado não avança — aguarda nova resposta do mentor.
**Gap:** Sem contador de tentativas. Mentor pode ficar em loop indefinido sem nunca ir para human intervention.

---

### Flow 3C — Mentor rejeita explicitamente

```mermaid
flowchart TD
    D[WAITING_DONATED_RESPONSE] --> E{SlotExtractorAgent}
    E -->|is_rejected = true| F[DONATED_REJECTED_SLOTS]
    F --> G[HUMAN_INTERVITION_REQUIRED]
    G --> H[Envia mensagem de intervenção\nbuild_human_intervention_message]
    H --> I([Estado resetado])
```

**Status:** ✅ Implementado (`handlers.py:82–86`).
**Gap crítico:** Nenhuma notificação ao AEE. Estado é resetado. AEE não sabe que houve rejeição.

---

### Flow 3D — Mentor não responde (timeout)

```mermaid
flowchart TD
    D[WAITING_DONATED_RESPONSE] --> E{check_timeout}
    E -->|elapsed > NO_RESPONSE_TIMEOUT_SECONDS| F[DONATED_NO_RESPONSE]
    F --> G[HUMAN_INTERVITION_REQUIRED]
    G --> H[Envia mensagem de timeout\nbuild_timeout_message]
    H --> I([Estado resetado])
```

**Status:** ✅ Implementado (`handlers.py:60–64`).
**Gap crítico 1:** `NO_RESPONSE_TIMEOUT_SECONDS = 30` — trinta segundos. Valor de dev. Precisa ser 48–72h em produção.
**Gap crítico 2:** O timeout só é verificado quando o mentor envia uma mensagem. Se o mentor nunca responder, o check nunca roda. Precisa de Celery Beat para verificação periódica.
**Gap crítico 3:** Sem notificação ao AEE.

---

### Flow 3E — Founder seleciona opção inválida / ambígua

```mermaid
flowchart TD
    H[WAITING_RECEIVED_RESPONSE] --> I{ConfirmationExtractorAgent}
    I -->|índice inválido ou ambíguo| J[Envia pedido de re-seleção\nbuild_unrecognized_selection_message]
    J --> H
```

**Status:** ✅ Implementado (`handlers.py:144–146`). Estado não avança — aguarda nova resposta.
**Gap:** Sem contador de tentativas. Founder pode ficar em loop indefinido.

---

### Flow 3F — Founder rejeita todos os slots

```mermaid
flowchart TD
    H[WAITING_RECEIVED_RESPONSE] --> I{ConfirmationExtractorAgent}
    I -->|is_rejected = true| J[RECEIVED_REJECTED]
    J --> K[HUMAN_INTERVITION_REQUIRED]
    K --> L[Envia mensagem de rejeição\nbuild_rejected_message]
    L --> M([Estado resetado])
```

**Status:** ✅ Implementado (`handlers.py:138–142`).
**Gap:** Sem notificação ao AEE. Sem loop para re-pedir slots ao mentor.

---

### Flow 3G — Founder não responde (timeout)

```mermaid
flowchart TD
    H[WAITING_RECEIVED_RESPONSE] --> I{check_timeout}
    I -->|elapsed > timeout| J[RECEIVED_NO_RESPONSE]
    J --> K[HUMAN_INTERVITION_REQUIRED]
    K --> L[Envia mensagem de timeout]
    L --> M([Estado resetado])
```

**Status:** ✅ Implementado (`handlers.py:112–116`).
**Mesmos gaps do Flow 3D:** timeout = 30s, sem Celery Beat, sem notificação ao AEE.

---

### Flow 3H — Mensagem de mídia (áudio, imagem, sticker) [EC-06]

**Status:** 🟡 Parcialmente implementado.
**O que existe:** Handler de fallback envia mensagem de texto. Estado NÃO é atualizado.
**Gap:** Se mentor está em `WAITING_DONATED_RESPONSE` e envia áudio, recebe fallback mas o estado permanece correto — próxima mensagem de texto é processada normalmente. Comportamento aceitável para MVP se verificado.
**Ação necessária:** Confirmar que o handler de mídia preserva o estado atual (não faz transição).

---

### Flow 3I — Chatbot aversion / recusa explícita [EC-10] — NÃO IMPLEMENTADO

```mermaid
flowchart TD
    D[qualquer estado ativo] --> E{Mentor/Founder responde}
    E -->|"não quero robô" / recusa explícita| F[RefusalDetectorAgent]
    F --> G[MENTOR_RECUSOU / FOUNDER_RECUSOU]
    G --> H[Envia mensagem humanizante\n'Entendido, vou avisar o time']
    H --> I[Notifica AEE imediatamente]
    I --> J[HUMAN_INTERVITION_REQUIRED]
    J --> K([Estado resetado com log de recusa])
```

**Status:** ❌ Não implementado.
**Hoje:** recusa explícita é tratada como rejeição de slots (if `is_rejected`) ou como resposta ambígua — nem sempre chega ao estado correto, e nunca notifica o AEE.

---

### Flow 3J — Trigger duplicado [EC-12] — NÃO IMPLEMENTADO

```mermaid
flowchart TD
    A([Trigger 1: meeting_id X, phone Y]) --> B{Estado existe para phone Y?}
    B -->|Não| C[Inicializa estado → fluxo normal]
    B -->|Sim| D[Ignora trigger duplicado]
    A2([Trigger 2: mesmo meeting_id X]) --> B
```

**Status:** ❌ Não implementado. Hoje dois triggers criariam dois fluxos concorrentes no mesmo `user_id` (phone number) no Redis, com risco de sobrescrição de estado.

---

### Flow 3K — Janela 24h expira entre mentor e founder [EC-09] — NÃO IMPLEMENTADO

**Cenário:** Mentor demora >24h para responder. Quando o agente tenta contatar o founder, a janela WhatsApp do founder (que nunca foi contactado) não está aberta — requer template.

**Status:** ❌ Não implementado. O `WhatsApp Window Service` verifica janela do remetente, mas não do próximo destinatário no fluxo.

---

## 4. Critérios de Handoff para Intervenção Humana

| Condição | Estado atual → destino | Notificação ao AEE | Implementado? |
|---|---|---|---|
| Mentor não responde após timeout | `WAITING_DONATED_RESPONSE` → `DONATED_NO_RESPONSE` → `HUMAN_INTERVITION_REQUIRED` | ❌ Não | ⚠️ Parcial (sem Celery Beat, timeout = 30s) |
| Mentor rejeita explicitamente | `WAITING_DONATED_RESPONSE` → `DONATED_REJECTED_SLOTS` → `HUMAN_INTERVITION_REQUIRED` | ❌ Não | ✅ Lógica sim |
| Founder não responde após timeout | `WAITING_RECEIVED_RESPONSE` → `RECEIVED_NO_RESPONSE` → `HUMAN_INTERVITION_REQUIRED` | ❌ Não | ⚠️ Parcial |
| Founder rejeita todos os slots | `WAITING_RECEIVED_RESPONSE` → `RECEIVED_REJECTED` → `HUMAN_INTERVITION_REQUIRED` | ❌ Não | ✅ Lógica sim |
| Recusa explícita do agente | qualquer → `HUMAN_INTERVITION_REQUIRED` | ❌ Não | ❌ Não |
| Ambiguidade após N tentativas | qualquer → `HUMAN_INTERVITION_REQUIRED` | ❌ Não | ❌ Não (sem contador) |

> **Gap sistêmico:** Nenhum caminho para `HUMAN_INTERVITION_REQUIRED` notifica o AEE. O estado é resetado silenciosamente. O AEE só saberia se monitorar ativamente — o que derruba H12 (confiança do AEE no agente).

---

## 5. Canal de Notificação ao AEE — Decisão em Aberto

Para que as notificações de human intervention funcionem, é necessário decidir o canal:

| Opção | Prós | Contras | Esforço |
|---|---|---|---|
| **WhatsApp** (mesmo número do agente) | Zero nova integração; AEE já usa WhatsApp | Mistura o canal do agente com monitoramento; pode confundir | Baixo |
| **Slack** | Canal dedicado; fácil de filtrar; suporta estrutura | Requer nova integração (Slack webhook ou bot) | Médio |
| **E-mail** | Registro formal; sem nova integração | AEE pode não ver em tempo real | Baixo |

**Recomendação para MVP:** WhatsApp (número dedicado ou o próprio número do agente, para um grupo de AEEs). Zero nova integração. Pode ser refinado pós-piloto.

---

## 6. Máquina de Estados Expandida (target state)

### Estados a adicionar (além dos 11 existentes)

| Estado novo | Trigger | Quem gera |
|---|---|---|
| `AWAITING_MENTOR_CLARIFICATION` | SlotExtractorAgent recebe resposta ambígua (1ª vez) | AmbiguityResolverAgent |
| `AWAITING_FOUNDER_CLARIFICATION` | ConfirmationExtractorAgent recebe seleção ambígua (1ª vez) | AmbiguityResolverAgent |
| `MENTOR_REFUSED_AGENT` | RefusalDetectorAgent detecta recusa | RefusalDetectorAgent |
| `FOUNDER_REFUSED_AGENT` | RefusalDetectorAgent detecta recusa | RefusalDetectorAgent |
| `AWAITING_MENTOR_FOLLOWUP` | Celery Beat detecta timeout sem resposta do mentor | TimeoutHandlerAgent |

### Estados a corrigir

| Estado atual | Problema | Correção |
|---|---|---|
| `HUMAN_INTERVITION_REQUIRED` | Typo: INTERVITION | Renomear para `HUMAN_INTERVENTION_REQUIRED` (breaking change — requer migração) |
| `WAITING_FOR_TEMPLATE_REPLY` | Definido mas sem handler | Implementar handler ou remover da lista |

---

## 7. Novos Agentes Necessários

| Agente | Input | Output | Prioridade |
|---|---|---|---|
| **RefusalDetectorAgent** | Texto da mensagem recebida | `{is_refusal: bool, sentiment: str}` | P0 — pré-piloto |
| **AmbiguityResolverAgent** | Texto ambíguo + contexto do estado | Mensagem de clarificação + contador de tentativas | P1 — piloto |
| **TimeoutHandlerAgent** | Estado atual + `last_interaction_time` | Mensagem de follow-up ou escalação | P1 — piloto |
| **NotificationAgent** (ou serviço simples) | Contexto do caso + canal | Mensagem ao AEE via WhatsApp/Slack | P1 — piloto |

---

## 8. Open Questions → Stage 7

| Questão | Decisão necessária |
|---|---|
| Redis ou MongoDB para persistência de estado? CLAUDE.md diz MongoDB, código usa Redis | Confirmar com Brunão — impacta TTL, histórico, análise pós-piloto |
| Qual é o SLA de timeout para mentor? (48h? 72h?) | Decisão de produto — Bruno PM |
| Qual é o SLA de timeout para founder? | Decisão de produto — Bruno PM |
| Quantas tentativas de clarificação antes de human intervention? (recomendação: 2) | Decisão de produto — Bruno PM |
| Canal de notificação ao AEE: WhatsApp vs Slack vs e-mail? | Decisão de produto — Bruno PM (recomendação: WhatsApp no MVP) |
| O typo `INTERVITION` deve ser corrigido antes do piloto? | Decisão de eng — Brunão (breaking change em Redis keys) |
| `WAITING_FOR_TEMPLATE_REPLY` — implementar handler ou remover? | Decisão de eng — Brunão |
