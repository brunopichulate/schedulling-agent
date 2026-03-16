# Flow Diagram — Scheduling Agent

> Versão: 4.0 | Data: 2026-03-16

> **Para visualizar:** abra no GitHub (renderiza automaticamente)
> **Para usar no Miro:** copie qualquer bloco `mermaid` → Miro → "+" → More → Mermaid → cole. O Miro converte em shapes editáveis.

---

## Diagrama 1 — Happy Path

Fluxo ideal sem desvios. Qualquer pessoa entende em 10 segundos.

```mermaid
flowchart TD
    START([▶ Connect aciona\no agente]) --> LOAD[Carrega dados\nda mentoria]
    LOAD --> WIN{Janela 24h\naberta?}
    WIN -->|Sim| MSG1[Envia mensagem\nao mentor]
    WIN -->|Não| TPL[Envia template\nhello_world]
    TPL --> MSG1
    MSG1 --> SLOTS[Mentor responde\ncom horários]
    SLOTS --> EXTRACT[SlotExtractorAgent\nextrai slots]
    EXTRACT --> MSG2[Envia opções\nao founder]
    MSG2 --> PICK[Founder escolhe\num horário]
    PICK --> CONFIRM[ConfirmationExtractorAgent\nconfirma slot]
    CONFIRM --> GCAL[Cria GCal invite\npara ambos]
    GCAL --> DONE([✅ Mentoria agendada\nAEE notificada])

    style START fill:#4CAF50,color:#fff,stroke:none
    style DONE fill:#4CAF50,color:#fff,stroke:none
    style EXTRACT fill:#2196F3,color:#fff,stroke:none
    style CONFIRM fill:#2196F3,color:#fff,stroke:none
    style GCAL fill:#2196F3,color:#fff,stroke:none
    style TPL fill:#9E9E9E,color:#fff,stroke:none
```

---

## Diagrama 2 — Fluxo Completo com Edge Cases

Happy path é a espinha central. Edge cases do mentor saem para a esquerda; do founder, para a direita. Todos os caminhos de intervenção convergem para ⚠️ AEE via EscalationService.

> EC-24 e EC-28 (founder com contra-disponibilidade) ativam o **Motor de Negociação** — ver Diagrama 2B.
> EC-39–44 (cancelamentos/remarcações) podem ocorrer em qualquer ponto do fluxo.

