"""
simular_fluxo.py — sem WhatsApp, sem APIs, só lógica.

Simula cada edge case turno a turno, com o agente se comportando como
uma secretária sênior experiente: empática, persistente, resolve quase
tudo com linguagem natural e só escala para o AEE quando necessário.

Uso:
  python simular_fluxo.py           → lista todos os cenários
  python simular_fluxo.py 24        → roda EC-24 específico
  python simular_fluxo.py all       → roda todos em sequência
"""

import sys
import io

# Força UTF-8 no stdout do Windows (cmd/PowerShell usam cp1252 por padrão)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

MENTOR   = "Dr. Roberto"
FOUNDER  = "Ana Lima"
DELEGADA = "Fernanda"
AEE      = "AEE Endeavor"

# ── Critério de HI ──────────────────────────────────────────────────────────
# O agente escala para HI SOMENTE quando:
#   1. Situação factualmente não verificável (EC-18, EC-07)
#   2. Risco de segurança / confiança (EC-11)
#   3. Gap técnico fora do escopo da conversa (EC-35, EC-37, EC-38)
#   4. Negociação genuinamente exaurida após MAX_NEGOTIATION_ROUNDS (EC-45)
#   5. Falhas de infraestrutura sem fallback (EC-13, EC-31, EC-32, EC-34, EC-36)
# Todo o restante o agente resolve com linguagem natural.
# ────────────────────────────────────────────────────────────────────────────


def exibir(turnos: list[dict]) -> None:
    for t in turnos:
        remetente = t["de"].upper()
        msg = t["msg"].strip()
        print(f"\n[{remetente}]")
        for linha in msg.splitlines():
            print(f"  {linha}")


def cabecalho(codigo: str, titulo: str, risco: str, resolve: str) -> None:
    sep = "─" * 64
    print(f"\n{sep}")
    print(f"  {codigo} · {titulo}")
    print(f"  Risco: {risco}  |  Agente resolve: {resolve}")
    print(sep)


# ── Happy Path ───────────────────────────────────────────────────────────────

def happy_path():
    cabecalho("HAPPY PATH", "Fluxo ideal sem desvios", "—", "✅")
    exibir([
        {"de": "agente", "msg": (
            f"Olá, {MENTOR}! 👋\n\n"
            f"Tenho uma mentoria para agendar com {FOUNDER} em março/2026.\n\n"
            "Para que eu possa apresentar opções ao mentorado, preciso de pelo menos "
            "2 horários disponíveis da sua parte.\n\n"
            "Sugestões para facilitar:\n"
            "• Segunda às 14h\n"
            "• Quarta às 10h\n"
            "• Sexta às 16h\n\n"
            "Fique à vontade para indicar outros. Caso prefira não agendar, basta me dizer."
        )},
        {"de": MENTOR, "msg": "Terça às 15h ou quinta às 9h."},
        {"de": "agente", "msg": (
            f"Olá, {FOUNDER}! 👋\n\n"
            f"O mentor {MENTOR} sugeriu os seguintes horários para a mentoria:\n\n"
            "1. Terça-feira às 15h\n"
            "2. Quinta-feira às 9h\n\n"
            "Qual dessas opções funciona melhor para você? "
            "(Pode responder com o número ou o horário. Se nenhum servir, me avise que busco alternativas.)"
        )},
        {"de": FOUNDER, "msg": "2"},
        {"de": "agente → founder", "msg": (
            "✅ Ótimo! Reunião confirmada.\n\n"
            f"*{MENTOR}* e *{FOUNDER}* se encontrarão na *quinta-feira às 9h*.\n\n"
            "O convite de calendário será enviado em breve."
        )},
        {"de": "agente → mentor", "msg": (
            "✅ Tudo certo!\n\n"
            f"*{MENTOR}* e *{FOUNDER}* se encontrarão na *quinta-feira às 9h*.\n\n"
            "O convite de calendário será enviado em breve."
        )},
    ])


# ── Mentor Side ───────────────────────────────────────────────────────────────

def ec01_delegacao_contato():
    cabecalho("EC-01", "Mentor pede para falar com assistente executiva", "🟡 Médio", "✅ pede contato → migra conversa com contexto")
    exibir([
        {"de": "agente", "msg": (
            f"Olá, {MENTOR}! 👋\n\n"
            f"Tenho uma mentoria para agendar com {FOUNDER}. Preciso de pelo menos 2 horários disponíveis. "
            "Pode me indicar?"
        )},
        {"de": MENTOR, "msg": "Quem gerencia minha agenda é a Fernanda. Consegue marcar com ela?"},
        {"de": "agente", "msg": (
            "Sem problema! Para continuar o agendamento com a Fernanda e não perder nenhum contexto, "
            "você poderia me informar o número de WhatsApp dela?"
        )},
        {"de": MENTOR, "msg": "11 98888-0000"},
        {"de": "sistema", "msg": (
            "[DB atualizado: contato delegado]\n"
            "  meeting_id: 1234\n"
            "  original_contact: Dr. Roberto · +55 11 9xxxx-xxxx\n"
            "  delegated_to: Fernanda · +55 11 98888-0000\n"
            "  context_preserved: true\n"
            "  state: AWAITING_MENTOR_SLOTS (retomado com Fernanda)"
        )},
        {"de": f"agente → {DELEGADA}", "msg": (
            f"Olá, Fernanda! 👋\n\n"
            f"Estou em contato a pedido do {MENTOR} para agendar uma mentoria com {FOUNDER} em março/2026.\n\n"
            "Para apresentar opções ao mentorado, preciso de pelo menos 2 horários disponíveis na agenda do Dr. Roberto. "
            "Você consegue me indicar?"
        )},
        {"de": DELEGADA, "msg": "Pode ser terça às 10h ou quarta às 14h."},
        {"de": "agente", "msg": (
            f"Olá, {FOUNDER}! 👋\n\n"
            f"O mentor {MENTOR} sugeriu os seguintes horários:\n\n"
            "1. Terça às 10h\n"
            "2. Quarta às 14h\n\n"
            "Qual você prefere?"
        )},
        {"de": "nota", "msg": (
            "[Fluxo continua normalmente. Fernanda fica como contato ativo para este meeting.\n"
            " Histórico completo preservado no banco para rastreabilidade.]"
        )},
    ])


def ec03_timeout_mentor():
    cabecalho("EC-03", "Mentor não responde em 48h", "🔴 Crítico", "✅ follow-up 1x → HI se persistir")
    exibir([
        {"de": "agente", "msg": (
            f"Olá, {MENTOR}! 👋\n\n"
            f"Tenho uma mentoria para agendar com {FOUNDER}. Preciso de pelo menos 2 horários disponíveis. "
            "Pode me indicar quando tiver um momento?"
        )},
        {"de": "sistema", "msg": "[48h sem resposta → dispara follow-up automático]"},
        {"de": "agente (follow-up)", "msg": (
            f"Olá, {MENTOR}! Quero garantir que a mentoria com {FOUNDER} aconteça. "
            "Quando tiver um instante, me manda 2 horários que funcionem para você — "
            "eu cuido do resto. 🙏"
        )},
        {"de": "sistema", "msg": "[Mais 48h sem resposta → encaminha para HI]"},
        {"de": "agente → aee", "msg": (
            f"[Escalação — EC-03]\n"
            f"Meeting ID: 1234 · Mentor: {MENTOR}\n"
            "Motivo: sem resposta após 2 tentativas (96h total)\n"
            "Ação necessária: contato alternativo com o mentor ou cancelamento"
        )},
    ])


