# Stage 4 — Assumption Map

> Versão: 1.0 | Data: 2026-03-13 | Agente líder: PM + Strategist
> Framework: Teresa Torres — Assumption Mapping
> Eixos: Importância (1–5) × Evidência (1–5 invertido — baixa evidência = alto risco)
> Risk Score = Importância × (6 − Evidência)

---

## Overview

Este artefato mapeia todas as crenças que precisam ser verdadeiras para o agente funcionar,
avalia quais são mais perigosas se estiverem erradas, e define os experimentos de validação
mais baratos para as hipóteses de maior risco.

A hipótese mais crítica do projeto — H1 (chatbot aversion) — foi identificada no Stage 3
e elevada para o topo desta lista. Se H1 for falsa com frequência, todas as outras
hipóteses perdem relevância.

---

## 1. Tabela de Hipóteses

### Adoção & Comportamento

| ID | Hipótese | Importância | Evidência hoje | Risk Score | Categoria |
|---|---|---|---|---|---|
| H1 | Mentores e founders vão interagir com um agente automatizado no WhatsApp (não vão ignorar, recusar ou se sentir inseguros) | 5 | 1 | **25** | Adoção |
| H2 | Mentores vão responder em texto (não em áudio, imagem ou sticker) | 4 | 2 | **16** | Comportamento |
| H3 | Mentores vão fornecer 2+ opções de horário em uma única mensagem | 4 | 2 | **16** | Comportamento |
| H4 | Founders vão selecionar um horário via texto livre sem confusão | 4 | 2 | **16** | Comportamento |
| H5 | Mentores não vão sentir que a interação automatizada prejudica a relação com a Endeavor | 4 | 1 | **20** | Adoção |
| H6 | Founders não vão confundir a mensagem do agente com phishing ou spam | 4 | 1 | **20** | Adoção |

### Acurácia do LLM

| ID | Hipótese | Importância | Evidência hoje | Risk Score | Categoria |
|---|---|---|---|---|---|
| H7 | GPT-4o-mini extrai slots corretamente do português natural em ≥90% dos casos | 5 | 3 | **15** | LLM |
| H8 | GPT-4o-mini identifica corretamente o slot escolhido pelo founder em ≥90% dos casos | 5 | 3 | **15** | LLM |
| H9 | Respostas ambíguas são raras o suficiente para que a taxa de intervenção humana seja operacionalmente aceitável (<20%) | 4 | 1 | **20** | LLM |

### Operacional

