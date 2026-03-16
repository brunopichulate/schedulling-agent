# Edge Cases

> Living document — update as cases are discovered, analyzed, and resolved.
> Status legend: 🔴 Crítico · 🟠 Alto · 🟡 Médio · 🟢 Baixo
> Agente resolve: ✅ sim (com prompt adequado) · ❌ precisa de transbordo humano

---

## Behavioral — Mentor Side

| # | Caso | Risco | Agente resolve? | Solução / Status |
|---|---|---|---|---|
| EC-01 | Assistente executiva responde no lugar do mentor | 🟡 Médio | ✅ | MVP: aceitar e processar normalmente. Solução real: pré-trigger (ver `docs/architecture.md` → Delegação de Contato) |
| EC-03 | Mentor não responde (timeout 48h) | 🔴 Crítico | ✅ | Follow-up 1x → HI. Mecanismo de timeout ainda não implementado — conversa trava indefinidamente |
| EC-05 | Resposta ambígua ("qualquer manhã", "semana que vem") | 🟠 Alto | ✅ | Agente pede clarificação (limite 2x por round) → HI se persistir |
| EC-06 | Mentor envia áudio, imagem, sticker | 🟠 Alto | ✅ | Pede texto. Bug ativo: estado não avança após fallback — conversa trava |
| EC-07 | Número do mentor desatualizado no Connect | 🟢 Baixo | ❌ | Limitação conhecida. Mensagem entregue à pessoa errada, sem detecção possível |
| EC-10 | Mentor recusa interagir com o agente | 🟠 Alto | ❌ | HI imediato |
| EC-14 | Mentor envia slots em mensagens separadas ("terça 14h" ... "ou quinta 10h") | 🔴 Crítico | ❌ | Hoje só processa a última mensagem. Precisa de agregação ou sinal de encerramento ("pode ser isso") |
| EC-15 | Slots no passado ("semana passada às 14h") | 🟠 Alto | ✅ | Agente detecta e pede datas futuras |
| EC-16 | Horário sem data ("às 14h ou às 16h") | 🟠 Alto | ✅ | Agente pede que especifique o dia |
| EC-17 | Slot condicional ("só se for videochamada") | 🟡 Médio | ✅ | Extrai horário + anota condição no contexto para AEE |
| EC-18 | Mentor e founder já combinaram diretamente | 🔴 Crítico | ❌ | HI imediato — não verificável pelo agente. AEE confirma e cria GCal manualmente |
| EC-19 | Mentor faz pergunta fora de escopo antes de dar slots | 🟡 Médio | ✅ | Agente redireciona ("sou assistente de agendamento, pode me enviar 2 horários?"). Limite 2x → HI |
| EC-20 | Mentor muda de disponibilidade enquanto founder ainda está escolhendo | 🟠 Alto | ❌ | Estado não suporta hoje. Precisa de ciclo de renegociação (ver Motor de Negociação) |
| EC-21 | Resposta emocional ou agressiva | 🟠 Alto | ❌ | HI imediato. Agente não tenta resolver conflito |
| EC-22 | Mentor responde DEPOIS de já estar em HI (resposta tardia) | 🟡 Médio | ❌ | Agente avisa que fluxo foi encerrado. AEE decide se reabre |
| EC-39 | Mentor cancela ANTES da confirmação | 🟠 Alto | ❌ | Notifica founder + AEE → inicia remarcação ou encerra. Ver Motor de Negociação |
| EC-41 | Mentor cancela APÓS confirmação (reunião já agendada) | 🔴 Crítico | ❌ | Notifica founder + AEE imediatamente. Novo ciclo de negociação. GCal deve ser cancelado |

---

## Behavioral — Founder Side