def ec05_resposta_ambigua():
    cabecalho("EC-05", "Resposta ambígua do mentor", "🟠 Alto", "✅ clarifica até 2x com linguagem natural → HI se persistir")
    exibir([
        {"de": "agente", "msg": f"Olá, {MENTOR}! 👋 Preciso de pelo menos 2 horários disponíveis para a mentoria com {FOUNDER}."},
        {"de": MENTOR, "msg": "Qualquer manhã da semana que vem."},
        {"de": "agente", "msg": (
            "Entendido! Para que eu possa apresentar ao mentorado, preciso de horários específicos. "
            "Por exemplo: *segunda às 9h e terça às 10h*. Consegue me confirmar dois horários exatos?"
        )},
        {"de": MENTOR, "msg": "Semana que vem de manhã, qualquer dia serve."},
        {"de": "agente", "msg": (
            f"Fico feliz com a flexibilidade! Vou sugerir *segunda às 9h* e *terça às 10h* como opções para {FOUNDER}. "
            "Posso confirmar esses dois?"
        )},
        {"de": MENTOR, "msg": "Sim, tudo bem."},
        {"de": "agente", "msg": (
            f"Olá, {FOUNDER}! 👋\n\n"
            f"O mentor {MENTOR} sugeriu:\n\n"
            "1. Segunda às 9h\n"
            "2. Terça às 10h\n\n"
            "Qual você prefere?"
        )},
        {"de": "nota", "msg": "[Agente não precisou ir a HI — usou linguagem natural para resolver a ambiguidade propondo horários concretos]"},
    ])


def ec06_midia():
    cabecalho("EC-06", "Mentor envia áudio / imagem / sticker", "🟠 Alto", "✅ pede texto — BUG ATIVO: estado pode travar após fallback")
    exibir([
        {"de": "agente", "msg": f"Olá, {MENTOR}! 👋 Preciso de pelo menos 2 horários disponíveis para a mentoria com {FOUNDER}."},
        {"de": MENTOR, "msg": "[🎵 Áudio de 18s]"},
        {"de": "agente", "msg": (
            "Recebi um áudio, mas no momento só consigo processar texto. "
            "Poderia me enviar os horários escrito? Algo como: *terça às 14h e quinta às 10h*."
        )},
        {"de": MENTOR, "msg": "[📷 Foto da agenda impressa]"},
        {"de": "agente", "msg": (
            "Entendo — às vezes é mais fácil tirar uma foto! Mas preciso dos horários em texto "
            "para conseguir repassar ao mentorado. Pode me digitar os dois melhores?"
        )},
        {"de": MENTOR, "msg": "Terça 14h ou quinta 10h."},
        {"de": "sistema (BUG)", "msg": (
            "[BUG ATIVO: estado pode não avançar corretamente após múltiplos fallbacks de mídia.\n"
            " Fluxo ideal acima. Na prática, pode travar aqui até correção do state machine.]"
        )},
    ])


def ec10_mentor_recusa():
    cabecalho("EC-10", "Mentor recusa interagir com o agente", "🟠 Alto", "✅ explica propósito com empatia → persiste 1x → HI se resistir")
    exibir([
        {"de": "agente", "msg": f"Olá, {MENTOR}! 👋 Tenho uma mentoria para agendar com {FOUNDER}. Preciso de 2 horários disponíveis."},
        {"de": MENTOR, "msg": "Não quero falar com bot. Me passa o contato da Endeavor."},
        {"de": "agente", "msg": (
            f"Entendo, {MENTOR}! Sou a assistente de agendamento da Endeavor — estou aqui justamente "
            f"para poupar seu tempo. Basta me enviar 2 horários e eu cuido de tudo com {FOUNDER}, "
            "incluindo o convite de calendário. Fica mais fácil assim. 😊"
        )},
        {"de": MENTOR, "msg": "Não, prefiro resolver com uma pessoa."},
        {"de": "agente → aee", "msg": (
            f"[Escalação — EC-10]\n"
            f"Meeting ID: 1234 · Mentor: {MENTOR}\n"
            "Motivo: mentor preferiu contato humano após explicação\n"
            "Ação necessária: AEE entra em contato diretamente"
        )},
        {"de": "agente → mentor", "msg": (
            f"Claro, {MENTOR}! Nossa equipe da Endeavor vai entrar em contato com você em breve. "
            "Obrigado pela paciência."
        )},
    ])


def ec14_slots_em_mensagens_separadas():
    cabecalho("EC-14", "Mentor envia slots em mensagens separadas", "🔴 Crítico", "❌ BUG: processa só a última — perde slots anteriores")
    exibir([
        {"de": "agente", "msg": f"Preciso de pelo menos 2 horários disponíveis para a mentoria com {FOUNDER}."},
        {"de": MENTOR, "msg": "Terça 14h"},
        {"de": "sistema (BUG)", "msg": "[Webhook recebido com 1 slot — insuficiente. Agente pede mais]"},
        {"de": "agente", "msg": "Recebido! Preciso de mais um horário como alternativa. Tem outro que funcione?"},
        {"de": MENTOR, "msg": "ou quinta 10h"},
        {"de": "sistema (BUG)", "msg": (
            "[Webhook recebido com 'ou quinta 10h' isolado.\n"
            " Agente perde 'terça 14h' da mensagem anterior — contexto não é agregado entre webhooks.\n"
            " Resultado: extrai só 1 slot novamente. Loop.]"
        )},
        {"de": "agente", "msg": "Desculpe, preciso de 2 horários na mesma mensagem para garantir que não perca nenhum. Consegue me enviar os dois juntos?"},
        {"de": MENTOR, "msg": "Terça às 14h ou quinta às 10h."},
        {"de": "agente", "msg": (
            f"Olá, {FOUNDER}! 👋\n\n"
            f"O mentor {MENTOR} sugeriu:\n\n"
            "1. Terça às 14h\n"
            "2. Quinta às 10h\n\n"
            "Qual você prefere?"
        )},
        {"de": "nota", "msg": "[Solução definitiva: agregação de mensagens por janela de tempo ou sinal de encerramento ('pode ser isso')]"},
    ])


def ec15_slots_no_passado():
    cabecalho("EC-15", "Slots no passado", "🟠 Alto", "✅ detecta e pede datas futuras com naturalidade")
    exibir([
        {"de": "agente", "msg": f"Preciso de pelo menos 2 horários disponíveis para a mentoria com {FOUNDER}."},
        {"de": MENTOR, "msg": "Semana passada às 14h ou na última terça."},
        {"de": "agente", "msg": (
            "Parece que esses horários já passaram! Sem problemas — preciso de datas a partir de hoje. "
            "Tem 2 janelas disponíveis nas próximas semanas?"
        )},
        {"de": MENTOR, "msg": "Próxima terça às 14h ou quarta às 10h."},
        {"de": "agente", "msg": (
            f"Olá, {FOUNDER}! 👋\n\n"
            f"O mentor {MENTOR} sugeriu:\n\n"
            "1. Próxima terça às 14h\n"
            "2. Quarta às 10h\n\n"
            "Qual você prefere?"
        )},
    ])


def ec16_horario_sem_data():
    cabecalho("EC-16", "Horário sem data ('às 14h ou às 16h')", "🟠 Alto", "✅ pede o dia com sugestão proativa")
    exibir([
        {"de": "agente", "msg": f"Preciso de pelo menos 2 horários disponíveis para a mentoria com {FOUNDER}."},
        {"de": MENTOR, "msg": "Às 14h ou às 16h."},
        {"de": "agente", "msg": (
            "Ótimos horários! Só preciso do dia também para fechar. "
            "Seria essa semana ou na próxima? Por exemplo: *terça às 14h e quinta às 16h*."
        )},
        {"de": MENTOR, "msg": "Terça às 14h ou quarta às 16h."},
        {"de": "agente", "msg": (
            f"Olá, {FOUNDER}! 👋\n\n"
            f"O mentor {MENTOR} sugeriu:\n\n"
            "1. Terça às 14h\n"
            "2. Quarta às 16h\n\n"
            "Qual você prefere?"
        )},
    ])


