import os
from mcp.server.fastmcp import FastMCP
import fitz
import chromadb
from sentence_transformers import SentenceTransformer  

# Initialize Server
mcp = FastMCP("ResearchAssistant") # Gave the server a name

FILES_DIR = "../data/files"
CHROMA_DIR = "../chroma_db"

# Ensure directories exist
os.makedirs(FILES_DIR, exist_ok=True)

# Initialize DB and Embeddings
client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_or_create_collection(name="research_files")
model = SentenceTransformer("all-MiniLM-L6-v2")


@mcp.tool()
def list_files() -> list:
    """Lists all available PDF files for research."""
    if not os.path.exists(FILES_DIR):
        return []
    
    return [f for f in os.listdir(FILES_DIR) if f.endswith(".pdf")]


@mcp.tool()
def extract_text(file_name: str) -> str:
    """Extract full text from a research paper."""
    path = os.path.join(FILES_DIR, file_name)

    if not os.path.exists(path):
        return "File not found"
    
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()

    return text # Removed the 15k limit to read full papers


@mcp.tool()
def get_file_metadata(file_name: str) -> dict:
    """Get metadata about a research paper (Size, Title, Author)."""
    path = os.path.join(FILES_DIR, file_name)

    if not os.path.exists(path):
        return {"Error": "File not found"}
    
    doc = fitz.open(path)
    metadata = doc.metadata
    size = os.path.getsize(path)
    
    return {
        "file": file_name,
        "size_bytes": size,
        "title": metadata.get("title", "Unknown"),
        "author": metadata.get("author", "Unknown"),
        "pages": len(doc)
    }


def chunk_text(text, chunk_size=500, overlap=100):
    """Chunks text while trying to avoid cutting words in half."""
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        
        # If we aren't at the end of the text, try to snap to the nearest space
        # to avoid cutting words in half
        if end < text_length:
            last_space = text.rfind(" ", start, end)
            if last_space != -1 and last_space > start:
                end = last_space
                
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
            
        start = end - overlap
        
    return chunks


@mcp.tool()
def index_file(file_name: str) -> str:
    """Index a research file into the vector database."""
    text = extract_text(file_name)

    if text == "File not found":
        return "File not found"
    
    chunks = chunk_text(text)
    
    if not chunks:
        return f"No text could be extracted from {file_name}."

    embeddings = model.encode(chunks).tolist()
    ids = [f"{file_name}_{i}" for i in range(len(chunks))]
    metadata = [{"file": file_name, "chunk": i} for i in range(len(chunks))]

    collection.delete(where={"file": file_name})

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadata
    )

    return f"Indexed {len(chunks)} chunks from {file_name}"


@mcp.tool()
def search_files(query: str, n_results: int = 5) -> list:
    """Search indexed files using semantic similarity."""
    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    # Fixed bug: changed `documents` to `docs` 
    docs = results.get("documents", [])
    metadatas = results.get("metadatas", [])

    if not docs or not docs[0]:
        return []

    output = []
    for doc, meta in zip(docs[0], metadatas[0]):
        output.append({
            "text": doc,
            "file": meta["file"],
            "chunk": meta["chunk"]
        })

    return output


@mcp.tool()
def list_indexed_files() -> list:
    """List files already indexed in the vector database."""
    results = collection.get(include=["metadatas"])
    metadatas = results.get("metadatas", [])

    files = set()
    for m in metadatas:
        if m and "file" in m: # Added a small safety check
            files.add(m["file"])

    return list(files)


@mcp.tool()
def index_all_files() -> str:
    """Index all PDF files in the data directory."""
    files = list_files()

    if not files:
        return "No files found."

    results = []
    for f in files:
        result = index_file(f)
        results.append(result)

    return "\n".join(results)

