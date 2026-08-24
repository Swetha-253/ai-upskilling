import os
from typing import Dict, List, Any

class Document:
    def __init__(self, content: str, metadata: Dict[str, Any]):
        self.content = content
        self.metadata = metadata
        self.validate()

    def validate(self):
        required_keys = ["source_file", "page_id", "sdk_version", "page_type"]
        for key in required_keys:
            if key not in self.metadata or not self.metadata[key]:
                raise ValueError(f"Ingest Failed: Missing required metadata '{key}' in document.")

def load_docs(docs_dir: str) -> List[Document]:
    documents = []
    for root, _, files in os.walk(docs_dir):
        for file in sorted(files):
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, docs_dir)
                
                # Derive metadata from path and filename
                parts = rel_path.split(os.sep)
                sdk_version = parts[0] if len(parts) > 1 else "v3"
                page_id = f"{sdk_version}_{os.path.splitext(file)[0]}"
                
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                metadata = {
                    "source_file": file_path,
                    "page_id": page_id,
                    "sdk_version": sdk_version,
                    "page_type": "reference"
                }
                
                doc = Document(content=content, metadata=metadata)
                documents.append(doc)
    return documents
