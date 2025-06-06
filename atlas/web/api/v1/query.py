import logging

from fastapi import APIRouter, HTTPException
from atlas.web.models.query_request import QueryRequest
from atlas.web.services import relational, vector, graph, llm
from atlas.web.services.utils import ServiceException

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/query")
async def handle_query(request: QueryRequest):
    service = request.service.lower()

    try:
        if service == "relational":
            result = relational.handle(request.query)
        elif service == "vector":
            result = vector.handle(request.query)
        elif service == "graph":
            result = graph.handle(request.query)
        elif service == "llm":
            if not request.llmProvider or not request.llmModel:
                raise HTTPException(status_code=400, detail="Missing llmProvider or llmModel for LLM service.")
            result = llm.handle(request.query, request.llmProvider, request.llmModel)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported service: {request.service}")

        return {
            "status": "success",
            "service": service,
            "result": result
        }
    except ServiceException as e:
        return {
            "status": "failure",
            "service": service,
            "result": f"{request.query}: {str(e)}"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Query failed with exception", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))