| # | Caso | Risco | Agente resolve? | Solução / Status |
|---|---|---|---|---|
| EC-02 | Founder tem múltiplos sócios | 🟢 Baixo | ❌ | Contato principal definido pelo Connect. Sem lógica multi-destinatário |
| EC-04 | Founder rejeita todos os slots sem oferecer alternativa | 🟠 Alto | ❌ | MVP: HI. Phase 2: agente volta ao mentor pedindo novos slots |
| EC-09 | Janela de 24h expirou antes de contatar o founder | 🟠 Alto | ✅ | Envia template `hello_world` antes da mensagem principal |
| EC-10 | Founder recusa interagir com o agente | 🟠 Alto | ❌ | HI imediato |
| EC-11 | Founder suspeita de phishing (número desconhecido) | 🔴 Crítico | ❌ | Prevenção pré-fluxo: AEE deve avisar founder via canal existente antes de o agente entrar em contato |
| EC-23 | Founder responde "sim" ou "ok" sem especificar opção | 🔴 Crítico | ✅ | Extremamente comum no WhatsApp. Agente pede qual número da lista |
| EC-24 | Founder rejeita todos os slots E oferece contra-disponibilidade | 🔴 Crítico | ✅ | Motor de Negociação: agente extrai disponibilidade do founder e retorna ao mentor com contra-proposta |
| EC-25 | Founder delega ao assistente mid-flow ("confirma com minha secretária, número X") | 🟠 Alto | ❌ | HI + AEE reconfigura contato. Solução real: pré-trigger (ver Delegação de Contato) |
| EC-26 | Founder confirma com modificação ("opção 2 mas 30 min antes") | 🟡 Médio | ❌ | HI para AEE mediar. Agente não renegocia horário |
| EC-27 | Founder escolhe por descrição em vez de número ("a de quinta") | 🟡 Médio | ✅ | ConfirmationExtractorAgent com bom prompt mapeia descrição → índice |
| EC-28 | Founder envia só disponibilidade em vez de escolher da lista | 🟡 Médio | ✅ | Motor de Negociação: extrai disponibilidade e leva ao mentor |
| EC-29 | Resposta emocional ou agressiva | 🟠 Alto | ❌ | HI imediato |
| EC-30 | Founder responde DEPOIS de já estar em HI | 🟡 Médio | ❌ | Agente avisa que fluxo foi encerrado. AEE decide se reabre |
| EC-40 | Founder cancela ANTES da confirmação | 🟠 Alto | ❌ | Notifica mentor + AEE → inicia remarcação ou encerra |
| EC-42 | Founder cancela APÓS confirmação | 🔴 Crítico | ❌ | Notifica mentor + AEE imediatamente. Novo ciclo de negociação. GCal deve ser cancelado |

---

## Behavioral — Pós-Confirmação

| # | Caso | Risco | Agente resolve? | Solução / Status |
|---|---|---|---|---|
| EC-43 | Mentor pede remarcação ("preciso mudar o horário") | 🔴 Crítico | ❌ | HI + novo ciclo de negociação. GCal invite deve ser atualizado ou cancelado e recriado |
| EC-44 | Founder pede remarcação | 🔴 Crítico | ❌ | Mesmo tratamento que EC-43 |
| EC-45 | Múltiplos ciclos sem convergência (N rounds sem slot em comum) | 🟠 Alto | ❌ | Após `MAX_NEGOTIATION_ROUNDS` (configurável), HI com resumo completo das disponibilidades de ambos |

---

## Technical / Infrastructure

| # | Caso | Risco | Agente resolve? | Solução / Status |
|---|---|---|---|---|
| EC-12 | Trigger duplicado (mesmo `meeting_id` disparado 2x) | 🟠 Alto | ✅ | Deduplicação na trigger endpoint — rejeita se workflow já ativo para aquele meeting |
| EC-13 | Redis TTL expira silenciosamente após 24h de conversa ativa | 🔴 Crítico | ❌ | Estado reseta para INIT sem aviso ao ator nem ao AEE. Precisaria de TTL refresh em cada mensagem + alerta de expiração |
| EC-31 | Webhook entregue 2x pelo Meta (retry automático) | 🟠 Alto | ❌ | Sem idempotência por `message_id`. Mesma mensagem processada 2x, podendo duplicar transições de estado |
| EC-32 | Tarefa Celery perdida (broker down ou crash mid-task) | 🔴 Crítico | ❌ | `ignore_result=True` sem retry strategy. Mensagem do usuário sumida silenciosamente. Precisa de DLQ |
| EC-33 | OpenAI indisponível ou rate limit durante extração de agente | 🟠 Alto | ❌ | Agente falha sem fallback ou retry. Conversa trava no estado atual indefinidamente |
| EC-34 | Mensagem WhatsApp falha APÓS update de estado | 🟠 Alto | ❌ | Stale state: estado avançou mas usuário nunca recebeu a mensagem. Sem atomicidade entre send e state write |
| EC-35 | Google Calendar não implementado (confirmação enviada sem criar evento) | 🔴 Crítico | ❌ | Gap de implementação ativo no MVP. Confirmação é enviada a mentor e founder mas GCal invite não é criado |