```mermaid
flowchart TD
    %% ===== PRÉ-FLUXO =====
    NOTE_EC11["📋 EC-11: AEE avisa founder\nsobre agente antes do fluxo"]
    NOTE_EC12["📋 EC-12: Deduplicação\npor meeting_id no trigger"]
    NOTE_DELEG["📋 EC-01/EC-25: contact_type\n+ assistant_phone no trigger\n(pré-decisão AEE)"]

    %% ===== HAPPY PATH — ESPINHA CENTRAL =====
    START([▶ Connect]) --> LOAD[Carregar dados]
    LOAD --> WIN{Janela 24h?}
    WIN -->|Sim| MSG1[Mensagem\nao mentor]
    WIN -->|Não| TPL[Template hello_world\nEC-09]
    TPL --> MSG1

    MSG1 --> MWAIT{Mentor\nresponde?}

    MWAIT -->|2+ slots válidos| EXTRACT[SlotExtractorAgent]
    EXTRACT --> MSG2[Mensagem\nao founder]
    MSG2 --> FWAIT{Founder\nresponde?}

    FWAIT -->|Slot escolhido| FCONF[ConfirmationExtractorAgent]
    FCONF --> GCAL[Criar GCal invite\n⚠️ EC-35: não implementado]
    GCAL --> NOTIFY[EscalationService\nnotifica AEE ✓]
    NOTIFY --> END([✅ Concluído])

    %% ===== MENTOR EDGE CASES =====
    MWAIT -->|Timeout 48h| MTO[Follow-up\nao mentor]
    MTO -->|Sem resposta| ESC
    MTO -->|Responde| EXTRACT

    MWAIT -->|1 slot| M1[Pedir\nmais opções]
    M1 --> MWAIT

    MWAIT -->|Ambíguo| MAMB[Pedir clarificação\nmáx 2x]
    MAMB -->|Clarifica| EXTRACT
    MAMB -->|2x sem sucesso| ESC

    MWAIT -->|Áudio / mídia| MED[Pedir texto]
    MED --> MWAIT

    MWAIT -->|Recusa agente| ESC
    MWAIT -->|Resposta emocional| ESC
    MWAIT -->|Já combinaram\ndireto EC-18| ESC

    MWAIT -->|Slots em mensagens\nseparadas EC-14| EC14["⚠️ Agente lê só\núltima mensagem\nnão implementado"]

    %% ===== FOUNDER EDGE CASES =====
    FWAIT -->|Timeout 48h| FTO[Follow-up\nao founder]
    FTO -->|Sem resposta| ESC
    FTO -->|Responde| FCONF

    FWAIT -->|Recusa agente| ESC
    FWAIT -->|Resposta emocional| ESC
    FWAIT -->|Rejeita + contra-disponibilidade\nEC-24 EC-28| NEGO["Motor de Negociação\n(ver Diagrama 2B)"]
    NEGO -->|Convergiu| FCONF
    NEGO -->|MAX_ROUNDS atingido| ESC

    FWAIT -->|"sim/ok" sem opção\nEC-23| FAMB[Pedir qual\nnúmero da lista]
    FAMB -->|Clarifica| FCONF
    FAMB -->|2x sem sucesso| ESC

    FWAIT -->|Rejeita todos\nsem alternativa| ESC

    %% ===== CANCELAMENTO / REMARCAÇÃO (EC-39–44) =====
    CANCEL_PRE["⚠️ EC-39/40: Cancelamento\nantes da confirmação\n→ notifica o outro lado + AEE"]
    CANCEL_POST["⚠️ EC-41/42/43/44: Cancelamento\nou remarcação pós-confirmação\n→ cancela GCal + novo ciclo ou AEE"]

    %% ===== CONVERGÊNCIA — INTERVENÇÃO HUMANA =====
    ESC([⚠️ EscalationService\nnotifica AEE com contexto])

    %% ===== ESTILOS =====
    style START fill:#4CAF50,color:#fff,stroke:none
    style END fill:#4CAF50,color:#fff,stroke:none
    style EXTRACT fill:#2196F3,color:#fff,stroke:none
    style FCONF fill:#2196F3,color:#fff,stroke:none
    style GCAL fill:#2196F3,color:#fff,stroke:none
    style NOTIFY fill:#2196F3,color:#fff,stroke:none
    style NEGO fill:#2196F3,color:#fff,stroke:none
    style ESC fill:#FF9800,color:#fff,stroke:none
    style CANCEL_PRE fill:#FF9800,color:#fff,stroke:none
    style CANCEL_POST fill:#FF9800,color:#fff,stroke:none
    style EC14 fill:#FF9800,color:#fff,stroke:none
    style M1 fill:#9E9E9E,color:#fff,stroke:none
    style MAMB fill:#9E9E9E,color:#fff,stroke:none
    style MED fill:#9E9E9E,color:#fff,stroke:none
    style MTO fill:#9E9E9E,color:#fff,stroke:none
    style FAMB fill:#9E9E9E,color:#fff,stroke:none
    style FTO fill:#9E9E9E,color:#fff,stroke:none
    style TPL fill:#9E9E9E,color:#fff,stroke:none
    style NOTE_EC11 fill:#FFF9C4,color:#333,stroke:#FBC02D
    style NOTE_EC12 fill:#FFF9C4,color:#333,stroke:#FBC02D
    style NOTE_DELEG fill:#FFF9C4,color:#333,stroke:#FBC02D
```

**Legenda:**
| Cor | Significado |
|---|---|
| 🟢 Verde | Início / fim com sucesso |
| 🔵 Azul | Ação do agente concluída |
| 🟠 Laranja | Intervenção humana / gap de implementação |
| ⬜ Cinza | Passo intermediário / edge case tratado |
| 🟡 Amarelo | Nota de pré-condição ou contexto |

---

## Diagrama 2B — Motor de Negociação (Vai-e-Vem)

Ativado quando o founder rejeita os slots e oferece contra-disponibilidade (EC-24, EC-28) ou quando o mentor atualiza slots enquanto o founder ainda escolhe (EC-20).