def ec17_slot_condicional():
    cabecalho("EC-17", "Slot condicional ('só se for videochamada')", "🟡 Médio", "✅ extrai horário + registra condição para AEE")
    exibir([
        {"de": "agente", "msg": f"Preciso de pelo menos 2 horários disponíveis para a mentoria com {FOUNDER}."},
        {"de": MENTOR, "msg": "Terça às 14h ou quinta às 10h, mas só se for por videochamada, não presencial."},
        {"de": "agente", "msg": (
            f"Entendido! Anotei a preferência por videochamada e vou repassar ao time da Endeavor.\n\n"
            f"Olá, {FOUNDER}! 👋\n\n"
            f"O mentor {MENTOR} sugeriu os seguintes horários:\n\n"
            "1. Terça às 14h\n"
            "2. Quinta às 10h\n\n"
            "Qual você prefere?"
        )},
        {"de": "sistema", "msg": (
            "[Contexto registrado para AEE: mentor solicitou formato videochamada.\n"
            " Confirmação final deve incluir link de videoconferência.]"
        )},
    ])


def ec18_ja_combinaram_direto():
    cabecalho("EC-18", "Mentor e founder já combinaram diretamente", "🔴 Crítico", "❌ HI — não verificável pelo agente")
    exibir([
        {"de": "agente", "msg": f"Preciso de pelo menos 2 horários disponíveis para a mentoria com {FOUNDER}."},
        {"de": MENTOR, "msg": "Já combinei com a Ana diretamente. Vai ser sexta às 15h."},
        {"de": "agente", "msg": (
            "Ótimo que já alinharam! Para garantir que o convite de calendário seja criado corretamente, "
            "vou repassar isso para nossa equipe confirmar com você. Um momento!"
        )},
        {"de": "agente → aee", "msg": (
            f"[Escalação — EC-18]\n"
            f"Meeting ID: 1234 · Mentor: {MENTOR} · Founder: {FOUNDER}\n"
            "Motivo: mentor afirma que já combinaram diretamente (sexta às 15h)\n"
            "Ação necessária: confirmar com founder e criar GCal manualmente"
        )},
    ])


def ec19_pergunta_fora_escopo():
    cabecalho("EC-19", "Mentor faz perguntas fora de escopo", "🟡 Médio", "✅ responde o que souber, redireciona naturalmente → HI se bloquear fluxo")
    exibir([
        {"de": "agente", "msg": f"Preciso de pelo menos 2 horários disponíveis para a mentoria com {FOUNDER}."},
        {"de": MENTOR, "msg": "Quem é o founder que vai participar? Qual empresa?"},
        {"de": "agente", "msg": (
            f"A mentoria é com {FOUNDER}! Infelizmente não tenho detalhes sobre a empresa no momento — "
            "mas se quiser, nossa equipe pode te enviar o briefing antes. "
            "Enquanto isso, consegue me informar 2 horários disponíveis para eu avançar com o agendamento?"
        )},
        {"de": MENTOR, "msg": "Qual é o tópico da mentoria?"},
        {"de": "agente", "msg": (
            "Não tenho essa informação aqui, mas posso pedir para o time enviar direto para você. "
            "Posso adiantar o agendamento em paralelo para não atrasar? Qualquer 2 horários que funcionem para você."
        )},
        {"de": MENTOR, "msg": "Ok, pode ser terça às 10h ou quarta às 14h."},
        {"de": "agente", "msg": (
            f"Olá, {FOUNDER}! 👋\n\n"
            f"O mentor {MENTOR} sugeriu:\n\n"
            "1. Terça às 10h\n"
            "2. Quarta às 14h\n\n"
            "Qual você prefere?"
        )},
    ])


def ec20_mentor_muda_disponibilidade():
    cabecalho("EC-20", "Mentor atualiza slots com founder já aguardando", "🟠 Alto", "❌ estado não suporta renegociação hoje — precisa de novo ciclo")
    exibir([
        {"de": "agente", "msg": f"Preciso de pelo menos 2 horários disponíveis para a mentoria com {FOUNDER}."},
        {"de": MENTOR, "msg": "Terça às 14h ou quinta às 10h."},
        {"de": "agente → founder", "msg": (
            f"Olá, {FOUNDER}! 👋\n\n"
            f"O mentor {MENTOR} sugeriu:\n\n"
            "1. Terça às 14h\n"
            "2. Quinta às 10h\n\n"
            "Qual você prefere?"
        )},
        {"de": "sistema", "msg": "[Estado: AWAITING_FOUNDER_SELECTION · founder ainda não respondeu]"},
        {"de": MENTOR, "msg": "Mudei de planos — não consigo mais na terça. Só quinta às 10h."},
        {"de": "agente (comportamento ideal — não implementado)", "msg": (
            "Entendido, Dr. Roberto! Só um momento que verifico o status com a Ana."
        )},
        {"de": "sistema (GAP)", "msg": (
            "[Agente recebeu mensagem do mentor fora do fluxo esperado.\n"
            " Estado atual: AWAITING_FOUNDER — sem suporte a renegociação lateral.\n"
            " Comportamento atual: processa como mensagem inesperada ou trava.\n"
            " Solução: Motor de Negociação com suporte a interrupção de qualquer parte.]"
        )},
    ])


def ec21_agressivo_mentor():
    cabecalho("EC-21", "Resposta emocional / agressiva — mentor", "🟠 Alto", "✅ de-escalada empática → HI somente se persistir")
    exibir([
        {"de": "agente", "msg": f"Preciso de pelo menos 2 horários disponíveis para a mentoria com {FOUNDER}."},
        {"de": MENTOR, "msg": "Isso é um absurdo! Já disse que não tenho tempo para essas reuniões!"},
        {"de": "agente", "msg": (
            f"Entendo totalmente, {MENTOR} — agenda cheia é uma pressão constante. "
            "Meu objetivo é exatamente poupar o seu tempo: com apenas 2 horários, eu cuido de todo o resto "
            "e você não precisa se envolver no vai e vem. Quando tiver 30 segundos, me manda duas janelas."
        )},
        {"de": MENTOR, "msg": "Não quero saber disso agora! Podem me ligar mais tarde!"},
        {"de": "agente", "msg": (
            f"Com certeza, {MENTOR}. Nossa equipe vai entrar em contato no melhor momento para você. "
            "Obrigado pela paciência!"
        )},
        {"de": "agente → aee", "msg": (
            f"[Escalação — EC-21]\n"
            f"Meeting ID: 1234 · Mentor: {MENTOR}\n"
            "Motivo: mentor demonstrou frustração persistente, preferiu contato por ligação\n"
            "Ação necessária: ligar para mentor para coletar disponibilidade"
        )},
    ])


def ec22_resposta_tardia_mentor():
    cabecalho("EC-22", "Mentor responde DEPOIS de estado HI", "🟡 Médio", "✅ avalia se ainda viável → propõe reabrir")
    exibir([
        {"de": "sistema", "msg": "[Estado atual: HUMAN_INTERVENTION_REQUIRED · HI aberto há 3 dias]"},
        {"de": MENTOR, "msg": "Desculpe a demora. Posso terça às 14h ou quinta às 10h."},
        {"de": "agente", "msg": (
            f"Que bom ouvir de você, {MENTOR}! 😊 Este caso foi encaminhado para nossa equipe há alguns dias, "
            "mas posso repassar sua disponibilidade imediatamente para eles verificarem se ainda é possível agendar. "
            "Eles entrarão em contato em breve."
        )},
        {"de": "agente → aee", "msg": (
            f"[EC-22 · Mentor respondeu após HI]\n"
            f"Mentor: {MENTOR} · Slots: terça 14h, quinta 10h\n"
            "Ação: verificar se founder ainda está disponível e retomar fluxo ou rejeitar"
        )},
    ])


