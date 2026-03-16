# Flow Diagram — Scheduling Agent

> Versão: 3.0 | Data: 2026-03-16

> **Para visualizar:** abra no GitHub (renderiza automaticamente)
> **Para usar no Miro:** copie qualquer bloco `mermaid` → Miro → "+" → More → Mermaid → cole. O Miro converte em shapes editáveis.

---

## Diagrama 1 — Happy Path

Fluxo ideal sem desvios. Objetivo: qualquer pessoa entende em 10 segundos o que o agente faz.

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

Happy path é a espinha central. Edge cases do mentor saem para a esquerda; do founder, para a direita. Todos os caminhos de intervenção convergem para um único nó ⚠️ AEE.

```mermaid
flowchart TD
    %% ===== PRÉ-FLUXO =====
    NOTE_EC11["📋 EC-11: AEE avisa mentor\nsobre risco phishing\nantes do fluxo iniciar"]
    NOTE_EC12["📋 EC-12: Deduplicação\nno trigger — ignora\ndisparo duplicado"]

    %% ===== HAPPY PATH — ESPINHA CENTRAL =====
    START([▶ Connect]) --> LOAD[Carregar dados]
    LOAD --> WIN{Janela 24h?}
    WIN -->|Sim| MSG1[Mensagem\nao mentor]
    WIN -->|Não| TPL[Template hello_world\nEC-09]
    TPL --> MSG1

    MSG1 --> MWAIT{Mentor\nresponde?}

    %% Mentor → Extração
    MWAIT -->|2+ slots válidos| EXTRACT[SlotExtractorAgent]
    EXTRACT --> MSG2[Mensagem\nao founder]
    MSG2 --> FWAIT{Founder\nresponde?}

    %% Founder → Confirmação
    FWAIT -->|Slot escolhido| FCONF[ConfirmationExtractorAgent]
    FCONF --> GCAL[Criar GCal invite]
    GCAL --> NOTIFY[Notificar AEE ✓\nEC-08: flag se dados\nConnect incompletos]
    NOTIFY --> END([✅ Concluído])

    %% ===== EDGE CASES — MENTOR LADO ESQUERDO =====
    MWAIT -->|Timeout 48h| MTO[Follow-up\nao mentor]
    MTO -->|Sem resposta| AEE
    MTO -->|Responde| EXTRACT

    MWAIT -->|1 slot| M1[Pedir\nmais opções]
    M1 --> MWAIT

    MWAIT -->|Ambíguo| MAMB[Pedir\nclarificação]
    MAMB -->|Clarifica| EXTRACT
    MAMB -->|2x sem sucesso| AEE

    MWAIT -->|Áudio / mídia| MED[Pedir texto]
    MED --> MWAIT

    MWAIT -->|Recusa agente| AEE

    MWAIT -->|Assistente responde\nEC-01| EC01["Aceitar e processar\nnormalmente — MVP"]
    EC01 --> EXTRACT

    MWAIT -->|Número errado\nEC-07| EC07["⚠️ Limitação conhecida\nnão detectável pelo agente"]

    %% ===== EDGE CASES — FOUNDER LADO DIREITO =====
    FWAIT -->|Timeout 48h| FTO[Follow-up\nao founder]
    FTO -->|Sem resposta| AEE
    FTO -->|Responde| FCONF

    FWAIT -->|Rejeita todos slots| AEE
    FWAIT -->|Recusa agente| AEE

    FWAIT -->|Seleção ambígua| FAMB[Pedir\nre-seleção]
    FAMB -->|Clarifica| FCONF
    FAMB -->|2x sem sucesso| AEE

    %% ===== CONVERGÊNCIA — INTERVENÇÃO HUMANA =====
    AEE([⚠️ AEE intervém\ncom contexto completo])

    %% ===== ESTILOS =====
    style START fill:#4CAF50,color:#fff,stroke:none
    style END fill:#4CAF50,color:#fff,stroke:none
    style EXTRACT fill:#2196F3,color:#fff,stroke:none
    style FCONF fill:#2196F3,color:#fff,stroke:none
    style GCAL fill:#2196F3,color:#fff,stroke:none
    style NOTIFY fill:#2196F3,color:#fff,stroke:none
    style AEE fill:#FF9800,color:#fff,stroke:none
    style EC07 fill:#FF9800,color:#fff,stroke:none
    style M1 fill:#9E9E9E,color:#fff,stroke:none
    style MAMB fill:#9E9E9E,color:#fff,stroke:none
    style MED fill:#9E9E9E,color:#fff,stroke:none
    style MTO fill:#9E9E9E,color:#fff,stroke:none
    style FAMB fill:#9E9E9E,color:#fff,stroke:none
    style FTO fill:#9E9E9E,color:#fff,stroke:none
    style TPL fill:#9E9E9E,color:#fff,stroke:none
    style EC01 fill:#9E9E9E,color:#fff,stroke:none
    style NOTE_EC11 fill:#FFF9C4,color:#333,stroke:#FBC02D
    style NOTE_EC12 fill:#FFF9C4,color:#333,stroke:#FBC02D
```

