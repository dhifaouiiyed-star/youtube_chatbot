from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.embeddings import get_embeddings
import  os

CHROMA_DIR = "chroma_db"


# Split transcript text into overlapping chunks for better RAG retrieval.
def chunk_text(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", "!", "?", " "]
    )
    return splitter.split_text(text)

def get_collection_name(video_id: str) -> str:
    return f"yt_{video_id}"


# Check if a video is already indexed in ChromaDB.
def video_exists(video_id: str) -> bool:
    collection_name = get_collection_name(video_id)
    embeddings = get_embeddings()
    db = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )
    return db._collection.count() > 0

# Chunk and embed transcript, store in ChromaDB.
# Returns number of chunks stored.
# Skips if video already indexed.
def index_transcript(video_id: str, text: str) -> int:
    if video_exists(video_id):
        print(f"[vectorstore] Video {video_id} already indexed, skipping.")
        db = Chroma(
            collection_name=get_collection_name(video_id),
            embedding_function=get_embeddings(),
            persist_directory=CHROMA_DIR,
        )
        return db._collection.count()
    chunks = chunk_text(text)
    embeddings = get_embeddings()

    db = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        collection_name=get_collection_name(video_id),
        persist_directory=CHROMA_DIR,
    )
    print(f"[vectorstore] Indexed {len(chunks)} chunks for video {video_id}.")
    return len(chunks)



# Return a LangChain retriever for a given video.
# k = number of chunks to retrieve per query.
def get_retriever(video_id: str, k: int = 4):
    embeddings = get_embeddings()
    db = Chroma(
        collection_name=get_collection_name(video_id),
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )
    return db.as_retriever(search_kwargs={"k": k})