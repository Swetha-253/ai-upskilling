import re
from typing import List, Dict, Any
from src.ingest import Document

class Chunk:
    def __init__(self, chunk_id: str, content: str, metadata: Dict[str, Any]):
        self.chunk_id = chunk_id
        self.content = content
        self.metadata = metadata
        # Validate source_file exists in metadata
        if "source_file" not in self.metadata or not self.metadata["source_file"]:
            raise ValueError("Failed Ingest: Chunk missing required 'source_file' metadata.")

class NaiveChunker:
    """
    Fixed character window chunking strategy.
    Blindly cuts text without respecting markdown boundaries, headers, parameter tables, or code fences.
    """
    def __init__(self, chunk_size: int = 220, chunk_overlap: int = 30):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, doc: Document) -> List[Chunk]:
        content = doc.content
        chunks = []
        start = 0
        idx = 0
        while start < len(content):
            end = min(start + self.chunk_size, len(content))
            chunk_text = content[start:end]
            chunk_id = f"{doc.metadata['page_id']}_naive_{idx}"
            
            chunk_metadata = doc.metadata.copy()
            chunk_metadata["chunk_id"] = chunk_id
            chunk_metadata["strategy"] = "naive"
            
            chunks.append(Chunk(chunk_id=chunk_id, content=chunk_text, metadata=chunk_metadata))
            if end >= len(content):
                break
            start += (self.chunk_size - self.chunk_overlap)
            idx += 1
        return chunks

class StructureAwareChunker:
    """
    Structure-aware Markdown chunker.
    Splits document on markdown headers (#, ##, ###) while ensuring:
    1. Header context remains attached to section content.
    2. Parameter tables remain unbroken.
    3. Fenced code blocks are preserved intact.
    """
    def chunk_document(self, doc: Document) -> List[Chunk]:
        content = doc.content
        chunks = []
        
        # Regex to split on headers while keeping header titles
        lines = content.split("\n")
        current_section_title = doc.metadata["page_id"]
        current_header_level = 0
        section_lines = []
        section_idx = 0

        def save_section(title: str, lines_list: List[str], idx: int):
            text = "\n".join(lines_list).strip()
            if not text:
                return
            
            # Generate clean anchor slug
            anchor = re.sub(r"[^a-zA-Z0-9_-]", "", title.lower().replace(" ", "-"))
            chunk_id = f"{doc.metadata['page_id']}#{anchor}"
            if any(c.chunk_id == chunk_id for c in chunks):
                chunk_id = f"{chunk_id}_{idx}"

            chunk_metadata = doc.metadata.copy()
            chunk_metadata["chunk_id"] = chunk_id
            chunk_metadata["strategy"] = "structure_aware"
            chunk_metadata["section_title"] = title
            
            chunks.append(Chunk(chunk_id=chunk_id, content=text, metadata=chunk_metadata))

        in_code_block = False
        in_table = False

        for line in lines:
            # Check for main section headers (# or ##) outside code blocks
            header_match = re.match(r"^(#{1,2})\s+(.*)$", line)
            if header_match and not in_code_block:
                if section_lines:
                    save_section(current_section_title, section_lines, section_idx)
                    section_idx += 1
                    section_lines = []
                current_section_title = header_match.group(2).strip()
                current_header_level = len(header_match.group(1))
                section_lines.append(line)
            else:
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                section_lines.append(line)

        if section_lines:
            save_section(current_section_title, section_lines, section_idx)

        return chunks
