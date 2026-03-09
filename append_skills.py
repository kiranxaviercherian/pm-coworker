import os
import glob
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import LanceDB
from langchain_huggingface import HuggingFaceEmbeddings
import lancedb

SKILLS_DIR = r"C:\Users\kiran\.gemini\antigravity\scratch\pm-coworker\lenny-skills\skills"
LANCEDB_PATH = r"C:\Users\kiran\.gemini\antigravity\scratch\pm-coworker\lancedb_data"
TABLE_NAME = "lenny_brain"

def main():
    if not os.path.exists(SKILLS_DIR):
        print(f"Skills directory not found: {SKILLS_DIR}")
        return

    md_files = glob.glob(os.path.join(SKILLS_DIR, "**", "*.md"), recursive=True)
    if not md_files:
        print(f"No markdown files found recursively in {SKILLS_DIR}")
        return

    print(f"Found {len(md_files)} skill transcripts. Processing...")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )

    all_chunks = []
    all_metadatas = []

    for filepath in md_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        filename = os.path.basename(filepath)
        title = os.path.splitext(filename)[0] # remove .md extension
        
        doc_metadata = {
            "source": filename,
            "guest": "RefoundAI Skills", # hardcoded guest
            "title": title
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
    
    # We assume the table already exists from the previous ingestion.
    # We will use LanceDB from_texts or init it and call add_texts
    try:
        print(f"Appending chunks to LanceDB (Table: {TABLE_NAME})...")
        vectorstore = LanceDB(
            connection=db,
            embedding=embeddings,
            table_name=TABLE_NAME
        )
        
        # Add to existing table
        vectorstore.add_texts(texts=all_chunks, metadatas=all_metadatas)
        print("Append complete!")
        
    except Exception as e:
        print(f"Error appending to LanceDB: {e}")

if __name__ == "__main__":
    main()
