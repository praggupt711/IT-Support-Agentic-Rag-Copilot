from pathlib import Path
from typing import Iterable
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from docx import Document as DocxDocument

SUPPORTED_FILE_TYPES = {".pdf", ".txt", ".docx", ".md"}

def load_file(path: Path) -> list[Document]:
    """
    Load a file and return a list of Document objects.

    Args:
        path (Path): The path to the file.

    Returns:
        list[Document]: A list of Document objects.
    """
    
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        loader = PyPDFLoader(str(path))
        return loader.load()
    if suffix in {".txt", ".md"}:
        loader = TextLoader(str(path), encoding="utf-8")
        return loader.load()
    if suffix == ".docx":
        doc = DocxDocument(str(path))
        text = "\n".join(para.text for para in doc.paragraphs if para.text.strip())
        return [Document(page_content=text, metadata={"source": str(path)})]
    raise ValueError(f"Unsupported file type: {suffix}. Supported types are: {SUPPORTED_FILE_TYPES}")


def chunk_documents(documents: Iterable[Document], chunk_size: int = 900, chunk_overlap: int = 120) -> list[Document]:
    """
    Chunk documents into smaller pieces.

    Args:
        documents (Iterable[Document]): An iterable of Document objects.
        chunk_size (int): The maximum size of each chunk.
        chunk_overlap (int): The number of overlapping characters between chunks.

    Returns:
        list[Document]: A list of chunked Document objects.
    """

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    
    all_chunks = []
    for doc in documents:
        chunks = text_splitter.split_text(doc.page_content)
        for i, chunk in enumerate(chunks):
            all_chunks.append(Document(page_content=chunk, metadata={**doc.metadata, "chunk_index": i}))
    
    return all_chunks