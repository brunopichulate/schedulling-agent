# Stage 3 — JTBD Map

> Versão: 1.0 | Data: 2026-03-13 | Agente líder: Researcher + PM
> Framework: Jobs-to-be-Done (Christensen / Moesta) + Switch Diagram (Four Forces)

---

## Overview

Este artefato responde: **o que cada ator realmente está tentando fazer quando entra neste fluxo?** Não o que eles fazem, mas qual "trabalho" estão contratando a solução para realizar. Isso informa o design do agente — o que ele deve fazer, o que nunca deve fazer, e quais forças vão impedir ou acelerar a adoção.

---

## JTBD por Ator

### AEE — Apoio a Empreendedores Endeavor

| Dimensão | Job |
|---|---|
| **Functional** | Fazer a mentoria acontecer: transformar um convite aceito em um evento no calendário, sem errar data, sem perder o contato, sem esquecer nenhuma das partes |
| **Emotional** | Sentir que está fazendo algo que importa — e não desperdiçar horas em logística que qualquer sistema poderia resolver |
| **Social** | Ser visto como o profissional que conecta empreendedores a mentores de forma eficiente — não como o gargalo do processo |

**Core Job Statement:**
> "Quando tenho uma mentoria para agendar, quero confirmar data e hora com mentor e founder o mais rápido possível, para poder me dedicar às atividades de apoio que exigem meu julgamento."

**O que o job revela:**
- O AEE não quer um assistente que *ajude* a fazer o agendamento — quer ser **completamente removido** da logística
- O sucesso não é "mensagem enviada" — é "evento no calendário criado"
- O AEE tem medo de ser o ponto de falha: se a mentoria não acontece, parte da responsabilidade é percebida como sua

---

### Mentor

| Dimensão | Job |
|---|---|
| **Functional** | Confirmar os detalhes práticos de uma mentoria que já aceitou fazer, com o mínimo de fricção e contexto possível |
| **Emotional** | Sentir que seu tempo está sendo respeitado — que o processo é rápido, claro e não vai exigir mais de uma interação para resolver |
| **Social** | Ser percebido como um mentor disponível e comprometido, sem parecer difícil de agendar |

**Core Job Statement:**
> "Quando recebo um contato para agendar uma mentoria, quero entender o que preciso fazer e confirmar os horários em uma única interação, para não precisar me lembrar de voltar depois."

**O que o job revela:**
- O mentor não é o usuário primário — é um participante que precisa ser *tratado como convidado*, não como usuário que adota uma ferramenta
- A experiência atual é fragmentada (e-mail formal → WhatsApp informal) e cria atrito desnecessário na primeira interação
- O maior risco não é rejeição — é indiferença: o mentor não responde simplesmente porque o contexto não ficou claro

---

### Founder

| Dimensão | Job |
|---|---|
| **Functional** | Saber que a mentoria está confirmada — com data, hora e mentor — para poder se preparar |
| **Emotional** | Sentir que o processo avança, que sua aprovação do mentor foi ouvida e que alguém está cuidando da logística |
| **Social** | Chegar à mentoria preparado e pontual — ser percebido pelo mentor como um founder organizado e respeitoso do tempo alheio |

**Core Job Statement:**
> "Quando aprovo um mentor, quero receber a confirmação da data e hora o mais rápido possível, para me preparar adequadamente para a reunião."

**O que o job revela:**
- O founder está "contratando" o agente para dar **visibilidade e certeza** — não só para confirmar horário
- Cada dia sem confirmação gera dúvida: "A mentoria vai acontecer mesmo?"
- A latência atual (dias entre aprovação e invite) é um job não realizado — e isso corrói o engajamento

---

## Switch Diagram — AEE adotando o agente

O Switch Diagram mapeia as forças que influenciam se o AEE vai ou não adotar e confiar no agente.

### Push (dor que empurra para longe da situação atual)
- Agendamento manual ocupa tempo que deveria ser dedicado a atividades de alto valor
- Sem processo padrão, cada AEE resolve diferente → inconsistência de experiência
- Com o crescimento do pipeline (Low/Tech-Touch 2026.1), o gargalo vai piorar
- Risco de erro humano: horário errado, e-mail errado, esquecimento de atualizar o Connect

### Pull (atração em direção ao agente)
- Mentoria se agenda automaticamente — AEE só monitora exceções
- Processo padronizado para todos os AEEs
- Rastreabilidade: log de cada mensagem enviada e recebida
- Founder recebe confirmação mais rápido → melhor experiência percebida pelo AEE

