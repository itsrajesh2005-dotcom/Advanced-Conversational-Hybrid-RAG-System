from ingestion.loader import load_documents
from ingestion.chunking import split_documents
from ingestion.embedding import load_embedding_model
from ingestion.vectorstore import store_vectors

from retrieval.hybrid_retriever import HybridRetriever
from query_rewriter.rewrite import rewrite_query

from llm.llm_model import load_llm
from utils.prompt import PROMPT_TEMPLATE


# Remove duplicate retrieved documents
def remove_duplicate_docs(docs):

    unique_docs = []
    seen = set()

    for doc in docs:

        content = doc.page_content.strip()

        if content not in seen:

            unique_docs.append(doc)
            seen.add(content)

    return unique_docs


# Get relevant chat history
def get_smart_history(chat_history, query):

    query_words = set(
        query.lower().split()
    )

    recent_history = chat_history[-6:]

    relevant_history = []


    for item in recent_history:

        history_words = set(
            item.lower().split()
        )

        if query_words.intersection(
            history_words
        ):

            relevant_history.append(item)


    return "\n".join(relevant_history)


# Load documents from data folder
documents = load_documents("data")


# Split documents into chunks
chunks = split_documents(documents)


# Load embedding model
embeddings = load_embedding_model()

# Store vectors in Pinecone
vectorstore = store_vectors(

    chunks,
    embeddings

)


# Create Hybrid Retriever
retriever = HybridRetriever(

    vectorstore,
    chunks

)


# Load LLM
llm = load_llm()


# Title
print("\n===================================")

print(" Advanced Conversational ")

print("      Hybrid RAG System ✅")

print("===================================")



# Store conversation history
chat_history = []


# Main chatbot loop
while True:


   
    # Get user query
    query = input(
        "\nAsk Question: "
    ).strip()

    # Exit condition
    if query.lower() in [

        "exit",
        "quit",
        "bye"

    ]:

        print("\nGoodbye!\n")

        break


   
    # Empty question validation
    if not query:

        print(
            "\nPlease ask a valid question.\n"
        )

        continue


   
    # Rewrite follow-up questions
    rewrite_prompt = rewrite_query(

        query,
        chat_history

    )


    rewritten_query = llm.invoke(

        rewrite_prompt

    ).content.strip()


   
    # Retrieve relevant documents
    docs = retriever.retrieve(
        rewritten_query
    )


   
    # Remove duplicate chunks
    docs = remove_duplicate_docs(
        docs
    )


  
    # If no documents found
    if not docs:

        print("\nAnswer:\n")

        print(
            "I don't know from the provided documents."
        )

        continue


   
    # Create context from retrieved docs
    context = "\n".join([

        doc.page_content

        for doc in docs

    ])


   
    # Get related conversation history
    history_text = get_smart_history(

        chat_history,
        rewritten_query

    )


  
    # Create final prompt
    prompt = PROMPT_TEMPLATE.format(

        chat_history=history_text,

        context=context,

        question=rewritten_query

    )


    # Generate answer 
    response = llm.invoke(prompt)

    answer = response.content.strip()


   
    # Print answer
    print("\nAnswer:\n")

    print(answer)


    
    # Save chat history
    chat_history.append(
        f"User: {query}"
    )

    chat_history.append(
        f"AI: {answer}"
    )