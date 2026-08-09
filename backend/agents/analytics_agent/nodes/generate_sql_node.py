from backend.agents.analytics_agent.analytics_agent_state import Analytics_Bot
from langchain_core.messages import get_buffer_string

import json

from langchain_core.prompts import ChatPromptTemplate
from backend.services.prompts_service import ANALYTICS_GENERATE_SQL_PROMPT
from backend.services.llm_service import llm

from utils.logger import logging
from utils.exception import CustomException

import sys







async def generate_sql(state: Analytics_Bot) -> Analytics_Bot:
    try:
        schema_data = json.loads(state["schema"])
        question = state['messages'][-1].content
        summary = state.get('conversation_summary') or "No conversation summary found"
        recent_messages = get_buffer_string(state['messages'][-6:])

        # Detect "all columns" intent — inject SELECT * or explicit cols directly
        all_columns_keywords = ["all columns", "all fields", "everything", "full details", "complete"]
        wants_all_columns = any(kw in question.lower() for kw in all_columns_keywords)

        schema_block = ""
        for item in schema_data:
            if wants_all_columns:
                col_hint = "SELECT ALL columns: " + ", ".join(f'"{c}"' for c in item["columns"])
            else:
                col_hint = "Available columns: " + ", ".join(f'"{c}"' for c in item["columns"])

            schema_block += f'Table: "{item["schema"]}"."{item["table"]}"\n'
            schema_block += f'{col_hint}\n\n'

        prompt = ChatPromptTemplate.from_template(
            ANALYTICS_GENERATE_SQL_PROMPT
        )

        chain = prompt | llm.llama_70b

        sql_query = await chain.ainvoke({
            "summary":summary,
            "recent_messages":recent_messages,
            "schema_block":schema_block,
            "question":question

        })

        return {
            "generated_sql":sql_query.content

        }
    
    except Exception as e:
        raise CustomException(e,sys)