from backend.agents.analytics_agent.analytics_agent_state import Analytics_Bot
from backend.services.llm_service import LLM

from langchain_core.messages import get_buffer_string
from langchain_core.messages import HumanMessage, RemoveMessage

from utils.logger import logging
from utils.exception import CustomException

import sys


def route_counter(state):
    llm = LLM()
    conversation = get_buffer_string(state["messages"])

    token_count = llm.mini_model_with_fallback.get_num_tokens(conversation)

    if token_count >= 3000:
        return "summarize"

    return "continue"

def token_counter(state):
    return {}

async def summarize_chat(state: Analytics_Bot) -> Analytics_Bot:
    llm = LLM()
    messages = state['messages']

    messages_to_summarize = messages[-10:]
    
    truncated = []
    for m in messages_to_summarize:
        content = m.content if isinstance(m.content, str) else str(m.content)
        truncated.append(f"{type(m).__name__}: {content[:500]}")  # max 500 chars per message

    prompt = f"""
    You are a chat summarization agent.

    MESSAGES:
    {chr(10).join(truncated)}

    - Summarize the conversation concisely.thsi 
    - Do not exclude important metrics or product names.
    - Keep the summary under 200 words.
    """

    result = await llm.large_model_with_fallback.ainvoke(prompt)
    summary = result.content

    latest_human = next(
        (m for m in reversed(messages) if isinstance(m, HumanMessage)),
        None
    )

    if latest_human is None:
        raise CustomException("No human message found during summarization", sys)
    
    remove_messages = [
        RemoveMessage(id=m.id) for m in messages if m.id is not None
    ]

    return {
        'conversation_summary': summary,
        'messages': [
            *remove_messages,
            HumanMessage(content=f"Previous summary: {summary}"),
            latest_human
            ]
    }
