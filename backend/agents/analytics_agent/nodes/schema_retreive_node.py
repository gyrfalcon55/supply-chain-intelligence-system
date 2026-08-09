from configs.config import load_config
from backend.services.db_schema_service import load_schema
from backend.services.llm_service import llm
from langchain_core.messages import get_buffer_string

from backend.agents.analytics_agent.analytics_agent_state import Analytics_Bot

from langchain_core.prompts import ChatPromptTemplate
import json
import sys

from utils.logger import logging
from utils.exception import CustomException

from configs.paths import ANALYTIC_DB_SCHEMAS_PATH


config = load_config()
analytics_schema_details = ANALYTIC_DB_SCHEMAS_PATH


RAW_SCHEMA = load_schema(analytics_schema_details)  # load once at startup, not inside the node

async def relevant_schema(state: Analytics_Bot) -> Analytics_Bot:
    try:
        question = state['messages'][-1].content
        summary = state.get('conversation_summary') or "No conversation summary found"
        recent_messages = get_buffer_string(state['messages'][-6:])
        # Give LLM only what it needs to PICK a table — no column details
        table_hints = [
            {
                "schema": e["schema"],
                "table": e["table"],
                "description": e["description"],
                "keywords": e["keywords"]   # ← LLM matches intent to keywords
            }
            for e in RAW_SCHEMA
        ]

        prompt = ChatPromptTemplate.from_template("""
            You are a table selector. Pick the relevant table(s) for the question.
            
            RECENT MESSAGES: {recent_messages} 
                                                  
            CONVERSATION SUMMARY (for context):
            {summary}   

            TABLES:
            {tables}

            QUESTION: {question}

            Rules:
            - Return ONLY valid JSON. No explanation.
            - Use exact schema and table names from the list above.

            Return format:
            [{{"schema": "...", "table": "..."}}]
            """)
        chain = prompt | llm.gpt_20b
        response = await chain.ainvoke({
            "summary":summary,
            "recent_messages": recent_messages,
            "tables": json.dumps(table_hints, indent=2),
            "question": question

        })

        # LLM picks the table — code fetches the exact columns
        selected = json.loads(response.content)
        enriched = []
        for item in selected:
            key = f"{item['schema']}.{item['table']}"
            match = next((e for e in RAW_SCHEMA if f"{e['schema']}.{e['table']}" == key), None)
            if match:
                enriched.append({
                    "schema": match["schema"],
                    "table": match["table"],
                    "columns": match["columns"]  # always from code, never from LLM
                })
        return {"schema": json.dumps(enriched)}

    except Exception as e:
        raise CustomException(e, sys)