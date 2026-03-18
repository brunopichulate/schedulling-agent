# MIGRATION_INVENTORY.md

> Gerado em: 2026-03-18
> Propósito: guia de migração cirúrgica deste repo pessoal (`schedulling-agent`)
> para a branch `playground` do repo oficial da Endeavor.
> Audiência: Bruno Pichulate (PM). Não requer conhecimento de código para executar.

---

## 🔴 ALERTA DE SEGURANÇA — LEIA ANTES DE QUALQUER COISA

**O arquivo `.env` na raiz deste repositório contém credenciais reais e ativas da Endeavor.**

| Credencial | Risco |
|---|---|
| `OPENAI__API_KEY` | Qualquer pessoa com essa chave pode gastar créditos da conta OpenAI |
| `META__ACCESS_TOKEN` | Permite enviar mensagens via o WhatsApp da Endeavor para qualquer número |
| `META__APP_SECRET` | Chave mestra do app Meta — risco crítico se vazar |
| `LANGFUSE__SECRET_KEY` | Acesso total ao projeto de observabilidade |
| `MONGODB__URL` | Acesso ao banco de dados de conversas (usuário: `kevin_silva` — verifique com Paulo se é uma conta compartilhada ou pessoal dele) |

**O arquivo está corretamente fora do Git** (listado no `.gitignore`) — não há risco de exposição pública por agora. Mas:

1. **NUNCA copie o `.env` para o repo destino** — nem para teste, nem "temporariamente"
2. **O repo destino (`Endeavor-Brasil/ai`) tem seu próprio `.env`** — use apenas ele
3. **Se o `kevin_silva` for credencial pessoal do Paulo**, considere pedir para ele rotacionar após a migração

---

## Resumo Executivo

### O que você construiu aqui

Este repositório começou como clone do MVP do Paulo e evoluiu para algo mais rico: um **laboratório de produto**. O código em si está parcialmente quebrado (alterações não controladas em infraestrutura), mas o **conhecimento de produto acumulado é de alta qualidade** e vale migrar.

### Estado do repositório

| Área | Estado | O que fazer |
|---|---|---|
| **Documentação (`docs/`)** | ✅ Excelente — 10+ artefatos de descoberta, PRD completo, specs | Migrar tudo sem revisão |
| **Ferramentas PM (`.claude/`)** | ✅ Excelente — hooks, 5 skills, metodologia | Migrar (com ajuste em 1 arquivo) |
| **Código novo (`src/`)** | 🟡 Parcialmente implementado — motor de negociação funcional mas não revisado | Migrar com revisão do Paulo |
| **Infraestrutura (`pyproject`, `docker-compose`, etc.)** | 🔴 Não tocar — pode contaminar o repo destino | Não migrar |

### Contagem por categoria

| Categoria | Arquivos | Ação |
|---|---|---|
| 🟢 Migrar sem revisão | 20 arquivos | Copiar diretamente |
| 🟡 Migrar com revisão | 8 arquivos | Mostrar para Paulo antes de integrar ao `develop` |
| 🔴 Não migrar | 10 arquivos | Ignorar completamente |
| ⚪ Ignorar | Diretórios gerados | Não existe ação |

---

## Lista Classificada Completa

### 🟢 MIGRAR SEM REVISÃO
*Arquivos de conhecimento puro — não contêm código que pode quebrar o repo destino.*

