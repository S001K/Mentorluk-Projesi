"""
Manages the persistent semantic vector store (Friend Memory).
Uses PostgreSQL with PGVector for persistent, multi-tenant storage.
"""
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres.vectorstores import PGVector
from config import DATABASE_URL
from utils import logger

# --- Setup ---
COLLECTION_NAME = "agent_memories"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

try:
    # Initialize embedding model
    embedding_function = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={'device': 'cpu'}
    )

    # Initialize vector store
    vector_store = PGVector(
        connection=DATABASE_URL,
        collection_name=COLLECTION_NAME,
        embeddings=embedding_function,
        pre_delete_collection=False
    )

    logger.info(f"PGVector store connected. Collection: '{COLLECTION_NAME}'")
    logger.info(f"Loaded embedding model: {EMBEDDING_MODEL_NAME}")

except Exception as e:
    logger.error(f"Failed to initialize semantic memory (PGVector): {e}", exc_info=True)
    raise


# --- Public Functions ---

def get_retriever_for_user(user_id: str, persona_id: str):
    """
    Belirli bir user_id ve persona_id için dinamik olarak
    filtrelenmiş bir retriever (alıcı) döndürür.
    """

    filter_query = {
        "user_id": user_id,
        "persona_id": persona_id
    }

    return vector_store.as_retriever(
        search_kwargs={"filter": filter_query, "k": 3}
    )


def add_memory(text: str, user_id: str, persona_id: str):
    """
    Vektör deposuna, ilişkili user_id ve persona_id meta verileriyle
    birlikte yeni bir metin parçası (anı) ekler.
    """
    try:
        new_doc = Document(
            page_content=text,
            metadata={
                "user_id": user_id,
                "persona_id": persona_id
            }
        )
        vector_store.add_documents([new_doc])
        logger.info(f"Added new memory for user '{user_id}' (Persona: '{persona_id}'): '{text}'")
    except Exception as e:
        logger.error(f"Failed to add memory to PGVector: {e}", exc_info=True)
        raise