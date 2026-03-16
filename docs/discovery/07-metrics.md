# Stage 7 — Success Metrics & Outcome Model

> Versão: 1.0 | Data: 2026-03-16 | Agente líder: PM + Strategist

---

## Overview

Este artefato responde: **como sabemos que resolvemos o problema?** Define o modelo de outcomes do agente — como os outputs técnicos se conectam aos resultados de negócio da iniciativa Low/Tech-Touch 2026.1 — e especifica as métricas, baseline, metas, e o que precisa ser instrumentado para medir.

**Premissa:** quase todas as métricas têm baseline = 0 hoje (não medido). Isso é esperado e documentado como gap de instrumentação, não como bloqueador do piloto.

---

## 1. Modelo de Outcomes

```
Output do agente              → Resultado imediato        → Outcome de negócio
─────────────────────────────────────────────────────────────────────────────
GCal invite criado            → Mentoria agendada         → Pipeline avança sem AEE
Conversa concluída em <2h     → Mentor/founder satisfeito → Relação Endeavor preservada
AEE não interveio             → Tempo AEE liberado        → Escala sem headcount
Ambiguidades tratadas         → Menos interrupções        → Agente confiável
```

O sucesso do agente não é técnico ("enviou a mensagem") — é operacional ("AEE gastou 0 minutos naquele agendamento") e relacional ("mentor não ficou confuso ou irritado").

---

## 2. North Star Metric

**Tempo médio entre "invite ao mentor enviado" (Etapa 6 Connect) e "GCal invite criado" (Etapa 7 concluída)**

| Campo | Detalhe |
|---|---|
| **Unidade** | Horas (ou dias) |
| **Baseline atual** | Não medido — dado crítico a coletar antes do piloto |
| **Meta com agente** | <24h para o happy path (mentor responde no mesmo dia) |
| **Como medir** | Timestamp do trigger do agente + timestamp da criação do GCal invite via Google Calendar API |
| **Por que é a North Star** | Capta tudo: se o mentor demora, se o founder demora, se o agente falha. Um número que resume a saúde do fluxo inteiro |

---

## 3. Tabela de Métricas

### Leading Indicators (medem saúde do fluxo em tempo real)

| # | Métrica | Tipo | Baseline | Meta MVP | Como medir |
|---|---|---|---|---|---|
| L1 | Taxa de resposta do mentor (% que responde na 1ª mensagem) | Leading | Não medido | ≥80% | Celery task: estados `WAITING_DONATED` → `DONATED_SELECTED_SLOT` |
| L2 | Taxa de resposta do founder (% que seleciona slot na 1ª mensagem) | Leading | Não medido | ≥80% | Celery task: estados `WAITING_RECEIVED` → `RECEIVED_CONFIRMED` |
| L3 | Taxa de extração bem-sucedida pelo SlotExtractorAgent (% sem fallback) | Leading | Não medido | ≥90% | Langfuse: trace de cada run do SlotExtractorAgent |
| L4 | Taxa de confirmação bem-sucedida pelo ConfirmationExtractorAgent | Leading | Não medido | ≥90% | Langfuse: trace de cada run do ConfirmationExtractorAgent |
| L5 | Tempo médio de resposta do mentor (horas entre envio e resposta) | Leading | Não medido | <24h | Redis: `last_interaction_time` vs timestamp da resposta |
| L6 | Tempo médio de resposta do founder (horas entre envio e resposta) | Leading | Não medido | <4h | Redis: `last_interaction_time` vs timestamp da resposta |

---

### Lagging Indicators (medem resultado do ciclo completo)

| # | Métrica | Tipo | Baseline | Meta MVP | Como medir |
|---|---|---|---|---|---|
| G1 | **North Star:** tempo médio invite → GCal invite (horas) | Lagging | Não medido | <24h happy path | Timestamp trigger + timestamp GCal API response |
| G2 | Taxa de conversão: Potential Meeting → Scheduled (%) | Lagging | Não medido | ≥70% (piloto) | Connect: status changes Potential → Scheduled |
| G3 | % de mentorias agendadas sem intervenção manual do AEE | Lagging | 0% (hoje tudo é manual) | ≥60% (piloto) | Contagem de agendamentos onde AEE não interveio |
| G4 | Tempo do AEE por agendamento (minutos) | Lagging | Não medido | <5min (só monitoramento) | Autoavaliação AEE semanal — planilha simples |

---

### Guardrails (limites que não podem ser violados)

| # | Métrica | Limite | Consequência se violado | Como medir |
|---|---|---|---|---|
| R1 | Taxa de intervenção humana (% de fluxos que vão para `HUMAN_INTERVITION_REQUIRED`) | <30% | Repensar threshold de ambiguidade e prompts | Redis: contagem de estados terminais |
| R2 | Taxa de chatbot aversion (% de mentores/founders que recusam interagir) | <10% | Pausar piloto, redesenhar abordagem de primeiro contato | Log manual no Concierge Test + piloto |
| R3 | Taxa de erro de entrega WhatsApp (% de mensagens não entregues) | <5% | Auditoria de números no Connect | WhatsApp Cloud API: delivery receipts |
| R4 | Reclamações explícitas de mentores sobre a experiência | 0 durante piloto | Pausar piloto imediatamente | Feedback AEE pós-mentoria |

