from backend.agents.analytics_agent.analytics_agent_state import Analytics_Bot
from langchain_core.messages import AIMessage
from backend.services.llm_service import LLM
from backend.services.guardrails_service import NeMoGuardrailsService

from utils.logger import logging
from utils.exception import CustomException
import sys

async def chat_node(state: Analytics_Bot):

    try:

        '''
        Chat_node takes the user query applies guardrails and if approved then pushes the query further, 
        otherwise returns the guardrail message.
        
        '''

        llm = LLM()

        logging.info("chat node initialized")

        guardrails = NeMoGuardrailsService().get_guardrails()
        logging.info("Nemo guardrails initialized")

        question = state['messages'][-1].content


        guarded_model = guardrails | llm.mini_model_with_fallback
        
        result = await guarded_model.ainvoke(question)


        return {
            "messages": [AIMessage(content=result)],
            "result":result
            }


    except Exception as e:
        logging.error("Error in the chat node")
        raise CustomException(e,sys)