from fastapi import APIRouter, HTTPException
from atlas.web.models.query_request import QueryRequest
from atlas.web.services import relational, vector, graph, llm

router = APIRouter()

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

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))