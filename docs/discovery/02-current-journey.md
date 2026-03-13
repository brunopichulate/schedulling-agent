# Stage 2 — Current State Journey Map

> Versão: 1.0 | Data: 2026-03-13 | Agente líder: Researcher

---

## Overview

O agendamento de mentorias na Endeavor é hoje uma tarefa manual, não estruturada, executada pelo time de AEE como intermediário entre mentor e founder. Após o sistema Connect enviar o e-mail de convite ao mentor, o AEE assume o controle total do processo: entra em contato pelo canal que preferir (WhatsApp ou e-mail, sem padrão), aguarda a resposta do mentor, repassa os horários ao founder, aguarda a escolha, cria o invite no Google Calendar e atualiza o Connect manualmente. Não há script, checklist, timeout, ni métrica de tempo. O processo depende inteiramente da iniciativa e disponibilidade do AEE, escala linearmente com o volume do pipeline, e gera experiências fragmentadas para mentor e founder.

---

## Atores

| Ator | Papel no fluxo | Canal atual | Estado emocional |
|---|---|---|---|
| **AEE** | Intermediário total — inicia, coordena, confirma e registra | WhatsApp pessoal, e-mail, Connect, Google Calendar | Sobrecarregado; tarefa repetitiva e sem valor de julgamento ocupa bandwidth estratégico |
| **Mentor** | Propõe horários disponíveis | WhatsApp pessoal (número registrado no Connect) | Confuso; recebe e-mail formal de convite, depois contato informal por WhatsApp — contexto fragmentado |
| **Founder** | Seleciona horário preferido | WhatsApp | Ansioso; aprovou o mentor na Etapa 5, agora espera sem visibilidade do status |

---

## Jornada Passo a Passo

### Etapa 1 — Convite formal enviado ao mentor
| Campo | Detalhe |
|---|---|
| **Quem age** | Connect (sistema automatizado) |
| **Canal** | E-mail |
| **O que acontece** | O Connect envia um e-mail formal de convite ao mentor após o AEE clicar em "Invite Mentor" na Etapa 6 do fluxo |
| **O que o mentor vê** | E-mail formal com contexto da mentoria — empresa, founder, tema |
| **Fricção** | Nenhuma nesta etapa — é automatizada |
| **Estado do founder** | Aguardando, sem notificação de que o convite foi enviado |

---

### Etapa 2 — AEE contata mentor para combinar horário
| Campo | Detalhe |
|---|---|
| **Quem age** | AEE |
| **Canal** | WhatsApp pessoal ou e-mail (decisão individual do AEE) |
| **O que acontece** | O AEE entra em contato com o mentor para pedir 2 ou mais opções de horário. Não há script padrão — cada AEE improvisa a mensagem |
| **O que o mentor vê** | Contato informal, sem referência ao e-mail formal já recebido — contexto duplicado e desconexo |
| **Fricção** | ⚠️ Canal inconsistente (WhatsApp vs e-mail) | Sem script ou tom padrão | Mentor precisa reconectar mentalmente ao e-mail que recebeu antes | Alguns AEEs usam WhatsApp pessoal, o que mistura vida profissional e pessoal |
| **Falhas conhecidas** | Mentor pode ignorar por não reconhecer o remetente | Mentor pode ter trocado de número sem atualizar o Connect |

---

### Etapa 3 — Mentor responde com horários disponíveis
| Campo | Detalhe |
|---|---|
| **Quem age** | Mentor |
| **Canal** | WhatsApp ou e-mail (espelha o canal usado pelo AEE) |
| **O que acontece** | Mentor responde com horários em formato livre ("terça depois das 14h", "pode ser qualquer manhã da semana que vem") |
| **O que o AEE recebe** | Texto não estruturado, sem formato padrão |
| **Fricção** | ⚠️ Resposta pode ser ambígua ou incompleta | Mentor pode demorar dias para responder | Não há mecanismo de follow-up definido | Mentor pode enviar áudio ou imagem |
| **Falhas conhecidas** | Mentor não responde → conversa fica em aberto indefinidamente | Mentor propõe apenas 1 horário (abaixo do mínimo necessário) | Mentor cancela o processo sem aviso |

