import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class QueryLearningSystem:
    """
    Extremely lightweight version of the query learning system.
    No database. JSON-based persistence. Simple heuristics.
    """

    def __init__(self, storage_path: str = "query_learning.json"):
        self.storage_path = Path(storage_path)
        self.data = {
            "executions": [],   # list of dicts
            "feedback": [],     # list of dicts
            "patterns": {}      # pattern -> metadata
        }
        self._load()

    # -------------------------
    # Internal persistence
    # -------------------------

    def _load(self):
        if self.storage_path.exists():
            self.data = json.load(self.storage_path.open("r"))

    def _save(self):
        json.dump(self.data, self.storage_path.open("w"), indent=2)

    # -------------------------
    # Pattern extraction
    # -------------------------

    def _extract_pattern(self, cypher: str) -> str:
        import re
        q = cypher
        q = re.sub(r"'[^']*'", "{VALUE}", q)
        q = re.sub(r'"[^"]*"', "{VALUE}", q)
        q = re.sub(r"\b\d+\b", "{NUM}", q)
        return q

    # -------------------------
    # Logging
    # -------------------------

    def log_execution(
        self,
        user_question: str,
        question_type: str,
        entities: List[str],
        cypher_query: str,
        success: bool,
        result_count: int = 0,
        error: Optional[str] = None,
    ) -> int:

        entry = {
            "id": len(self.data["executions"]) + 1,
            "timestamp": datetime.now().isoformat(),
            "user_question": user_question,
            "question_type": question_type,
            "entities": entities,
            "cypher": cypher_query,
            "success": success,
            "result_count": result_count,
            "error": error,
        }

        self.data["executions"].append(entry)

        if success and result_count > 0:
            self._update_pattern(question_type, cypher_query)

        self._save()
        return entry["id"]

    def add_feedback(self, exec_id: int, rating: int, text: str = ""):
        fb = {
            "exec_id": exec_id,
            "rating": rating,
            "text": text,
            "timestamp": datetime.now().isoformat(),
        }
        self.data["feedback"].append(fb)
        self._update_confidence(exec_id, rating)
        self._save()

    # -------------------------
    # Pattern Learning
    # -------------------------

    def _update_pattern(self, qtype: str, cypher: str):
        pattern = self._extract_pattern(cypher)

        if pattern not in self.data["patterns"]:
            self.data["patterns"][pattern] = {
                "question_type": qtype,
                "success_count": 0,
                "avg_rating": 4.0,
                "confidence": 0.5,
            }

        p = self.data["patterns"][pattern]
        p["success_count"] += 1

    def _update_confidence(self, exec_id: int, rating: int):
        exec_entry = next((e for e in self.data["executions"] if e["id"] == exec_id), None)
        if not exec_entry:
            return

        pattern = self._extract_pattern(exec_entry["cypher"])
        p = self.data["patterns"].get(pattern)
        if not p:
            return

        # Simple moving average
        p["avg_rating"] = (p["avg_rating"] + rating) / 2
        p["confidence"] = min(0.99, (p["avg_rating"] / 5))

    # -------------------------
    # API for WorkflowAgent
    # -------------------------

    def get_confidence(self, cypher: str) -> Tuple[float, str]:
        pattern = self._extract_pattern(cypher)
        p = self.data["patterns"].get(pattern)
        if not p:
            return 0.3, "No prior data for this query pattern"
        
        explanation = (
            f"Seen {p['success_count']} times | "
            f"Avg rating {p['avg_rating']:.1f}/5"
        )
        return p["confidence"], explanation

    def get_similar_questions(self, question: str, limit: int = 5):
        """Super lightweight word-overlap similarity."""
        q_words = set(question.lower().split())
        scored = []

        for e in self.data["executions"]:
            cand_words = set(e["user_question"].lower().split())
            sim = len(q_words & cand_words) / len(q_words | cand_words)

            scored.append((sim, e))

        scored.sort(reverse=True, key=lambda x: x[0])
        return scored[:limit]