def ec39_mentor_cancela_antes():
    cabecalho("EC-39", "Mentor cancela ANTES da confirmação", "🟠 Alto", "✅ agente inicia novo ciclo ou encerra conforme resposta")
    exibir([
        {"de": "agente → founder", "msg": (
            f"O mentor {MENTOR} sugeriu:\n1. Terça às 14h\n2. Quinta às 10h\n\nQual você prefere?"
        )},
        {"de": "sistema", "msg": "[Founder ainda não respondeu]"},
        {"de": MENTOR, "msg": "Preciso cancelar essa mentoria, minha agenda está impossível esse mês."},
        {"de": "agente → mentor", "msg": (
            f"Entendo, {MENTOR}. Vou notificar {FOUNDER} e nossa equipe agora. "
            "Se em algum momento a agenda abrir, é só me avisar que retomamos rapidinho."
        )},
        {"de": "agente → founder", "msg": (
            f"Olá, {FOUNDER}! Infelizmente o mentor precisou cancelar sua disponibilidade para este mês. "
            "Nossa equipe vai entrar em contato para buscar uma nova data. Obrigado pela compreensão! 🙏"
        )},
        {"de": "agente → aee", "msg": (
            f"[EC-39]\nMeeting ID: 1234 · Mentor: {MENTOR} cancelou antes da confirmação\n"
            "Ação: verificar reagendamento ou encerrar mentoria"
        )},
    ])


def ec41_mentor_cancela_apos():
    cabecalho("EC-41", "Mentor cancela APÓS confirmação (GCal criado)", "🔴 Crítico", "❌ notifica ambos + cancela GCal + novo ciclo")
    exibir([
        {"de": "sistema", "msg": "[Estado: CONFIRMED · quinta às 10h · GCal invite enviado]"},
        {"de": MENTOR, "msg": "Precisei de um imprevisto — não vou conseguir fazer a reunião de quinta."},
        {"de": "agente → mentor", "msg": (
            f"Entendo, {MENTOR}. Vou notificar {FOUNDER} agora e nossa equipe vai buscar uma nova data. "
            "Quando sua agenda estiver mais tranquila, é só me avisar!"
        )},
        {"de": "agente → founder", "msg": (
            f"Olá, {FOUNDER}! Infelizmente o mentor precisou cancelar a reunião de quinta às 10h. "
            "Nossa equipe vai entrar em contato para reagendar. Pedimos desculpas pelo inconveniente!"
        )},
        {"de": "sistema", "msg": (
            "[GCal invite a cancelar — ação manual até implementação automática]\n"
            "[Notificação enviada ao AEE para iniciar novo ciclo de negociação]"
        )},
    ])


# ── Founder Side ──────────────────────────────────────────────────────────────

def ec04_founder_rejeita_sem_alternativa():
    cabecalho("EC-04", "Founder rejeita todos os slots sem oferecer alternativa", "🟠 Alto", "✅ agente tenta extrair disponibilidade → volta ao mentor · HI se bloquear")
    exibir([
        {"de": "agente → founder", "msg": (
            f"Olá, {FOUNDER}! 👋\n\n"
            f"O mentor {MENTOR} sugeriu:\n1. Terça às 14h\n2. Quinta às 10h\n\nQual você prefere?"
        )},
        {"de": FOUNDER, "msg": "Não posso em nenhum desses horários."},
        {"de": "agente", "msg": (
            "Sem problema! Para eu conseguir uma opção que funcione para você, "
            "pode me dizer quais dias e horários têm disponibilidade? Assim busco com o mentor uma alternativa."
        )},
        {"de": FOUNDER, "msg": "Eu tenho segunda de manhã ou sexta à tarde."},
        {"de": "agente → mentor", "msg": (
            f"Olá, {MENTOR}! 👋\n\n"
            f"{FOUNDER} não pôde confirmar os horários sugeridos, mas tem disponibilidade "
            "em: segunda de manhã ou sexta à tarde.\n\n"
            "Você conseguiria encaixar algum desses? Se sim, me manda 2 opções de horário exato."
        )},
    ])


def ec09_janela_24h():
    cabecalho("EC-09", "Janela de 24h com founder expirou", "🟠 Alto", "✅ envia template Meta aprovado antes da mensagem principal")
    exibir([
        {"de": MENTOR, "msg": "Terça às 14h ou quinta às 10h."},
        {"de": "sistema", "msg": (
            "[Janela ativa de 24h com founder expirada.\n"
            " Regra Meta: é obrigatório enviar template aprovado antes de mensagem livre.]"
        )},
        {"de": "agente (template Meta — hello_world)", "msg": (
            "Olá! A Endeavor entrará em contato sobre o agendamento da sua mentoria."
        )},
        {"de": "agente (mensagem principal — após template abrir janela)", "msg": (
            f"Olá, {FOUNDER}! 👋\n\n"
            f"O mentor {MENTOR} sugeriu:\n\n"
            "1. Terça às 14h\n"
            "2. Quinta às 10h\n\n"
            "Qual você prefere?"
        )},
    ])


def ec10_founder_recusa():
    cabecalho("EC-10 (founder)", "Founder recusa interagir com o agente", "🟠 Alto", "✅ explica propósito → persiste 1x → HI se resistir")
    exibir([
        {"de": "agente → founder", "msg": (
            f"Olá, {FOUNDER}! 👋\n\n"
            f"O mentor {MENTOR} sugeriu:\n1. Terça às 14h\n2. Quinta às 10h\n\nQual você prefere?"
        )},
        {"de": FOUNDER, "msg": "Não quero falar com robô. Quero uma pessoa."},
        {"de": "agente", "msg": (
            f"Entendo, {FOUNDER}! Sou a assistente de agendamento da Endeavor — estou aqui para tornar isso "
            "rápido e fácil para você. Só preciso de uma confirmação de horário e já encaminho tudo. "
            "Qual das opções funciona melhor: 1 (terça às 14h) ou 2 (quinta às 10h)?"
        )},
        {"de": FOUNDER, "msg": "Não, quero falar com gente."},
        {"de": "agente → founder", "msg": (
            "Claro! Nossa equipe vai entrar em contato com você diretamente. Obrigado pela paciência!"
        )},
        {"de": "agente → aee", "msg": (
            f"[Escalação — EC-10]\nFounder: {FOUNDER} preferiu contato humano\n"
            "Ação: AEE entra em contato diretamente para coletar confirmação de horário"
        )},
    ])


def ec11_phishing():
    cabecalho("EC-11", "Founder suspeita de phishing", "🔴 Crítico", "❌ HI — prevenção é pré-fluxo (AEE avisa founder antes)")
    exibir([
        {"de": "sistema (prevenção — deve ocorrer ANTES)", "msg": (
            "[AEE envia email/Connect ao founder avisando:\n"
            " 'Você receberá uma mensagem de WhatsApp da Endeavor para agendar sua mentoria.']"
        )},
        {"de": "agente → founder", "msg": (
            f"Olá, {FOUNDER}! 👋\n\n"
            f"O mentor {MENTOR} sugeriu:\n1. Terça às 14h\n2. Quinta às 10h\n\nQual você prefere?"
        )},
        {"de": FOUNDER, "msg": "Como você conseguiu meu número? Isso parece golpe."},
        {"de": "agente", "msg": (
            f"Entendo sua preocupação, {FOUNDER} — é sempre bom verificar! "
            "Sou a assistente de agendamento oficial da Endeavor. Se quiser confirmar, "
            "pode entrar em contato com a equipe Endeavor pelo canal que você já usa. "
            "Nossa equipe também vai entrar em contato para confirmar."
        )},
        {"de": "agente → aee", "msg": (
            f"[Escalação — EC-11]\nFounder: {FOUNDER} · suspeita de phishing\n"
            "Ação: AEE confirma identidade com founder via canal confiável e autoriza retomada"
        )},
    ])


