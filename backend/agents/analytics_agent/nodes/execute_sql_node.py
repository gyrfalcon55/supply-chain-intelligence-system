from backend.services.mcp_service import mcp
from backend.agents.analytics_agent.analytics_agent_state import Analytics_Bot
from backend.services.sql_query_validation_service import SQLSafetyService

import re
import sys
import json 

from utils.logger import logging
from utils.exception import CustomException


async def execute_sql(state: Analytics_Bot) -> Analytics_Bot:
    try:

        logging.info("Sql execution triggered")
        raw = state["generated_sql"].strip()
        raw = re.sub(r'```(?:json)?|```', '', raw).strip()

        arrays = re.findall(r'\[.*?\]', raw, re.DOTALL)
        if len(arrays) > 1:
            merged = []
            for a in arrays:
                merged.extend(json.loads(a))
            queries = merged
        elif len(arrays) == 1:
            queries = json.loads(arrays[0])
        else:
            raise CustomException(f"No valid JSON array found in: {raw}", sys)

        if not queries:
            raise CustomException("LLM returned empty query list", sys)

        results = []
        previous_result = None  
        for item in queries:
            try:
                sql = item["query"]
               
                if previous_result is not None and "{{previous_result}}" in sql:
                    sql = sql.replace("{{previous_result}}", str(previous_result))

                
                SQLSafetyService.validate(sql)
                result = await mcp.EXECUTE_TOOL.ainvoke({"sql": sql})
                logging.info("Sql execution done")
                
                previous_result = result

                results.append({
                    "table": item["table"],
                    "data": result
                })

            except Exception as e:
                results.append({
                    "table": item["table"],
                    "data": f"Query failed: {str(e)}"
                })

        return {"sql_result": str(results)}

    except json.JSONDecodeError:
        raise CustomException(f"LLM returned invalid JSON: {state['generated_sql']}", sys)
    except Exception as e:
        logging.error("Error while sql execution")
        raise CustomException(e, sys)