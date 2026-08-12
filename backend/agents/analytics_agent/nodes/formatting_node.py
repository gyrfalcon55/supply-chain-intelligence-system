from langchain_core.messages import AIMessage
from backend.services.llm_service import LLM
from backend.agents.analytics_agent.analytics_agent_state import Analytics_Bot

from backend.services.prompts_service import ANALYTICS_FORMAT_OUTPUT_PROMPT

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import get_buffer_string

from utils.logger import logging
from utils.exception import CustomException

import sys


async def format_output(state: Analytics_Bot) -> Analytics_Bot:
    try:
        llm = LLM()
        sql_result = state.get('sql_result') or "Use the data from recent messages"
        question = state['messages'][-1].content
        recent_messages = get_buffer_string(state['messages'][-6:])

        prompt = ChatPromptTemplate.from_template(
            ANALYTICS_FORMAT_OUTPUT_PROMPT   
        )

        chain = prompt | llm.large_model_with_fallback
        result = await chain.ainvoke({
            "question":question,
            "sql_result":sql_result,
            "recent_messages":recent_messages
        })

        logging.info(result)
        return {
            "messages": [AIMessage(content=result.content)],
            "result":result.content
        }

    except Exception as e:
        raise CustomException(e, sys)