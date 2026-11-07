"""Build or replace MovieUp's persistent Chroma knowledge collection."""

import argparse
from pathlib import Path

import chromadb
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DOCUMENT = PROJECT_ROOT / "movie_up" / "chatbot" / "data" / "chatbot.md"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"
COLLECTION_NAME = "movieup_chatbot"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def ingest(document_path: Path = DEFAULT_DOCUMENT) -> int:
    """Load, split, embed, and persist the knowledge document in Chroma."""
    if not document_path.is_file():
        raise FileNotFoundError(f"Knowledge document not found: {document_path}")

    documents = TextLoader(str(document_path), encoding="utf-8").load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n## ", "\n### ", "\n", ". ", " "],
    )
    chunks = splitter.split_documents(documents)
    if not chunks:
        raise ValueError(f"Knowledge document is empty: {document_path}")

    # Replace this chatbot's collection so re-ingesting edited content cannot
    # leave obsolete chunks behind. Other collections in chroma_db are kept.
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection_names = {
        getattr(collection, "name", collection)
        for collection in client.list_collections()
    }
    if COLLECTION_NAME in collection_names:
        client.delete_collection(COLLECTION_NAME)

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
        collection_name=COLLECTION_NAME,
    )
    print(f"{len(chunks)} chunks ingested from {document_path}")
    print(f"Chroma collection '{COLLECTION_NAME}' saved in {CHROMA_DIR}")
    return len(chunks)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest MovieUp's Markdown knowledge into Chroma."
    )
    parser.add_argument(
        "file",
        nargs="?",
        type=Path,
        default=DEFAULT_DOCUMENT,
        help=f"Markdown document (default: {DEFAULT_DOCUMENT})",
    )
    args = parser.parse_args()
    ingest(args.file.resolve())


if __name__ == "__main__":
    main()