def ec23_ok_sem_opcao():
    cabecalho("EC-23", "'Ok' / 'sim' sem especificar opção", "🔴 Crítico", "✅ muito comum no WhatsApp — agente pede qual número")
    exibir([
        {"de": "agente → founder", "msg": (
            f"O mentor {MENTOR} sugeriu:\n1. Terça às 14h\n2. Quinta às 10h\n\nQual você prefere?"
        )},
        {"de": FOUNDER, "msg": "Ok"},
        {"de": "agente", "msg": (
            "Ótimo! Só para confirmar — você prefere a *opção 1 (terça às 14h)* ou *opção 2 (quinta às 10h)*? "
            "Pode responder só com o número. 😊"
        )},
        {"de": FOUNDER, "msg": "1"},
        {"de": "agente → founder", "msg": (
            "✅ Reunião confirmada!\n\n"
            f"*{MENTOR}* e *{FOUNDER}* se encontrarão na *terça às 14h*."
        )},
        {"de": "agente → mentor", "msg": (
            "✅ Reunião confirmada!\n\n"
            f"*{MENTOR}* e *{FOUNDER}* se encontrarão na *terça às 14h*."
        )},
    ])


def ec24_contra_disponibilidade():
    cabecalho("EC-24", "Founder rejeita todos E oferece contra-disponibilidade", "🔴 Crítico", "✅ Motor de Negociação — vai e vem natural")
    exibir([
        {"de": "agente → founder", "msg": (
            f"O mentor {MENTOR} sugeriu:\n1. Terça às 14h\n2. Quinta às 10h\n\nQual você prefere?"
        )},
        {"de": FOUNDER, "msg": "Não tenho nesses horários. Posso segunda às 9h ou sexta à tarde."},
        {"de": "agente → mentor", "msg": (
            f"Olá, {MENTOR}! 👋\n\n"
            f"{FOUNDER} não pôde confirmar os horários sugeridos, mas tem disponibilidade em: "
            "segunda às 9h ou sexta à tarde.\n\n"
            "Você tem alguma janela nessas opções? Me manda 2 horários exatos se tiver."
        )},
        {"de": MENTOR, "msg": "Segunda às 9h consigo sim."},
        {"de": "agente → founder", "msg": (
            f"Boa notícia, {FOUNDER}! O mentor confirmou disponibilidade na *segunda às 9h*. "
            "Posso confirmar esse horário para você?"
        )},
        {"de": FOUNDER, "msg": "Sim, perfeito!"},
        {"de": "agente → founder", "msg": (
            "✅ Reunião confirmada!\n\n"
            f"*{MENTOR}* e *{FOUNDER}* se encontrarão na *segunda às 9h*."
        )},
        {"de": "agente → mentor", "msg": (
            "✅ Reunião confirmada!\n\n"
            f"*{MENTOR}* e *{FOUNDER}* se encontrarão na *segunda às 9h*."
        )},
    ])


def ec25_founder_delega_assistente():
    cabecalho("EC-25", "Founder delega ao assistente mid-flow", "🟠 Alto", "✅ pede contato → migra conversa com contexto")
    exibir([
        {"de": "agente → founder", "msg": (
            f"O mentor {MENTOR} sugeriu:\n1. Terça às 14h\n2. Quinta às 10h\n\nQual você prefere?"
        )},
        {"de": FOUNDER, "msg": "Pode falar com minha assistente Carla, ela gerencia minha agenda. Número 11 97777-0000."},
        {"de": "agente", "msg": (
            f"Sem problema! Vou continuar o agendamento com a Carla e manter todo o contexto. "
            f"Obrigado, {FOUNDER}!"
        )},
        {"de": "sistema", "msg": (
            "[DB atualizado: contato delegado]\n"
            f"  founder original: {FOUNDER}\n"
            "  delegated_to: Carla · +55 11 97777-0000\n"
            "  context: slots do mentor preservados, estado AWAITING_FOUNDER retomado"
        )},
        {"de": "agente → carla", "msg": (
            f"Olá, Carla! 👋\n\n"
            f"Estou em contato a pedido de {FOUNDER} para confirmar o horário de uma mentoria com {MENTOR}.\n\n"
            "As opções disponíveis são:\n1. Terça às 14h\n2. Quinta às 10h\n\n"
            "Qual delas funciona melhor para a agenda dela?"
        )},
    ])


def ec26_confirmacao_com_modificacao():
    cabecalho("EC-26", "Founder confirma COM modificação de horário", "🟡 Médio", "✅ agente renegocia diretamente com mentor")
    exibir([
        {"de": "agente → founder", "msg": (
            f"O mentor {MENTOR} sugeriu:\n1. Terça às 14h\n2. Quinta às 10h\n\nQual você prefere?"
        )},
        {"de": FOUNDER, "msg": "Opção 2, mas preferia às 9h30 em vez das 10h."},
        {"de": "agente → mentor", "msg": (
            f"Olá, {MENTOR}! Boa notícia — {FOUNDER} gostaria da quinta, "
            "mas perguntou se seria possível às *9h30* em vez das 10h. Você topa?"
        )},
        {"de": MENTOR, "msg": "Pode ser, tudo bem."},
        {"de": "agente → founder", "msg": (
            "✅ Confirmado!\n\n"
            f"*{MENTOR}* e *{FOUNDER}* se encontrarão na *quinta às 9h30*."
        )},
        {"de": "agente → mentor", "msg": (
            "✅ Tudo certo!\n\n"
            f"*{MENTOR}* e *{FOUNDER}* se encontrarão na *quinta às 9h30*."
        )},
    ])


def ec27_escolha_por_descricao():
    cabecalho("EC-27", "Founder escolha por descrição ('a de quinta')", "🟡 Médio", "✅ ConfirmationExtractorAgent mapeia descrição → índice")
    exibir([
        {"de": "agente → founder", "msg": (
            f"O mentor {MENTOR} sugeriu:\n1. Terça às 14h\n2. Quinta às 10h\n\nQual você prefere?"
        )},
        {"de": FOUNDER, "msg": "A de quinta tá melhor pra mim."},
        {"de": "sistema", "msg": "[ConfirmationExtractorAgent: 'de quinta' → opção 2 (quinta às 10h)]"},
        {"de": "agente → founder", "msg": (
            "✅ Reunião confirmada!\n\n"
            f"*{MENTOR}* e *{FOUNDER}* se encontrarão na *quinta às 10h*."
        )},
    ])


def ec28_founder_envia_disponibilidade():
    cabecalho("EC-28", "Founder envia disponibilidade em vez de escolher da lista", "🟡 Médio", "✅ Motor de Negociação — extrai disponibilidade e leva ao mentor")
    exibir([
        {"de": "agente → founder", "msg": (
            f"O mentor {MENTOR} sugeriu:\n1. Terça às 14h\n2. Quinta às 10h\n\nQual você prefere?"
        )},
        {"de": FOUNDER, "msg": "Eu tenho disponibilidade segunda de manhã ou sexta qualquer hora."},
        {"de": "agente", "msg": (
            f"Entendido! Vou verificar com o mentor se algum desses horários funciona. Um momento!"
        )},
        {"de": "agente → mentor", "msg": (
            f"Olá, {MENTOR}! 👋\n\n"
            f"{FOUNDER} tem disponibilidade em: segunda de manhã ou sexta qualquer hora.\n\n"
            "Você conseguiria encaixar algum desses? Me manda 2 opções de horário exato se sim."
        )},
    ])


