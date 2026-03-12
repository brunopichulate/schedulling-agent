# Stage 1 — Problem Framing

> Versão: 1.0 | Data: 2026-03-12 | Agente líder: PM + Strategist

---

## Problem Statement

O time de AEE (Apoio a Empreendedores Endeavor) executa manualmente o agendamento de mentorias após o convite ao mentor ser enviado pelo Connect. Essa etapa — feita via WhatsApp ou e-mail, sem estrutura definida — exige que o AEE aja como intermediário de coordenação entre mentor e founder, trocando mensagens até confirmar data e hora. É uma tarefa puramente logística, repetitiva, sem valor de julgamento, que consome bandwidth do time e cria gargalo no pipeline de mentorias. Com a iniciativa Low/Tech-Touch de 2026.1 exigindo que a Endeavor escale o apoio a founders sem crescimento proporcional de headcount, esse é o ponto de maior alavanca para automação no happy path de mentorias.

---

## Contexto do Fluxo

O agendamento manual (Etapa 7) é um micro-processo dentro de um fluxo de 10 etapas:

```
Checkpoint → Suggested Priorities → Edit Priority → RecSys/My List
→ Validar com Founder → Book Meeting + Invite Mentor
→ [SCHEDULING: combinar data/hora manualmente] ← ponto de intervenção do agente
→ Briefing → Facilitar Meeting + GC → Post-Mentorship
```

O agente entra **após** o e-mail de convite ser enviado pelo Connect e **antes** do invite do Google Calendar ser criado. Tudo entre esses dois pontos é hoje feito de forma não estruturada pelo AEE.

---

## Quem Sente a Dor

### 1. AEE (Apoio a Empreendedores Endeavor) — dor primária
- É o intermediário: recebe a confirmação do mentor, consulta o founder, volta ao mentor, confirma data, atualiza o Connect, cria o invite no GCal
- Repete esse ciclo para cada mentoria no pipeline — e o pipeline tende a crescer
- Não há estrutura: cada AEE resolve isso do seu jeito (WhatsApp pessoal, e-mail, mistura dos dois)
- No modelo Low/Tech-Touch, essa tarefa é o arquétipo do que não deve escalar com headcount

### 2. Mentor — dor secundária
- Recebe um e-mail formal de convite, depois espera contato manual para combinar horário
- A experiência é fragmentada: e-mail para aceitar, WhatsApp para combinar data — sem contexto compartilhado
- Mentores ocupados perdem o fio da conversa; se o AEE demora para responder, a janela de engajamento fecha

### 3. Founder — dor terciária (mas importante)
- Já validou o mentor na Etapa 5 (Text to Founder)
- Fica aguardando o AEE confirmar data — sem visibilidade do status
- Cada dia de espera entre "aprovei o mentor" e "recebi o invite" é uma oportunidade de desengajamento

---

## Evidências do Problema

| Evidência | Fonte |
|---|---|
| Etapa 7 do SOP descreve o agendamento em 3 linhas ("combine manualmente") sem nenhum processo estruturado | SOP Endeavor Connect |
| O checklist da Etapa 7 está incompleto no próprio documento operacional | SOP Endeavor Connect |
| A iniciativa Low/Tech-Touch 2026.1 identifica explicitamente "scheduling" como etapa a automatizar | CLAUDE.md / contexto estratégico |
| O agente já existe em MVP funcional para o happy path — validando que a dor é real o suficiente para justificar desenvolvimento | Codebase atual |
| A cadeia de comunicação hoje mistura e-mail (convite) + WhatsApp (combinação) + Connect (registro) + GCal (invite) — 4 ferramentas para uma única tarefa | Análise do fluxo |

> **Lacuna de dados:** não há métrica atual de tempo médio entre "convite enviado" e "data confirmada", nem taxa de conversão de Potential Meeting → Scheduled. Isso precisa ser instrumentado.

---

## Por Que Agora

1. **Iniciativa estratégica ativa:** Low/Tech-Touch Business Models é a aposta de 2026.1 da Endeavor Brasil — validar escala sem headcount. Scheduling é o ponto de maior ROI de automação no happy path.

2. **Volume tende a crescer:** Se o modelo funcionar, mais founders entram no pipeline. O gargalo de agendamento manual se agrava linearmente com o volume.

3. **A tecnologia está disponível:** WhatsApp Business API + agentes de linguagem permitem automatizar negociação de agenda via conversação natural. O MVP já prova a viabilidade técnica.

4. **O momento é pré-escala:** Resolver isso agora, enquanto o volume é controlado, permite aprender com baixo risco. Resolver depois, com volume alto, é mais custoso e mais arriscado.

---

## Anti-Metas (O Que Está Fora de Escopo)

| Fora de escopo | Por quê |
|---|---|
| Automatizar o convite ao mentor (Etapa 6) | Já tem automação via Connect (Invite Mentor) |
| Automatizar o briefing (Etapa 8) | Já tem automação via Connect |
| Substituir o AEE na curadoria de mentores (RecSys/My List) | Requer julgamento humano; não é coordenação |
| Automatizar o GC e rating pós-mentoria | Fora do escopo do scheduling agent |
| Integrar com agenda do mentor (Google Calendar API do mentor) | Requer OAuth por mentor; complexidade desproporcional para MVP |
| Resolver matchmaking ou qualidade do fit mentor-founder | Problema do RecSys, não do scheduling |
| Suportar mentorias em grupo ou com múltiplos mentores | Fora do happy path atual |

---

## Open Questions (a responder nos próximos stages)

- Qual é o tempo médio atual entre "convite enviado" e "data confirmada"? (Stage 6 — Métricas)
- Qual é a taxa de Potential Meetings que nunca viram Scheduled? (Stage 6 — Métricas)
- O que acontece quando o mentor não responde? Quando o founder rejeita os slots? (Stage 5 — Edge Cases)
- Quando o AEE deve ser notificado de uma falha no agente, e por qual canal? (Stage 6 — Flow Map)
- O agente deve agir também na comunicação pré-briefing, ou apenas até o GCal invite? (Stage 8 — PRD)