**Legenda de cores:**
| Cor | Significado |
|---|---|
| 🟢 Verde | Início / fim com sucesso |
| 🔵 Azul | Ação do agente concluída |
| 🟠 Laranja | Intervenção humana (AEE assume) |
| ⬜ Cinza | Passo intermediário / edge case tratado |
| 🟡 Amarelo | Nota de contexto / pré-condição |

---

## Diagrama 3 — Orquestração de Agentes

Quem chama quem. Cenários: happy path, edge cases do mentor, edge cases do founder.

```mermaid
sequenceDiagram
    actor AEE
    participant Connect
    participant Workflow as Workflow +<br/>State Machine
    participant SlotAgent as SlotExtractorAgent
    participant ConfAgent as ConfirmationExtractorAgent
    participant Mentor
    participant Founder

    Note over AEE,Connect: Pré-fluxo: AEE avisa mentor sobre agente (EC-11)

    AEE->>Connect: Aciona scheduling
    Connect->>Workflow: Trigger com dados da mentoria
    Note over Connect,Workflow: EC-12: deduplicação — ignora trigger duplicado

    Workflow->>Mentor: WhatsApp: solicita horários
    Note over Workflow,Mentor: EC-09: envia template se janela 24h fechada

    alt Happy Path — mentor responde com 2+ slots
        Mentor-->>Workflow: Responde com horários
        Workflow->>SlotAgent: Extrai slots da resposta
        SlotAgent-->>Workflow: Slots estruturados

    else Edge case — mentor envia áudio ou mídia
        Mentor-->>Workflow: Envia áudio/imagem
        Workflow->>Mentor: Pede que mande texto
        Mentor-->>Workflow: Reenvio em texto
        Workflow->>SlotAgent: Extrai slots

    else Edge case — mentor envia 1 slot
        Mentor-->>Workflow: Apenas 1 horário
        Workflow->>Mentor: Pede mais opções
        Mentor-->>Workflow: Mais horários
        Workflow->>SlotAgent: Extrai slots

    else Edge case — resposta ambígua (mentor)
        Mentor-->>Workflow: Resposta não interpretável
        Workflow->>Mentor: Pede clarificação (1x)
        alt Clarifica
            Mentor-->>Workflow: Resposta clara
            Workflow->>SlotAgent: Extrai slots
        else Não clarifica
            Workflow->>AEE: ⚠️ Notificação: mentor ambíguo repetido
        end

    else Edge case — timeout mentor
        Note over Workflow,Mentor: 48h sem resposta
        Workflow->>Mentor: Follow-up (1x)
        alt Responde
            Mentor-->>Workflow: Responde com horários
            Workflow->>SlotAgent: Extrai slots
        else Não responde
            Workflow->>AEE: ⚠️ Notificação: mentor sem resposta
        end

    else Edge case — mentor recusa agente
        Mentor-->>Workflow: "Não quero usar agente"
        Workflow->>AEE: ⚠️ Notificação imediata
    end

    Workflow->>Founder: WhatsApp: envia opções de horário

    alt Happy Path — founder escolhe slot
        Founder-->>Workflow: Escolhe horário
        Workflow->>ConfAgent: Confirma seleção
        ConfAgent-->>Workflow: Slot confirmado

    else Edge case — seleção ambígua (founder)
        Founder-->>Workflow: Resposta ambígua
        Workflow->>Founder: Pede re-seleção (1x)
        alt Clarifica
            Founder-->>Workflow: Resposta clara
            Workflow->>ConfAgent: Confirma seleção
        else Não clarifica
            Workflow->>AEE: ⚠️ Notificação: founder ambíguo repetido
        end

    else Edge case — founder rejeita todos slots
        Founder-->>Workflow: Rejeita todos
        Workflow->>AEE: ⚠️ Notificação: mediação necessária

    else Edge case — timeout founder
        Note over Workflow,Founder: 48h sem resposta
        Workflow->>Founder: Follow-up (1x)
        alt Responde
            Founder-->>Workflow: Escolhe horário
            Workflow->>ConfAgent: Confirma seleção
        else Não responde
            Workflow->>AEE: ⚠️ Notificação: founder sem resposta
        end

    else Edge case — founder recusa agente
        Founder-->>Workflow: "Não quero usar agente"
        Workflow->>AEE: ⚠️ Notificação imediata
    end

    Workflow->>Mentor: WhatsApp: confirmação ✅
    Workflow->>Founder: WhatsApp: confirmação ✅
    Workflow->>Connect: Cria GCal invite
    Note over Workflow,Connect: EC-08: notifica AEE se dados Connect incompletos
    Connect->>AEE: GCal invite + notificação ✅
```

