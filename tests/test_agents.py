import pytest
from unittest.mock import AsyncMock

from fastapi import Request

from backend.schemas.request import ChatRequest
from backend.api.chat_routes import chat


class FakeWorkflow:

    def __init__(self):

        self.ainvoke = AsyncMock(
            return_value={
                "messages": [
                    type(
                        "Message",
                        (),
                        {
                            "content": (
                                "There are 25 critical products."
                            )
                        }
                    )()
                ]
            }
        )


class FakeState:

    def __init__(self):

        self.workflow = FakeWorkflow()


class FakeApp:

    def __init__(self):

        self.state = FakeState()


class FakeRequest:

    def __init__(self):

        self.app = FakeApp()


@pytest.mark.asyncio
async def test_chat_agent():

    request = FakeRequest()

    chat_request = ChatRequest(
        query="How many critical products are there?",
        thread_id="test-thread-1"
    )

    response = await chat(
        request,
        chat_request
    )

    assert response.answer == (
        "There are 25 critical products."
    )

    request.app.state.workflow.ainvoke.assert_awaited_once()

    call_args = (
        request.app.state.workflow
        .ainvoke.call_args
    )

    input_data = call_args.args[0]

    config = call_args.kwargs["config"]

    assert (
        input_data["messages"][0].content
        == "How many critical products are there?"
    )

    assert (
        config["configurable"]["thread_id"]
        == "test-thread-1"
    )


@pytest.mark.asyncio
async def test_chat_agent_returns_response():

    workflow = FakeWorkflow()

    workflow.ainvoke.return_value = {
        "messages": [
            type(
                "Message",
                (),
                {
                    "content": "Inventory is sufficient."
                }
            )()
        ]
    }

    request = FakeRequest()
    request.app.state.workflow = workflow

    chat_request = ChatRequest(
        query="What is the inventory status?",
        thread_id="test-thread-2"
    )

    response = await chat(
        request,
        chat_request
    )

    assert response.answer == (
        "Inventory is sufficient."
    )


@pytest.mark.asyncio
async def test_chat_agent_preserves_thread_id():

    request = FakeRequest()

    chat_request = ChatRequest(
        query="Show me supplier information.",
        thread_id="thread-123"
    )

    await chat(
        request,
        chat_request
    )

    workflow = (
        request
        .app
        .state
        .workflow
    )

    config = (
        workflow
        .ainvoke
        .call_args
        .kwargs["config"]
    )

    assert (
        config["configurable"]["thread_id"]
        == "thread-123"
    )