### Anxiety (medo que retarda a adoção)
- "E se o agente enviar uma mensagem errada para o mentor?"
- "E se o mentor ficar confuso e a mentoria não acontecer por culpa do agente?"
- "Como vou saber se algo deu errado? Vou perder visibilidade?"
- "Se o agente falhar, vai parecer que eu falhei"
- "E os casos fora do padrão — o agente vai saber lidar?"
- "E se o mentor ou founder simplesmente não quiser interagir com um robô?" ← **risco de adoção crítico** (ver Edge Case #10)

### Habit (inércia da situação atual)
- AEEs já têm WhatsApp no celular e sabem resolver manualmente
- Processo funciona (devagar, mas funciona) — não há urgência pessoal para mudar
- O SOP nunca exigiu automação aqui — não há pressão institucional direta sobre o AEE
- Relação pessoal com mentores já estabelecida — "melhor eu mesmo entrar em contato"

---

## Switch Diagram — Mentor respondendo ao agente

O mentor não "adota" o agente — ele apenas precisa responder uma mensagem. Mas as forças ainda existem.

### Push
- Processo atual é confuso (e-mail formal + WhatsApp sem contexto = dois contatos desconexos)
- Nenhum processo estruturado → difícil saber o que exatamente está sendo pedido

### Pull
- Mensagem clara, direta, com contexto da mentoria já incluído
- Uma única interação resolve — não precisa de troca de mensagens
- Familiar: é uma conversa no WhatsApp, não um formulário ou sistema novo

### Anxiety
- "Quem está me mandando isso? É automático ou tem uma pessoa?"
- "Posso confiar que minha resposta vai ser interpretada corretamente?"
- "E se eu mandar a hora errada — tem como corrigir?"
- "Não quero falar com robô — prefiro lidar com uma pessoa real" ← **chatbot aversion** (ver Edge Case #10)
- "É seguro? Pode ser phishing?" ← ceticismo de segurança, especialmente em mentores seniores

### Habit
- Mentores acostumados com contato humano (o AEE) — agente impessoal pode gerar estranhamento inicial
- Alguns mentores preferem e-mail; WhatsApp pode ser visto como invasivo
- Mentores com perfil executivo tendem a delegar WhatsApp para assistentes (ver Edge Case #1)

---

## Implicações de Design

Com base nos JTBDs e Switch Diagrams, o agente deve:

| Implicação | Razão |
|---|---|
| **Incluir contexto da mentoria na primeira mensagem** | Mentor precisa reconectar ao e-mail formal sem precisar procurá-lo |
| **Concluir o fluxo em no máximo 2 interações por ator** | Core job do mentor: resolver em uma interação única |
| **Notificar o AEE quando algo sair do happy path** | Maior anxiety do AEE: perder visibilidade. Sem notificação, não adota |
| **Confirmar para o founder assim que o slot for escolhido** | Job do founder é certeza — cada hora sem confirmação corrói o engajamento |
| **Nunca deixar o agente "sumir" silenciosamente** | Anxiety de todos os atores: não saber se algo foi processado |
| **Linguagem simples e direta no WhatsApp** | Job do mentor: entender o que fazer sem esforço cognitivo |
| **Não impersonar uma pessoa** | Anxiety do mentor: "quem está me mandando isso?" — transparência sobre ser automático reduz fricção |

O agente **nunca deve:**
- Enviar mensagem sem identificar o contexto da mentoria (empresa, mentor, tipo de sessão)
- Deixar uma conversa sem resposta (qualquer falha deve gerar uma mensagem de fallback)
- Bloquear o AEE de intervir manualmente a qualquer momento

---

## Open Questions

| Questão | Stage que responde |
|---|---|
| Qual hipótese sobre comportamento do mentor é mais arriscada — que vai responder, ou que vai entender a mensagem? | Stage 4 — Assumption Map |
| O anxiety do AEE ("vou perder visibilidade") é suficientemente forte para bloquear adoção sem um painel de monitoramento? | Stage 4 — Assumption Map |
| A habit force do AEE ("relação pessoal com mentores") vai enfraquecer com o tempo ou requer intervenção ativa? | Stage 4 — Assumption Map |
| O founder quer ser notificado do progresso intermediário (ex: "aguardando resposta do mentor"), ou apenas da confirmação final? | Stage 6 — Flow Map |
| Como comunicar ao mentor que a mensagem é automatizada sem gerar percepção negativa ("robô")? | Stage 8 — PRD / copy |
| Qual % de mentores/founders tem chatbot aversion forte o suficiente para não interagir? É frequente o suficiente para invalidar o modelo? | Stage 4 — Assumption Map (hipótese de adoção de alto risco) |
| Deve o agente se identificar explicitamente como automático, ou isso piora a taxa de resposta? | Stage 4 — Assumption Map + Stage 8 copy |