---

## Process

| # | Caso | Risco | Agente resolve? | Solução / Status |
|---|---|---|---|---|
| EC-08 | AEE não atualiza status no Connect após agendar | 🟡 Médio | ❌ | Pipeline fica desatualizado. Notificação de sucesso ao AEE deve incluir lembrete de atualizar Connect |
| EC-36 | Nenhuma notificação chega ao AEE quando conversa vai para HI | 🔴 Crítico | ❌ | Casos acumulam silenciosamente. AEE só descobre por reclamação. Ver `docs/architecture.md` → EscalationService |
| EC-37 | Reunião cancelada no Connect enquanto fluxo está ativo | 🟡 Médio | ❌ | Agente continua negociando uma reunião que já não existe. Precisa de webhook ou polling de status do Connect |
| EC-38 | Email do mentor ausente no Connect — GCal invite não pode ser criado | 🟡 Médio | ❌ | Descoberto tarde (após toda a negociação). Validar no trigger antes de iniciar o fluxo |

---

## Framework: Agente Resolve vs Transbordo Humano

**Regra geral:** agente resolve quando a solução é textual e determinística (pedir mais info, reformular, redirecionar). Precisa de HI quando envolve verificação de realidade, mudança de configuração do fluxo ou julgamento humano.

| Agente resolve ✅ | Precisa de transbordo ❌ |
|---|---|
| Resposta ambígua → pede clarificação (máx 2x por round) | Já combinaram diretamente (não verificável) |
| Áudio/mídia → pede texto | Confirmação com modificação de horário |
| Slots no passado → pede datas futuras | Delegação de contato mid-flow |
| Horário sem data → pede dia específico | Resposta emocional ou agressiva |
| Pergunta fora de escopo → redireciona (máx 2x) | Resposta tardia após HI (AEE decide se reabre) |
| "Sim/ok" sem opção → pede número | Slots enviados em múltiplas mensagens separadas |
| Escolha por descrição → mapeia para índice | N rounds sem convergência (limite atingido) |
| Founder com contra-disponibilidade → leva ao mentor | Cancelamento ou remarcação pós-confirmação |
| Slot condicional → extrai horário + anota condição | Mentor atualiza slots com founder já aguardando |

**Limite de retentativas:** máximo 2 pedidos de clarificação por sessão no mesmo ponto. Após isso, HI.
**Limite de rounds de negociação:** configurável via `MAX_NEGOTIATION_ROUNDS` (recomendado: 2). Após isso, HI com histórico completo.

---

## Handling Today

Todos os edge cases atualmente roteiam para o estado `HUMAN_INTERVITION_REQUIRED`. Não existe:
- Notificação ao time AEE
- UI para gerenciar conversas em intervenção
- Lógica de retry ou escalonamento
- Motor de negociação com múltiplos ciclos

Essa é a próxima área de investimento após validação do MVP.

---

## Architectural Implication

Cada edge case resolvido provavelmente requer:
1. Novo estado na state machine (ou campo de contexto para rastrear round/fase)
2. Novo agente ou branch de agente (ex: ambiguity resolver, cancellation detector, counter-proposal extractor)
3. `EscalationService` para notificar o AEE no canal correto
4. Motor de negociação com ciclos para suportar vai-e-vem

Ver `docs/architecture.md` para:
- Motor de Negociação (Vai-e-Vem)
- Delegação de Contato no Trigger
- EscalationService e canais de notificação

---

## Resolved Edge Cases

*(nenhum ainda — mover casos aqui quando resolvidos com notas de implementação)*
