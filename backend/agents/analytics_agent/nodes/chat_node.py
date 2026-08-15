from backend.agents.analytics_agent.analytics_agent_state import Analytics_Bot
from langchain_core.messages import AIMessage
from backend.services.llm_service import LLM
from backend.services.guardrails_service import NeMoGuardrailsService

async def chat_node(state: Analytics_Bot):

    llm = LLM()

    guardrails = NeMoGuardrailsService().get_guardrails()

    question = state['messages'][-1].content


    guarded_model = guardrails | llm.mini_model_with_fallback
    
    result = await guarded_model.ainvoke(question)


    return {
        "messages": [AIMessage(content=result)],
        "result":result
        }