| Arquivo | Por que migrar |
|---|---|
| `docs/discovery/README.md` | Índice completo dos 8 estágios de discovery com status — referência central |
| `docs/discovery/01-problem-framing.md` | Framing do problema, personas, evidências, anti-goals — fundação de tudo |
| `docs/discovery/02-current-journey.md` | Jornada atual do AEE com 7 passos, canais, pontos de fricção |
| `docs/discovery/03-jtbd.md` | Jobs-to-be-Done dos 3 atores + Switch Diagram — explica o porquê do produto |
| `docs/discovery/04-assumption-map.md` | 17 hipóteses mapeadas por risco — guia de priorização do piloto |
| `docs/discovery/05-edge-cases-deep.md` | 45 edge cases com taxonomia, frequência e implicações arquiteturais |
| `docs/discovery/06-flow-map.md` | Blueprint de agentes, estados e fluxos alternativos — ponte discovery → código |
| `docs/discovery/07-metrics.md` | Modelo de métricas, North Star, leading/lagging indicators, guardrails |
| `docs/discovery/flow-diagram.md` | Diagramas Mermaid: happy path, edge cases, orquestração de agentes |
| `docs/discovery/agent-journey.md` | Swimlane por ator (mentor, founder, AEE) com ramificações de edge cases |
| `docs/discovery/08-prd.md` | PRD completo: 10 features, critérios de aceite testáveis, decisões abertas |
| `docs/specs.md` | Specs técnicas de implementação para Paulo/Brunão — lista features em ordem, arquivos a tocar, como testar |
| `docs/architecture.md` | Referência técnica: data flow, state machine, componentes, Motor de Negociação |
| `docs/business-rules.md` | Regras de negócio formais: trigger, extração de slots, seleção, GCal |
| `docs/edge-cases.md` | Matriz viva de edge cases com classificação de risco e status de implementação |
| `simular_fluxo.py` | Simulador standalone de 45 cenários de conversa — roda sem WhatsApp ou APIs |
| `.claude/settings.json` | Hooks: injeta contexto git em todo prompt + lembra de /evaluate e /update-docs ao editar arquivos críticos |
| `.claude/commands/discovery-status.md` | Skill `/discovery-status`: relatório de status PM com hipóteses, artefatos e próximas prioridades |
| `.claude/commands/evaluate.md` | Skill `/evaluate`: checklist de coerência em 5 fases (código, bugs, segurança, alinhamento de produto) |
| `.claude/commands/new-edge-case.md` | Skill `/new-edge-case`: adiciona novo edge case documentado à matriz |
| `.claude/commands/resolve-edge-case.md` | Skill `/resolve-edge-case`: marca edge case como implementado e move para seção Resolved |
| `.claude/commands/update-docs.md` | Skill `/update-docs`: sincroniza docs com mudanças de código após cada feature |

### 🟡 MIGRAR COM REVISÃO
*Arquivos com valor mas que precisam de inspeção ou ajuste antes de migrar.*

| Arquivo | O que revisar antes de migrar |
|---|---|
| `CLAUDE.md` | **Remover a linha do Git Remote** na seção Git: `Remote origin deve apontar para https://github.com/brunopichulate/schedulling-agent` — essa linha é do seu repo pessoal, não do destino. O restante é excelente e deve migrar inteiro. |
| `src/agents/main/counter_availability_extractor_agent.py` | Agente novo que detecta contra-propostas de disponibilidade. Funcionalmente completo. Paulo deve revisar se o prompt fallback hardcoded é aceitável ou se prefere criar um prompt no Langfuse antes de integrar. |
| `src/workflows/meeting_shared/handlers.py` | Contém o Motor de Negociação (counter-proposal, rodadas de negociação, contagem de clarificações). Lógica funcional mas adicionada em iteração rápida com alguns números mágicos. Paulo deve revisar a integração antes de ir para `develop`. |
| `src/workflows/meeting_shared/messages.py` | Dois novos builders de mensagem: `build_max_clarifications_message()` e `build_negotiation_counter_message()`. Baixo risco, mas Paulo deve confirmar se o texto está alinhado com o tom da Endeavor. |
| `src/services/state_machine_service.py` | Adicionado FakeRedis (fallback para dev sem Redis) e novos campos de estado para negociação. Paulo deve confirmar se o FakeRedis é desejado no destino ou se preferem deixar o Redis obrigatório. |
| `src/core/config.py` | Adicionado `no_response_timeout_seconds` (padrão: 48h). Mudança pequena e bem feita. Paulo deve confirmar o valor padrão. |
| `.claude/settings.local.json` | Contém caminho hardcoded `find /c/Users/bruno.pichulate_ende/ai/tests` — **precisa atualizar o caminho** para o diretório correto no ambiente destino antes de migrar. |

### 🔴 NÃO MIGRAR
*Estes arquivos podem contaminar o repo destino ou são específicos deste ambiente.*