```mermaid
flowchart TD
    TRIGGER(["Founder rejeita + oferece\ndisponibilidade própria"]) --> EXTRACT_F[CounterAvailabilityExtractorAgent\nextrai disponibilidade do founder]

    EXTRACT_F --> CHECK{current_round\n< MAX_ROUNDS?}

    CHECK -->|Não — limite atingido| LIMIT["EscalationService.notify\nmax_rounds_reached\ncom histórico completo"]
    LIMIT --> HI([⚠️ AEE com todos os rounds])

    CHECK -->|Sim — Round N+1| MENTOR_MSG["Envia mensagem ao mentor\ncom disponibilidade do founder:\n'O founder pode: [horários]'\nVocê tem alguma desses?"]

    MENTOR_MSG --> MRESP{Mentor\nresponde?}

    MRESP -->|Timeout| HI
    MRESP -->|Recusa| HI
    MRESP -->|2+ slots que cruzam\ncom disponibilidade founder| EXTRACT_M[SlotExtractorAgent\nextrai slots do mentor]

    EXTRACT_M --> FOUNDER_MSG["Envia novas opções ao founder\n(slots que já sabemos que funcionam)"]

    FOUNDER_MSG --> FRESP{Founder\nresponde?}

    FRESP -->|Escolhe slot ✅| CONFIRM[ConfirmationExtractorAgent]
    CONFIRM --> GCAL[GCal invite + notificação AEE ✓]
    FRESP -->|Rejeita novamente| CHECK2{Round N+2\n< MAX_ROUNDS?}
    CHECK2 -->|Não| LIMIT
    CHECK2 -->|Sim| EXTRACT_F

    style TRIGGER fill:#9E9E9E,color:#fff,stroke:none
    style CONFIRM fill:#2196F3,color:#fff,stroke:none
    style GCAL fill:#2196F3,color:#fff,stroke:none
    style EXTRACT_M fill:#2196F3,color:#fff,stroke:none
    style EXTRACT_F fill:#2196F3,color:#fff,stroke:none
    style HI fill:#FF9800,color:#fff,stroke:none
    style LIMIT fill:#FF9800,color:#fff,stroke:none
```

**Variável de controle:** `current_round` e `max_rounds` são armazenados no `MeetingContext` (não como estados separados — evita explosão de estados). Recomendado: `MAX_NEGOTIATION_ROUNDS = 2`.

---

## Diagrama 3 — Orquestração de Agentes

Sequência de chamadas entre atores em 3 cenários: happy path, motor de negociação, cancelamento.

```mermaid
sequenceDiagram
    actor AEE
    participant Connect
    participant Workflow as Workflow +<br/>State Machine
    participant SlotAgent as SlotExtractorAgent
    participant CounterAgent as CounterAvailability<br/>ExtractorAgent
    participant ConfAgent as ConfirmationExtractorAgent
    participant EscSvc as EscalationService
    participant Mentor
    participant Founder

    Note over AEE,Connect: Pré-fluxo: AEE avisa founder (EC-11). Trigger com contact_type (EC-01/EC-25).

    AEE->>Connect: Aciona scheduling
    Connect->>Workflow: Trigger (meeting_id + phones + contact_type)
    Note over Connect,Workflow: EC-12: deduplicação por meeting_id

    Workflow->>Mentor: WhatsApp: solicita horários
    Note over Workflow,Mentor: EC-09: template se janela 24h fechada

    %% ======= HAPPY PATH =======
    rect rgb(232, 245, 233)
        Note over Workflow,Founder: Cenário 1 — Happy Path
        Mentor-->>Workflow: Responde com horários
        Workflow->>SlotAgent: Extrai slots
        SlotAgent-->>Workflow: Slots estruturados
        Workflow->>Founder: WhatsApp: envia opções
        Founder-->>Workflow: Escolhe horário
        Workflow->>ConfAgent: Confirma seleção
        ConfAgent-->>Workflow: Slot confirmado
        Workflow->>Mentor: WhatsApp: confirmação ✅
        Workflow->>Founder: WhatsApp: confirmação ✅
        Workflow->>Connect: Cria GCal invite
        Workflow->>EscSvc: notify(success)
        EscSvc->>AEE: Notificação ✅ com link Connect
    end

    %% ======= MOTOR DE NEGOCIAÇÃO =======
    rect rgb(227, 242, 253)
        Note over Workflow,Founder: Cenário 2 — Motor de Negociação (2 rounds)
        Mentor-->>Workflow: Responde com horários
        Workflow->>SlotAgent: Extrai slots (Round 1)
        SlotAgent-->>Workflow: Slots
        Workflow->>Founder: WhatsApp: envia opções
        Founder-->>Workflow: Rejeita + envia disponibilidade própria
        Workflow->>CounterAgent: Extrai disponibilidade do founder
        CounterAgent-->>Workflow: Disponibilidade estruturada
        Workflow->>Mentor: WhatsApp: "founder pode [horários], tem algum?"
        Mentor-->>Workflow: Novos slots (Round 2)
        Workflow->>SlotAgent: Extrai slots (Round 2)
        SlotAgent-->>Workflow: Slots que cruzam
        Workflow->>Founder: WhatsApp: novas opções
        Founder-->>Workflow: Escolhe ✅
        Workflow->>ConfAgent: Confirma
        Workflow->>Connect: Cria GCal invite
        Workflow->>EscSvc: notify(success, rounds=2)
        EscSvc->>AEE: Notificação ✅
    end

    %% ======= CANCELAMENTO PÓS-CONFIRMAÇÃO =======
    rect rgb(255, 243, 224)
        Note over Workflow,Mentor: Cenário 3 — Cancelamento pós-confirmação
        Mentor-->>Workflow: "preciso cancelar a reunião"
        Workflow->>Founder: WhatsApp: avisa cancelamento
        Workflow->>Connect: Cancela GCal invite
        Workflow->>EscSvc: notify(cancelled_post_confirm)
        EscSvc->>AEE: ⚠️ Cancelamento — mediação necessária
    end
```

