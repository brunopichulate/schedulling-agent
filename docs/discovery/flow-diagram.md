# Flow Diagram — Scheduling Agent (Completo)

> Versão: 1.0 | Data: 2026-03-16
> Público: devs, tech lead, PM
> Baseado em: Stage 6 (flow map) + leitura direta do código

---

## 1. Happy Path

```mermaid
flowchart TD
    START([Connect: trigger com meeting_id + phones]) --> INIT

    INIT[INIT\nCarregar dados da reunião no estado] --> WINDOW{Janela 24h\naberta para mentor?}

    WINDOW -->|Sim| SEND_TEMPLATE_MSG[Enviar mensagem inicial ao mentor\ncom contexto da mentoria]
    WINDOW -->|Não| SEND_HELLO[Enviar template hello_world\naguardar reply para abrir janela]
    SEND_HELLO --> WAIT_TEMPLATE[WAITING_FOR_TEMPLATE_REPLY]
    WAIT_TEMPLATE -->|Mentor responde qualquer coisa| SEND_TEMPLATE_MSG

    SEND_TEMPLATE_MSG --> W_DONATED[WAITING_DONATED_RESPONSE\naguardando slots do mentor]

    W_DONATED --> MENTOR_MSG{Mentor responde}
    MENTOR_MSG -->|2+ slots válidos| DONATED_SELECTED[DONATED_SELECTED_SLOT\nSalvar slots no estado]
    DONATED_SELECTED --> SEND_FOUNDER[Enviar opções de horário ao founder]
    SEND_FOUNDER --> W_RECEIVED[WAITING_RECEIVED_RESPONSE\naguardando seleção do founder]

    W_RECEIVED --> FOUNDER_MSG{Founder responde}
    FOUNDER_MSG -->|Slot confirmado| CONFIRMED[RECEIVED_CONFIRMED\nEnviar confirmação para ambos]
    CONFIRMED --> GCAL[Criar Google Calendar invite\n@endeavor como organizador]
    GCAL --> END([Fim — estado resetado])

    style START fill:#4CAF50,color:#fff
    style END fill:#4CAF50,color:#fff
    style CONFIRMED fill:#2196F3,color:#fff
    style GCAL fill:#2196F3,color:#fff
```

---

## 2. Branches Alternativos — Lado Mentor

```mermaid
flowchart TD
    W_DONATED[WAITING_DONATED_RESPONSE]

    W_DONATED --> CHECK_TO_D{check_timeout\nmentор?}
    CHECK_TO_D -->|Sim — sem resposta| DNR[DONATED_NO_RESPONSE]
    DNR --> HI1[HUMAN_INTERVENTION_REQUIRED\n+ notificar AEE ⚠️ não implementado]
    HI1 --> RESET1([Estado resetado])

    W_DONATED --> MENTOR_R{Mentor responde}

    MENTOR_R -->|Rejeição explícita| DRS[DONATED_REJECTED_SLOTS]
    DRS --> HI2[HUMAN_INTERVENTION_REQUIRED\n+ notificar AEE ⚠️ não implementado]
    HI2 --> RESET2([Estado resetado])

    MENTOR_R -->|1 slot apenas| ASK_MORE[Pedir mais opções\nbuild_need_more_options_message]
    ASK_MORE --> W_DONATED

    MENTOR_R -->|Resposta ambígua / 0 slots| UNREC[Mensagem genérica\nbuild_unrecognized_options_message\n⚠️ sem contador de tentativas]
    UNREC --> W_DONATED

    MENTOR_R -->|Áudio / imagem / sticker| MEDIA[Fallback: só texto\n⚠️ estado preservado mas não confirmado no código]
    MEDIA --> W_DONATED

    MENTOR_R -->|'Não quero robô' / recusa| REFUSAL_D[⛔ RefusalDetectorAgent\nNÃO IMPLEMENTADO]
    REFUSAL_D --> HI3[HUMAN_INTERVENTION_REQUIRED\n+ notificar AEE imediatamente]
    HI3 --> RESET3([Estado resetado com log de recusa])

    style HI1 fill:#FF9800,color:#fff
    style HI2 fill:#FF9800,color:#fff
    style HI3 fill:#f44336,color:#fff
    style REFUSAL_D fill:#f44336,color:#fff
    style RESET1 fill:#9E9E9E,color:#fff
    style RESET2 fill:#9E9E9E,color:#fff
    style RESET3 fill:#9E9E9E,color:#fff
```

---

## 3. Branches Alternativos — Lado Founder

