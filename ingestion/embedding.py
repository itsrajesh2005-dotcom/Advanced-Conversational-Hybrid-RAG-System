from langchain_community.embeddings import FastEmbedEmbeddings


def load_embedding_model():

    embeddings = FastEmbedEmbeddings(

        model_name="BAAI/bge-small-en-v1.5"
    )

    return embeddings