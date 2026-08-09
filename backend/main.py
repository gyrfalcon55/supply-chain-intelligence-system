
from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.services.mcp_service import mcp
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from configs.config import api
from backend.agents.analytics_agent.analytics_agent_graph import build_graph

#routes
from backend.api.chat_routes import router as chat_router
from backend.api.Visualization_routes import router as visualization_router
from backend.api.ml_pipeline_routes import router as ml_pipeline_router
from backend.api.reportgeneration_routes import router as reportgeneration_router
from backend.api.procurementOrders_routes import router as procurement_router
from backend.api.simulation_routes import router as Simulation_router

workflow = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global workflow

    await mcp.initialize_mcp()

    async with AsyncPostgresSaver.from_conn_string(api.DB_URL) as checkpointer:
        await checkpointer.setup()
        app.state.workflow = build_graph(checkpointer)
        yield

    # cleanup if necessary



app = FastAPI(lifespan=lifespan)

app.include_router(chat_router)
app.include_router(visualization_router)
app.include_router(ml_pipeline_router)
app.include_router(procurement_router)
app.include_router(reportgeneration_router)
app.include_router(Simulation_router)

@app.get("/")
def home():
    return {"message":"Backend running"}



'''
mlflow server `
>>   --backend-store-uri "postgresql://postgres:7869@localhost:5432/MLflowDatabase" `
>>   --default-artifact-root "./artifacts" `
>>   --host 127.0.0.1 `
>>   --port 5000

streamlit run streamlit_app.py


uvicorn main:app --reload
'''

