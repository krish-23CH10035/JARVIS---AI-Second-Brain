"""Vector Database — PostgreSQL pgvector integration for semantic knowledge retrieval."""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.memory.structured_db import DocumentChunk
from app.utils.config import settings
from app.utils.logger import get_logger

logger = get_logger("vector_db")


class VectorDB:
    """pgvector database client."""

    def __init__(self, async_session: async_sessionmaker = None):
        self.async_session = async_session

    async def create_index(self):
        """Enable pgvector extension."""
        try:
            async with self.async_session() as session:
                await session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                await session.commit()
            logger.info("pgvector extension ensured", event_type="index_created")
        except Exception as e:
            logger.error(f"Failed to create vector extension: {e}", exc_info=True)

    async def store_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """Store document chunks with embeddings in pgvector."""
        try:
            async with self.async_session() as session:
                docs = []
                for chunk in chunks:
                    doc = DocumentChunk(
                        id=str(uuid.uuid4()),
                        document_id=chunk.get("document_id", ""),
                        user_id=chunk.get("user_id", ""),
                        content=chunk.get("content", ""),
                        embedding=chunk.get("embedding", []),
                        topic=chunk.get("topic", "general"),
                        source_filename=chunk.get("source_filename", ""),
                        chunk_index=chunk.get("chunk_index", 0),
                        page_number=chunk.get("page_number", 0),
                        section_heading=chunk.get("section_heading", ""),
                    )
                    docs.append(doc)
                
                session.add_all(docs)
                await session.commit()
                
                logger.info(
                    f"Indexed {len(docs)}/{len(chunks)} chunks",
                    event_type="chunks_indexed",
                    metadata={"total": len(chunks), "indexed": len(docs)},
                )
                return len(docs)

        except Exception as e:
            logger.error(f"Failed to store chunks in pgvector: {e}", exc_info=True)
            raise

    async def search(
        self,
        query: str,
        query_embedding: Optional[List[float]] = None,
        user_id: str = "",
        top_k: int = 7,
        topic_filter: str = "",
    ) -> List[Dict[str, Any]]:
        """Perform vector search against pgvector."""
        try:
            async with self.async_session() as session:
                stmt = select(DocumentChunk)
                
                if user_id:
                    stmt = stmt.where(DocumentChunk.user_id == user_id)
                if topic_filter:
                    stmt = stmt.where(DocumentChunk.topic == topic_filter)
                
                if query_embedding:
                    # Order by cosine distance (L2 distance is <->, Cosine is <=>)
                    stmt = stmt.order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
                
                stmt = stmt.limit(top_k)
                result = await session.execute(stmt)
                chunks = result.scalars().all()

                search_results = []
                for chunk in chunks:
                    search_results.append({
                        "id": chunk.id,
                        "document_id": chunk.document_id,
                        "content": chunk.content,
                        "topic": chunk.topic,
                        "source_filename": chunk.source_filename,
                        "chunk_index": chunk.chunk_index,
                        "page_number": chunk.page_number,
                        "section_heading": chunk.section_heading,
                        "score": 1.0, # We'd have to extract the distance from the query, defaulting to 1.0
                    })

                logger.info(
                    f"Search returned {len(search_results)} results",
                    event_type="vector_search",
                    metadata={"query_preview": query[:100], "results": len(search_results)},
                )
                return search_results

        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            raise

    async def delete_document_chunks(self, document_id: str):
        """Delete all chunks belonging to a specific document."""
        try:
            async with self.async_session() as session:
                stmt = select(DocumentChunk).where(DocumentChunk.document_id == document_id)
                result = await session.execute(stmt)
                chunks = result.scalars().all()
                for chunk in chunks:
                    await session.delete(chunk)
                await session.commit()
                logger.info(f"Deleted {len(chunks)} chunks for document {document_id}")
        except Exception as e:
            logger.error(f"Failed to delete chunks: {e}", exc_info=True)