---

## Máquina de Estados

```mermaid
stateDiagram-v2
    [*] --> INIT
    INIT --> WAITING_FOR_TEMPLATE_REPLY : janela fechada
    INIT --> WAITING_DONATED_RESPONSE : janela aberta
    WAITING_FOR_TEMPLATE_REPLY --> WAITING_DONATED_RESPONSE : mentor responde
    WAITING_DONATED_RESPONSE --> WAITING_DONATED_RESPONSE : ambíguo / 1 slot / mídia
    WAITING_DONATED_RESPONSE --> DONATED_SELECTED_SLOT : 2+ slots ✓
    WAITING_DONATED_RESPONSE --> DONATED_NO_RESPONSE : timeout
    WAITING_DONATED_RESPONSE --> DONATED_REJECTED_SLOTS : rejeição
    DONATED_SELECTED_SLOT --> WAITING_RECEIVED_RESPONSE : opções enviadas
    WAITING_RECEIVED_RESPONSE --> WAITING_RECEIVED_RESPONSE : ambíguo
    WAITING_RECEIVED_RESPONSE --> RECEIVED_CONFIRMED : slot confirmado ✓
    WAITING_RECEIVED_RESPONSE --> RECEIVED_NO_RESPONSE : timeout
    WAITING_RECEIVED_RESPONSE --> RECEIVED_REJECTED : rejeição
    DONATED_NO_RESPONSE --> HUMAN_INTERVENTION_REQUIRED
    DONATED_REJECTED_SLOTS --> HUMAN_INTERVENTION_REQUIRED
    RECEIVED_NO_RESPONSE --> HUMAN_INTERVENTION_REQUIRED
    RECEIVED_REJECTED --> HUMAN_INTERVENTION_REQUIRED
    RECEIVED_CONFIRMED --> [*]
    HUMAN_INTERVENTION_REQUIRED --> [*]
```
