# Chatbot 2.0 — Streamlit + LangChain

Simple Streamlit chatbot with lightweight memory and provider selection (OpenAI or Groq).

## Setup

- `python -m pip install -r requirements.txt`
- Create a `.env` file with:
  - `OPENAI_API_KEY=...` (optional)
  - `GROQ_API_KEY=...` (optional)

## Run

- `streamlit run app.py`

Use the sidebar to select provider and model. Memory is stored locally in `memory.json`.

## Notes

- `.env` and `memory.json` are ignored by Git.
- For Streamlit Community Cloud, configure secrets in the Cloud UI instead of committing `.env`.