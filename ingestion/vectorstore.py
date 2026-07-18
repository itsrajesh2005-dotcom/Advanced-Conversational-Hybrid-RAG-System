from pinecone import Pinecone, ServerlessSpec

from langchain_pinecone import PineconeVectorStore

import os

from dotenv import load_dotenv


load_dotenv()


INDEX_NAME = "hybrid-rag"


def store_vectors(chunks, embeddings):


    # Pinecone Client
    pc = Pinecone(

        api_key=os.getenv(
            "PINECONE_API_KEY"
        )
    )


    # Existing Indexes
    existing_indexes = [

        index["name"]

        for index in pc.list_indexes()
    ]


    # Create Index IF NOT EXISTS
    if INDEX_NAME not in existing_indexes:


        print(
            "\nCreating New Pinecone Index... 🚀"
        )


        pc.create_index(

            name=INDEX_NAME,

            dimension=384,

            metric="cosine",

            spec=ServerlessSpec(

                cloud="aws",

                region="us-east-1"
            )
        )


    # Connect Vector Store
    vectorstore = PineconeVectorStore(

        index_name=INDEX_NAME,

        embedding=embeddings
    )


    # Store Documents ONLY First Time
    if INDEX_NAME not in existing_indexes:


        vectorstore.add_documents(
            chunks
        )


        print(
            "\nVectors Stored Successfully ✅"
        )


    return vectorstore