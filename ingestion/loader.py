import os

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader
)


def load_documents(data_folder):

    documents = []

    for file in os.listdir(data_folder):

        # Skip temporary/hidden files (e.g., Word lock files like ~$filename.docx)
        if file.startswith("~$"):
            continue

        file_path = os.path.join(
            data_folder,
            file
        )


        # PDF Files
        if file.endswith(".pdf"):

            loader = PyPDFLoader(file_path)

            docs = loader.load()

            documents.extend(docs)


        # DOCX Files
        elif file.endswith(".docx"):

            loader = Docx2txtLoader(file_path)

            docs = loader.load()

            documents.extend(docs)


        # TXT Files
        elif file.endswith(".txt"):

            loader = TextLoader(
                file_path,
                encoding="utf-8"
            )

            docs = loader.load()

            documents.extend(docs)

        # Markdown Files
        elif file.endswith(".md"):

           loader = TextLoader(
               file_path,
              encoding="utf-8"
            )

           docs = loader.load()

           documents.extend(docs)
            


    return documents