def ec29_agressivo_founder():
    cabecalho("EC-29", "Resposta emocional / agressiva — founder", "🟠 Alto", "✅ de-escalada empática → HI somente se persistir")
    exibir([
        {"de": "agente → founder", "msg": (
            f"O mentor {MENTOR} sugeriu:\n1. Terça às 14h\n2. Quinta às 10h\n\nQual você prefere?"
        )},
        {"de": FOUNDER, "msg": "Que perda de tempo! Chega de bot!"},
        {"de": "agente", "msg": (
            f"Entendo, {FOUNDER} — prometo ser rápida! Só preciso saber: *terça às 14h* ou *quinta às 10h*? "
            "Uma resposta e já encerro por aqui. 😊"
        )},
        {"de": FOUNDER, "msg": "Não quero nada! Cancela tudo."},
        {"de": "agente → founder", "msg": (
            f"Tudo bem, {FOUNDER}. Nossa equipe vai entrar em contato para entender melhor. "
            "Obrigado e desculpe o incômodo!"
        )},
        {"de": "agente → aee", "msg": (
            f"[Escalação — EC-29]\nFounder: {FOUNDER} · resposta emocional persistente\n"
            "Ação: AEE entra em contato para entender resistência e decisão sobre a mentoria"
        )},
    ])


def ec30_resposta_tardia_founder():
    cabecalho("EC-30", "Founder responde DEPOIS de estado HI", "🟡 Médio", "✅ avalia se ainda viável → propõe reabrir")
    exibir([
        {"de": "sistema", "msg": "[Estado: HUMAN_INTERVENTION_REQUIRED · HI aberto há 2 dias]"},
        {"de": FOUNDER, "msg": "Desculpe a demora! Prefiro a opção 2, quinta às 10h."},
        {"de": "agente", "msg": (
            f"Que bom ouvir de você, {FOUNDER}! 😊 Este caso foi encaminhado para nossa equipe, "
            "mas vou repassar sua preferência imediatamente para verificarem se o horário ainda está disponível. "
            "Eles entrarão em contato em breve!"
        )},
        {"de": "agente → aee", "msg": (
            f"[EC-30 · Founder respondeu após HI]\n"
            f"Founder: {FOUNDER} · Escolha: opção 2 (quinta às 10h)\n"
            "Ação: verificar com mentor se horário ainda disponível e retomar ou rejeitar"
        )},
    ])


def ec40_founder_cancela_antes():
    cabecalho("EC-40", "Founder cancela ANTES da confirmação", "🟠 Alto", "✅ agente notifica mentor + AEE · propõe reagendamento")
    exibir([
        {"de": "agente → founder", "msg": (
            f"O mentor {MENTOR} sugeriu:\n1. Terça às 14h\n2. Quinta às 10h\n\nQual você prefere?"
        )},
        {"de": FOUNDER, "msg": "Preciso cancelar a mentoria por enquanto, não tenho como agora."},
        {"de": "agente → founder", "msg": (
            f"Entendo, {FOUNDER}. Vou comunicar ao {MENTOR} e à nossa equipe. "
            "Quando sua agenda abrir, é só nos avisar que retomamos o agendamento rapidamente!"
        )},
        {"de": "agente → mentor", "msg": (
            f"Olá, {MENTOR}! {FOUNDER} precisou cancelar a mentoria por ora. "
            "Nossa equipe vai entrar em contato sobre próximos passos. Obrigado pela compreensão!"
        )},
        {"de": "agente → aee", "msg": (
            f"[EC-40]\nFounder: {FOUNDER} cancelou antes da confirmação\n"
            "Ação: verificar reagendamento ou encerrar a mentoria no Connect"
        )},
    ])


def ec42_founder_cancela_apos():
    cabecalho("EC-42", "Founder cancela APÓS confirmação (GCal criado)", "🔴 Crítico", "❌ notifica ambos + cancela GCal + novo ciclo")
    exibir([
        {"de": "sistema", "msg": "[Estado: CONFIRMED · quinta às 10h · GCal invite enviado]"},
        {"de": FOUNDER, "msg": "Precisei cancelar a reunião de quinta, surgiu um imprevisto urgente."},
        {"de": "agente → founder", "msg": (
            f"Entendo, {FOUNDER} — imprevistos acontecem! Vou notificar o {MENTOR} agora e nossa equipe vai "
            "buscar uma nova data assim que você tiver disponibilidade."
        )},
        {"de": "agente → mentor", "msg": (
            f"Olá, {MENTOR}! {FOUNDER} precisou cancelar a reunião de quinta às 10h por um imprevisto. "
            "Nossa equipe vai entrar em contato para buscar uma nova data."
        )},
        {"de": "sistema", "msg": "[GCal invite a cancelar — ação manual até implementação automática]"},
        {"de": "agente → aee", "msg": (
            f"[EC-42]\nFounder: {FOUNDER} · cancelou após confirmação · quinta às 10h\n"
            "Ação: cancelar GCal · iniciar novo ciclo de negociação"
        )},
    ])


# ── Pós-Confirmação ───────────────────────────────────────────────────────────

def ec43_mentor_remarcacao():
    cabecalho("EC-43", "Mentor pede remarcação após confirmação", "🔴 Crítico", "✅ agente inicia novo ciclo de negociação naturalmente")
    exibir([
        {"de": "sistema", "msg": "[Estado: CONFIRMED · quinta às 10h · GCal enviado]"},
        {"de": MENTOR, "msg": "Preciso mudar o horário da reunião de quinta, surgiu um compromisso."},
        {"de": "agente → mentor", "msg": (
            f"Sem problema, {MENTOR}! Vou verificar a disponibilidade de {FOUNDER} para um novo horário. "
            "Você tem 2 janelas disponíveis nas próximas semanas que eu possa oferecer a ela?"
        )},
        {"de": MENTOR, "msg": "Pode ser segunda às 11h ou sexta às 15h."},
        {"de": "agente → founder", "msg": (
            f"Olá, {FOUNDER}! 👋 O mentor precisou remarcar a reunião de quinta. Ele sugeriu:\n\n"
            "1. Segunda às 11h\n"
            "2. Sexta às 15h\n\n"
            "Qual dessas opções funciona para você?"
        )},
        {"de": FOUNDER, "msg": "1"},
        {"de": "agente → founder", "msg": "✅ Reagendado! Nova data: *segunda às 11h*. O convite atualizado será enviado em breve."},
        {"de": "agente → mentor", "msg": "✅ Reagendado! {FOUNDER} confirmou *segunda às 11h*. O convite atualizado será enviado."},
        {"de": "sistema", "msg": "[GCal: invite original cancelado · novo invite criado · segunda às 11h]"},
    ])


