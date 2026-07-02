import os
import pickle
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Vector Analogy Sandbox API",
    description="Backend engine for calculating high-dimensional word vector algebra."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VECTORS = None
WORDS = []
WORD_TO_IDX = {}


def get_nearest_neighbors(target_vector: np.ndarray, k: int = 50):
    global VECTORS, WORDS

    target_vector = np.array(target_vector, dtype=np.float32)

    dot_products = np.dot(VECTORS, target_vector)

    matrix_norms = np.linalg.norm(VECTORS, axis=1)
    target_norm = np.linalg.norm(target_vector)

    if target_norm == 0:
        return []

    cosine_similarities = dot_products / (matrix_norms * target_norm)

    top_indices = np.argsort(cosine_similarities)[::-1][:k]

    results = []
    for idx in top_indices:
        results.append({
            "word": WORDS[idx],
            "similarity": float(cosine_similarities[idx])
        })

    return results


@app.on_event("startup")
def load_vector_space():
    global VECTORS, WORDS, WORD_TO_IDX

    vectors_path = "../data/vectors.npy"
    metadata_path = "../data/metadata.pkl"

    print("Loading vector space into memory...")

    if not os.path.exists(vectors_path) or not os.path.exists(metadata_path):
        raise RuntimeError(
            "Missing preprocessed files! Run preprocess.py first.")

    VECTORS = np.load(vectors_path)

    with open(metadata_path, "rb") as f:
        metadata = pickle.load(f)
        WORDS = metadata["words"]
        WORD_TO_IDX = metadata["word_to_idx"]

    print(f"Vector space loaded successfully. Shape: {VECTORS.shape}")


@app.get("/")
def read_root():
    return {"status": "online", "vocab_size": len(WORDS), "dimensions": VECTORS.shape[1] if VECTORS is not None else 0}


@app.get("/vector/{word}")
def get_word_vector(word: str):
    clean_word = word.lower().strip()

    if clean_word not in WORD_TO_IDX:
        raise HTTPException(
            status_code=404, detail=f"Word '{word}' not found in vocabulary sandbox.")

    idx = WORD_TO_IDX[clean_word]
    vector = VECTORS[idx]

    return {
        "word": clean_word,
        "index": idx,
        "vector": vector.tolist()
    }


@app.get("/neighbors/{word}")
def find_word_neighbors(word: str, k: int = 25):
    clean_word = word.lower().strip()

    if clean_word not in WORD_TO_IDX:
        raise HTTPException(
            status_code=404, detail=f"Word '{word}' not found.")

    word_idx = WORD_TO_IDX[clean_word]
    word_vector = VECTORS[word_idx]

    neighbors = get_nearest_neighbors(word_vector, k=k)

    return {
        "query_word": clean_word,
        "neighbors": neighbors
    }
