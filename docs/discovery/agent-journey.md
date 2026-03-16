# Agent Journey — Jornada dos Atores

> Versão: 3.0 | Data: 2026-03-16

> **Para visualizar:** abra no GitHub (renderiza automaticamente)
> **Para usar no Miro:** copie qualquer bloco `mermaid` → Miro → "+" → More → Mermaid → cole.

---

## Happy Path — Swimlane

```mermaid
flowchart LR
    subgraph CONNECT["🖥️ Connect"]
        C1([Invite Mentor\nenviado])
        C2([GCal invite\ncriado])
    end

    subgraph AGENTE["🤖 Agente"]
        A1[Carrega\ndados]
        A2[Extrai\nslots]
        A3[Formata\nopções]
        A4[Confirma\nslot]
        A5[Envia\nconfirmações]
    end

    subgraph MENTOR["👤 Mentor"]
        M1[Recebe\nmensagem]
        M2[Responde\ncom horários]
        M3[Recebe\nconfirmação ✅]
    end

    subgraph FOUNDER["🏢 Founder"]
        F1[Recebe\nopções]
        F2[Escolhe\nhorário]
        F3[Recebe\nconfirmação ✅]
    end

    subgraph AEE["👩 AEE"]
        AEE1[Recebe GCal\ninvite ✅]
    end

    C1 --> A1 --> M1 --> M2 --> A2 --> A3 --> F1 --> F2 --> A4 --> A5
    A5 --> M3
    A5 --> F3
    A5 --> C2 --> AEE1
```

---

## Jornada do Mentor

Inclui edge cases comportamentais do lado do mentor.

```mermaid
flowchart TD
    M_START([Recebe WhatsApp\ndo agente]) --> M_READ{Lê a\nmensagem}

    M_READ -->|Responde normalmente| M_TEXT[Envia horários\nem texto]
    M_READ -->|Manda áudio| M_AUDIO[Agente pede\nque mande texto]
    M_AUDIO --> M_TEXT

    M_TEXT --> M_EXT{Agente\nextrai slots}
    M_EXT -->|2+ slots claros| M_OK[✅ Slots recebidos\nFounder é contactado]
    M_EXT -->|Ambíguo| M_CLARIFY[Agente pede\nclarificação\nmáx 2x]
    M_CLARIFY --> M_TEXT
    M_EXT -->|Só 1 slot| M_ONE[Agente pede\nmais opções]
    M_ONE --> M_TEXT
    M_EXT -->|Slots no passado| M_PAST[Agente pede\ndatas futuras]
    M_PAST --> M_TEXT
    M_EXT -->|Horário sem data| M_DATE[Agente pede\ndia específico]
    M_DATE --> M_TEXT

    M_OK --> M_WAIT([Aguarda\nfounder escolher])
    M_WAIT --> M_CONFIRM([✅ Recebe confirmação\ncom data e hora])

    M_READ -->|Faz pergunta\nfora de escopo| M_REDIR[Agente redireciona\nmáx 2x]
    M_REDIR --> M_READ

    M_READ -->|Ignora / não responde| M_TIMEOUT[Agente faz\nfollow-up após 48h]
    M_TIMEOUT --> M_READ2{Responde?}
    M_READ2 -->|Sim| M_TEXT
    M_READ2 -->|Não| M_HI([⚠️ EscalationService\nnotifica AEE])

    M_READ -->|Recusa o agente| M_REFUSE([⚠️ EscalationService\nnotifica AEE — imediato])
    M_READ -->|Resposta emocional| M_EMO([⚠️ EscalationService\nnotifica AEE — imediato])
    M_READ -->|Já combinamos diretamente| M_DIRECT([⚠️ EscalationService\nnotifica AEE — imediato])

    M_WAIT --> M_CANCEL{Mentor quer\ncancelar?}
    M_CANCEL -->|Antes da confirmação| M_CAN_PRE([⚠️ Notifica founder + AEE\nfluxo encerrado])
    M_CONFIRM --> M_RESCH{Precisa\nremarcar?}
    M_RESCH -->|Sim| M_CAN_POST([⚠️ Notifica founder + AEE\ncancela GCal\nnovo ciclo])

    style M_START fill:#4CAF50,color:#fff,stroke:none
    style M_CONFIRM fill:#2196F3,color:#fff,stroke:none
    style M_OK fill:#4CAF50,color:#fff,stroke:none
    style M_HI fill:#FF9800,color:#fff,stroke:none
    style M_REFUSE fill:#FF9800,color:#fff,stroke:none
    style M_EMO fill:#FF9800,color:#fff,stroke:none
    style M_DIRECT fill:#FF9800,color:#fff,stroke:none
    style M_CAN_PRE fill:#FF9800,color:#fff,stroke:none
    style M_CAN_POST fill:#FF9800,color:#fff,stroke:none
```

---

## Jornada do Founder

Inclui motor de negociação (contra-proposta) e cancelamento.

