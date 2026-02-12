# Endeavor AI

Este projeto implementa agentes de IA inteligentes e workflows automatizados utilizando a biblioteca [Agno](https://github.com/agno-agi/agno) (anteriormente Phidata) e [OpenAI](https://openai.com/). Além disso, inclui integração completa com [Langfuse](https://langfuse.com/) para observabilidade e gerenciamento de prompts.

O projeto agora expõe uma API REST desenvolvida com [FastAPI](https://fastapi.tiangolo.com/) e processamento assíncrono de tarefas via [Celery](https://docs.celeryq.dev/).

## 📋 Funcionalidades

- **Agentes Especializados**: Agentes de IA que realizam tarefas específicas.
- **Workflows**: Orquestração de tarefas complexas, coordenando múltiplos agentes.
- **API REST**: Interface HTTP para interação com os agentes e serviços.
- **Integração WhatsApp**: Recebimento e processamento de mensagens via Webhook.
- **Background Tasks**: Processamento assíncrono de mensagens e workflows pesados via Celery e Redis.
- **Observabilidade**: Integração com Langfuse local via Docker para monitoramento de traces e gerenciamento de prompts.

## 🛠️ Pré-requisitos

- Python 3.12 ou superior
- Docker e Docker Compose (para rodar Redis e Langfuse)
- Gerenciador de dependências `uv`

## 🚀 Instalação

1. **Clone o repositório:**

```bash
git clone <url-do-repositorio>
cd endeavor-ai
```

2. **Configure o ambiente virtual e instale as dependências:**

```bash
uv sync
```

3. **Configure as variáveis de ambiente:**

Copie o arquivo de exemplo e preencha com suas chaves:
```bash
cp .env.example .env
```
Certifique-se de configurar:
- `OPENAI_API_KEY`
- Credenciais do Langfuse
- Credenciais do WhatsApp/Meta (para integração com WhatsApp)
- URL do Redis (para Celery e Rate Limiting)
- URL do MongoDB

## 🐳 Infraestrutura (Redis e Langfuse)

O projeto utiliza Redis como broker para o Celery e para Rate Limiting da API. O Langfuse é usado para observabilidade.

1. Inicie os serviços via Docker:
```bash
docker-compose up -d
```
2. Acesse o painel do Langfuse em `http://localhost:3000` (se habilitado).

## 💻 Como Usar

### Executando a API e o App

Para rodar a API (FastAPI):

```bash
uv run ./main.py

uv run celery -A src.core.celery worker --loglevel=info
```
A API estará disponível em `http://localhost:8000`.

### Executando os Workers (Celery)

Para processar tarefas em segundo plano (como mensagens do WhatsApp):

```bash
uv run celery -A src.core.celery worker --loglevel=info
```

### Executando um Workflow (Exemplo CLI)

Para rodar o workflow de teste com o gradio:

```bash
uv run ./chat.py
```

## 📂 Estrutura do Projeto

- `src/api`: Rotas e controladores da API FastAPI.
- `src/agents`: Definição dos agentes (ex: Researcher, Writer) e suas ferramentas.
- `src/tasks`: Tarefas assíncronas do Celery (ex: processamento de WhatsApp).
- `src/services`: Serviços de integração (ex: WhatsApp client).
- `src/workflows`: Definição dos fluxos de trabalho que orquestram os agentes.
- `src/core`: Configurações centrais (Config, Celery, Langfuse).
- `docker-compose.yml`: Definição da infraestrutura local para o Langfuse e Redis.
- `pyproject.toml`: Gerenciamento de dependências e configurações do projeto.

## 🧪 Testes

Para rodar os testes automatizados:

```bash
pytest
```

## Lint

```bash
uv run ruff check .
uv run ruff check . --fix
uv run ruff format .
```

## Flower + Celery

```bash
uv run .\main.py
uv run celery -A src.core.celery worker -P solo --concurrency=1 --loglevel=info
uv run celery -A src.core.celery flower

http://localhost:5555
```

# Researcher prompt (langfuse)

```bash
Role: You are an expert assistant specialized in the Endeavor mentor network. Your goal is to help entrepreneurs find the right mentors.
Capabilities:

1.  **Search by Name**: Use `search_mentor_tool` when the user asks for a specific person.
2.  **Recommend by Skill/Topic**: Use `recommend_mentor_tool` when the user asks for help with a specific problem or topic.
Instructions:
- When recommending mentors, always explain *why* you selected them based on their `functional_skills` or `biography`.
- Provide a summary of their relevant experience.
- If no mentors are found, apologize and suggest a broader topic.
- Always answer in the same language as the user's question (Portuguese or English).
Example Queries:
- User: "Quem é o mentor de marketing?" -> Tool: `recommend_mentor_tool("marketing")`
- User: "Me fale sobre Jorge Paulo Lemann" -> Tool: `search_mentor_tool("Jorge Paulo Lemann")`
```

# Writer prompt (langfuse)

```bash
You are a writing agent.

You will receive:
- A research text
- A line in the format: WORD_COUNT: <number>

Your tasks:
1. Write a concise and clear summary of the research.
2. At the end of your response, show the word count in the format:

Total words in research: <number>

Rules:
- Do NOT recalculate the word count.
- Use ONLY the provided number.
- Do NOT mention tools or intermediate steps.
```
