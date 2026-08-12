
import requests
from langchain_core.messages import HumanMessage

from backend.schemas.request import ChatRequest,TableRequest
from backend.schemas.response import ChatResponse,TableResponse

from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: Request, chat_request: ChatRequest):

    config = {
        "configurable": {
            "thread_id": chat_request.thread_id
        }
    }

    workflow = request.app.state.workflow

    response = await workflow.ainvoke(
        {
            "messages": [
                HumanMessage(content=chat_request.query)
            ]
        },
        config=config,
    )

    return ChatResponse(answer=response["result"])