```mermaid
flowchart TD
    F_START([Recebe WhatsApp\ncom opções de horário]) --> F_READ{Lê as\nopções}

    F_READ -->|Escolhe uma opção| F_TEXT[Responde\nem texto]
    F_TEXT --> F_EXT{Agente\nidentifica slot}
    F_EXT -->|Claro| F_OK([✅ Recebe\nconfirmação])
    F_EXT -->|"sim/ok" sem opção| F_WHICH[Agente pergunta\nqual número da lista]
    F_WHICH --> F_TEXT
    F_EXT -->|Ambíguo| F_CLARIFY[Agente pede\nre-seleção\nmáx 2x]
    F_CLARIFY --> F_TEXT
    F_EXT -->|Escolhe por descrição| F_DESC[Agente mapeia\ndescricão → índice]
    F_DESC --> F_OK

    F_READ -->|Rejeita todos\nsem alternativa| F_REJECT([⚠️ EscalationService\nnotifica AEE])
    F_READ -->|Rejeita + oferece disponibilidade| F_NEGO["🔄 Motor de Negociação\nAgente leva disponibilidade\nao mentor (Round N+1)"]
    F_NEGO -->|Mentor encontra slot| F_TEXT
    F_NEGO -->|MAX_ROUNDS atingido| F_REJECT

    F_READ -->|Não responde| F_TIMEOUT[Agente faz\nfollow-up após 48h]
    F_TIMEOUT --> F_READ2{Responde?}
    F_READ2 -->|Sim| F_TEXT
    F_READ2 -->|Não| F_HI([⚠️ EscalationService\nnotifica AEE])
    F_READ -->|Recusa o agente| F_REFUSE([⚠️ EscalationService\nnotifica AEE — imediato])
    F_READ -->|Resposta emocional| F_EMO([⚠️ EscalationService\nnotifica AEE — imediato])

    F_OK --> F_CANCEL{Founder quer\ncancelar?}
    F_CANCEL -->|Sim pós-confirmação| F_CAN([⚠️ Notifica mentor + AEE\ncancela GCal\nnovo ciclo ou encerra])

    style F_START fill:#4CAF50,color:#fff,stroke:none
    style F_OK fill:#2196F3,color:#fff,stroke:none
    style F_NEGO fill:#2196F3,color:#fff,stroke:none
    style F_REJECT fill:#FF9800,color:#fff,stroke:none
    style F_HI fill:#FF9800,color:#fff,stroke:none
    style F_REFUSE fill:#FF9800,color:#fff,stroke:none
    style F_EMO fill:#FF9800,color:#fff,stroke:none
    style F_CAN fill:#FF9800,color:#fff,stroke:none
```

---

## Jornada do AEE

Inclui EscalationService como canal de notificação e os cenários de intervenção expandidos.

```mermaid
flowchart TD
    AEE_START([Aciona o agente\nno Connect]) --> AEE_CONFIG{Configurar\ncontato?}
    AEE_CONFIG -->|Mentor direto| AEE_DIRECT[Preenche\ndonated_phone]
    AEE_CONFIG -->|Via assistente| AEE_ASST[Preenche\nassistant_phone\nEC-01]
    AEE_DIRECT --> AEE_WAIT
    AEE_ASST --> AEE_WAIT

    AEE_WAIT[Aguarda\nem background] --> AEE_NOTIF{Recebe\nnotificação?}

    AEE_NOTIF -->|Não — happy path| AEE_GCAL([✅ Recebe GCal\ninvite + link Connect])
    AEE_NOTIF -->|Sim — via WhatsApp ou Slack| AEE_ESC[EscalationService\nenvia contexto completo]

    AEE_ESC --> AEE_TYPE{Tipo de\nescalada}
    AEE_TYPE -->|Timeout sem resposta| AEE_CALL[Contato manual\ncom mentor/founder]
    AEE_TYPE -->|Recusa do agente| AEE_TAKEOVER[Assume conversa\nmanualmente via WhatsApp]
    AEE_TYPE -->|Slots incompatíveis\nMAX_ROUNDS| AEE_MEDIATE[Mediar nova rodada\nde horários manualmente]
    AEE_TYPE -->|Cancelamento pós-confirm| AEE_GCAL_CANCEL[Cancela GCal\ne coordena remarcação]
    AEE_TYPE -->|Já combinaram diretamente| AEE_VERIFY[Verifica combinado\ne cria GCal manual]

    AEE_CALL --> AEE_RESOLVE([Resolução manual\nAtualizar status no Connect])
    AEE_TAKEOVER --> AEE_RESOLVE
    AEE_MEDIATE --> AEE_RESOLVE
    AEE_GCAL_CANCEL --> AEE_RESOLVE
    AEE_VERIFY --> AEE_RESOLVE

    style AEE_START fill:#4CAF50,color:#fff,stroke:none
    style AEE_GCAL fill:#2196F3,color:#fff,stroke:none
    style AEE_ESC fill:#FF9800,color:#fff,stroke:none
    style AEE_RESOLVE fill:#FF9800,color:#fff,stroke:none
```

---

## Legenda

| Cor | Significado |
|---|---|
| 🟢 Verde | Início / sucesso |
| 🔵 Azul | Ação do agente concluída / Motor de Negociação |
| 🟠 Laranja | Intervenção humana via EscalationService |
| ⬜ Cinza | Passo intermediário |
