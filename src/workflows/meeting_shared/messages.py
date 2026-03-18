from typing import List

def build_initial_message(donated_name: str, received_name: str, date_display: str, slots: List[str], use_bold_asterisks: bool = True) -> str:
    bold_marker = "*" if use_bold_asterisks else "**"
    return (
        f"Olá, {donated_name}! 👋\n\n"
        f"Temos uma reunião com {received_name} prevista para {bold_marker}{date_display}{bold_marker}.\n\n"
        f"Para agendar, envie pelo menos 2 horários disponíveis para que possamos oferecer opções ao participante.\n\n"
        f"Escolha um dos horários abaixo ou informe outro de sua preferência "
        f"(ex: *amanhã*, *dia 29*, *às 13:00*, *de manhã*):\n\n"
        + "\n".join(slots)
        + "\n\nCaso não queira agendar, basta dizer."
    )

def build_timeout_message(role: str) -> str:
    if role == "donated":
        return "⏰ O mentor não respondeu a tempo. O caso foi encaminhado para intervenção humana."
    return "⏰ O mentorado não respondeu a tempo. O caso foi encaminhado para intervenção humana."

def build_rejected_message(role: str, received_name: str = "") -> str:
    if role == "donated":
        return "Entendido, o mentor optou por não agendar. O caso foi encaminhado para intervenção humana."
    return f"O mentorado {received_name} não aceitou os horários sugeridos. O caso foi encaminhado para intervenção humana."

def build_slot_selection_message(received_name: str, donated_name: str, slots_text: str) -> str:
    return (
        f"Olá, {received_name}! 👋\n\n"
        f"O mentor {donated_name} sugeriu os seguintes horários para a reunião:\n\n"
        f"{slots_text}\n\n"
        f"Qual dessas opções você prefere? (Responda com o número da opção ou o horário, ou diga se não puder em nenhum)."
    )

def build_need_more_options_message() -> str:
    return "Por favor, forneça pelo menos duas opções de horário para o mentorado escolher (ex: *segunda às 14h* ou *terça às 10h*)."

def build_unrecognized_options_message() -> str:
    return "Não consegui identificar os horários informados. Poderia informar pelo menos duas opções de horários? (ex: *dia 29 às 14h* ou *amanhã de manhã*)"

def build_unrecognized_selection_message() -> str:
    return "Não consegui identificar qual opção você escolheu. Poderia responder visualmente com o número da opção (ex: 1 ou 2) ou confirmar o horário exato desejado?"

def build_confirmation_message(donated_name: str, received_name: str, slot_display: str, use_bold_asterisks: bool = True) -> str:
    bold_marker = "*" if use_bold_asterisks else "**"
    return (
        f"✅ Reunião agendada com sucesso!\n\n"
        f"{bold_marker}{donated_name}{bold_marker} e {bold_marker}{received_name}{bold_marker} se encontrarão em "
        f"{bold_marker}{slot_display}{bold_marker}."
    )

def build_human_intervention_message() -> str:
    return "Este atendimento já foi encerrado e encaminhado para intervenção humana."

def build_already_confirmed_message() -> str:
    return "A reunião já foi confirmada. Nenhuma ação adicional é necessária."

def build_unexpected_state_message(current_status: str) -> str:
    return f"Estado inesperado: `{current_status}`. Por favor, reinicie o fluxo."


def build_max_clarifications_message() -> str:
    return (
        "Não consegui entender as respostas fornecidas. "
        "O caso foi encaminhado para o time Endeavor, que entrará em contato em breve."
    )


def build_negotiation_counter_message(
    donated_name: str, received_name: str, windows_text: str
) -> str:
    return (
        f"Olá, {donated_name}! 👋\n\n"
        f"{received_name} não pôde confirmar os horários sugeridos, mas tem disponibilidade em: "
        f"{windows_text}.\n\n"
        f"Você teria disponibilidade em alguma dessas janelas? "
        f"Se sim, envie pelo menos 2 opções de horário."
    )
