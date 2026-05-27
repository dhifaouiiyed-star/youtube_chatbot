from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from app.core.transcript import get_transcript
from app.core.vectorstore import index_transcript, video_exists
from app.core.rag import ask_question

router = APIRouter()

class IngestRequest(BaseModel):
    url: str
class IngestResponse(BaseModel):
    video_id: str
    language: str
    language_code: str
    num_chunks: int
    already_indexed: bool
    message: str
class QuestionRequest(BaseModel):
    video_id: str
    question: str
class QuestionResponse(BaseModel):
    video_id: str
    question: str
    answer: str
    sources: list[str]

@router.post("/ingest",response_model=IngestResponse)
async def ingest(request: IngestRequest):
    try:
        transcript = get_transcript(request.url)
        video_id = transcript["video_id"]
        already_indexed = video_exists(video_id)
        if already_indexed:
            return IngestResponse(
                video_id=video_id,
                language=transcript["language"],
                language_code=transcript["language_code"],
                num_chunks=0,
                already_indexed=True,
                message="Video already indexed. You can start asking questions.",
            )
        # Index transcript
        num_chunks = index_transcript(video_id, transcript["text"])
        return IngestResponse(
            video_id=video_id,
            language=transcript["language"],
            language_code=transcript["language_code"],
            num_chunks=num_chunks,
            already_indexed=False,
            message=f"Video indexed successfully with {num_chunks} chunks.",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
@router.post("/ask_question",response_model=QuestionResponse)
async def ask(request: QuestionRequest):
    try:
        if not video_exists(request.video_id):
            raise HTTPException(
                status_code=404,
                detail="Video not indexed yet. Please call /ingest first.",
            )
        result = ask_question(request.video_id, request.question)
        return QuestionResponse(
            video_id=request.video_id,
            question=request.question,
            answer=result["answer"],
            sources=result["sources"],
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/status/{video_id}")
async def check_status(video_id: str):
    """Check if a video is already indexed."""
    return {
        "video_id": video_id,
        "indexed": video_exists(video_id),
    }


@router.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}