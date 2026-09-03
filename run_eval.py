import os
import json
import time
import re
import numpy as np
from typing import List, Dict, Any

from src.ingest import load_docs, Document
from src.chunkers import StructureAwareChunker, Chunk
from src.retriever import Retriever
from src.generator import RAGGenerator

def run_evaluation():
    print("=== Week 4 Practical — Task Set E Evaluation Engine ===")
    
    # 1. Load Corpus
    docs_dir = os.path.join(os.path.dirname(__file__), "data", "docs")
    documents = load_docs(docs_dir)
    print(f"Loaded {len(documents)} documents across SDK versions.")

    chunker = StructureAwareChunker()
    chunks: List[Chunk] = []
    for doc in documents:
        chunks.extend(chunker.chunk_document(doc))
    print(f"Total Structure-Aware Chunks: {len(chunks)}")

    # 2. Load Golden Set
    golden_set_path = os.path.join(os.path.dirname(__file__), "golden_set.jsonl")
    golden_set = []
    with open(golden_set_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                golden_set.append(json.loads(line.strip()))
    print(f"Loaded {len(golden_set)} golden set questions.")

    # 3. Instantiate Retrievers
    dense_retriever = Retriever(chunks, mode="dense")
    hybrid_retriever = Retriever(chunks, mode="hybrid")
    generator = RAGGenerator()

    # 4. Measure Baseline Dense Retriever Performance (Hit-Rate@3 & Latency)
    print("\n--- Running Baseline Dense Retriever Evaluation ---")
    dense_hits = 0
    dense_latencies = []
    dense_inspection = []

    for q in golden_set:
        qid = q["question_id"]
        query = q["query"]
        target_chunk_id = q["known_correct_chunk_id"]

        # Latency benchmark (100 iterations per query)
        t_start = time.perf_counter()
        res_3 = dense_retriever.search_dense(query, top_k=3)
        t_elapsed = (time.perf_counter() - t_start) * 1000.0  # ms
        
        # Warmup benchmark runs for p50 latency
        lat_samples = []
        for _ in range(50):
            t0 = time.perf_counter()
            _ = dense_retriever.search_dense(query, top_k=3)
            lat_samples.append((time.perf_counter() - t0) * 1000.0)
        p50_query_lat = np.median(lat_samples)
        dense_latencies.append(p50_query_lat)

        retrieved_chunk_ids = [r["chunk_id"] for r in res_3]
        
        if target_chunk_id is None:
            # Out of corpus question: hit is achieved if generator correctly refuses or context doesn't contain target
            hit = False # Out-of-corpus is a miss for retrieval of target chunk
            label = "Not-In-Corpus"
            evidence = f"Question asks for out-of-corpus data not documented in v2/v3 SDK specs; top retrieved chunk '{retrieved_chunk_ids[0]}' has no answer."
        else:
            hit = target_chunk_id in retrieved_chunk_ids
            if hit:
                label = "HIT"
                evidence = f"Known target chunk '{target_chunk_id}' retrieved at rank {retrieved_chunk_ids.index(target_chunk_id) + 1}."
                dense_hits += 1
            else:
                label = "R"  # Retrieval fetched bad context (target chunk not in top-3)
                top_1_id = retrieved_chunk_ids[0] if retrieved_chunk_ids else "None"
                evidence = f"Top-3 retrieved semantic guides ({', '.join(retrieved_chunk_ids)}) missed exact token target '{target_chunk_id}'."

        dense_inspection.append({
            "question_id": qid,
            "query": query,
            "category": q["category"],
            "target_chunk_id": target_chunk_id,
            "hit": hit,
            "top_3_ids": retrieved_chunk_ids,
            "label": label,
            "evidence": evidence,
            "p50_latency_ms": p50_query_lat
        })

    baseline_hit_rate = (dense_hits / len(golden_set)) * 100.0
    baseline_p50_lat = np.median(dense_latencies)

    print(f"Baseline Dense Retriever Hit-Rate@3: {dense_hits}/12 ({baseline_hit_rate:.1f}%)")
    print(f"Baseline Dense Retriever p50 Latency: {baseline_p50_lat:.3f} ms")

    # 5. Measure Single Change: Hybrid RRF Retriever Performance
    print("\n--- Running Single Change (Hybrid RRF, k=60) Evaluation ---")
    hybrid_hits = 0
    hybrid_latencies = []
    hybrid_inspection = []

    for q in golden_set:
        qid = q["question_id"]
        query = q["query"]
        target_chunk_id = q["known_correct_chunk_id"]

        # Latency benchmark (50 iterations per query)
        lat_samples = []
        for _ in range(50):
            t0 = time.perf_counter()
            _ = hybrid_retriever.search_hybrid(query, top_k=3, rrf_k=60, candidate_k=25)
            lat_samples.append((time.perf_counter() - t0) * 1000.0)
        p50_query_lat = np.median(lat_samples)
        hybrid_latencies.append(p50_query_lat)

        res_3 = hybrid_retriever.search_hybrid(query, top_k=3, rrf_k=60, candidate_k=25)
        retrieved_chunk_ids = [r["chunk_id"] for r in res_3]

        if target_chunk_id is None:
            hit = False
            label = "Not-In-Corpus"
            evidence = f"Out-of-corpus query correctly returned no matching target chunk in top-3 ({', '.join(retrieved_chunk_ids)})."
        else:
            hit = target_chunk_id in retrieved_chunk_ids
            if hit:
                label = "HIT"
                evidence = f"Hybrid RRF retrieved exact target '{target_chunk_id}' at rank {retrieved_chunk_ids.index(target_chunk_id) + 1}."
                hybrid_hits += 1
            else:
                label = "R"
                evidence = f"Target chunk '{target_chunk_id}' not in top-3 ({', '.join(retrieved_chunk_ids)})."

        hybrid_inspection.append({
            "question_id": qid,
            "query": query,
            "target_chunk_id": target_chunk_id,
            "hit": hit,
            "top_3_ids": retrieved_chunk_ids,
            "label": label,
            "evidence": evidence,
            "p50_latency_ms": p50_query_lat
        })

    hybrid_hit_rate = (hybrid_hits / len(golden_set)) * 100.0
    hybrid_p50_lat = np.median(hybrid_latencies)

    print(f"Hybrid RRF Retriever Hit-Rate@3: {hybrid_hits}/12 ({hybrid_hit_rate:.1f}%)")
    print(f"Hybrid RRF Retriever p50 Latency: {hybrid_p50_lat:.3f} ms")

    # 6. Measure Bonus Challenge: MMR Diversification
    print("\n--- Running Bonus Challenge (MMR Diversification, lambda=0.7) Evaluation ---")
    mmr_hits = 0
    mmr_unique_sources = []
    
    for q in golden_set:
        query = q["query"]
        target_chunk_id = q["known_correct_chunk_id"]
        res_3 = hybrid_retriever.search_mmr(query, top_k=3, lmbda=0.7, candidate_k=15)
        retrieved_chunk_ids = [r["chunk_id"] for r in res_3]
        retrieved_sources = set([r["source_file"] for r in res_3])
        mmr_unique_sources.append(len(retrieved_sources))

        if target_chunk_id and target_chunk_id in retrieved_chunk_ids:
            mmr_hits += 1

    mmr_hit_rate = (mmr_hits / len(golden_set)) * 100.0
    avg_diversity = np.mean(mmr_unique_sources)

    print(f"MMR (lambda=0.7) Hit-Rate@3: {mmr_hits}/12 ({mmr_hit_rate:.1f}%)")
    print(f"MMR Average Unique Files in Top-3: {avg_diversity:.2f} / 3")

    # 7. Print Comprehensive Summary Output
    print("\n" + "="*80)
    print("SUMMARY COMPARISON TABLE")
    print("="*80)
    print(f"{'QID':<4} | {'Query Snippet':<35} | {'Baseline (Dense)':<16} | {'Single Change (Hybrid RRF)':<24} | {'Status':<12}")
    print("-" * 100)

    for i in range(len(golden_set)):
        d_item = dense_inspection[i]
        h_item = hybrid_inspection[i]
        q_snip = d_item["query"][:33] + ".." if len(d_item["query"]) > 35 else d_item["query"]
        d_status = "HIT (Rank " + str(d_item["top_3_ids"].index(d_item["target_chunk_id"])+1) + ")" if d_item["hit"] else f"MISS ({d_item['label']})"
        h_status = "HIT (Rank " + str(h_item["top_3_ids"].index(h_item["target_chunk_id"])+1) + ")" if h_item["hit"] else f"MISS ({h_item['label']})"

        if not d_item["hit"] and h_item["hit"]:
            change_status = "FIXED"
        elif d_item["hit"] and h_item["hit"]:
            change_status = "PRESERVED"
        elif not d_item["hit"] and not h_item["hit"]:
            if d_item["label"] == "Not-In-Corpus":
                change_status = "NOT IN CORPUS"
            else:
                change_status = "UNFIXED"
        else:
            change_status = "REGRESSED"

        print(f"{d_item['question_id']:<4} | {q_snip:<35} | {d_status:<16} | {h_status:<24} | {change_status:<12}")

    print("-" * 100)
    print(f"Baseline Hit-Rate@3: {baseline_hit_rate:.1f}% ({dense_hits}/12) | p50 Latency: {baseline_p50_lat:.3f} ms")
    print(f"Hybrid RRF Hit-Rate@3: {hybrid_hit_rate:.1f}% ({hybrid_hits}/12) | p50 Latency: {hybrid_p50_lat:.3f} ms")
    print("="*80)

    return {
        "golden_set": golden_set,
        "dense_inspection": dense_inspection,
        "hybrid_inspection": hybrid_inspection,
        "baseline_hit_rate": baseline_hit_rate,
        "baseline_p50_lat": baseline_p50_lat,
        "hybrid_hit_rate": hybrid_hit_rate,
        "hybrid_p50_lat": hybrid_p50_lat,
        "mmr_hit_rate": mmr_hit_rate,
        "avg_diversity": avg_diversity
    }

if __name__ == "__main__":
    run_evaluation()
