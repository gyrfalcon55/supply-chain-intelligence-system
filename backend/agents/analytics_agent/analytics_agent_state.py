from typing import TypedDict, Annotated
from langgraph.graph.message import BaseMessage, add_messages


class Analytics_Bot(TypedDict):
    
    messages:Annotated[list[BaseMessage],add_messages]
    conversation_summary:str
    schema:str
    generated_sql:str
    sql_result:str
    result:str