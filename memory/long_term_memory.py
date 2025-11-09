
"""
Manages the persistent long-term vector store (Friend Memory).
Uses PostgreSQL with PGVector for persistent, multi-tenant storage.
"""
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres.vectorstores import PGVector
from config import DATABASE_URL
from utils import logger
from typing import List, Tuple

# --- Setup (Değişiklik yok) ---
COLLECTION_NAME = "agent_memories"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

try:
    embedding_function = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={'device': 'cpu'}
    )

    # --- BU BLOK DÜZELTİLDİ ---

    # PGVector'ü 'from_collection_name' metoduyla değil,
    # doğrudan constructor (sınıfın kendisi) ile çağırıyoruz.
    # Doğru parametre adı 'embedding' değil, 'embedding_function'dır.
    vector_store = PGVector(
        connection=DATABASE_URL,
        collection_name=COLLECTION_NAME,
        embeddings=embedding_function,
        pre_delete_collection=False
    )

    # --- DÜZELTME SONU ---

    logger.info(f"PGVector store connected. Collection: '{COLLECTION_NAME}'")
    logger.info(f"Loaded embedding model: {EMBEDDING_MODEL_NAME}")

except Exception as e:
    logger.error(f"Failed to initialize long-term memory (PGVector): {e}", exc_info=True)
    raise


# --- Public Functions (Bu fonksiyonlar zaten doğruydu) ---

def search_memories_with_score(input_text: str, user_id: str, persona_id: str) -> List[Tuple[Document, float]]:
    """
    Vektör deposunu (store) filtreleyerek arar ve hem dokümanları
    hem de onların benzerlik puanlarını (skorlarını) döndürür.
    """
    filter_query = {
        "user_id": user_id,
        "persona_id": persona_id
    }

    results = vector_store.similarity_search_with_score(
        query=input_text,
        filter=filter_query,
        k=3
    )
    return results


def add_memory(text: str, user_id: str, persona_id: str):
    """
    Vektör deposuna yeni bir anı (metin) ekler.
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
        logger.info(f"Added new memory for user '{user_id}' (Persona: '{persona_id}'): '{text[:50]}...'")
    except Exception as e:
        logger.error(f"Failed to add memory to PGVector: {e}", exc_info=True)
        raise

# --- ESKİ YAKLAŞIM (Referans Olarak Yorum Satırında) ---
#
# def get_retriever_for_user(user_id: str, persona_id: str):
#     """
#     Returns a retriever dynamically filtered for a specific
#     user_id and persona_id.
#     (Bu fonksiyon artık kullanılmıyor, yerine search_memories_with_score kullanılıyor)
#     """
#     filter_query = {
#         "user_id": user_id,
#         "persona_id": persona_id
#     }
#     
#     return vector_store.as_retriever(
#         search_kwargs={"filter": filter_query, "k": 3}
#     )
#
# --- ESKİ YAKLAŞIM SONU ---