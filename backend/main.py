from pydantic import BaseModel
import re
import os
import pickle
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sklearn.decomposition import PCA

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


class EquationRequest(BaseModel):
    equation: str
    k: int = 25


@app.post("/api/analogy")
def calculate_analogy(payload: EquationRequest):
    global VECTORS, WORD_TO_IDX, WORDS

    raw_equation = payload.equation
    k = payload.k

    tokens = re.findall(r'[\w]+|[\+\-]', raw_equation.lower().strip())
    if not tokens:
        raise HTTPException(
            status_code=400, detail="Empty equation string provided.")

    input_words = [t for t in tokens if t not in ['+', '-']]
    unique_input_words = list(set(input_words))

    for word in unique_input_words:
        if word not in WORD_TO_IDX:
            raise HTTPException(
                status_code=404, detail=f"Word '{word}' is out of vocabulary.")

    result_vector = np.zeros(VECTORS.shape[1], dtype=np.float32)
    current_operator = '+'

    for token in tokens:
        if token in ['+', '-']:
            current_operator = token
        else:
            word_idx = WORD_TO_IDX[token]
            word_vec = VECTORS[word_idx]
            if current_operator == '+':
                result_vector += word_vec
            elif current_operator == '-':
                result_vector -= word_vec

    raw_neighbors = get_nearest_neighbors(
        result_vector, k=k + len(unique_input_words))
    filtered_neighbors = [
        n for n in raw_neighbors if n["word"] not in unique_input_words
    ][:k]

    cluster_payload = []

    for word in unique_input_words:
        idx = WORD_TO_IDX[word]
        cluster_payload.append({
            "word": word,
            "vector": VECTORS[idx],
            "type": "input"
        })

    for neighbor in filtered_neighbors:
        word = neighbor["word"]
        idx = WORD_TO_IDX[word]
        cluster_payload.append({
            "word": word,
            "vector": VECTORS[idx],
            "type": "neighbor"
        })

    cluster_payload.append({
        "word": "[RESULT_COORDINATE]",
        "vector": result_vector,
        "type": "math_point"
    })

    high_dim_vectors = [item["vector"] for item in cluster_payload]

    pca = PCA(n_components=3)
    reduced_coordinates = pca.fit_transform(high_dim_vectors)

    for i, item in enumerate(cluster_payload):
        item["x"] = float(reduced_coordinates[i][0])
        item["y"] = float(reduced_coordinates[i][1])
        item["z"] = float(reduced_coordinates[i][2])

        del item["vector"]

    return {
        "equation": raw_equation,
        "cluster_size": len(cluster_payload),
        "cluster": cluster_payload
    }
