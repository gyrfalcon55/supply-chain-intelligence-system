from backend.agents.analytics_agent.analytics_agent_state import Analytics_Bot
from langgraph.graph import StateGraph, START, END

from utils.logger import logging
from utils.exception import CustomException

import sys

## nodes

from backend.agents.analytics_agent.nodes.schema_retreive_node import relevant_schema

from backend.agents.analytics_agent.nodes.generate_sql_node import generate_sql

from backend.agents.analytics_agent.nodes.execute_sql_node import execute_sql

from backend.agents.analytics_agent.nodes.formatting_node import format_output

from backend.agents.analytics_agent.nodes.conversation_summary_node import summarize_chat, token_counter, route_counter

from backend.agents.analytics_agent.nodes.get_intent_node import intent_router, classify_intent

from backend.agents.analytics_agent.nodes.chat_node import chat_node



def build_graph(checkpointer):
    
    try:

        graph = StateGraph(Analytics_Bot)

        graph.add_node('relevant_schema',relevant_schema)

        graph.add_node('generate_sql',generate_sql)

        graph.add_node('execute_sql',execute_sql)

        graph.add_node('format_output',format_output)

        graph.add_node('summarize_chat',summarize_chat)

        graph.add_node('token_counter', token_counter)

        graph.add_node('classify_intent', classify_intent)

        graph.add_node('chat_node',chat_node)

        graph.add_edge(START,'token_counter')
        graph.add_conditional_edges('token_counter',route_counter,
                                    {
                                        "summarize":'summarize_chat',
                                        "continue":'relevant_schema'
                                    }
                                    )
        graph.add_edge('summarize_chat','relevant_schema')
        graph.add_edge('relevant_schema', 'classify_intent')     
        graph.add_conditional_edges('classify_intent', intent_router, {
            "sql": 'generate_sql',                                 
            "format": 'format_output',
            "formal_chat":'chat_node'                              
        })
        graph.add_edge('generate_sql','execute_sql')
        graph.add_edge('execute_sql','format_output')
        graph.add_edge('format_output',END)
        graph.add_edge('chat_node',END)

        workflow = graph.compile(checkpointer)


        return workflow

    except Exception as e:
        raise CustomException(e,sys)