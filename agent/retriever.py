import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv

load_dotenv()

from sentence_transformers import SentenceTransformer


class RunbookRetriever:
    def __init__(self, runbooks_dir: str = "data/runbooks") -> None:
        model_name = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5")
        print(f"[HuggingFace] Loading embedding model: {model_name} (cache: {os.getenv('HF_HOME')})")
        self.model = SentenceTransformer(model_name)
        self.runbooks: list[dict[str, str]] = []
        self.embeddings: np.ndarray | None = None
        self._index_runbooks(Path(runbooks_dir))

    def _index_runbooks(self, directory: Path) -> None:
        texts: list[str] = []
        for file_path in sorted(directory.glob("*.md")):
            content = file_path.read_text(encoding="utf-8")
            self.runbooks.append({"filename": file_path.name, "content": content})
            texts.append(content)

        self.embeddings = self.model.encode(texts, normalize_embeddings=True)
        print(f"[HuggingFace] Indexed {len(self.runbooks)} runbooks (shape: {self.embeddings.shape})")

    def search(self, query: str, top_k: int = 1) -> list[dict]:
        query_vec = self.model.encode([query], normalize_embeddings=True)[0]
        scores = np.dot(self.embeddings, query_vec)
        best_indices = np.argsort(scores)[::-1][:top_k]

        return [
            {
                "filename": self.runbooks[idx]["filename"],
                "score": float(scores[idx]),
                "content": self.runbooks[idx]["content"],
            }
            for idx in best_indices
        ]


if __name__ == "__main__":
    retriever = RunbookRetriever()
    sample_query = "Container crashes with exit code 137 due to out of memory"
    hit = retriever.search(sample_query, top_k=1)[0]
    print(f"\nQuery: {sample_query}")
    print(f"Best match: {hit['filename']} (score: {hit['score']:.4f})\n")
    print(hit["content"])