| Arquivo | Por que não migrar |
|---|---|
| `.env` | **NUNCA** — contém credenciais reais da Endeavor (ver alerta no início) |
| `pyproject.toml` | O repo destino tem seu próprio — adicionar `fakeredis` aqui pode gerar conflito de dependências |
| `uv.lock` | O lockfile do destino é autoritativo — nunca sobrescrever |
| `docker-compose.yml` | Infraestrutura local — o destino tem a sua |
| `Dockerfile` | O destino tem o seu |
| `start.sh` | Script de entrypoint do destino — não sobrescrever |
| `.env.example` | O destino tem o seu template |
| `pytest.ini` | O destino tem sua própria configuração de testes |
| `.python-version` | O destino define sua própria versão de Python |
| `reset_state.py` | Utilitário de debug que você criou localmente; sem valor no destino |
| `main.py` | Entrypoint do servidor — o destino tem o seu |
| `chat.py` | Interface Gradio — o destino tem o seu |
| `tests/__init__.py` | Arquivo vazio, placeholder; o destino tem a estrutura de testes própria |

### ⚪ IGNORAR (não copiar nem mencionar)

| Item | Motivo |
|---|---|
| `.git/` | Histórico do seu repo pessoal — irrelevante no destino |
| `__pycache__/` | Arquivos gerados automaticamente pelo Python |
| `.venv/` | Ambiente virtual local — jamais copiar |
| `uv.lock` | Já listado em 🔴 |
| `.claude/` como diretório inteiro | Migrar **apenas os arquivos específicos** listados em 🟢 e 🟡, nunca copiar a pasta inteira (contém dados de sessão do Claude Code que não fazem sentido no destino) |

---

## Plano de Migração em Ordem

Execute do mais seguro para o que precisa de mais cuidado.

### Etapa 1 — Preparação (faça no repo destino)

```
1. Faça checkout da branch playground no repo destino:
   git checkout playground

2. Crie as pastas que vão receber os arquivos (se não existirem):
   mkdir -p docs/discovery
   mkdir -p .claude/commands
```

### Etapa 2 — Migrar documentação de produto (🟢 risco zero)

Copie cada arquivo abaixo do seu repo pessoal para o repo destino:

```
# Documentação de discovery (copiar pasta inteira)
cp -r docs/discovery/ [caminho-do-repo-destino]/docs/discovery/

# Docs principais
cp docs/architecture.md    [caminho-do-repo-destino]/docs/architecture.md
cp docs/business-rules.md  [caminho-do-repo-destino]/docs/business-rules.md
cp docs/edge-cases.md      [caminho-do-repo-destino]/docs/edge-cases.md
cp docs/specs.md           [caminho-do-repo-destino]/docs/specs.md
```

### Etapa 3 — Migrar ferramentas PM (🟢 risco zero)

```
# Simulador de conversas
cp simular_fluxo.py  [caminho-do-repo-destino]/simular_fluxo.py

# Hooks do Claude Code
cp .claude/settings.json  [caminho-do-repo-destino]/.claude/settings.json

# Skills
cp .claude/commands/discovery-status.md  [caminho-do-repo-destino]/.claude/commands/discovery-status.md
cp .claude/commands/evaluate.md          [caminho-do-repo-destino]/.claude/commands/evaluate.md
cp .claude/commands/new-edge-case.md     [caminho-do-repo-destino]/.claude/commands/new-edge-case.md
cp .claude/commands/resolve-edge-case.md [caminho-do-repo-destino]/.claude/commands/resolve-edge-case.md
cp .claude/commands/update-docs.md       [caminho-do-repo-destino]/.claude/commands/update-docs.md
```

### Etapa 4 — Migrar CLAUDE.md com edição (🟡 uma linha a remover)

1. Copie o arquivo: `cp CLAUDE.md [caminho-do-repo-destino]/CLAUDE.md`
2. Abra o arquivo no editor e **remova ou substitua esta seção**:

```
## Git

- Remote `origin` deve apontar para `https://github.com/brunopichulate/schedulling-agent`
- **Nunca** fazer push para `Endeavor-Brasil/ai`
```

Substitua por:
```
## Git

