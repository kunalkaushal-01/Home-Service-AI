# # utils/faiss_utils.py
# import os
# import faiss
# import numpy as np
# import joblib
# from typing import List, Dict, Any, Tuple,Optional
# from sentence_transformers import SentenceTransformer

# BASE_DIR = os.path.join(os.getcwd(), "vectors")
# os.makedirs(BASE_DIR, exist_ok=True)

# # one embedding model singleton (all categories reuse)
# _EMBED_MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# _DIM = _EMBED_MODEL.get_sentence_embedding_dimension()

# def _index_dir(category: str) -> str:
#     d = os.path.join(BASE_DIR, category)
#     os.makedirs(d, exist_ok=True)
#     return d

# def _index_path(category: str) -> Tuple[str,str]:
#     d = _index_dir(category)
#     return os.path.join(d, "index.faiss"), os.path.join(d, "meta.joblib")

# def _load_index(category: str):
#     idx_path, meta_path = _index_path(category)
#     if os.path.exists(idx_path) and os.path.exists(meta_path):
#         index = faiss.read_index(idx_path)
#         meta = joblib.load(meta_path)
#         print(meta,'meta')
#         return index, meta
#     # if not exists, create empty index + metadata
#     index = faiss.IndexFlatIP(_DIM)  # inner product after normalization
#     meta = {"texts": [], "metadatas": []}
#     return index, meta

# def _save_index(category: str, index, meta):
#     idx_path, meta_path = _index_path(category)
#     faiss.write_index(index, idx_path)
#     joblib.dump(meta, meta_path)

# def _embed(texts: List[str]) -> np.ndarray:
#     embs = _EMBED_MODEL.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
#     # ensure shape (n, dim)
#     return np.array(embs, dtype="float32")

# def add_texts(category: str, texts: List[str], metadatas: List[Dict[str, Any]]):
#     """
#     Add texts + metadatas into the category index (appends).
#     """
#     if not texts:
#         return 0
#     index, meta = _load_index(category)
#     vecs = _embed(texts)
#     # If index currently empty, need to reinitialize the IndexFlatIP with correct dim
#     # IndexFlatIP supports adding vectors directly
#     index.add(vecs)  # add vectors
#     meta["texts"].extend(texts)
#     meta["metadatas"].extend(metadatas)
#     _save_index(category, index, meta)
#     return len(texts)

# def search(category: str, query: str, k: int = 3) -> List[Dict]:
#     """
#     Return list of hits: {text, metadata, score}
#     """
#     index, meta = _load_index(category)
#     if len(meta["texts"]) == 0:
#         return []
#     qv = _embed([query])
#     D, I = index.search(qv, k)
#     hits = []
#     for score, idx in zip(D[0], I[0]):
#         if idx < 0:
#             continue
#         hits.append({
#             "text": meta["texts"][int(idx)],
#             "metadata": meta["metadatas"][int(idx)],
#             "score": float(score)
#         })
#     return hits


# def clear_index(category: str):
#     idx_path, meta_path = _index_path(category)
#     try:
#         if os.path.exists(idx_path):
#             os.remove(idx_path)
#         if os.path.exists(meta_path):
#             os.remove(meta_path)
#     except Exception:
#         pass



# utils/faiss_utils.py
import os
import joblib
from typing import List, Dict, Any
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from utils.embeddings import SBERTEmbeddings

BASE_DIR = os.path.join(os.getcwd(), "vectors")
os.makedirs(BASE_DIR, exist_ok=True)

# Shared embeddings
embeddings = SBERTEmbeddings()

def _index_dir(category: str) -> str:
    d = os.path.join(BASE_DIR, category)
    os.makedirs(d, exist_ok=True)
    return d

def _index_path(category: str):
    d = _index_dir(category)
    return os.path.join(d, "index"), os.path.join(d, "meta.joblib")

def _save_index(category: str, faiss_store: FAISS, meta: Dict):
    idx_path, meta_path = _index_path(category)
    faiss_store.save_local(idx_path)
    joblib.dump(meta, meta_path)

def _load_index(category: str):
    idx_path, meta_path = _index_path(category)
    if os.path.exists(meta_path) and os.path.isdir(idx_path):
        meta = joblib.load(meta_path)
        faiss_store = FAISS.load_local(idx_path, embeddings, allow_dangerous_deserialization=True)
        return faiss_store, meta
    return None, {"texts": [], "metadatas": []}

def add_texts(category: str, texts: List[str], metadatas: List[Dict[str, Any]]):
    """
    Add texts + metadata into LangChain FAISS index.
    """
    docs = [Document(page_content=t, metadata=m) for t, m in zip(texts, metadatas)]
    faiss_store, meta = _load_index(category)

    if faiss_store is None:
        faiss_store = FAISS.from_documents(docs, embeddings)
    else:
        faiss_store.add_documents(docs)

    meta["texts"].extend(texts)
    meta["metadatas"].extend(metadatas)

    _save_index(category, faiss_store, meta)
    return len(texts)

def search(category: str, query: str, k: int = 3, filters: Dict[str, Any] = None):
    """
    LangChain similarity search with optional metadata filters.
    """
    faiss_store, meta = _load_index(category)
    if faiss_store is None or len(meta["texts"]) == 0:
        return []

    results = faiss_store.similarity_search(query, k=k, filter=filters)
    return [
        {"text": r.page_content, "metadata": r.metadata}
        for r in results
    ]

def clear_index(category: str):
    idx_path, meta_path = _index_path(category)
    try:
        if os.path.isdir(idx_path):
            import shutil
            shutil.rmtree(idx_path)
        if os.path.exists(meta_path):
            os.remove(meta_path)
    except Exception:
        pass