---

### Etapa 4 — AEE interpreta resposta e formata as opções
| Campo | Detalhe |
|---|---|
| **Quem age** | AEE |
| **Canal** | Interno (sem ferramenta dedicada) |
| **O que acontece** | O AEE lê a resposta do mentor, interpreta os horários propostos, e formula uma mensagem com as opções formatadas para o founder |
| **Ferramentas** | Nenhuma — processo mental, às vezes anotação no próprio WhatsApp ou bloco de notas |
| **Fricção** | ⚠️ Interpretação humana de texto ambíguo → risco de erro | Sem registro formal do que o mentor propôs | Se o AEE abre a mensagem e não responde imediatamente, perde o contexto |

---

### Etapa 5 — AEE envia opções de horário ao founder
| Campo | Detalhe |
|---|---|
| **Quem age** | AEE |
| **Canal** | WhatsApp |
| **O que acontece** | AEE envia as opções de horário ao founder, pedindo que escolha uma |
| **O que o founder vê** | Primeira comunicação direta sobre a mentoria desde que aprovou o mentor (Etapa 5). Pode ter passado dias |
| **Fricção** | ⚠️ Sem padrão de formatação — cada AEE apresenta as opções de forma diferente | Founder pode não lembrar do contexto se o tempo de espera foi longo | Founder pode não responder imediatamente |
| **Estado emocional do founder** | Alívio ("finalmente!") ou frustração ("demorou demais") |

---

### Etapa 6 — Founder escolhe o horário
| Campo | Detalhe |
|---|---|
| **Quem age** | Founder |
| **Canal** | WhatsApp |
| **O que acontece** | Founder responde com a opção preferida em texto livre |
| **Fricção** | ⚠️ Resposta pode ser ambígua ("o primeiro tá ótimo" sem citar qual é) | Founder pode sugerir um horário diferente dos propostos | Founder pode rejeitar todos os horários |
| **Falhas conhecidas** | Founder não responde → conversa fica aberta | Founder com múltiplos sócios — qual deles recebe a mensagem? |

---

### Etapa 7 — AEE cria o invite no Google Calendar
| Campo | Detalhe |
|---|---|
| **Quem age** | AEE |
| **Canal** | Google Calendar |
| **O que acontece** | AEE cria manualmente o evento no Google Calendar. Organizador: conta @endeavor. Convidados: mentor (e-mail pessoal ou corporativo) + founder |
| **Fricção** | ⚠️ E-mail do mentor pode estar desatualizado no Connect | AEE precisa encontrar o e-mail correto manualmente | Sem validação — invite pode ser enviado para o endereço errado |
| **Título do evento** | `<Empresa> × <Nome do Mentor>` (por convenção — não há automação) |

---

### Etapa 8 — AEE atualiza o Connect
| Campo | Detalhe |
|---|---|
| **Quem age** | AEE |
| **Canal** | Endeavor Connect |
| **O que acontece** | AEE atualiza manualmente o status da reunião no Connect (Potential Meeting → Scheduled) e registra data/hora confirmada |
| **Fricção** | ⚠️ Etapa frequentemente esquecida ou adiada | Sem notificação automática para o sistema | Dados desatualizados no Connect geram relatórios incorretos |

---

## Resumo de Fricções

| # | Fricção | Severidade | Onde ocorre |
|---|---|---|---|
| F1 | Nenhum script ou processo padrão — cada AEE improvisa | 🔴 Alta | Etapas 2, 5 |
| F2 | Fragmentação de canal: e-mail formal → WhatsApp informal (mentor não conecta os dois) | 🔴 Alta | Etapas 1→2 |
| F3 | Founder sem visibilidade entre o convite ao mentor e o recebimento das opções | 🔴 Alta | Etapas 1→5 |
| F4 | Sem timeout ou follow-up definido — conversa pode ficar em aberto indefinidamente | 🔴 Alta | Etapas 3, 6 |
| F5 | AEE é gargalo síncrono — cada mentoria exige atenção ativa do AEE | 🔴 Alta | Todo o fluxo |
| F6 | Respostas em formato livre → interpretação manual → risco de erro | 🟡 Média | Etapas 3, 4, 6 |
| F7 | Atualização do Connect manual e frequentemente esquecida | 🟡 Média | Etapa 8 |
| F8 | E-mail do mentor pode estar errado no Connect — sem mecanismo de validação | 🟡 Média | Etapa 7 |
| F9 | AEE usa WhatsApp pessoal — mistura canal profissional e pessoal | 🟡 Média | Etapas 2, 5 |
| F10 | SOP tem apenas 3 linhas para esta etapa inteira — sem checklist | 🟡 Média | Todo o fluxo |