| ID | Hipótese | Importância | Evidência hoje | Risk Score | Categoria |
|---|---|---|---|---|---|
| H10 | Os números de WhatsApp dos mentores no Connect estão corretos o suficiente para entrega bem-sucedida | 4 | 2 | **16** | Operacional |
| H11 | A janela de 24h do WhatsApp é suficiente para o tempo típico de resposta do mentor | 3 | 2 | **12** | Operacional |
| H12 | O AEE vai confiar no agente o suficiente para parar de intervir manualmente em cada caso | 4 | 1 | **20** | Adoção |
| H13 | A falta de atualização automática do Connect (Edge Case #8) não vai bloquear o Briefing no MVP | 3 | 2 | **12** | Operacional |

### Escala & Valor

| ID | Hipótese | Importância | Evidência hoje | Risk Score | Categoria |
|---|---|---|---|---|---|
| H14 | O agendamento é o maior custo de tempo do AEE no pipeline de mentorias | 4 | 2 | **16** | Valor |
| H15 | Edge cases são infrequentes o suficiente para que rotear todos para intervenção humana seja aceitável no MVP | 4 | 2 | **16** | Escala |
| H16 | O contato correto do founder é identificável nos dados do Connect (em casos de múltiplos sócios) | 4 | 2 | **16** | Operacional |
| H17 | Founders aceitam ao menos um dos slots propostos pelo mentor em ≥X% dos casos (não rejeitam todos) | 4 | 1 | **20** | Comportamento |

> **Legenda de evidência:** 1 = nenhuma evidência / pura crença | 2 = evidência anedótica fraca | 3 = evidência indireta razoável | 4 = evidência direta parcial | 5 = validado

---

## 2. Mapa 2×2 — Importância × Risco

```
                    ALTO RISCO (Risk Score ≥ 16)
                    ┌─────────────────────────────────────────────┐
                    │                                             │
ALTA                │  H1 (25) — chatbot aversion                 │
IMPORTÂNCIA         │  H5 (20) — relação com Endeavor             │  ← ZONA DE AÇÃO
(≥ 4)              │  H6 (20) — phishing/spam                    │     Validar ANTES do piloto
                    │  H9 (20) — taxa de ambiguidade              │
                    │  H12 (20) — confiança do AEE                │
                    │  H2 (16) — resposta em texto                │
                    │  H3 (16) — 2+ slots por mensagem            │
                    │  H4 (16) — founder seleciona sem confusão   │
                    │  H7 (15) — acurácia LLM slots               │
                    │  H8 (15) — acurácia LLM confirmação         │
                    │  H10 (16) — números corretos no Connect      │
                    │  H14 (16) — scheduling é maior custo AEE    │
                    │  H15 (16) — edge cases infrequentes         │
                    ├─────────────────────────────────────────────┤
BAIXA               │  H11 (12) — janela 24h suficiente           │  ← Monitorar no piloto
IMPORTÂNCIA         │  H13 (12) — Connect update não bloqueia     │
(< 4)               │                                             │
                    └─────────────────────────────────────────────┘
                    ALTO RISCO                    BAIXO RISCO
```

> **Insight:** Quase todas as hipóteses estão no quadrante de alto risco — porque quase todas têm evidência ≤ 2. Isso é esperado em um MVP não pilotado. A prioridade é resolver as de maior importância primeiro.

---

## 3. Top 5 Hipóteses de Maior Risco

### H1 — Mentores e founders vão interagir com o agente (Risk Score: 25)

**O que acreditamos:** A maioria dos mentores e founders vai abrir a mensagem no WhatsApp, ler, entender que é um agente automatizado da Endeavor, e responder cooperativamente.

**Por que é arriscado:** Esta é a premissa zero do projeto. Se um segmento significativo de mentores ignorar a mensagem ou recusar interação com "robô", o agente não funciona — independente de quão bom seja o LLM ou o fluxo. Não temos nenhum dado histórico porque isso nunca foi testado.

**Evidência hoje:** Nenhuma. O MVP existente nunca foi testado com mentores reais. O Concierge Test (Wizard of Oz) foi cogitado mas não executado.

**Experimento de validação (custo: baixo):**
- **Concierge Test manual:** AEE envia manualmente 5–10 mensagens para mentores reais usando o mesmo texto/tom que o agente usaria, via WhatsApp pessoal. Medir: taxa de resposta, tempo de resposta, reações ("é robô?", ignora, responde normalmente).
- **Custo:** ~2h do AEE, 0 código novo.
- **Critério de sucesso:** ≥70% dos mentores respondem de forma cooperativa na primeira tentativa.
- **Quando rodar:** antes do primeiro piloto técnico.

---

### H5 — Mentores não vão sentir que a interação prejudica a relação com a Endeavor (Risk Score: 20)

**O que acreditamos:** Mentores da Endeavor, mesmo sendo executivos ocupados, vão aceitar positivamente a automação do agendamento — entendendo que é uma melhoria de processo, não um sinal de que a Endeavor não se importa com eles.

**Por que é arriscado:** Mentores da Endeavor são um ativo relacional de alto valor. Uma experiência negativa pode não bloquear o agendamento atual, mas pode reduzir a propensão a futuras mentorias. O risco não é operacional — é relacional.

**Evidência hoje:** Nenhuma. Não há pesquisa de satisfação de mentor sobre o processo atual.

**Experimento de validação (custo: baixo):**
- Após o Concierge Test (H1), adicionar 2 perguntas ao AEE para fazer oralmente após a mentoria: "Como foi a experiência de agendamento?" e "Notou algo diferente no processo desta vez?"
- **Custo:** 0 código, ~5min por mentoria.
- **Critério de sucesso:** 0 reações explicitamente negativas sobre o processo de agendamento automatizado.

---

### H6 — Founders não vão confundir a mensagem com phishing (Risk Score: 20)

**O que acreditamos:** Founders vão reconhecer a mensagem do agente como legítima — vindas de um número desconhecido (o número virtual da Salvy), sem contexto prévio estabelecido pelo AEE.

**Por que é arriscado:** Hoje o AEE prepara o founder ("vou te mandar uma mensagem sobre os horários"). O agente não faz isso. Um número desconhecido, com mensagem formal sobre "agendamento de mentoria", pode parecer phishing — especialmente para founders mais céticos com tecnologia.

**Evidência hoje:** Nenhuma. Problema identificado no Stage 3 e confirmado como edge case distinto do #10.

**Experimento de validação (custo: baixo):**
- No Concierge Test, incluir founders também. Alternativa: o AEE pode enviar uma mensagem de "aviso prévio" manual ao founder antes do agente entrar em contato. Medir se o aviso prévio reduz taxa de non-response.
- **Hipótese secundária:** aviso prévio do AEE ("você vai receber uma mensagem nossa sobre o agendamento") elimina o risco de phishing.

---

### H9 — Taxa de respostas ambíguas é aceitável (<20% de intervenção humana) (Risk Score: 20)

**O que acreditamos:** A maioria dos mentores vai fornecer horários claros o suficiente para o SlotExtractorAgent processar. A maioria dos founders vai confirmar de forma clara o suficiente para o ConfirmationExtractorAgent processar.

**Por que é arriscado:** Português conversacional no WhatsApp é ambíguo por natureza ("qualquer dia", "pode ser de manhã", "semana que vem tá bom"). Se ≥20% das interações exigirem intervenção humana, o custo operacional do AEE pode não cair — ele muda de "fazer o agendamento" para "resolver exceções".

**Evidência hoje:** O LLM funciona em simulações com textos limpos (Gradio UI). Nunca testado com respostas reais de mentores.

**Experimento de validação (custo: médio):**
- Coletar 20–30 respostas reais de mentores (via Concierge Test ou piloto) e passar offline pelo SlotExtractorAgent. Medir: taxa de extração bem-sucedida, taxa de ambiguidade, tipos de falha mais comuns.
- **Critério de sucesso:** ≥80% de extração bem-sucedida sem intervenção.

---

### H12 — O AEE vai confiar no agente e parar de intervir manualmente (Risk Score: 20)

**O que acreditamos:** Após validar que o agente funciona, o AEE vai reduzir o monitoramento manual e deixar o agente operar de forma autônoma no happy path.

**Por que é arriscado:** Se o AEE continuar verificando manualmente cada conversa, o ganho de tempo é zero — só adicionamos complexidade. A adoção comportamental do AEE é tão crítica quanto a adoção técnica.

**Evidência hoje:** Nenhuma — nenhum AEE usou o agente em produção.

**Experimento de validação (custo: baixo):**
- Durante o piloto, medir quantas vezes o AEE intervém em conversas que estão no happy path (sem falha). Entrevista pós-piloto: "Em quais momentos você sentiu necessidade de verificar manualmente?"
- **Critério de sucesso:** AEE intervém em <10% das conversas happy path após semana 2 do piloto.

---

## 4. Roadmap de Validação

Ordenado por custo crescente:

| Prioridade | Experimento | Hipóteses validadas | Custo | Quando |
|---|---|---|---|---|
| 1 | **Concierge Test com mentores** — AEE envia manualmente mensagens com o script do agente para 5–10 mentores reais | H1, H2, H3, H5, H10 | ~2h AEE, 0 código | Antes do piloto técnico |
| 2 | **Aviso prévio ao founder** — AEE avisa founder antes do agente entrar em contato; medir taxa de resposta vs. sem aviso | H6 | ~1h AEE | Junto ao Concierge Test |
| 3 | **Teste offline de extração** — coletar respostas reais do Concierge Test e rodar pelo SlotExtractorAgent offline | H7, H9 | ~3h dev | Após Concierge Test |
| 4 | **Piloto técnico (3–5 mentorias)** — agente em produção com monitoramento ativo do AEE | H1, H4, H8, H12, H15 | ~1 semana | Após validações manuais |
| 5 | **Medição de tempo** — AEE registra tempo gasto em agendamentos 4 semanas antes e depois do piloto | H14 | ~4 semanas | Paralelo ao piloto |
| 6 | **Entrevista pós-piloto com AEE e mentores** | H5, H12 | ~2h | Após piloto |

---

## 5. Open Questions

| Questão | Stage que responde |
|---|---|
| Quais edge cases têm maior frequência estimada — o que os dados do Concierge Test vão revelar? | Stage 5 — Edge Case Taxonomy |
| Quantas vezes o agente precisa tentar extrair slots antes de desistir e ir para human intervention? | Stage 6 — Flow Map |
| Qual é o critério de sucesso do piloto para declarar o MVP validado? | Stage 7 — Métricas |
| O aviso prévio do AEE ao founder deve ser incorporado ao fluxo do agente ou é sempre manual? | Stage 6 — Flow Map + Stage 8 — PRD |
| Se H1 falhar para um subgrupo de mentores, há um fallback para contato via e-mail ou ligação? | Stage 6 — Flow Map |
