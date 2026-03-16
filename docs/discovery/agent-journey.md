# Agent Journey — Jornada dos Atores

> Versão: 2.1 | Data: 2026-03-16

> **Para visualizar:** abra no GitHub (renderiza automaticamente)
> **Para usar no Miro:** copie qualquer bloco `mermaid` → Miro → "+" → More → Mermaid → cole. O Miro converte em shapes editáveis.

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

```mermaid
flowchart TD
    M_START([Recebe WhatsApp\ndo agente]) --> M_READ{Lê a\nmensagem}

    M_READ -->|Responde normalmente| M_TEXT[Envia horários\nem texto]
    M_READ -->|Manda áudio| M_AUDIO[Agente pede\nque mande texto]
    M_AUDIO --> M_TEXT

    M_TEXT --> M_EXT{Agente\nextrai slots}
    M_EXT -->|2+ slots claros| M_OK[✅ Slots recebidos\nFounder é contactado]
    M_EXT -->|Ambíguo| M_CLARIFY[Agente pede\nclarificação]
    M_CLARIFY --> M_TEXT
    M_EXT -->|Só 1 slot| M_ONE[Agente pede\nmais opções]
    M_ONE --> M_TEXT

    M_OK --> M_WAIT([Aguarda\nfounder escolher])
    M_WAIT --> M_CONFIRM([✅ Recebe confirmação\ncom data e hora])

    M_READ -->|Ignora / não responde| M_TIMEOUT[Agente faz\nfollow-up após 48h]
    M_TIMEOUT --> M_READ2{Responde?}
    M_READ2 -->|Sim| M_TEXT
    M_READ2 -->|Não| M_HI([⚠️ AEE assume\no contato])

    M_READ -->|Recusa o agente| M_REFUSE([⚠️ AEE assume\nimediatamente])

    style M_START fill:#4CAF50,color:#fff,stroke:none
    style M_CONFIRM fill:#2196F3,color:#fff,stroke:none
    style M_HI fill:#FF9800,color:#fff,stroke:none
    style M_REFUSE fill:#FF9800,color:#fff,stroke:none
    style M_OK fill:#4CAF50,color:#fff,stroke:none
```

---

## Jornada do Founder

```mermaid
flowchart TD
    F_START([Recebe WhatsApp\ncom opções de horário]) --> F_READ{Lê as\nopções}

    F_READ -->|Escolhe uma opção| F_TEXT[Responde\nem texto]
    F_TEXT --> F_EXT{Agente\nidentifica slot}
    F_EXT -->|Claro| F_OK([✅ Recebe\nconfirmação])
    F_EXT -->|Ambíguo| F_CLARIFY[Agente pede\nre-seleção]
    F_CLARIFY --> F_TEXT

    F_READ -->|Rejeita todos| F_REJECT([⚠️ AEE assume\npara mediar])
    F_READ -->|Não responde| F_TIMEOUT[Agente faz\nfollow-up após 48h]
    F_TIMEOUT --> F_READ2{Responde?}
    F_READ2 -->|Sim| F_TEXT
    F_READ2 -->|Não| F_HI([⚠️ AEE assume\no contato])
    F_READ -->|Recusa o agente| F_REFUSE([⚠️ AEE assume\nimediatamente])

    style F_START fill:#4CAF50,color:#fff,stroke:none
    style F_OK fill:#2196F3,color:#fff,stroke:none
    style F_REJECT fill:#FF9800,color:#fff,stroke:none
    style F_HI fill:#FF9800,color:#fff,stroke:none
    style F_REFUSE fill:#FF9800,color:#fff,stroke:none
```

---

## Jornada do AEE

```mermaid
flowchart TD
    AEE_START([Aciona o agente\nno Connect]) --> AEE_WAIT[Aguarda\nem background]

    AEE_WAIT --> AEE_CHECK{Agente\nprecisa de ajuda?}
    AEE_CHECK -->|Não — tudo ok| AEE_GCAL([✅ Recebe GCal\ninvite no e-mail])
    AEE_CHECK -->|Sim — notificação| AEE_NOTIFY[Recebe alerta\ncom contexto completo]

    AEE_NOTIFY --> AEE_ACT{Tipo de\nproblema}
    AEE_ACT -->|Mentor sem resposta| AEE_CALL[Contato\nmanual com mentor]
    AEE_ACT -->|Slots rejeitados| AEE_MEDIATE[Mediar nova\nrodada de horários]
    AEE_ACT -->|Recusou agente| AEE_TAKEOVER[Assumir conversa\nmanualmente]

    AEE_CALL --> AEE_RESOLVE([Resolução\nmanual])
    AEE_MEDIATE --> AEE_RESOLVE
    AEE_TAKEOVER --> AEE_RESOLVE

    style AEE_START fill:#4CAF50,color:#fff,stroke:none
    style AEE_GCAL fill:#2196F3,color:#fff,stroke:none
    style AEE_RESOLVE fill:#FF9800,color:#fff,stroke:none
```

---

## Legenda

| Cor | Significado |
|---|---|
| 🟢 Verde | Início / sucesso |
| 🔵 Azul | Ação do agente concluída |
| 🟠 Laranja | Intervenção humana necessária |
| ⬜ Cinza | Passo intermediário |