---

## 4. Instrumentação — O Que Precisa Ser Construído

### Disponível hoje (sem código novo)

| Dado | Onde está | Limitação |
|---|---|---|
| Traces de cada agente (slots extraídos, confirmações) | Langfuse | Requer query manual — sem dashboard automático |
| Estados da conversa | Redis | TTL de 24h — dados somem. Sem histórico persistente |
| Logs de erros | Logger estruturado | Não centralizado para análise |

### Gaps de instrumentação (precisam ser construídos)

| Gap | Impacto | Prioridade | Esforço estimado |
|---|---|---|---|
| **Timestamp do trigger e do GCal invite** não são logados juntos | Impossível medir North Star (G1) | P0 | ~2h |
| **Estado final de cada conversa** não é persistido (Redis reseta em terminais) | Impossível medir G2, G3, R1 sem histórico | P0 | ~4h — gravar snapshot em MongoDB antes de resetar |
| **Identificação de intervenção manual do AEE** | G3 depende disso | P1 | Manual no piloto (planilha) |
| **Delivery receipts do WhatsApp** não são processados | R3 não é mensurável | P1 | ~3h — webhook para status de entrega |
| **Tempo de resposta por ator** | L5, L6 requerem dois timestamps | P1 | ~2h — gravar timestamp de cada mensagem recebida |
| **Taxa de aversion/recusa** | R2 sem detecção automática | P2 | Manual no piloto; P1 com RefusalDetectorAgent |

---

## 5. Estratégia de Medição no Piloto

### Antes do piloto (semana -1)

- AEE registra tempo gasto em agendamentos manuais por 1 semana (baseline de G4)
- AEE estima % de mentorias que vão para Potential → Scheduled hoje (baseline de G2)
- Instrumentar: gravar snapshot de estado antes de resetar (P0)
- Instrumentar: logar timestamps de trigger e GCal invite (P0)

### Durante o piloto (3–10 mentorias)

- AEE preenche planilha simples após cada mentoria: interveio? (sim/não), tempo gasto, observações
- Langfuse: monitorar taxa de extração (L3, L4) manualmente após cada conversa
- Log manual de qualquer recusa ou aversion (R2)
- AEE relata qualquer feedback de mentor sobre a experiência (R4)

### Após o piloto

- Calcular North Star (G1) com timestamps coletados
- Calcular taxa de conversão (G2) com dados do Connect + logs
- Comparar tempo AEE por agendamento antes vs. depois (G4)
- Decisão: escalar, iterar, ou pausar — baseada em G3 ≥60% e R1 <30% e R4 = 0

---

## 6. Experimento de Comparação (Before/After)

Para provar ROI, precisamos de um grupo de controle:

| Abordagem | Descrição | Viabilidade |
|---|---|---|
| **Antes/depois** | Medir N mentorias manuais, depois N com agente | ✅ Simples — AEE já faz isso |
| **A/B contemporâneo** | Metade das mentorias no agente, metade manual, ao mesmo tempo | ⚠️ Requer volume suficiente e coordenação do AEE |
| **Shadow mode** | Agente roda em paralelo ao AEE manual, sem enviar mensagens | ✅ Para validar LLM accuracy antes do piloto real |

**Recomendação MVP:** antes/depois simples. Coletar baseline 2 semanas antes, piloto por 2 semanas, comparar G1 e G4.

---

## 7. Conexão com a Iniciativa Low/Tech-Touch

O agente precisa contribuir para os KPIs da iniciativa 2026.1:

| KPI da iniciativa | Métrica do agente que evidencia contribuição |
|---|---|
| Escalar suporte a founders sem crescer headcount AEE | G3 (% sem intervenção AEE) + G4 (tempo AEE por agendamento) |
| Manter qualidade da experiência de mentoria | R4 (0 reclamações de mentores) + L1/L2 (taxas de resposta) |
| Validar modelo replicável para outras etapas do pipeline | G2 (taxa de conversão Potential → Scheduled) |

---

## 8. Open Questions → Stage 8 (PRD)

| Questão | Decisão necessária |
|---|---|
| Quem é responsável por coletar e analisar as métricas durante o piloto? | Bruno PM (produto) ou Brunão (eng)? |
| Qual é o critério formal para declarar o piloto bem-sucedido e escalar? | Combinação de G3 ≥60% + R1 <30% + R4 = 0? |
| As métricas de LLM (L3, L4) devem ter dashboard no Langfuse antes do piloto? | Prioridade de eng pré-piloto |
| Snapshot de estado antes do reset (gap P0) deve usar MongoDB ou outro storage? | Resolver decisão Redis vs MongoDB da Stage 6 |
| O shadow mode é viável antes do piloto para validar acurácia do LLM sem risco? | Decisão de produto + eng |
