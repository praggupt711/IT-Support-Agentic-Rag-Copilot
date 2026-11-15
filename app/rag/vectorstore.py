import time
from docx import settings
from pinecone import Pinecone , ServerlessSpec
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from app.core.config import get_settings


settings = get_settings()

_embeddings = None
_vectorstore = None

EMBEDDING_DIMENSION = {
    "gemini-embedding-001": 3072,
    "gemini-embedding-2": 3072,
    "text-embedding-005": 768,
} 

def get_embedding_dimension(model_name: str | None = None) -> int:
    """
    Get the embedding dimension for a given model name.

    Args:
        model_name (str): The name of the embedding model. 
    
    Returns:
        int: The embedding dimension for the specified model.
    """
    name = (model_name or settings.embeddings_model or "").strip()
    if not name:
        raise RuntimeError("Embedding model name is not configured.")
    
    normalised_name = name.lower()
    
    for model, dimension in EMBEDDING_DIMENSION.items():
        if model in normalised_name:
            return dimension
        
    raise ValueError(f"Unsupported embedding model: {name} for Pinecone."
                     "Add the matching dimension to the EMBEDDING_DIMENSION dictionary in app/rag/vectorstore.py.")
    
    
    
def get_embeddings():
    """
    Get the GeminiEmbeddings instance, initializing it if necessary.
    """
    global _embeddings
    if _embeddings is None:
        if not settings.gemini_api_key:
            raise RuntimeError("Gemini API key is not configured.")
        _embeddings = GoogleGenerativeAIEmbeddings(
            google_api_key=settings.gemini_api_key, 
            model=settings.embeddings_model
            )
    return _embeddings


def ensure_index():
    """
    Ensure that the Pinecone index exists and is configured correctly.
    If the index does not exist, it will be created with the appropriate dimension.
    If the index exists but has a different dimension, it will be deleted and recreated.
    """
    if not settings.pinecone_api_key:
        raise RuntimeError("PINECONE_API_KEY is missing")

    desired_dimension = get_embedding_dimension()
    pc = Pinecone(api_key=settings.pinecone_api_key)
    names = [x["name"] for x in pc.list_indexes()]

    if settings.pinecone_index_name in names:
        index_info = pc.describe_index(settings.pinecone_index_name)
        current_dimension = getattr(index_info, "dimension", None)
        if current_dimension is None and isinstance(index_info, dict):
            current_dimension = index_info.get("dimension")

        if current_dimension is not None and current_dimension != desired_dimension:
            pc.delete_index(name=settings.pinecone_index_name)
            while settings.pinecone_index_name in [x["name"] for x in pc.list_indexes()]:
                time.sleep(1)

    if settings.pinecone_index_name not in [x["name"] for x in pc.list_indexes()]:
        pc.create_index(
            name=settings.pinecone_index_name,
            dimension=desired_dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        while not pc.describe_index(settings.pinecone_index_name).status["ready"]:
            time.sleep(1)

    return pc.Index(settings.pinecone_index_name)


def get_vectorstore():
    """
    Get the PineconeVectorStore instance, initializing it if necessary.
    """
    global _vectorstore
    if _vectorstore is None:
        index = ensure_index()
        embeddings = get_embeddings()
        _vectorstore = PineconeVectorStore(index=index, 
                                           embedding=embeddings, 
                                           namespace=settings.pinecone_namespace)
    return _vectorstore

def get_retriever():
    """
    Get a retriever from the Pinecone vector store.
    """
    vectorstore = get_vectorstore()
    return vectorstore.as_retriever(search_kwargs={"k": settings.pinecone_top_k})


def add_documents(chunks):
    """
    Add documents to the Pinecone vector store.

    Args:
        chunks (list[Document]): A list of Document objects to be added to the vector store.
    """
    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)