"""
Kairos Session Tracking – remembers previous stages per user.
Supports in‑memory (default) and optional file persistence.
"""

import json
import os
import time
from typing import List, Optional
from dataclasses import dataclass, asdict

@dataclass
class KairosSnapshot:
    timestamp: float
    dominant_stage: int
    expected_stage: float
    entropy: float
    trap_energy: float
    therapeutic_note: str
    somatic_invitation: str
    trickster_wisdom: str

class KairosSession:
    def __init__(self, system_id: str, storage_backend: str = "memory", file_path: Optional[str] = None):
        self.system_id = system_id
        self.storage_backend = storage_backend
        self.file_path = file_path or f"kairos_{system_id}.json"
        self.snapshots: List[KairosSnapshot] = []
        self._load()

    def _load(self):
        if self.storage_backend == "file" and os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                self.snapshots = [KairosSnapshot(**item) for item in data.get("snapshots", [])]

    def _save(self):
        if self.storage_backend == "file":
            with open(self.file_path, 'w') as f:
                json.dump({"snapshots": [asdict(s) for s in self.snapshots]}, f, indent=2)

    def add_snapshot(self, snapshot: KairosSnapshot):
        self.snapshots.append(snapshot)
        if len(self.snapshots) > 500:
            self.snapshots = self.snapshots[-500:]
        self._save()

    def get_last_snapshot(self) -> Optional[KairosSnapshot]:
        return self.snapshots[-1] if self.snapshots else None

    def get_history(self, limit: int = 100) -> List[KairosSnapshot]:
        return self.snapshots[-limit:]

    def get_previous_stage(self) -> Optional[int]:
        last = self.get_last_snapshot()
        return last.dominant_stage if last else None

    def get_regression_count(self, window: int = 20) -> int:
        stages = [s.dominant_stage for s in self.snapshots[-window:]]
        count = 0
        for i in range(1, len(stages)):
            if stages[i-1] == 8 and stages[i] == 7:
                count += 1
        return count

    def detect_cynical_loop(self, window: int = 10) -> bool:
        stages = [s.dominant_stage for s in self.snapshots[-window:]]
        for i in range(len(stages)-2):
            if stages[i] == 8 and stages[i+1] == 7 and stages[i+2] == 8:
                return True
        alt_count = 0
        for i in range(len(stages)-1):
            if stages[i] in (7,8) and stages[i+1] in (7,8) and stages[i] != stages[i+1]:
                alt_count += 1
        return alt_count >= 2
