import os
import pickle
import numpy as np

RAW_GLOVE_PATH = "data/glove.840B.300d.txt"
OUTPUT_VECTORS_PATH = "data/vectors.npy"
OUTPUT_METADATA_PATH = "data/metadata.pkl"

VOCAB_SIZE = 200000
VECTOR_DIM = 300


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
        count = 0
        for idx, line in enumerate(f):
            if idx >= VOCAB_SIZE:
                break

            parts = line.rstrip().split(' ')
            if len(parts) < VECTOR_DIM + 1:
                continue

            vector_parts = parts[-VECTOR_DIM:]
            word_parts = parts[:-VECTOR_DIM]
            raw_word = " ".join(word_parts).strip()

            word = raw_word.lower()

            if not word or word in word_to_idx:
                continue

            try:
                vector = np.array(vector_parts, dtype=np.float32)
                if vector.shape[0] != VECTOR_DIM:
                    continue

                words.append(word)
                vectors.append(vector)
                word_to_idx[word] = count
                count += 1

                if count % 20000 == 0:
                    print(
                        f"Successfully processed {count}/{VOCAB_SIZE} unique tokens...")

            except ValueError:
                continue

    vectors_matrix = np.array(vectors, dtype=np.float32)
    print(
        f"Saving {vectors_matrix.shape[0]} optimized binary files to /data...")

    np.save(OUTPUT_VECTORS_PATH, vectors_matrix)

    metadata = {"words": words, "word_to_idx": word_to_idx}
    with open(OUTPUT_METADATA_PATH, 'wb') as f:
        pickle.dump(metadata, f)

    print("Preprocessing complete.")


if __name__ == "__main__":
    preprocess_glove()