---

## Diagrama 4 — Máquina de Estados

```mermaid
stateDiagram-v2
    [*] --> INIT
    INIT --> WAITING_FOR_TEMPLATE_REPLY : janela fechada
    INIT --> WAITING_DONATED_RESPONSE : janela aberta
    WAITING_FOR_TEMPLATE_REPLY --> WAITING_DONATED_RESPONSE : mentor responde
    WAITING_DONATED_RESPONSE --> WAITING_DONATED_RESPONSE : ambíguo / 1 slot / mídia\n(máx 2x clarificação)
    WAITING_DONATED_RESPONSE --> DONATED_SELECTED_SLOT : 2+ slots ✓
    WAITING_DONATED_RESPONSE --> DONATED_NO_RESPONSE : timeout
    WAITING_DONATED_RESPONSE --> DONATED_REJECTED_SLOTS : rejeição / recusa
    DONATED_SELECTED_SLOT --> WAITING_RECEIVED_RESPONSE : opções enviadas
    WAITING_RECEIVED_RESPONSE --> WAITING_RECEIVED_RESPONSE : ambíguo / sim-ok\n(máx 2x clarificação)
    WAITING_RECEIVED_RESPONSE --> WAITING_DONATED_RESPONSE : contra-proposta\n(round N+1, se < MAX_ROUNDS)
    WAITING_RECEIVED_RESPONSE --> RECEIVED_CONFIRMED : slot confirmado ✓
    WAITING_RECEIVED_RESPONSE --> RECEIVED_NO_RESPONSE : timeout
    WAITING_RECEIVED_RESPONSE --> RECEIVED_REJECTED : rejeição sem alternativa
    DONATED_NO_RESPONSE --> HUMAN_INTERVENTION_REQUIRED
    DONATED_REJECTED_SLOTS --> HUMAN_INTERVENTION_REQUIRED
    RECEIVED_NO_RESPONSE --> HUMAN_INTERVENTION_REQUIRED
    RECEIVED_REJECTED --> HUMAN_INTERVENTION_REQUIRED
    RECEIVED_CONFIRMED --> RESCHEDULING_REQUESTED : cancelamento/remarcação pós-confirm
    RESCHEDULING_REQUESTED --> INIT : novo ciclo autorizado pelo AEE
    RESCHEDULING_REQUESTED --> HUMAN_INTERVENTION_REQUIRED : AEE encerra
    RECEIVED_CONFIRMED --> [*]
    HUMAN_INTERVENTION_REQUIRED --> [*]

    note right of WAITING_RECEIVED_RESPONSE
        current_round e max_rounds
        são campos de contexto,
        não estados separados
    end note
```

> **Nota:** `HUMAN_INTERVITION_REQUIRED` é o nome atual no código (typo). Será corrigido para `HUMAN_INTERVENTION_REQUIRED` em breaking-change coordenada com Brunão (requer migração de Redis keys).
