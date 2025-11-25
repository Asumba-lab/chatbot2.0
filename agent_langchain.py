# agent_langchain.py
"""
Simple LangChain agent wrapper.
Uses OpenAI via LangChain by default. Groq support is a placeholder.
"""

import os
from typing import Optional

# LangChain imports (support multiple versions)
ChatOpenAI = None
Tool = None
initialize_agent = None
AgentType = None
try:
    from langchain.chat_models import ChatOpenAI  # older API path
except Exception:
    try:
        from langchain_openai import ChatOpenAI  # newer package split
    except Exception:
        pass
try:
    from langchain.agents import Tool, initialize_agent, AgentType
except Exception:
    try:
        from langchain.tools import Tool
        from langchain.agents import initialize_agent, AgentType
    except Exception:
        pass
try:
    from langchain.llms import OpenAI as LLM_OpenAI
except Exception:
    pass

# OpenAI python fallback (for direct API calls if needed)
import openai

class ChatAgent:
    def __init__(self, openai_api_key: Optional[str]=None, groq_api_key: Optional[str]=None):
        self.openai_api_key = openai_api_key
        self.groq_api_key = groq_api_key
        if self.openai_api_key:
            openai.api_key = self.openai_api_key

        # Tools: only set if Tool is available
        if Tool:
            self.tools = [
                Tool(
                    name="web_search",
                    func=self._web_search,
                    description="Search the web for a short factual summary. Input: query string."
                ),
                Tool(
                    name="run_python",
                    func=self._run_python,
                    description="Run short Python snippets and return the result. Use carefully - it's sandboxed minimally."
                )
            ]
        else:
            self.tools = []

        # lazy init of agent to allow model choice at runtime
        self.agent = None

    # --- Tools
    def _web_search(self, query: str) -> str:
        # Placeholder: replace with SerpAPI or other search provider for real usage.
        # For bootcamp demo, we return a deterministic placeholder response.
        return f"[Search results placeholder for: {query}]"

    def _run_python(self, code: str) -> str:
        # VERY limited sandbox: do NOT use in production with untrusted code.
        try:
            # Restrict builtins for some safety
            restricted_globals = {"__builtins__": {}}
            local_vars = {}
            exec(code, restricted_globals, local_vars)
            # return 'result' variable if set, else repr of locals
            return str(local_vars.get("result", local_vars))
        except Exception as e:
            return f"Python execution error: {e}"

    # --- Agent runner
    def _init_agent_for_model(self, model_choice: str, temperature: float = 0.2):
        """
        Initialize LangChain agent according to chosen model.
        If you pick groq, you'll need to implement a Groq LLM wrapper.
        """
        if "groq" in model_choice.lower():
            try:
                groq_model_map = {
                    "groq/groq-model (placeholder)": "llama-3.1-8b-instruct"
                }
                if model_choice in groq_model_map:
                    model_name = groq_model_map[model_choice]
                else:
                    model_name = model_choice.split("/", 1)[1] if "/" in model_choice else model_choice
                if ChatOpenAI and initialize_agent and AgentType:
                    llm = ChatOpenAI(model=model_name, temperature=temperature, openai_api_key=self.groq_api_key, openai_api_base="https://api.groq.com/openai/v1")
                    agent = initialize_agent(self.tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=False)
                    self.agent = agent
                    return agent
                else:
                    self.agent = None
                    return None
            except Exception as e:
                self.agent = None
                return None
        else:
            # using ChatOpenAI from langchain
            try:
                model_map = {
                    "openai/gpt-4o-mini": "gpt-4o-mini",
                    "openai/gpt-4o": "gpt-4o",
                    "openai/gpt-3.5-turbo": "gpt-3.5-turbo"
                }
                model_name = model_map.get(model_choice, model_choice)
                if ChatOpenAI and initialize_agent and AgentType:
                    llm = ChatOpenAI(model=model_name, temperature=temperature, openai_api_key=self.openai_api_key)
                    agent = initialize_agent(self.tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=False)
                    self.agent = agent
                    return agent
                else:
                    self.agent = None
                    return None
            except Exception:
                self.agent = None
                return None

    def run(self, user_input: str, memory_context: str = "", model_choice: str = "openai/gpt-4o-mini",
            temperature: float = 0.2, memory_window: int = 5) -> str:
        """
        Run the agent to get a reply. We include memory context as part of the user instruction.
        """
        # initialize agent if necessary (or reinit if model changed)
        if self.agent is None:
            agent = self._init_agent_for_model(model_choice, temperature)
        # Build a prompt including memory context
        system_instructions = (
            "You are a helpful assistant that uses the user's memory to be consistent. "
            "Use the memory context when relevant and avoid repeating irrelevant history."
        )

        # If we can use the agent (LangChain), ask it to answer using the memory.
        if self.agent:
            # We send a compact directive + memory + question to the agent via its run() method.
            prompt = f"{system_instructions}\n\nMemory:\n{memory_context}\n\nUser: {user_input}\nAssistant:"
            try:
                # agent.run returns text. It may call tools internally if needed.
                result = self.agent.run(prompt)
                return str(result).strip()
            except Exception as e:
                return self._openai_fallback(user_input, memory_context, model_choice, temperature)
        else:
            return self._openai_fallback(user_input, memory_context, model_choice, temperature)

    def _openai_fallback(self, user_input: str, memory_context: str, model_choice: str, temperature: float):
        # Simple fallback using OpenAI ChatCompletion
        system_prompt = "You are a helpful assistant. Use memory context where it helps."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Memory:\n{memory_context}\n\nUser: {user_input}"},
        ]
        try:
            if "groq" in model_choice.lower() and self.groq_api_key:
                openai.api_key = self.groq_api_key
                openai.api_base = "https://api.groq.com/openai/v1"
                default_model = "llama-3.1-8b-instruct"
            else:
                openai.api_key = self.openai_api_key or self.groq_api_key
                openai.api_base = getattr(openai, "api_base", "https://api.openai.com/v1")
                default_model = "gpt-3.5-turbo"
            resp = openai.ChatCompletion.create(
                model=default_model,
                messages=messages,
                temperature=temperature,
                max_tokens=600
            )
            return resp["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"(OpenAI fallback error: {e})"
