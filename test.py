from app.core.transcript import get_transcript
from app.core.vectorstore import index_transcript, get_retriever
url = "https://youtu.be/sVcwVQRHIc8"

# Step 1: get transcript
print("📥 Fetching transcript...")
result = get_transcript(url)
print(f"✅ Got transcript: {len(result['text'])} characters, language: {result['language']}")

# Step 2: index into ChromaDB
print("\n📦 Indexing into ChromaDB...")
num_chunks = index_transcript(result["video_id"], result["text"])
print(f"✅ Indexed {num_chunks} chunks")

# Step 3: test retrieval
print("\n🔍 Testing retrieval...")
retriever = get_retriever(result["video_id"])
docs = retriever.invoke("What is this song about?")
print(f"✅ Retrieved {len(docs)} chunks:")
for i, doc in enumerate(docs):
    print(f"\n--- Chunk {i+1} ---\n{doc.page_content}")