- Remote `origin` aponta para `https://github.com/Endeavor-Brasil/ai`
- Branch de trabalho do playground: `playground`
- PRs para `develop` passam por revisão do Brunão (ZRP)
```

### Etapa 5 — Migrar settings.local.json com edição (🟡 um path a corrigir)

1. Copie o arquivo: `cp .claude/settings.local.json [caminho-do-repo-destino]/.claude/settings.local.json`
2. Abra o arquivo e substitua o caminho hardcoded:

**Antes:**
```json
"Bash(find /c/Users/bruno.pichulate_ende/ai/tests -type f -name \"*.py\" 2>/dev/null | head -20)"
```

**Depois** (use o caminho correto do repo destino no seu computador):
```json
"Bash(find ./tests -type f -name \"*.py\" 2>/dev/null | head -20)"
```

### Etapa 6 — Migrar código novo com revisão (🟡 Paulo deve revisar)

Estes arquivos têm valor mas precisam de olhar do Paulo antes de ir para `develop`.
**No playground, copie normalmente. Deixe uma nota para Paulo revisar antes do merge.**

```
cp src/agents/main/counter_availability_extractor_agent.py \
   [caminho-do-repo-destino]/src/agents/main/counter_availability_extractor_agent.py

cp src/workflows/meeting_shared/handlers.py \
   [caminho-do-repo-destino]/src/workflows/meeting_shared/handlers.py

cp src/workflows/meeting_shared/messages.py \
   [caminho-do-repo-destino]/src/workflows/meeting_shared/messages.py

cp src/services/state_machine_service.py \
   [caminho-do-repo-destino]/src/services/state_machine_service.py

cp src/core/config.py \
   [caminho-do-repo-destino]/src/core/config.py
```

Após copiar, abra um draft de PR no GitHub com o título:
> `[playground → develop] Motor de negociação + counter-availability agent`

E na descrição, escreva: "Paulo, estes arquivos precisam de revisão antes de integrar ao develop. Ver MIGRATION_INVENTORY.md para contexto."

### Etapa 7 — Commit no playground

```
git add .
git commit -m "migrate product knowledge + negotiation engine from Bruno's personal repo"
git push origin playground
```

---

## O que Descartar Permanentemente

Estes arquivos não têm valor duradouro e podem ser deletados do seu repo pessoal sem perda:

| Arquivo | Por que descartar |
|---|---|
| `reset_state.py` | Script de 5 linhas para resetar Redis de teste local. Não tem valor de produto. |
| `tests/__init__.py` | Arquivo vazio. Se um dia houver testes reais, o repo destino criará este arquivo automaticamente. |
| `README.md` | Duplica quase todo o conteúdo do `CLAUDE.md`, que é mais completo e atualizado. Não acrescenta nada. |

---

## Alertas Finais

### ⚠️ Antes de executar a migração

1. **Confirme com Paulo** o usuário `kevin_silva` no MongoDB URL — verifique se é uma conta compartilhada ou pessoal dele que pode precisar ser rotacionada.

2. **Não teste código neste repo** após a migração — qualquer mudança deve acontecer no playground do repo destino de agora em diante.

3. **O `docs/specs.md`** é escrito para os devs (Brunão, Paulo, Pedro G.) — é o roteiro de implementação do MVP. É um dos arquivos mais importantes a migrar. Garanta que chegue ao playground antes de qualquer conversa técnica com eles.

4. **O motor de negociação nos handlers** (`MAX_CLARIFICATIONS = 2`, `MAX_NEGOTIATION_ROUNDS = 2`) foi implementado nesta sessão mas pode ter divergências em relação ao comportamento descrito no `docs/specs.md`. Paulo deve checar antes do merge.

5. **O `simular_fluxo.py`** só funciona com Python instalado. No playground, teste com `python simular_fluxo.py` para confirmar que roda sem erros antes de apresentar para alguém.

---

## HANDOVER PARA O PLAYGROUND

> **Copie e cole este bloco como primeira mensagem quando abrir o Claude Code no repo destino (branch `playground`).**

---

```
Contexto de onboarding para esta sessão:

Sou Bruno Pichulate, PM da Endeavor Brasil. Estou no repositório oficial da Endeavor
(Endeavor-Brasil/ai), branch `playground`. Acabei de migrar conhecimento de produto
acumulado no meu repo pessoal para cá.

O que foi migrado:
- docs/discovery/ — 10 artefatos de discovery completos (problem framing, JTBD,
  assumption map, edge cases, flow map, métricas, diagramas, agent journey, PRD)
