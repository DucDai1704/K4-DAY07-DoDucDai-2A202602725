from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        if self.store.get_collection_size() == 0:
            return "Knowledge base is empty. Cannot answer the question."
            
        results = self.store.search(question, top_k=top_k)
        if not results:
            return "No relevant information found in the knowledge base."
            
        context_parts = []
        for i, res in enumerate(results, 1):
            source = res.get('metadata', {}).get('source_url', res.get('metadata', {}).get('doc_id', 'Unknown'))
            context_parts.append(f"[{i}] Source: {source}\n{res['content']}")
            
        context_str = "\n\n".join(context_parts)
        
        prompt = (
            "You are a helpful assistant. Use ONLY the provided context to answer the question.\n"
            "If the answer is not in the context, say 'I cannot find the answer in the provided documents.'\n"
            "Cite your sources using the bracketed numbers like [1], [2].\n\n"
            f"Context:\n{context_str}\n\n"
            f"Question: {question}\n"
            "Answer:"
        )
        
        return self.llm_fn(prompt)
