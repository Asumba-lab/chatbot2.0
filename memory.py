# memory.py
import json
import os
import threading

_lock = threading.Lock()

class MemoryStore:
    """
    Simple JSON-backed per-session memory store.
    Keeps last 100 items per session by default.
    """

    def __init__(self, path="memory.json", max_items=100):
        self.path = path
        self.max_items = max_items
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _read(self):
        with _lock:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)

    def _write(self, data):
        with _lock:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def append_session_memory(self, session_id, text):
        data = self._read()
        if session_id not in data:
            data[session_id] = []
        data[session_id].append(text)
        # prune
        data[session_id] = data[session_id][-self.max_items:]
        self._write(data)

    def get_session_memory(self, session_id):
        data = self._read()
        return data.get(session_id, [])

    def clear_session(self, session_id):
        data = self._read()
        if session_id in data:
            data[session_id] = []
            self._write(data)