---

## Timing & Volume

### O que sabemos
- O fluxo tem 8 etapas manuais após o trigger automático (Etapa 1)
- Cada mentoria exige pelo menos 2 rodadas de contato (mentor + founder) antes do invite
- O volume de mentorias tende a crescer com a iniciativa Low/Tech-Touch 2026.1

### Lacunas de dados (não medidos hoje)

| Métrica | Por que importa |
|---|---|
| Tempo médio entre "convite enviado" (Etapa 1) e "data confirmada" (Etapa 7) | Mede o custo real do processo atual — baseline para comparação pós-agente |
| Taxa de conversão Potential Meeting → Scheduled | Revela quantas mentorias "morrem" no processo de agendamento |
| Número de follow-ups por agendamento (média) | Mede esforço real do AEE por mentoria |
| % de agendamentos que exigem intervenção por ambiguidade ou falha | Dimensiona o problema de edge cases |
| Volume atual de mentorias por mês e tendência | Projeta o crescimento do gargalo |

> **Ação necessária:** instrumentar estas métricas antes ou durante o piloto, mesmo que manualmente via planilha. Sem baseline, é impossível provar ROI do agente.

---

## Insights-Chave

1. **O AEE é um roteador humano, não um tomador de decisão.** Em nenhuma das 8 etapas o AEE exerce julgamento sobre o conteúdo da mentoria — apenas transmite informação entre partes. Este é o arquétipo da tarefa que pode ser automatizada sem perda de qualidade.

2. **A fragmentação de canal cria contexto duplicado para o mentor.** O mentor recebe um e-mail formal (Connect) e depois um WhatsApp informal (AEE), sem ligação explícita entre os dois. A primeira mensagem do agente deve referenciar o convite anterior para criar continuidade.

3. **O founder é a persona mais invisível do fluxo atual.** Entre aprovar o mentor (Etapa 5 do fluxo geral) e receber o invite do GCal, o founder não recebe nenhuma atualização. Cada dia de silêncio é uma janela de desengajamento.

4. **Ausência de timeout é o risco operacional mais imediato.** Um único mentor que não responde tranca um agendamento indefinidamente. No modelo atual isso fica visível só quando o AEE percebe. No modelo automatizado, sem timeout, a conversa some silenciosamente.

5. **A inconsistência entre AEEs não é um problema de pessoas — é um problema de ausência de processo.** O SOP tem 3 linhas para esta etapa. A variação é estrutural. O agente não apenas automatiza: ele padroniza pela primeira vez.

---

## Open Questions

Estas questões não podem ser respondidas com os dados disponíveis nesta etapa. Alimentam os stages seguintes:

| Questão | Stage que responde |
|---|---|
| Qual é o JTBD real do AEE nesta etapa — o que ele quer "contratar" o agente para fazer? | Stage 3 — JTBD |
| Qual é o JTBD do mentor ao ser contatado para agendar? O que torna essa experiência boa ou ruim para ele? | Stage 3 — JTBD |
| Quais hipóteses sobre o comportamento do mentor e do founder são mais arriscadas? | Stage 4 — Assumption Map |
| Com que frequência cada edge case (ambiguidade, timeout, assistente) realmente ocorre? | Stage 5 — Edge Cases |
| Quando o agente falha, quem deve ser notificado, por qual canal, e em quanto tempo? | Stage 6 — Flow Map |
| Qual é o tempo aceitável de resposta para o mentor antes de um follow-up? | Stage 6 + decisão de produto |
