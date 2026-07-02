import os
import pickle
import numpy as np

RAW_GLOVE_PATH = "../data/glove.6B.100d.txt"
OUTPUT_VECTORS_PATH = "../data/vectors.npy"
OUTPUT_METADATA_PATH = "../data/metadata.pkl"

VOCAB_SIZE = 50000
VECTOR_DIM = 100


def preprocess_glove():
    print(f"Starting preprocessing of {RAW_GLOVE_PATH}...")

    if not os.path.exists(RAW_GLOVE_PATH):
        print(
            f"Error: Could not find {RAW_GLOVE_PATH}. Did you download it to the right folder?")
        return

    words = []
    vectors = []
    word_to_idx = {}

    with open(RAW_GLOVE_PATH, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            if idx >= VOCAB_SIZE:
                break

            parts = line.strip().split(' ')
            word = parts[0]

            try:
                vector = [float(x) for x in parts[1:]]
            except ValueError:
                continue

            words.append(word)
            vectors.append(vector)
            word_to_idx[word] = idx

            if (idx + 1) % 10000 == 0:
                print(f"Parsed {idx + 1}/{VOCAB_SIZE} words...")

    vectors_matrix = np.array(vectors, dtype=np.float32)

    print("Saving optimized binary files to /data...")

    np.save(OUTPUT_VECTORS_PATH, vectors_matrix)

    metadata = {
        "words": words,
        "word_to_idx": word_to_idx
    }
    with open(OUTPUT_METADATA_PATH, 'wb') as f:
        pickle.dump(metadata, f)

    print("Preprocessing complete.")


if __name__ == "__main__":
    preprocess_glove()
