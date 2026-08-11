from backend.agents.analytics_agent.analytics_agent_state import Analytics_Bot
from langchain_core.messages import get_buffer_string

from backend.services.llm_service import LLM

from utils.logger import logging
from utils.exception import CustomException
import sys


async def classify_intent(state):
    return {}

async def intent_router(state: Analytics_Bot) -> str:
    llm = LLM()
    question = state['messages'][-1].content
    recent_messages = get_buffer_string(state['messages'][-6:])

    prompt = f"""
    You are an intent classifier.
    
    RECENT MESSAGES: {recent_messages}
    QUESTION: {question}

    Classify the question into one of:
    - "formal_chat" → greeting from user or general chatting 
    - "sql"       → needs database query (fetch/filter/aggregate data)
    - "format"    → just reformatting or summarizing already returned data

    Return ONLY one word: sql or format or formal_chat. No explanation.
    """

    result = await llm.mini_model_with_fallback.ainvoke(prompt)
    intent = result.content.strip().lower()

    if "format" in intent:
        return "format"
    elif "sql" in intent:
        return "sql"
    else:
        return "formal_chat"