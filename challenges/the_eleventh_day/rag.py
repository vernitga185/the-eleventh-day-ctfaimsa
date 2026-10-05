import json
import os
import string

STOP_WORDS = {"is", "the", "a", "an", "what", "this", "of", "and", "to", "in", "for", "with", "on", "are", "do", "how", "who", "why", "can", "i", "make", "made"}

class RAGService:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        lore_path = os.path.join(current_dir, "data", "drona_11_lore.jsonl")
        self.corpus = []
        if os.path.exists(lore_path):
            with open(lore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.corpus.append(json.loads(line))

    def search(self, query: str, top_k: int = 6) -> list:
        query_lower = query.lower()
        scored = []
        query_clean = query_lower.translate(str.maketrans("", "", string.punctuation))
        query_words = set(w for w in query_clean.split() if w not in STOP_WORDS)
        for doc in self.corpus:
            # Skip procedural rules intended for Satyajit
            if doc.get("episode") == "RULES":
                continue
            text_clean = doc["text"].lower().translate(str.maketrans("", "", string.punctuation))
            text_words = set(w for w in text_clean.split() if w not in STOP_WORDS)
            score = len(query_words.intersection(text_words))
            scored.append((score, doc))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        if scored and scored[0][0] > 0:
            return [doc for score, doc in scored[:top_k]]
            
        return []

    def get_source(self, source_id: str) -> dict:
        for doc in self.corpus:
            if doc.get("source_id") == source_id:
                return doc
        return {"error": "Source not found."}

rag_service = RAGService()
