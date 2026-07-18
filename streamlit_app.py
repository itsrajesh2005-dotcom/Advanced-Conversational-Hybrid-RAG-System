import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

import logging

logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("fastembed").setLevel(logging.ERROR)

import warnings
import streamlit as st

from ingestion.loader import load_documents
from ingestion.chunking import split_documents
from ingestion.embedding import load_embedding_model
from ingestion.vectorstore import store_vectors

from retrieval.hybrid_retriever import HybridRetriever
from query_rewriter.rewrite import rewrite_query

from llm.llm_model import load_llm
from utils.prompt import PROMPT_TEMPLATE

# --------------------------------------------------
# Environment Settings
# --------------------------------------------------

os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

warnings.filterwarnings("ignore")

# --------------------------------------------------
# Streamlit Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Advanced Conversational Hybrid RAG",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Advanced Conversational Hybrid RAG System")

# --------------------------------------------------
# Initialize RAG System
# --------------------------------------------------

@st.cache_resource
def initialize_system():

    documents = load_documents("data")

    chunks = split_documents(documents)

    embeddings = load_embedding_model()

    vectorstore = store_vectors(
        chunks,
        embeddings
    )

    retriever = HybridRetriever(
        vectorstore,
        chunks
    )

    llm = load_llm()

    return retriever, llm


retriever, llm = initialize_system()

# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def remove_duplicate_docs(docs):

    unique_docs = []
    seen = set()

    for doc in docs:

        content = doc.page_content.strip()

        if content not in seen:

            unique_docs.append(doc)

            seen.add(content)

    return unique_docs


# --------------------------------------------------
# Session State
# --------------------------------------------------

if "chat_history" not in st.session_state:

    st.session_state.chat_history = []


# --------------------------------------------------
# Display Previous Messages
# --------------------------------------------------

for item in st.session_state.chat_history:

    if item.startswith("User:"):

        with st.chat_message("user"):

            st.write(
                item.replace("User: ", "")
            )

    elif item.startswith("AI:"):

        with st.chat_message("assistant"):

            st.write(
                item.replace("AI: ", "")
            )


# --------------------------------------------------
# User Input
# --------------------------------------------------

query = st.chat_input(
    "Ask your question..."
)

# --------------------------------------------------
# Process Query
# --------------------------------------------------

if query:

    with st.chat_message("user"):

        st.write(query)

    greetings = {
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening"
    }

    farewells = {
        "bye",
        "byee",
        "goodbye",
        "bye bye",
        "see you",
        "see you later",
        "take care"
    }

    thanks_words = {
        "thanks",
        "thank you",
        "thx"
    }

    try:

        if query.lower().strip() in greetings:

            answer = "Hello! How can I help you today? 😊"

        elif query.lower().strip() in thanks_words:

            answer = "You're welcome! 😊"

        elif query.lower().strip() in farewells:

            answer = "Goodbye! Have a great day. 👋"

        else:

            with st.spinner("Thinking..."):

                # Query Rewriting

                rewrite_prompt = rewrite_query(
                    query,
                    st.session_state.chat_history
                )

                if isinstance(rewrite_prompt, str):

                    rewritten_query = llm.invoke(
                        rewrite_prompt
                    ).content.strip()

                else:

                    rewritten_query = query

                # Debug Sidebar

                st.sidebar.markdown(
                    "### Query Debug"
                )

                st.sidebar.write(
                    "Original Query:",
                    query
                )

                st.sidebar.write(
                    "Rewritten Query:",
                    rewritten_query
                )

                # Retrieve Documents

                docs = retriever.retrieve(
                    rewritten_query
                )

                docs = remove_duplicate_docs(
                    docs
                )

                # No Documents Found

                if not docs:

                    answer = (
                        "I don't know from the provided documents."
                    )

                else:

                    # Build Context

                    context = "\n".join(

                        doc.page_content

                        for doc in docs
                    )

                    history_text = "\n".join(

                        st.session_state.chat_history[-6:]
                    )

                    prompt = PROMPT_TEMPLATE.format(

                        chat_history=history_text,

                        context=context,

                        question=rewritten_query
                    )

                    answer = llm.invoke(
                        prompt
                    ).content.strip()

                    # Retrieved Context Viewer

                    with st.expander(
                        "Retrieved Context"
                    ):

                        for i, doc in enumerate(
                            docs,
                            start=1
                        ):

                            st.markdown(
                                f"### Document {i}"
                            )

                            st.write(
                                doc.page_content[:500]
                            )

        # Display Assistant Answer

        with st.chat_message("assistant"):

            st.write(answer)

        # Save Chat History

        st.session_state.chat_history.append(
            f"User: {query}"
        )

        st.session_state.chat_history.append(
            f"AI: {answer}"
        )

    except Exception as e:

        st.error(
            f"System Error: {str(e)}"
        )