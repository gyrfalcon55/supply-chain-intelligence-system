from backend.agents.analytics_agent.analytics_agent_state import Analytics_Bot
from langchain_core.messages import AIMessage
from backend.services.llm_service import LLM


async def chat_node(state: Analytics_Bot):

    llm = LLM()

    question = state['messages'][-1].content

    prompt =f'''
        you are an helpful assistant. reply to the user only if the question is not harmful
        and related to tech only. or greetings.

        otherwise say "can only reply to tech related queries"

        {question}
        '''
    
    result = await llm.mini_model_with_fallback.ainvoke(prompt)


    return {
        "messages": [AIMessage(content=result.content)],
        "result":result.content
        }