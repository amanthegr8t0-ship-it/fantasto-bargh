import requests
import faiss
import numpy as np
from core.config import NVIDIA_API_KEY

def embedding(text_chunk, type="passage"):
    response = requests.post(
        "https://integrate.api.nvidia.com/v1/embeddings",
        headers={"Authorization": f"Bearer {NVIDIA_API_KEY}"},
        json={
            "input": [text_chunk],
            "model": "nvidia/nv-embedqa-e5-v5",
            "input_type": type
        })
    result = response.json()["data"][0]["embedding"]
    return result

def store_embedded(chunks):
    vectors = []
    for chunk in chunks:
        vectors.append(embedding(chunk))

    dimension = len(vectors[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(vectors, dtype=np.float32))
    return index, chunks

def fetch_embedded(f_index, original_chunk, search_embedded):
    llm_sending = []

    embedded_query = embedding(search_embedded, type="query")
    query_vector = np.array([embedded_query], dtype=np.float32)
    distances, indices = f_index.search(query_vector, k=3)
    for index in indices[0]:
        llm_sending.append(original_chunk[index])
    
    return llm_sending