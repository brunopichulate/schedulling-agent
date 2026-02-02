# Endeavor AI

Este projeto implementa agentes de IA inteligentes e workflows automatizados utilizando a biblioteca [Agno](https://github.com/agno-agi/agno) (anteriormente Phidata) e [OpenAI](https://openai.com/). Além disso, inclui integração completa com [Langfuse](https://langfuse.com/) para observabilidade e gerenciamento de prompts.

## 📋 Funcionalidades

- **Agentes Especializados**: Agentes de IA que realizam tarefas específicas.
- **Workflows**: Orquestração de tarefas complexas, coordenando múltiplos agentes.
- **Observabilidade**: Integração com Langfuse local via Docker para monitoramento de traces e gerenciamento de prompts.

## 🛠️ Pré-requisitos

- Python 3.12 ou superior
- Docker e Docker Compose (para rodar o Langfuse localmente)
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
Certifique-se de configurar sua `OPENAI_API_KEY` e as credenciais do Langfuse no arquivo `.env`.

## 🐳 Configurando o Langfuse (Local)

O projeto inclui um `docker-compose.yml` para rodar o Langfuse localmente (Server, Postgres e Redis).

1. Inicie os serviços:
```bash
docker-compose up -d
```
2. Acesse o painel do Langfuse em `http://localhost:3000` (ou a porta configurada).
3. Crie um projeto e obtenha suas chaves (Public Key, Secret Key, Host) para adicionar ao `.env`.

## 💻 Como Usar

### Executando um Workflow

Para rodar o workflow de teste com o gradio rode o seguinte comando:

```bash
uv run ./chat.py
```

## 📂 Estrutura do Projeto

- `src/agents`: Definição dos agentes (ex: Researcher, Writer) e suas ferramentas.
- `src/workflows`: Definição dos fluxos de trabalho que orquestram os agentes.
- `src/core`: Configurações centrais, como a integração com Langfuse.
- `docker-compose.yml`: Definição da infraestrutura local para o Langfuse.
- `pyproject.toml`: Gerenciamento de dependências e configurações do projeto.

## 🧪 Testes

Para rodar os testes automatizados:

```bash
pytest
```
