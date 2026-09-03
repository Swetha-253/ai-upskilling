import math
import re
import numpy as np
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

from src.chunkers import Chunk

def tokenize(text: str) -> List[str]:
    return re.findall(r"\b[a-zA-Z0-9_]+\b", text.lower())

class Retriever:
    """
    Retriever engine supporting:
    1. Baseline Dense Retrieval (Embedding/Vector Cosine Similarity)
    2. BM25 Lexical Retrieval
    3. Hybrid RRF (Reciprocal Rank Fusion with k=60)
    4. MMR (Maximal Marginal Relevance) Diversification
    """
    def __init__(self, chunks: List[Chunk], mode: str = "hybrid"):
        self.chunks = chunks
        self.mode = mode  # "dense", "bm25", or "hybrid"
        
        # 1. Lexical BM25 Setup
        self.corpus_tokens = [tokenize(c.content) for c in chunks]
        self.bm25 = BM25Okapi(self.corpus_tokens)

        # 2. Dense Embedding Setup (TF-IDF + TruncatedSVD Dense Vector Space)
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        corpus_texts = [c.content for c in chunks]
        X = self.vectorizer.fit_transform(corpus_texts)
        
        n_comp = min(20, max(2, X.shape[1] - 1))
        self.svd = TruncatedSVD(n_components=n_comp, random_state=42)
        dense_vecs = self.svd.fit_transform(X)
        
        # L2 Normalize dense vectors
        norms = np.linalg.norm(dense_vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.dense_embeddings = dense_vecs / norms

    def _get_dense_scores(self, query: str) -> np.ndarray:
        q_vec = self.vectorizer.transform([query])
        q_dense = self.svd.transform(q_vec)
        q_norm = np.linalg.norm(q_dense)
        if q_norm > 0:
            q_dense = q_dense / q_norm
        return np.dot(self.dense_embeddings, q_dense.T).flatten()

    def _get_bm25_scores(self, query: str) -> np.ndarray:
        query_tokens = tokenize(query)
        if not query_tokens:
            return np.zeros(len(self.chunks))
        return np.array(self.bm25.get_scores(query_tokens))

    def search_dense(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        scores = self._get_dense_scores(query)
        return self._format_results(scores, top_k=top_k, filters=filters)

    def search_bm25(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        scores = self._get_bm25_scores(query)
        return self._format_results(scores, top_k=top_k, filters=filters)

    def search_hybrid(self, query: str, top_k: int = 5, rrf_k: int = 60, candidate_k: int = 25, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Hybrid Retrieval via Reciprocal Rank Fusion (RRF, k=60).
        Fuses ranks from Dense Search and BM25 Search.
        """
        # Filter chunks if metadata filter is provided
        eligible_indices = list(range(len(self.chunks)))
        if filters:
            eligible_indices = [
                i for i, c in enumerate(self.chunks)
                if all(c.metadata.get(k) == v for k, v in filters.items())
            ]

        if not eligible_indices:
            return []

        # Get scores over all chunks
        dense_scores = self._get_dense_scores(query)
        bm25_scores = self._get_bm25_scores(query)

        # Rank eligible indices for dense
        dense_ranked = sorted(eligible_indices, key=lambda i: dense_scores[i], reverse=True)[:candidate_k]
        dense_ranks = {idx: rank + 1 for rank, idx in enumerate(dense_ranked)}

        # Rank eligible indices for BM25
        bm25_ranked = sorted(eligible_indices, key=lambda i: bm25_scores[i], reverse=True)[:candidate_k]
        bm25_ranks = {idx: rank + 1 for rank, idx in enumerate(bm25_ranked)}

        # RRF Fusion
        candidate_indices = set(dense_ranks.keys()).union(set(bm25_ranks.keys()))
        rrf_scores = {}
        for idx in candidate_indices:
            r_dense = dense_ranks.get(idx, 1000)
            r_bm25 = bm25_ranks.get(idx, 1000)
            score = (1.0 / (rrf_k + r_dense)) + (1.0 / (rrf_k + r_bm25))
            rrf_scores[idx] = score

        sorted_candidates = sorted(candidate_indices, key=lambda idx: rrf_scores[idx], reverse=True)

        results = []
        for idx in sorted_candidates[:top_k]:
            chunk = self.chunks[idx]
            results.append({
                "chunk": chunk,
                "score": round(float(rrf_scores[idx]), 6),
                "chunk_id": chunk.chunk_id,
                "source_file": chunk.metadata["source_file"],
                "page_id": chunk.metadata["page_id"],
                "sdk_version": chunk.metadata["sdk_version"],
                "content": chunk.content
            })
        return results

    def search_mmr(self, query: str, top_k: int = 3, lmbda: float = 0.7, candidate_k: int = 15, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Maximal Marginal Relevance (MMR) Diversification over Fused Candidates.
        MMR = lmbda * Relevance(c) - (1 - lmbda) * MaxSimilarity(c, selected)
        """
        fused = self.search_hybrid(query, top_k=candidate_k, filters=filters)
        if not fused:
            return []

        # Get dense vectors for similarity calculation
        fused_indices = [self.chunks.index(r["chunk"]) for r in fused]
        fused_vecs = self.dense_embeddings[fused_indices]

        selected = []
        selected_indices = []

        # Normalize score array for scale balance
        scores = np.array([r["score"] for r in fused])
        if scores.max() > scores.min():
            norm_scores = (scores - scores.min()) / (scores.max() - scores.min())
        else:
            norm_scores = np.ones_like(scores)

        unselected = list(range(len(fused)))

        while len(selected) < min(top_k, len(fused)):
            if not selected:
                # Select top candidate
                best_idx = 0
            else:
                best_mmr = -1e9
                best_idx = unselected[0]
                for idx in unselected:
                    rel = norm_scores[idx]
                    # Compute max cosine similarity to already selected candidates
                    sims = np.dot(fused_vecs[idx], fused_vecs[selected_indices].T)
                    max_sim = float(np.max(sims)) if sims.size > 0 else 0.0
                    mmr_val = lmbda * rel - (1 - lmbda) * max_sim
                    if mmr_val > best_mmr:
                        best_mmr = mmr_val
                        best_idx = idx

            selected.append(fused[best_idx])
            selected_indices.append(best_idx)
            unselected.remove(best_idx)

        return selected

    def search(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if self.mode == "dense":
            return self.search_dense(query, top_k=top_k, filters=filters)
        elif self.mode == "bm25":
            return self.search_bm25(query, top_k=top_k, filters=filters)
        elif self.mode == "hybrid":
            return self.search_hybrid(query, top_k=top_k, filters=filters)
        else:
            raise ValueError(f"Unknown retriever mode: {self.mode}")

    def _format_results(self, scores: np.ndarray, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        results = []
        for i, chunk in enumerate(self.chunks):
            if filters:
                if not all(chunk.metadata.get(k) == v for k, v in filters.items()):
                    continue
            results.append({
                "chunk": chunk,
                "score": round(float(scores[i]), 4),
                "chunk_id": chunk.chunk_id,
                "source_file": chunk.metadata["source_file"],
                "page_id": chunk.metadata["page_id"],
                "sdk_version": chunk.metadata["sdk_version"],
                "content": chunk.content
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
