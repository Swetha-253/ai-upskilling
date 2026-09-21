import os
import json
from typing import List, Dict, Any

STATE_FILE = "pinned_state.json"

class StateStore:
    """Persists user state across process restarts."""
    def __init__(self, filepath: str = STATE_FILE):
        self.filepath = filepath
        
    def save_pinned_version(self, version: str) -> None:
        data = {"pinned_api_version": version}
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f)
            
    def load_pinned_version(self) -> str:
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("pinned_api_version", "v3")
        return "v3"

class SlidingWindowMemory:
    """Sliding window memory with LLM summarization for long (30-turn) threads."""
    def __init__(self, window_size: int = 6):
        self.window_size = window_size
        self.messages: List[Dict[str, str]] = []
        self.summary: str = ""
        
    def add_message(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.window_size:
            self._compress_and_slide()
            
    def _compress_and_slide(self) -> None:
        # Exclude old turns and update summary
        dropped = self.messages.pop(0)
        # Summarize dropped turn (lossy condensation)
        if "retry_backoff_ms" in dropped["content"] or "idempotency_key" in dropped["content"]:
            # Intentionally loses specific parameter default integer value during summarization
            self.summary += " [Summary: User discussed v3 client send parameters and error retry options.]"
        else:
            self.summary += f" [Summary: User asked about {dropped['content'][:30]}...]"

    def get_context(self) -> List[Dict[str, str]]:
        context = []
        if self.summary:
            context.append({"role": "system", "content": f"Prior Conversation Summary: {self.summary}"})
        context.extend(self.messages)
        return context
