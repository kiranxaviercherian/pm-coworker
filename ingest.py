import os
import glob
import yaml
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import LanceDB
from langchain_huggingface import HuggingFaceEmbeddings
import lancedb
from typing import List, Dict, Any, Optional

TRANSCRIPT_DIR = r"C:\Users\kiran\.gemini\antigravity\scratch\pm-coworker\lennys-podcast-transcripts"
LANCEDB_PATH = r"C:\Users\kiran\.gemini\antigravity\scratch\pm-coworker\lancedb_data"
TABLE_NAME = "lenny_brain"

def extract_frontmatter_and_content(filepath):
    """Reads a markdown file and extracts YAML frontmatter and the main content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Simple parsing to find frontmatter bounded by ---
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter_str = parts[1]
            main_content = parts[2].strip()
            try:
                metadata = yaml.safe_load(frontmatter_str)
                return metadata, main_content
            except yaml.YAMLError as e:
                print(f"Error parsing YAML in {filepath}: {e}")
                return {}, main_content
    
    return {}, content

def main():
    if not os.path.exists(TRANSCRIPT_DIR):
        print(f"Transcript directory not found: {TRANSCRIPT_DIR}")
        return

    md_files = glob.glob(os.path.join(TRANSCRIPT_DIR, "**", "*.md"), recursive=True)
    # Filter out README, CLAUDE, etc.
    md_files = [f for f in md_files if os.path.basename(f) not in ["README.md", "CLAUDE.md"]]
    
    if not md_files:
        print(f"No markdown files found in {TRANSCRIPT_DIR}")
        return

    print(f"Found {len(md_files)} transcripts. Processing...")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )

    all_chunks: List[str] = []
    all_metadatas: List[Dict[str, Any]] = []

    for filepath in md_files:
        metadata, content = extract_frontmatter_and_content(filepath)
        
        # We want to keep 'guest' and 'title' if available
        doc_metadata = {
            "source": os.path.basename(filepath),
            "guest": metadata.get("guest", "Unknown"),
            "title": metadata.get("title", "Unknown Title")
        }

        # Chunk the content
        chunks = text_splitter.split_text(content)
        
        all_chunks.extend(chunks)
        all_metadatas.extend([doc_metadata] * len(chunks))

    print(f"Created {len(all_chunks)} chunks from {len(md_files)} files.")

    print("Initializing embedding model (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print(f"Connecting to LanceDB at {LANCEDB_PATH}...")
    db = lancedb.connect(LANCEDB_PATH)
    
    print(f"Storing {len(all_chunks)} chunks into LanceDB (Table: {TABLE_NAME}) in batches...")
    
    # Initialize VectorStore with first batch to create table
    batch_size = 500
    vectorstore: Optional[LanceDB] = None
    
    for i in range(0, len(all_chunks), batch_size):
        chunk_batch = all_chunks[i:i + batch_size]
        meta_batch = all_metadatas[i:i + batch_size]
        
        print(f"Processing batch {i // batch_size + 1}...")
        
        if vectorstore is None:
            # Create the table on first batch
            vectorstore = LanceDB.from_texts(
                texts=chunk_batch,
                embedding=embeddings,
                metadatas=meta_batch,
                connection=db,
                table_name=TABLE_NAME
            )
        else:
            # Add to existing table
            vectorstore.add_texts(texts=chunk_batch, metadatas=meta_batch)

    print(f"Successfully processed {len(all_chunks)} chunks.")
    print("Ingestion complete!")

if __name__ == "__main__":
    main()
