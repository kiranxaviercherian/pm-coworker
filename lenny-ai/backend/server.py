from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import lancedb

# Load environment variables from .env file
load_dotenv()

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import LanceDB
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

app = FastAPI()

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LANCEDB_PATH = r"C:\Users\kiran\.gemini\antigravity\scratch\pm-coworker\lancedb_data"
TABLE_NAME = "lenny_brain"

# Load references
try:
    print("Connecting to LanceDB...")
    db = lancedb.connect(LANCEDB_PATH)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Check if table exists
    if TABLE_NAME not in db.table_names():
        raise RuntimeError(f"Table '{TABLE_NAME}' not found in LanceDB.")
        
    vectorstore = LanceDB(
        connection=db,
        embedding=embeddings,
        table_name=TABLE_NAME
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    
    print("Initializing Gemini LLM...")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
    
except Exception as e:
    print(f"Error during initialization: {str(e)}")


system_prompt = """You are a world-class Product Manager coworker. You give extremely practical, actionable advice based on a blend of top-tier industry insights and general product management best practices.

You have been provided with context excerpts from Lenny's Podcast transcripts.

Your goal is to answer the user's question comprehensively.

CRITICAL RULE 1: Prioritize the Context
Always look to the provided context first. If the context contains relevant frameworks, stories, or advice, you must lead with them. Whenever you use information from the context, you MUST explicitly cite the guest.
Example: "As Brian Chesky mentioned, you should focus on..."

CRITICAL RULE 2: Enhance with Internal Knowledge
If the provided context does not fully answer the question, or if a concept from the context needs further explanation, you should seamlessly bring in your own general knowledge of product management, agile methodologies, and tech industry standards to provide a complete, robust answer.

CRITICAL RULE 3: Clear Delineation
You must make it clear to the user what advice comes directly from the podcast guests versus what is general PM best practice.
Example: "To build on Shreyas Doshi's point about risk mitigation, a standard industry practice you can also apply here is..." or "While the podcast excerpts don't cover this specific metric, standard PM methodology suggests..."

Context:
{context}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{question}")
])

class ChatRequest(BaseModel):
    query: str

class SourceMetadata(BaseModel):
    guest: str
    title: str
    source: str
    content_snippet: str

class ChatResponse(BaseModel):
    reply: str
    sources: list[SourceMetadata]

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    try:
        # Retrieve relevant chunks
        docs = retriever.invoke(request.query)
        
        # Format context and sources
        formatted_context = ""
        sources = []
        seen_combinations = set()
        
        for i, doc in enumerate(docs):
            guest = doc.metadata.get("guest", "Unknown")
            title = doc.metadata.get("title", "Unknown Title")
            source_file = doc.metadata.get("source", "Unknown file")
            
            # Add to context
            formatted_context += f"\n--- Source {i+1} (Guest: {guest}, Episode: {title}) ---\n{doc.page_content}\n"
            
            # Format unique sources for response metadata
            combo = f"{guest}-{title}"
            if combo not in seen_combinations:
                seen_combinations.add(combo)
                sources.append(
                    SourceMetadata(
                        guest=guest,
                        title=title,
                        source=source_file,
                        content_snippet=doc.page_content[:150] + "..."
                    )
                )
        
        # Format prompt and invoke LLM
        chain = prompt | llm
        response = chain.invoke({
            "context": formatted_context,
            "question": request.query
        })
        
        return ChatResponse(
            reply=response.content,
            sources=sources
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