def ec44_founder_remarcacao():
    cabecalho("EC-44", "Founder pede remarcação após confirmação", "🔴 Crítico", "✅ agente inicia novo ciclo de negociação naturalmente")
    exibir([
        {"de": "sistema", "msg": "[Estado: CONFIRMED · quinta às 10h · GCal enviado]"},
        {"de": FOUNDER, "msg": "Oi! Posso remarcar a reunião de quinta?"},
        {"de": "agente → founder", "msg": (
            f"Claro, {FOUNDER}! Vou verificar a disponibilidade de {MENTOR}. "
            "Tem algum dia / horário preferido para a nova data?"
        )},
        {"de": FOUNDER, "msg": "Prefiro semana que vem, de preferência no começo da semana."},
        {"de": "agente → mentor", "msg": (
            f"Olá, {MENTOR}! 👋 {FOUNDER} precisa remarcar a reunião de quinta. "
            "Ela prefere semana que vem no começo da semana. "
            "Tem 2 horários disponíveis que eu possa oferecer a ela?"
        )},
        {"de": MENTOR, "msg": "Segunda às 10h ou terça às 14h."},
        {"de": "agente → founder", "msg": (
            "O mentor sugeriu:\n1. Segunda às 10h\n2. Terça às 14h\n\nQual você prefere?"
        )},
        {"de": FOUNDER, "msg": "Segunda às 10h."},
        {"de": "agente → founder", "msg": "✅ Reagendado! Nova data: *segunda às 10h*. O convite atualizado será enviado."},
        {"de": "sistema", "msg": "[GCal: invite original cancelado · novo invite criado · segunda às 10h]"},
    ])


def ec45_sem_convergencia():
    cabecalho("EC-45", "N rounds sem convergência (MAX_NEGOTIATION_ROUNDS)", "🟠 Alto", "❌ HI após limite — com resumo completo")
    exibir([
        {"de": "agente → founder", "msg": (
            f"O mentor {MENTOR} sugeriu:\n1. Terça às 14h\n2. Quinta às 10h\n\nQual você prefere?"
        )},
        {"de": FOUNDER, "msg": "Não posso. Tenho segunda às 9h ou sexta às 15h."},
        {"de": "agente → mentor (round 1)", "msg": (
            f"Olá, {MENTOR}! {FOUNDER} não pôde confirmar, mas tem disponibilidade em: "
            "segunda às 9h ou sexta às 15h. Consegue algum desses?"
        )},
        {"de": MENTOR, "msg": "Não consigo segunda nem sexta. Só quarta às 11h ou quinta às 14h."},
        {"de": "agente → founder (round 2)", "msg": (
            "Novas opções do mentor:\n1. Quarta às 11h\n2. Quinta às 14h\n\nAlguma serve?"
        )},
        {"de": FOUNDER, "msg": "Não tenho disponibilidade em nenhum desses também."},
        {"de": "sistema", "msg": "[MAX_NEGOTIATION_ROUNDS=2 atingido · sem sobreposição encontrada]"},
        {"de": "agente → mentor", "msg": (
            f"Olá, {MENTOR}. Infelizmente não conseguimos encontrar um horário em comum com {FOUNDER} "
            "nas rodadas de negociação. Nossa equipe vai entrar em contato para resolver."
        )},
        {"de": "agente → founder", "msg": (
            f"Olá, {FOUNDER}. Não encontramos uma janela em comum com o mentor. "
            "Nossa equipe vai entrar em contato para buscar uma alternativa."
        )},
        {"de": "agente → aee", "msg": (
            "[Escalação — EC-45 · MAX_NEGOTIATION_ROUNDS atingido]\n"
            f"Meeting ID: 1234 · Mentor: {MENTOR} · Founder: {FOUNDER}\n"
            f"Disponibilidade mentor: terça 14h, quinta 10h, quarta 11h, quinta 14h\n"
            f"Disponibilidade founder: segunda 9h, sexta 15h\n"
            "Sem sobreposição — mediação manual necessária"
        )},
    ])


# ── Técnico / Infra ───────────────────────────────────────────────────────────

def ec12_trigger_duplicado():
    cabecalho("EC-12", "Trigger duplicado (mesmo meeting_id disparado 2x)", "🟠 Alto", "✅ deduplicação no endpoint — rejeita HTTP 409")
    exibir([
        {"de": "sistema (disparo 1)", "msg": "[POST /trigger · meeting_id=1234 · workflow iniciado com sucesso · HTTP 201]"},
        {"de": "sistema (disparo 2)", "msg": "[POST /trigger · meeting_id=1234 · duplicata detectada]"},
        {"de": "sistema (deduplicação)", "msg": (
            "[Workflow já ativo para meeting_id=1234 · segundo disparo rejeitado · HTTP 409 Conflict]\n"
            "[Nenhuma nova mensagem enviada · estado não alterado]"
        )},
    ])


def ec13_redis_ttl():
    cabecalho("EC-13", "Redis TTL expira silenciosamente após 24h", "🔴 Crítico", "❌ estado reseta para INIT sem aviso — BUG CRÍTICO")
    exibir([
        {"de": "sistema", "msg": "[Conversa ativa há 24h · Redis TTL expira silenciosamente]"},
        {"de": MENTOR, "msg": "Terça às 14h ou quinta às 10h."},
        {"de": "sistema (BUG)", "msg": (
            "[Estado resetou para INIT · contexto perdido · nenhum aviso ao mentor, founder ou AEE]\n"
            "[Agente recomeça o fluxo como se fosse novo contato — mentor recebe mensagem inicial duplicada]"
        )},
        {"de": "agente (comportamento errado — loop)", "msg": (
            f"Olá, {MENTOR}! 👋\n\n"
            f"Tenho uma mentoria para agendar com {FOUNDER}. Preciso de pelo menos 2 horários disponíveis..."
        )},
        {"de": "nota", "msg": (
            "[Solução: TTL refresh em cada mensagem recebida +\n"
            " alerta ao AEE quando TTL estiver próximo de expirar com conversa ativa]"
        )},
    ])


def ec31_webhook_duplicado():
    cabecalho("EC-31", "Webhook entregue 2x pelo Meta (retry automático)", "🟠 Alto", "❌ sem idempotência por message_id — processa 2x")
    exibir([
        {"de": "sistema (webhook 1)", "msg": "[Meta entrega webhook · message_id=msg_abc · processado · estado avança]"},
        {"de": "sistema (webhook 2)", "msg": "[Meta reenvia mesmo webhook · message_id=msg_abc · retry automático]"},
        {"de": "sistema (BUG)", "msg": (
            "[Sem verificação de message_id · mesma mensagem processada 2x]\n"
            "[Risco: transição de estado duplicada · resposta enviada 2x ao usuário]"
        )},
        {"de": "nota", "msg": "[Solução: deduplicação por message_id no início da task Celery (Redis SET NX com TTL de 24h)]"},
    ])


def ec34_estado_avancou_msg_falhou():
    cabecalho("EC-34", "Estado avançou mas mensagem WhatsApp falhou", "🟠 Alto", "❌ stale state — sem atomicidade entre state write e send")
    exibir([
        {"de": "sistema", "msg": "[SlotExtractorAgent extraiu slots com sucesso]"},
        {"de": "sistema", "msg": "[State machine avança: AWAITING_MENTOR_SLOTS → AWAITING_FOUNDER_SELECTION]"},
        {"de": "sistema", "msg": "[Tenta enviar mensagem ao founder via WhatsApp API]"},
        {"de": "sistema (BUG)", "msg": (
            "[WhatsApp API retorna erro 500 · mensagem NÃO entregue ao founder]\n"
            "[Estado já avançou · founder nunca recebeu a mensagem]\n"
            "[Próxima mensagem do mentor será processada em estado AWAITING_FOUNDER — incorreto]"
        )},
        {"de": "nota", "msg": (
            "[Solução: inverter ordem (send → commit state) OU\n"
            " two-phase: marcar 'send_pending', confirmar após ACK da API,\n"
            " rollback de estado se send falhar definitivamente]"
        )},
    ])


