import os
import json
import hashlib
import glob
from datetime import datetime, timezone
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.rag import rag_service
from backend.config import settings

RAW_DIR = os.path.join(settings.BASE_DIR, "rag", "raw")
MANIFEST_PATH = os.path.join(settings.BASE_DIR, "rag", "manifest.json")

def compute_file_hash(filepath: str) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def ingest_corpus():
    print(f"Starting corpus ingestion from {RAW_DIR}...")
    
    raw_files = glob.glob(os.path.join(RAW_DIR, "*.jsonl"))
    
    total_chunks = 0
    file_hashes = {}
    
    for filepath in raw_files:
        filename = os.path.basename(filepath)
        file_hashes[filename] = compute_file_hash(filepath)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_idx, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                    source_id = chunk.pop("source_id")
                    text = chunk.pop("text")
                    
                    rag_service.ingest_chunk(source_id=source_id, text=text, metadata=chunk)
                    total_chunks += 1
                except Exception as e:
                    print(f"Error parsing {filename} line {line_idx+1}: {e}")
                    
    print(f"Ingested {total_chunks} chunks into Supabase pgvector.")

    manifest = {
        "build_timestamp": datetime.now(timezone.utc).isoformat(),
        "corpus_version": "1.0",
        "total_chunks": total_chunks,
        "embedding_model": "BAAI/bge-m3",
        "database": "supabase_pgvector",
        "source_files": file_hashes
    }
    
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Manifest written to {MANIFEST_PATH}.")

if __name__ == "__main__":
    ingest_corpus()
