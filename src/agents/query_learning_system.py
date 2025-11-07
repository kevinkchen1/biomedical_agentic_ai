"""
Query Learning System with Feedback Loop

This module implements a self-improving query system that learns from:
- Successful vs failed query executions
- User feedback on result quality
- Query patterns that produce good results
- Entity and question type correlations

The system builds a knowledge base of proven query patterns and uses it to:
- Suggest similar successful queries to users
- Improve query generation over time
- Provide confidence scores for generated queries
- Recommend related questions users might find useful
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class QueryLearningSystem:
    """Manages query history, feedback, and learning analytics."""

    def __init__(self, db_path: str = "query_learning.db"):
        """Initialize the learning system with SQLite database."""
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self):
        """Create database tables for query learning."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Table for query executions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_question TEXT NOT NULL,
                question_type TEXT,
                entities TEXT,
                cypher_query TEXT NOT NULL,
                execution_success BOOLEAN NOT NULL,
                results_count INTEGER,
                execution_time_ms REAL,
                error_message TEXT
            )
        """)

        # Table for user feedback
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_execution_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                feedback_text TEXT,
                was_helpful BOOLEAN,
                FOREIGN KEY (query_execution_id) REFERENCES query_executions(id)
            )
        """)

        # Table for query patterns (learned successful patterns)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_type TEXT NOT NULL,
                pattern_template TEXT NOT NULL,
                success_count INTEGER DEFAULT 0,
                avg_rating REAL,
                last_used TEXT,
                confidence_score REAL
            )
        """)

        # Table for similar query recommendations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_similarities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_id_1 INTEGER NOT NULL,
                query_id_2 INTEGER NOT NULL,
                similarity_score REAL,
                FOREIGN KEY (query_id_1) REFERENCES query_executions(id),
                FOREIGN KEY (query_id_2) REFERENCES query_executions(id)
            )
        """)

        conn.commit()
        conn.close()

    def log_query_execution(
        self,
        user_question: str,
        question_type: str,
        entities: List[str],
        cypher_query: str,
        execution_success: bool,
        results_count: int = 0,
        execution_time_ms: float = 0.0,
        error_message: Optional[str] = None,
    ) -> int:
        """Log a query execution and return the execution ID."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO query_executions 
                (timestamp, user_question, question_type, entities, cypher_query,
                 execution_success, results_count, execution_time_ms, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    datetime.now().isoformat(),
                    user_question,
                    question_type,
                    json.dumps(entities),
                    cypher_query,
                    execution_success,
                    results_count,
                    execution_time_ms,
                    error_message,
                ),
            )

            execution_id = cursor.lastrowid
            conn.commit()

            # Update query patterns if successful
            if execution_success and results_count > 0:
                self._update_query_pattern(question_type, cypher_query)

            return execution_id
        finally:
            conn.close()

    def add_user_feedback(
        self,
        query_execution_id: int,
        rating: int,
        feedback_text: Optional[str] = None,
        was_helpful: bool = True,
    ):
        """Record user feedback for a query execution."""
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO user_feedback 
            (query_execution_id, timestamp, rating, feedback_text, was_helpful)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                query_execution_id,
                datetime.now().isoformat(),
                rating,
                feedback_text,
                was_helpful,
            ),
        )

        conn.commit()
        conn.close()

        # Update pattern confidence based on feedback
        self._update_pattern_confidence(query_execution_id, rating)

    def _update_query_pattern(self, question_type: str, cypher_query: str):
        """Extract and store successful query patterns."""
        # Extract pattern template (replace specific values with placeholders)
        pattern = self._extract_pattern_template(cypher_query)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if pattern exists
        cursor.execute(
            """
            SELECT id, success_count FROM query_patterns 
            WHERE question_type = ? AND pattern_template = ?
        """,
            (question_type, pattern),
        )
        result = cursor.fetchone()

        if result:
            # Update existing pattern
            pattern_id, success_count = result
            cursor.execute(
                """
                UPDATE query_patterns 
                SET success_count = ?, last_used = ?
                WHERE id = ?
            """,
                (success_count + 1, datetime.now().isoformat(), pattern_id),
            )
        else:
            # Insert new pattern
            cursor.execute(
                """
                INSERT INTO query_patterns 
                (question_type, pattern_template, success_count, last_used, 
                 confidence_score)
                VALUES (?, ?, 1, ?, 0.5)
            """,
                (question_type, pattern, datetime.now().isoformat()),
            )

        conn.commit()
        conn.close()

    def _extract_pattern_template(self, cypher_query: str) -> str:
        """Convert specific query to reusable pattern template."""
        import re
        
        # Simple pattern extraction - replace specific values with placeholders
        pattern = cypher_query

        # Replace string literals with {VALUE}
        pattern = re.sub(r"'[^']*'", "{VALUE}", pattern)
        pattern = re.sub(r'"[^"]*"', "{VALUE}", pattern)

        # Replace numbers with {NUM}
        pattern = re.sub(r"\b\d+\b", "{NUM}", pattern)

        return pattern

    def _update_pattern_confidence(self, query_execution_id: int, rating: int):
        """Update confidence scores for patterns based on feedback."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get the query details
        cursor.execute(
            """
            SELECT question_type, cypher_query FROM query_executions
            WHERE id = ?
        """,
            (query_execution_id,),
        )
        result = cursor.fetchone()

        if result:
            question_type, cypher_query = result
            pattern = self._extract_pattern_template(cypher_query)

            # Update average rating and confidence
            cursor.execute(
                """
                SELECT AVG(uf.rating) as avg_rating, COUNT(*) as feedback_count
                FROM user_feedback uf
                JOIN query_executions qe ON uf.query_execution_id = qe.id
                JOIN query_patterns qp ON qe.question_type = qp.question_type
                WHERE qp.pattern_template = ?
            """,
                (pattern,),
            )
            stats = cursor.fetchone()

            if stats and stats[0]:
                avg_rating, feedback_count = stats
                # Confidence increases with more feedback and higher ratings
                confidence = min(0.99, (avg_rating / 5.0) * (1 - 1 / (feedback_count + 1)))

                cursor.execute(
                    """
                    UPDATE query_patterns 
                    SET avg_rating = ?, confidence_score = ?
                    WHERE question_type = ? AND pattern_template = ?
                """,
                    (avg_rating, confidence, question_type, pattern),
                )

        conn.commit()
        conn.close()

    def get_similar_queries(
        self, user_question: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find similar successful queries based on question similarity."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get successful queries with good feedback
        cursor.execute(
            """
            SELECT DISTINCT 
                qe.id,
                qe.user_question,
                qe.cypher_query,
                qe.results_count,
                AVG(uf.rating) as avg_rating
            FROM query_executions qe
            LEFT JOIN user_feedback uf ON qe.id = uf.query_execution_id
            WHERE qe.execution_success = 1 
            AND qe.results_count > 0
            GROUP BY qe.id
            HAVING AVG(COALESCE(uf.rating, 4)) >= 3
            ORDER BY qe.timestamp DESC
            LIMIT 50
        """
        )

        candidates = cursor.fetchall()
        conn.close()

        if not candidates:
            return []

        # Calculate similarity scores using simple word overlap
        similarities = []
        question_words = set(user_question.lower().split())

        for candidate in candidates:
            query_id, candidate_question, cypher, result_count, avg_rating = candidate
            candidate_words = set(candidate_question.lower().split())

            # Jaccard similarity
            intersection = len(question_words & candidate_words)
            union = len(question_words | candidate_words)
            similarity = intersection / union if union > 0 else 0

            similarities.append(
                {
                    "query_id": query_id,
                    "question": candidate_question,
                    "cypher_query": cypher,
                    "results_count": result_count,
                    "avg_rating": avg_rating or 4.0,
                    "similarity_score": similarity,
                }
            )

        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
        return similarities[:limit]

    def get_query_confidence(
        self, question_type: str, cypher_query: str
    ) -> Tuple[float, str]:
        """Get confidence score and explanation for a generated query."""
        pattern = self._extract_pattern_template(cypher_query)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT confidence_score, success_count, avg_rating
            FROM query_patterns
            WHERE question_type = ? AND pattern_template = ?
        """,
            (question_type, pattern),
        )
        result = cursor.fetchone()
        conn.close()

        if result:
            confidence, success_count, avg_rating = result
            explanation = (
                f"This query pattern has been used {success_count} times successfully"
            )
            if avg_rating:
                explanation += f" with an average rating of {avg_rating:.1f}/5"
            return confidence, explanation
        else:
            return 0.3, "This is a new query pattern - no historical data available"

    def get_learning_analytics(self) -> Dict[str, Any]:
        """Get analytics about the learning system's performance."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total queries
        cursor.execute("SELECT COUNT(*) FROM query_executions")
        total_queries = cursor.fetchone()[0]

        # Success rate
        cursor.execute(
            """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN execution_success = 1 THEN 1 ELSE 0 END) as successes
            FROM query_executions
        """
        )
        result = cursor.fetchone()
        success_rate = (result[1] / result[0] * 100) if result[0] > 0 else 0

        # Average rating
        cursor.execute("SELECT AVG(rating) FROM user_feedback")
        avg_rating = cursor.fetchone()[0] or 0

        # Most common question types
        cursor.execute(
            """
            SELECT question_type, COUNT(*) as count
            FROM query_executions
            GROUP BY question_type
            ORDER BY count DESC
            LIMIT 5
        """
        )
        top_question_types = cursor.fetchall()

        # Query patterns learned
        cursor.execute("SELECT COUNT(DISTINCT pattern_template) FROM query_patterns")
        patterns_learned = cursor.fetchone()[0]

        # Improvement over time (last 10 vs first 10 queries)
        cursor.execute(
            """
            SELECT AVG(results_count) FROM (
                SELECT results_count FROM query_executions 
                WHERE execution_success = 1
                ORDER BY timestamp ASC LIMIT 10
            )
        """
        )
        early_avg = cursor.fetchone()[0] or 0

        cursor.execute(
            """
            SELECT AVG(results_count) FROM (
                SELECT results_count FROM query_executions 
                WHERE execution_success = 1
                ORDER BY timestamp DESC LIMIT 10
            )
        """
        )
        recent_avg = cursor.fetchone()[0] or 0

        conn.close()

        return {
            "total_queries": total_queries,
            "success_rate": round(success_rate, 1),
            "average_rating": round(avg_rating, 2),
            "top_question_types": top_question_types,
            "patterns_learned": patterns_learned,
            "improvement_trend": {
                "early_avg_results": round(early_avg, 1),
                "recent_avg_results": round(recent_avg, 1),
                "improvement_pct": round(
                    ((recent_avg - early_avg) / early_avg * 100) if early_avg > 0 else 0,
                    1,
                ),
            },
        }

    def get_recommended_questions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recommended questions based on successful queries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 
                qe.user_question,
                qe.question_type,
                qe.results_count,
                AVG(COALESCE(uf.rating, 4)) as avg_rating,
                COUNT(uf.id) as feedback_count
            FROM query_executions qe
            LEFT JOIN user_feedback uf ON qe.id = uf.query_execution_id
            WHERE qe.execution_success = 1 
            AND qe.results_count > 0
            GROUP BY qe.user_question
            HAVING AVG(COALESCE(uf.rating, 4)) >= 3.5
            ORDER BY avg_rating DESC, feedback_count DESC
            LIMIT ?
        """,
            (limit,),
        )

        recommendations = []
        for row in cursor.fetchall():
            recommendations.append(
                {
                    "question": row[0],
                    "question_type": row[1],
                    "results_count": row[2],
                    "avg_rating": round(row[3], 1),
                    "times_rated": row[4],
                }
            )

        conn.close()
        return recommendations