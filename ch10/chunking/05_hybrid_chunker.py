# Combines structural and embedding-based chunking for best results
from semantic_chunker import SemanticChunker
from structural_chunker import StructuralChunker
from typing import List
import numpy as np


class HybridChunker:
    """
    Two-pass chunking strategy:
    1. Structural pass identifies obvious boundaries (headings, paragraphs)
    2. Embedding pass refines large sections into semantic units

    This approach is faster than pure embedding while more accurate than
    pure structural analysis.
    """

    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        similarity_threshold: float = 0.5,
        min_chunk_size: int = 150,
        max_chunk_size: int = 1500,
        embedding_refinement_threshold: int = 800
    ):
        # Structural chunker for first pass
        self.structural = StructuralChunker(
            min_chunk_size=min_chunk_size,
            max_chunk_size=max_chunk_size * 2,  # Allow larger initial chunks
            boundary_threshold=0.7
        )

        # Semantic chunker for refinement
        self.semantic = SemanticChunker(
            model_name=embedding_model,
            similarity_threshold=similarity_threshold,
            min_chunk_size=min_chunk_size,
            max_chunk_size=max_chunk_size
        )

        # Only refine chunks larger than this
        self.refinement_threshold = embedding_refinement_threshold

        # Final size limits
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size

    def chunk(self, text: str) -> List[str]:
        """
        Process document through structural then semantic chunking.
        """
        # Pass 1: Structural chunking (fast, catches obvious breaks)
        structural_chunks = self.structural.chunk(text)

        # Pass 2: Refine large chunks with embedding analysis
        final_chunks = []

        for chunk in structural_chunks:
            if len(chunk) > self.refinement_threshold:
                # This chunk is large enough to potentially contain
                # multiple semantic topics - refine it
                refined = self.semantic.chunk(chunk)
                final_chunks.extend(refined)
            else:
                final_chunks.append(chunk)

        # Pass 3: Merge any chunks that ended up too small
        return self.merge_small_chunks(final_chunks)

    def merge_small_chunks(self, chunks: List[str]) -> List[str]:
        """
        Merge undersized chunks with neighbors when possible.
        """
        if len(chunks) <= 1:
            return chunks

        merged = []
        buffer = chunks[0]

        for chunk in chunks[1:]:
            if len(buffer) < self.min_chunk_size:
                combined = buffer + "\n\n" + chunk
                if len(combined) <= self.max_chunk_size:
                    buffer = combined
                else:
                    merged.append(buffer)
                    buffer = chunk
            else:
                merged.append(buffer)
                buffer = chunk

        merged.append(buffer)
        return merged

    def chunk_with_metadata(self, text: str) -> List[dict]:
        """
        Returns chunks with additional metadata for debugging and analysis.
        """
        chunks = self.chunk(text)

        results = []
        char_offset = 0

        for i, chunk in enumerate(chunks):
            # Find actual position in original text
            start_pos = text.find(chunk[:50], char_offset)
            if start_pos == -1:
                start_pos = char_offset

            results.append({
                'index': i,
                'text': chunk,
                'char_count': len(chunk),
                'word_count': len(chunk.split()),
                'start_position': start_pos,
                'preview': chunk[:100] + '...' if len(chunk) > 100 else chunk
            })

            char_offset = start_pos + len(chunk)

        return results
        
if __name__ == "__main__":
    document = open('doc.txt', encoding='utf8').read()

    # Initialize chunker with tuned parameters
    chunker = HybridChunker(
        similarity_threshold=0.5,  # Adjust based on your content
        min_chunk_size=100,
        max_chunk_size=1500
    )

    chunks = chunker.chunk(document)

    print(f"Document split into {len(chunks)} semantic chunks:\n")
    for i, chunk in enumerate(chunks, 1):
        print(f"--- Chunk {i} ({len(chunk)} chars) ---")
        print(chunk[:200] + "..." if len(chunk) > 200 else chunk)
        print()            