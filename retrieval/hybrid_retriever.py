from rank_bm25 import BM25Okapi


class HybridRetriever:

    def __init__(self, vectorstore, documents):

        self.vectorstore = vectorstore

        self.documents = documents

        self.texts = [
            doc.page_content
            for doc in documents
        ]

        tokenized_docs = [
            text.split()
            for text in self.texts
        ]

        self.bm25 = BM25Okapi(tokenized_docs)

    def retrieve(self, query, k=4):

        # Dense Search
        dense_docs = self.vectorstore.similarity_search(
            query,
            k=k
        )

        # Sparse Search
        tokenized_query = query.split()

        bm25_scores = self.bm25.get_scores(
            tokenized_query
        )

        top_indices = sorted(
            range(len(bm25_scores)),
            key=lambda i: bm25_scores[i],
            reverse=True
        )[:k]

        sparse_docs = [
            self.documents[i]
            for i in top_indices
        ]

        # Combine Results
        final_docs = dense_docs + sparse_docs

        return final_docs