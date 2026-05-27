from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
app = FastAPI(
    title="YouTube RAG Agent",
    description="Ask questions about any YouTube video using AI",
    version="1.0.0",
)

# Allow all origins for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api")
@app.get("/")
async def root():
    return {
        "message": "YouTube RAG Agent is running!",
        "docs": "/docs",
    }
