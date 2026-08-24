import math
import re
from typing import List, Dict, Any, Optional
# pyrefly: ignore [missing-import]
from rank_bm25 import BM25Okapi
from src.chunkers import Chunk

def tokenize(text: str) -> List[str]:
    # Lowercase and extract alphanumeric terms & underscores
    return re.findall(r"\b[a-zA-Z0-9_]+\b", text.lower())

class Retriever:
    def __init__(self, chunks: List[Chunk]):
        self.chunks = chunks
        self.corpus_tokens = [tokenize(c.content) for c in chunks]
        self.bm25 = BM25Okapi(self.corpus_tokens)

    def search(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        bm25_scores = self.bm25.get_scores(query_tokens)
        
        results = []
        for i, chunk in enumerate(self.chunks):
            # Apply metadata filters if specified
            if filters:
                match = True
                for k, v in filters.items():
                    if chunk.metadata.get(k) != v:
                        match = False
                        break
                if not match:
                    continue

            score = float(bm25_scores[i])
            results.append({
                "chunk": chunk,
                "score": round(score, 4),
                "chunk_id": chunk.chunk_id,
                "source_file": chunk.metadata["source_file"],
                "page_id": chunk.metadata["page_id"],
                "sdk_version": chunk.metadata["sdk_version"],
                "content": chunk.content
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
