# Lightweight semantic chunking using document structure
# No ML models required - pure heuristics

import re
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class ChunkBoundary:
    """Represents a potential chunk boundary with confidence score."""
    position: int
    score: float
    reason: str


class StructuralChunker:
    """
    Chunks documents based on structural patterns rather than embeddings.

    Detects boundaries using:
    - Paragraph breaks (double newlines)
    - Heading patterns (markdown, HTML)
    - List transitions
    - Topic sentence indicators
    """

    def __init__(
        self,
        min_chunk_size: int = 200,
        max_chunk_size: int = 1500,
        boundary_threshold: float = 0.6
    ):
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.boundary_threshold = boundary_threshold

        # Patterns that indicate topic transitions
        self.transition_patterns = [
            (r'^\s*#{1,6}\s+', 1.0, 'markdown_heading'),
            (r'^\s*<h[1-6]>', 1.0, 'html_heading'),
            (r'\n\n+', 0.7, 'paragraph_break'),
            (r'^\s*[-*+]\s+', 0.4, 'list_item'),
            (r'^\s*\d+\.\s+', 0.4, 'numbered_list'),
            (r'^\s*(However|Moreover|Furthermore|In addition|On the other hand|Conversely)\b', 0.6, 'transition_word'),
            (r'^\s*(First|Second|Third|Finally|Lastly|In conclusion)\b', 0.5, 'sequence_word'),
        ]

    def find_boundaries(self, text: str) -> List[ChunkBoundary]:
        """
        Scan text for potential chunk boundaries based on structure.
        Returns sorted list of boundaries with confidence scores.
        """
        boundaries = []

        for pattern, score, reason in self.transition_patterns:
            for match in re.finditer(pattern, text, re.MULTILINE):
                boundaries.append(ChunkBoundary(
                    position=match.start(),
                    score=score,
                    reason=reason
                ))

        # Sort by position
        boundaries.sort(key=lambda b: b.position)

        # Remove duplicates within 10 characters
        filtered = []
        last_pos = -100
        for b in boundaries:
            if b.position - last_pos > 10:
                filtered.append(b)
                last_pos = b.position

        return filtered

    def select_split_points(
        self,
        text: str,
        boundaries: List[ChunkBoundary]
    ) -> List[int]:
        """
        Choose which boundaries to use for actual splits.
        Balances semantic breaks with chunk size constraints.
        """
        split_points = []
        current_chunk_start = 0

        for boundary in boundaries:
            # Skip if boundary is below threshold
            if boundary.score < self.boundary_threshold:
                continue

            current_chunk_size = boundary.position - current_chunk_start

            # If chunk would be too small, skip this boundary
            if current_chunk_size < self.min_chunk_size:
                continue

            # If chunk is approaching max size, force a split
            if current_chunk_size >= self.max_chunk_size * 0.8:
                split_points.append(boundary.position)
                current_chunk_start = boundary.position
                continue

            # For high-confidence boundaries, always split
            if boundary.score >= 0.8:
                split_points.append(boundary.position)
                current_chunk_start = boundary.position

        return split_points

    def chunk(self, text: str) -> List[str]:
        """
        Split document into chunks using structural analysis.
        """
        if len(text) <= self.max_chunk_size:
            return [text.strip()] if text.strip() else []

        boundaries = self.find_boundaries(text)
        split_points = self.select_split_points(text, boundaries)

        # Build chunks from split points
        chunks = []
        start = 0

        for point in split_points:
            chunk = text[start:point].strip()
            if chunk:
                chunks.append(chunk)
            start = point

        # Add final chunk
        final_chunk = text[start:].strip()
        if final_chunk:
            chunks.append(final_chunk)

        # Handle oversized chunks by falling back to sentence splitting
        result = []
        for chunk in chunks:
            if len(chunk) > self.max_chunk_size:
                result.extend(self.split_oversized(chunk))
            else:
                result.append(chunk)

        return result

    def split_oversized(self, text: str) -> List[str]:
        """
        Fall back to sentence splitting for chunks exceeding max size.
        """
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current = []
        current_len = 0

        for sentence in sentences:
            if current_len + len(sentence) > self.max_chunk_size and current:
                chunks.append(' '.join(current))
                current = [sentence]
                current_len = len(sentence)
            else:
                current.append(sentence)
                current_len += len(sentence) + 1

        if current:
            chunks.append(' '.join(current))

        return chunks