- docs/specs.md — specs técnicas de implementação escritas para Paulo/Brunão/Pedro G.
- docs/architecture.md, docs/business-rules.md, docs/edge-cases.md — referências
  técnicas e de produto atualizadas
- simular_fluxo.py — simulador de 45 edge cases de conversa (sem dependências externas)
- .claude/settings.json + .claude/commands/ — hooks e skills de PM
  (/evaluate, /update-docs, /discovery-status, /new-edge-case, /resolve-edge-case)
- Código novo em src/ que precisa de revisão do Paulo antes de ir para develop:
  counter_availability_extractor_agent.py, handlers.py, messages.py,
  state_machine_service.py, config.py (Motor de Negociação implementado)

Estado ao chegar:
- Happy path funcional no repo destino
- Motor de Negociação (EC-24, EC-28) implementado mas não revisado pelo Paulo
- EscalationService (EC-36) ainda não implementado — AEE não recebe notificações de HI
- Google Calendar (EC-35) ainda não implementado
- Typo HUMAN_INTERVITION_REQUIRED ainda ativo (specs.md tem instrução para corrigir)
- Todos esses gaps estão documentados em docs/specs.md e docs/edge-cases.md

Primeiros passos recomendados no playground:
1. Leia docs/specs.md — é o roteiro de implementação do MVP para os devs
2. Rode `python simular_fluxo.py` para ver os edge cases simulados
3. Use /discovery-status para ter um panorama do estado atual do produto

Não sou desenvolvedor. Meu trabalho é produto: edge cases, regras de negócio,
fluxos conversacionais, alinhamento com o time da ZRP.

## Como quero trabalhar no playground: modo laboratório

### O problema que quero resolver
Quero conseguir testar o comportamento do agente — mensagens, decisões,
edge cases, fluxos alternativos — de forma rápida e local, sem precisar
que Redis, Celery, WhatsApp ou qualquer API externa esteja funcionando.

Quando chego numa hipótese que funciona bem, aí sim faço commit, push
para o playground e aviso o Bruno Batista para ele avaliar.

### O que já existe e posso usar hoje
- `uv run ./chat.py` — interface Gradio que simula conversas localmente
- `python simular_fluxo.py` — 45 cenários de edge case sem dependências

### O que quero construir com sua ajuda
Quero um **modo laboratório** dentro do playground. Na prática, isso significa:

**1. Um runner de cenários simples**
Um script (`lab/run_scenario.py`) onde eu consigo escrever um cenário
de conversa em texto simples e ver como o agente responderia a cada turno,
sem precisar abrir nenhuma interface. Algo como:

  turno 1 → eu digito uma mensagem simulando o mentor
  turno 2 → o agente responde
  turno 3 → eu digito a resposta do mentor
  ... e assim por diante

**2. Fixtures de cenários salvos**
Uma pasta `lab/scenarios/` com arquivos `.md` ou `.json` descrevendo
cada cenário que quero testar. Ex: `mentor-responde-um-horario.md`,
`mentor-de-ferias.md`, `assistente-cuida-da-agenda.md`. Assim eu
documento e reproduzo edge cases sem precisar redigitar tudo.

**3. Separação clara de camadas**
Quando eu quiser explorar uma hipótese nova, quero poder:
- Mudar o prompt de um agente em `src/agents/`
- Mudar uma regra de negócio em `src/workflows/`
- Testar via `chat.py` ou `lab/run_scenario.py`
- Ver o resultado
- Decidir se vale um commit

Sem precisar mexer em nada de infra.

### O que você deve fazer quando eu pedir para testar algo
1. Me pergunte: "isso é um teste de lógica ou precisa de integração?"
2. Se for lógica: sugira como testar via `chat.py` ou `lab/run_scenario.py` sem subir nada
3. Se precisar de integração real: documente como hipótese em docs/edge-cases.md e me ajude a escrever a spec para o Bruno Batista implementar. Nunca tente subir infra comigo.
4. Nunca assuma que tenho Redis, Celery ou WhatsApp disponível — sempre confirme antes
```

---

*Fim do inventário. Gerado com auditoria completa em 2026-03-18.*
