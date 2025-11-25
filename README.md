# Chatbot 2.0 — Streamlit + LangChain

Interactive chatbot built with Streamlit and LangChain, featuring lightweight session memory and the ability to switch between OpenAI and Groq providers.

## Overview

- Streamlit UI for chatting, session control, and model/provider selection
- Persistent session memory in `memory.json`
- Supports OpenAI and Groq via environment variables
- Includes simple tools inside the agent (placeholder web search; sandboxed Python execution)
- Fallback path for direct OpenAI ChatCompletion requests if the LangChain agent fails

## Architecture

- `c:\Users\Steve\Desktop\Chatbot\app.py` — Streamlit app/UX, environment loading, agent wiring
  - Loads `.env` (`app.py:6-9`), reads `OPENAI_API_KEY` and `GROQ_API_KEY` (`app.py:14-17`)
  - Initializes and uses `ChatAgent` (`app.py:33`) and manages UI inputs/outputs (`app.py:20-25`, `app.py:45-75`)
- `c:\Users\Steve\Desktop\Chatbot\agent_langchain.py` — LangChain-based agent
  - Multi-version imports for LangChain components (`agent_langchain.py:10-23`)
  - Tools `web_search` and `run_python` (`agent_langchain.py:31-41`, `agent_langchain.py:47-63`)
  - Model init and provider routing (`agent_langchain.py:65-89`)
  - Agent `run` method constructs prompt with memory (`agent_langchain.py:90-116`)
  - Fallback to OpenAI/Groq chat API if needed (`agent_langchain.py:118-134`)
- `c:\Users\Steve\Desktop\Chatbot\memory.py` — Simple JSON-backed memory store

## Requirements

- Python 3.10+
- `pip`
- Recommended: a virtual environment

## Installation

```bash
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root:

```ini
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
```

Notes:
- `.env` is loaded automatically on app start (`app.py:6-9`).
- It’s OK to set only one of the keys; the app warns if neither is present (`app.py:16-17`).

## Running Locally

```bash
streamlit run app.py
```

If you want headless mode (no email prompt):

```bash
streamlit run app.py --server.headless true
```

Open the URL shown in the terminal (typically `http://localhost:8501`).

## Using Providers & Models

- Select provider/model in the sidebar (`app.py:21-23`).
- OpenAI options: `openai/gpt-4o-mini`, `openai/gpt-4o`, `openai/gpt-3.5-turbo`.
- Groq option: `groq/groq-model (placeholder)` mapped internally to `mixtral-8x7b-32768` (`agent_langchain.py:70-86`).

Custom Groq models:
- You can type/select a value like `groq/<model-name>`, e.g. `groq/mixtral-8x7b-32768` or `groq/llama3-8b-8192`.
- The agent will pass the part after `groq/` as the model name to Groq’s OpenAI-compatible endpoint.

## Session Memory

- Memory is keyed by `Session ID` and persisted in `memory.json` (`app.py:29-41`).
- `Memory window` controls how many most-recent items are included in the prompt (`app.py:24`, `app.py:57-59`).
- Use “Clear memory for this session” to wipe entries for the current session (`app.py:49-51`).

## Deployment (Streamlit Community Cloud)

1. Push the code to a public GitHub repository (e.g., `https://github.com/Asumba-lab/chatbot2.0`).
2. In Streamlit Community Cloud, choose “New app”, select the repo and branch.
3. Configure secrets in the Cloud UI (do not commit `.env`):
   - Add `OPENAI_API_KEY` and/or `GROQ_API_KEY` in the secrets manager.
4. Deploy the app.

Tips:
- Locally you use `.env`; on Cloud, prefer `st.secrets` and environment variables.
- This app reads keys via `os.getenv(...)`. If you want `st.secrets` fallback, you can update the code in `app.py` to read from `st.secrets` when available.

## Troubleshooting

- `NameError: name 'Tool' is not defined` — Caused by LangChain API changes.
  - Fixed by multi-version imports (`agent_langchain.py:10-23`).
  - Alternatively pin LangChain to `0.0.250` (`requirements.txt`).
- “No OPENAI_API_KEY or GROQ_API_KEY found” warning — Set keys in `.env` or environment variables.
- `.env` not loading — Ensure `python-dotenv` is installed and `.env` is at the project root.
- Pip/Numpy build issues on Windows — Update pip (`python -m pip install --upgrade pip`) and retry.

## Security

- `.env` and `memory.json` are ignored by Git (`.gitignore`).
- Never commit API keys or secrets to the repository.
- Avoid logging sensitive information.

## Project Structure

```
Chatbot/
├─ app.py
├─ agent_langchain.py
├─ memory.py
├─ requirements.txt
├─ README.md
├─ .env               # not committed
├─ memory.json        # not committed
└─ .gitignore
```

## License

This project is licensed under the MIT License.