def ec35_gcal_nao_implementado():
    cabecalho("EC-35", "Google Calendar não implementado — gap ativo no MVP", "🔴 Crítico", "❌ confirmação enviada sem criar evento")
    exibir([
        {"de": FOUNDER, "msg": "1"},
        {"de": "agente → founder", "msg": (
            "✅ Reunião confirmada!\n\n"
            f"*{MENTOR}* e *{FOUNDER}* se encontrarão na *terça às 14h*.\n\n"
            "O convite de calendário será enviado em breve."
        )},
        {"de": "agente → mentor", "msg": (
            "✅ Tudo certo!\n\n"
            f"*{MENTOR}* e *{FOUNDER}* se encontrarão na *terça às 14h*.\n\n"
            "O convite de calendário será enviado em breve."
        )},
        {"de": "sistema (GAP CRÍTICO)", "msg": (
            "[GCal invite NÃO criado · gap de implementação ativo no MVP]\n"
            "[Mentor e founder receberam confirmação mas não há evento no Google Calendar]\n"
            "[AEE precisa criar o convite manualmente até implementação automática]"
        )},
        {"de": "agente → aee", "msg": (
            f"[AÇÃO MANUAL NECESSÁRIA — EC-35]\n"
            f"Meeting ID: 1234 · {MENTOR} + {FOUNDER} · terça às 14h\n"
            "Criar convite GCal manualmente e enviar para ambos"
        )},
    ])


def ec36_sem_notificacao_hi():
    cabecalho("EC-36", "Nenhuma notificação chega ao AEE quando conversa vai para HI", "🔴 Crítico", "❌ casos acumulam silenciosamente — EscalationService não implementado")
    exibir([
        {"de": MENTOR, "msg": "Não quero saber disso agora!"},
        {"de": "agente → mentor", "msg": "Nossa equipe vai entrar em contato. Obrigado!"},
        {"de": "sistema", "msg": "[Estado: HUMAN_INTERVENTION_REQUIRED]"},
        {"de": "sistema (GAP)", "msg": (
            "[EscalationService NÃO implementado]\n"
            "[AEE não recebe nenhuma notificação]\n"
            "[Caso fica parado indefinidamente · AEE só descobre por reclamação]"
        )},
        {"de": "nota", "msg": (
            "[Solução: EscalationService dispara ao entrar em HI]\n"
            "[Canal: Slack / email / webhook para AEE]\n"
            "[Payload: meeting_id, motivo, último turno, contatos envolvidos]"
        )},
    ])


# ── Registro e entry point ────────────────────────────────────────────────────

CENARIOS: dict[str, tuple[str, callable]] = {
    "0":   ("Happy Path (referência)", happy_path),
    # Mentor Side
    "1":   ("EC-01 · Delegação de contato para assistente", ec01_delegacao_contato),
    "3":   ("EC-03 · Timeout mentor 48h", ec03_timeout_mentor),
    "5":   ("EC-05 · Resposta ambígua", ec05_resposta_ambigua),
    "6":   ("EC-06 · Mentor envia mídia (áudio/foto)", ec06_midia),
    "10m": ("EC-10 · Mentor recusa agente", ec10_mentor_recusa),
    "14":  ("EC-14 · Slots em mensagens separadas", ec14_slots_em_mensagens_separadas),
    "15":  ("EC-15 · Slots no passado", ec15_slots_no_passado),
    "16":  ("EC-16 · Horário sem data", ec16_horario_sem_data),
    "17":  ("EC-17 · Slot condicional", ec17_slot_condicional),
    "18":  ("EC-18 · Já combinaram diretamente", ec18_ja_combinaram_direto),
    "19":  ("EC-19 · Pergunta fora de escopo", ec19_pergunta_fora_escopo),
    "20":  ("EC-20 · Mentor atualiza disponibilidade com founder aguardando", ec20_mentor_muda_disponibilidade),
    "21":  ("EC-21 · Resposta emocional/agressiva — mentor", ec21_agressivo_mentor),
    "22":  ("EC-22 · Mentor responde após HI", ec22_resposta_tardia_mentor),
    "39":  ("EC-39 · Mentor cancela antes da confirmação", ec39_mentor_cancela_antes),
    "41":  ("EC-41 · Mentor cancela após confirmação", ec41_mentor_cancela_apos),
    # Founder Side
    "4":   ("EC-04 · Founder rejeita sem alternativa", ec04_founder_rejeita_sem_alternativa),
    "9":   ("EC-09 · Janela 24h expirada", ec09_janela_24h),
    "10f": ("EC-10 · Founder recusa agente", ec10_founder_recusa),
    "11":  ("EC-11 · Founder suspeita de phishing", ec11_phishing),
    "23":  ("EC-23 · 'Ok' sem especificar opção", ec23_ok_sem_opcao),
    "24":  ("EC-24 · Founder oferece contra-disponibilidade", ec24_contra_disponibilidade),
    "25":  ("EC-25 · Founder delega ao assistente mid-flow", ec25_founder_delega_assistente),
    "26":  ("EC-26 · Confirmação com modificação de horário", ec26_confirmacao_com_modificacao),
    "27":  ("EC-27 · Escolha por descrição ('a de quinta')", ec27_escolha_por_descricao),
    "28":  ("EC-28 · Founder envia disponibilidade em vez de escolher", ec28_founder_envia_disponibilidade),
    "29":  ("EC-29 · Resposta emocional/agressiva — founder", ec29_agressivo_founder),
    "30":  ("EC-30 · Founder responde após HI", ec30_resposta_tardia_founder),
    "40":  ("EC-40 · Founder cancela antes da confirmação", ec40_founder_cancela_antes),
    "42":  ("EC-42 · Founder cancela após confirmação", ec42_founder_cancela_apos),
    # Pós-Confirmação
    "43":  ("EC-43 · Mentor pede remarcação", ec43_mentor_remarcacao),
    "44":  ("EC-44 · Founder pede remarcação", ec44_founder_remarcacao),
    "45":  ("EC-45 · N rounds sem convergência", ec45_sem_convergencia),
    # Técnico / Infra
    "12":  ("EC-12 · Trigger duplicado", ec12_trigger_duplicado),
    "13":  ("EC-13 · Redis TTL expira silenciosamente", ec13_redis_ttl),
    "31":  ("EC-31 · Webhook duplicado pelo Meta", ec31_webhook_duplicado),
    "34":  ("EC-34 · Estado avançou, mensagem falhou", ec34_estado_avancou_msg_falhou),
    "35":  ("EC-35 · GCal não implementado", ec35_gcal_nao_implementado),
    "36":  ("EC-36 · Sem notificação de HI ao AEE", ec36_sem_notificacao_hi),
}

GRUPOS = [
    ("Happy Path",         ["0"]),
    ("Mentor Side",        ["1","3","5","6","10m","14","15","16","17","18","19","20","21","22","39","41"]),
    ("Founder Side",       ["4","9","10f","11","23","24","25","26","27","28","29","30","40","42"]),
    ("Pós-Confirmação",    ["43","44","45"]),
    ("Técnico / Infra",    ["12","13","31","34","35","36"]),
]


def listar() -> None:
    print("\nCenários disponíveis:\n")
    for grupo, chaves in GRUPOS:
        print(f"  ── {grupo}")
        for k in chaves:
            titulo = CENARIOS[k][0]
            print(f"    {k:>4}  {titulo}")
    print("\nUso:")
    print("  python simular_fluxo.py <número>   → roda cenário específico")
    print("  python simular_fluxo.py all        → roda todos em sequência\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        listar()
        sys.exit(0)

    arg = sys.argv[1].lower()

    if arg == "all":
        for chave, (titulo, fn) in CENARIOS.items():
            fn()
        print()
        sys.exit(0)

    if arg not in CENARIOS:
        print(f"\nCenário '{arg}' não encontrado.")
        listar()
        sys.exit(1)

    CENARIOS[arg][1]()
    print()
