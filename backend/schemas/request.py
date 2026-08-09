from pydantic import BaseModel
import pandas as pd
from typing import Any

class ChatRequest(BaseModel):
    query: str
    thread_id: str = "1"

class TableRequest(BaseModel):
    table_name: str
    limit: int = 100
    thread_id: str = "1"



class ReportGenerationRequest(BaseModel):
    report_name :str

class FinalProcurementList(BaseModel):
    planning_date:str
    data: list[dict[str, Any]]