```mermaid
flowchart TD
    W_RECEIVED[WAITING_RECEIVED_RESPONSE]

    W_RECEIVED --> CHECK_TO_R{check_timeout\nfounder?}
    CHECK_TO_R -->|Sim — sem resposta| RNR[RECEIVED_NO_RESPONSE]
    RNR --> HI4[HUMAN_INTERVENTION_REQUIRED\n+ notificar AEE ⚠️ não implementado]
    HI4 --> RESET4([Estado resetado])

    W_RECEIVED --> FOUNDER_R{Founder responde}

    FOUNDER_R -->|Rejeita todos os slots| RREJ[RECEIVED_REJECTED]
    RREJ --> HI5[HUMAN_INTERVENTION_REQUIRED\n+ notificar AEE ⚠️ não implementado]
    HI5 --> RESET5([Estado resetado])

    FOUNDER_R -->|Seleção inválida / ambígua| UNREC_R[Pedir re-seleção\nbuild_unrecognized_selection_message\n⚠️ sem contador de tentativas]
    UNREC_R --> W_RECEIVED

    FOUNDER_R -->|'Não quero robô' / recusa| REFUSAL_R[⛔ RefusalDetectorAgent\nNÃO IMPLEMENTADO]
    REFUSAL_R --> HI6[HUMAN_INTERVENTION_REQUIRED\n+ notificar AEE imediatamente]
    HI6 --> RESET6([Estado resetado com log de recusa])

    style HI4 fill:#FF9800,color:#fff
    style HI5 fill:#FF9800,color:#fff
    style HI6 fill:#f44336,color:#fff
    style REFUSAL_R fill:#f44336,color:#fff
    style RESET4 fill:#9E9E9E,color:#fff
    style RESET5 fill:#9E9E9E,color:#fff
    style RESET6 fill:#9E9E9E,color:#fff
```

---

## 4. Máquina de Estados — Visão Completa

```mermaid
stateDiagram-v2
    [*] --> INIT

    INIT --> WAITING_FOR_TEMPLATE_REPLY : janela 24h fechada
    INIT --> WAITING_DONATED_RESPONSE : janela aberta

    WAITING_FOR_TEMPLATE_REPLY --> WAITING_DONATED_RESPONSE : mentor responde template

    WAITING_DONATED_RESPONSE --> DONATED_SELECTED_SLOT : 2+ slots válidos
    WAITING_DONATED_RESPONSE --> WAITING_DONATED_RESPONSE : 1 slot / ambíguo / mídia
    WAITING_DONATED_RESPONSE --> DONATED_NO_RESPONSE : timeout
    WAITING_DONATED_RESPONSE --> DONATED_REJECTED_SLOTS : rejeição explícita

    DONATED_SELECTED_SLOT --> WAITING_RECEIVED_RESPONSE : slots enviados ao founder

    WAITING_RECEIVED_RESPONSE --> RECEIVED_CONFIRMED : slot confirmado
    WAITING_RECEIVED_RESPONSE --> WAITING_RECEIVED_RESPONSE : seleção inválida
    WAITING_RECEIVED_RESPONSE --> RECEIVED_NO_RESPONSE : timeout
    WAITING_RECEIVED_RESPONSE --> RECEIVED_REJECTED : rejeição explícita

    DONATED_NO_RESPONSE --> HUMAN_INTERVENTION_REQUIRED
    DONATED_REJECTED_SLOTS --> HUMAN_INTERVENTION_REQUIRED
    RECEIVED_NO_RESPONSE --> HUMAN_INTERVENTION_REQUIRED
    RECEIVED_REJECTED --> HUMAN_INTERVENTION_REQUIRED

    RECEIVED_CONFIRMED --> [*] : GCal invite criado
    HUMAN_INTERVENTION_REQUIRED --> [*] : AEE assume

    note right of HUMAN_INTERVENTION_REQUIRED
        ⚠️ Hoje: sem notificação ao AEE
        Estado resetado silenciosamente
    end note

    note right of WAITING_DONATED_RESPONSE
        ⚠️ Timeout = 30s (dev)
        Produção: 48–72h úteis
        Requer Celery Beat
    end note
```

---

## 5. Gaps Críticos de Implementação (resumo visual)

```mermaid
flowchart LR
    subgraph IMPLEMENTADO["✅ Implementado"]
        HP[Happy path completo]
        TO[Timeout handler]
        REJ[Rejeição de slots]
        AMB[Resposta ambígua]
        MEDIA2[Fallback mídia]
    end

    subgraph PARCIAL["⚠️ Parcialmente implementado"]
        TO_VAL[Timeout — valor = 30s\nprecisa ser dias]
        TO_BEAT[Timeout — sem Celery Beat\nnunca dispara se usuário não responde]
        MEDIA_ST[Mídia — estado preservado?\nnão confirmado]
    end

    subgraph NAO_IMPL["❌ Não implementado"]
        NOTIF[Notificação ao AEE\nem qualquer handoff]
        REFUSAL2[RefusalDetectorAgent\nchatbot aversion]
        DEDUP[Deduplicação por meeting_id]
        COUNTER[Contador de tentativas\nantes de human intervention]
        WINDOW_F[Janela 24h para founder\nverificação antes de contactar]
    end
```

---

## Legenda de Status

| Cor / Símbolo | Significado |
|---|---|
| 🟢 Verde | Implementado e funcionando |
| 🟠 Laranja | Parcialmente implementado — gap crítico |
| 🔴 Vermelho | Não implementado — bloqueia piloto |
| ⚪ Cinza | Estado terminal — reseta estado |
