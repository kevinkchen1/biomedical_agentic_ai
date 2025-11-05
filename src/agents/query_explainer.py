"""
Interactive Query Explainer & Debugger

Provides human-readable explanations of Cypher queries and helpful debugging.
Shows users exactly what their query is doing step-by-step.
"""

import re
from typing import Dict, List, Optional, Tuple


class QueryExplainer:
    """Explains Cypher queries in plain English with visual steps."""

    def __init__(self):
        """Initialize the query explainer."""
        pass

    def explain_query(self, cypher_query: str) -> Dict[str, any]:
        """
        Break down a Cypher query into understandable steps.
        
        Returns a dictionary with:
        - summary: One-line description
        - steps: List of step-by-step explanations
        - complexity: Query complexity rating
        - warnings: Potential issues or improvements
        - visual: ASCII diagram of the query pattern
        """
        query = cypher_query.strip()
        
        explanation = {
            "summary": self._generate_summary(query),
            "steps": self._extract_steps(query),
            "complexity": self._assess_complexity(query),
            "warnings": self._check_for_issues(query),
            "visual": self._create_visual_diagram(query),
            "estimated_results": self._estimate_result_size(query)
        }
        
        return explanation

    def _generate_summary(self, query: str) -> str:
        """Generate a one-line summary of what the query does."""
        query_lower = query.lower()
        
        # Count key operations
        match_count = len(re.findall(r'\bmatch\b', query_lower))
        where_count = len(re.findall(r'\bwhere\b', query_lower))
        return_count = len(re.findall(r'\breturn\b', query_lower))
        
        # Extract node types
        node_pattern = r'\((\w+):(\w+)\)'
        nodes = re.findall(node_pattern, query)
        node_types = [n[1] for n in nodes]
        
        # Extract relationship types
        rel_pattern = r'\[(\w+)?:(\w+)\]'
        rels = re.findall(rel_pattern, query)
        rel_types = [r[1] for r in rels if r[1]]
        
        # Build summary
        if not node_types:
            return "Query structure unclear"
        
        if len(node_types) == 1:
            summary = f"Find all {node_types[0]} nodes"
        elif len(node_types) == 2 and rel_types:
            summary = f"Find {node_types[0]} connected to {node_types[1]} via {rel_types[0]}"
        else:
            summary = f"Complex query involving {', '.join(set(node_types))}"
        
        if where_count > 0:
            summary += " with filters"
        
        return summary

    def _extract_steps(self, query: str) -> List[Dict[str, str]]:
        """Break query into step-by-step explanations."""
        steps = []
        query_lower = query.lower()
        
        # Step 1: MATCH clauses
        match_patterns = re.finditer(
            r'MATCH\s+(.*?)(?=WHERE|RETURN|MATCH|$)', 
            query, 
            re.IGNORECASE | re.DOTALL
        )
        
        for i, match in enumerate(match_patterns, 1):
            pattern = match.group(1).strip()
            explanation = self._explain_match_pattern(pattern)
            steps.append({
                "number": i,
                "operation": "MATCH",
                "code": f"MATCH {pattern}",
                "explanation": explanation,
                "icon": "🔍"
            })
        
        # Step 2: WHERE clauses
        where_patterns = re.finditer(
            r'WHERE\s+(.*?)(?=RETURN|MATCH|WITH|$)', 
            query, 
            re.IGNORECASE | re.DOTALL
        )
        
        for match in where_patterns:
            conditions = match.group(1).strip()
            explanation = self._explain_where_conditions(conditions)
            steps.append({
                "number": len(steps) + 1,
                "operation": "WHERE",
                "code": f"WHERE {conditions}",
                "explanation": explanation,
                "icon": "🔎"
            })
        
        # Step 3: RETURN clause
        return_match = re.search(
            r'RETURN\s+(.*?)(?:LIMIT|ORDER|$)', 
            query, 
            re.IGNORECASE | re.DOTALL
        )
        
        if return_match:
            returns = return_match.group(1).strip()
            explanation = self._explain_return_clause(returns)
            steps.append({
                "number": len(steps) + 1,
                "operation": "RETURN",
                "code": f"RETURN {returns}",
                "explanation": explanation,
                "icon": "📤"
            })
        
        # Step 4: LIMIT clause
        limit_match = re.search(r'LIMIT\s+(\d+)', query, re.IGNORECASE)
        if limit_match:
            limit = limit_match.group(1)
            steps.append({
                "number": len(steps) + 1,
                "operation": "LIMIT",
                "code": f"LIMIT {limit}",
                "explanation": f"Return only the first {limit} results",
                "icon": "✂️"
            })
        
        return steps

    def _explain_match_pattern(self, pattern: str) -> str:
        """Explain a MATCH pattern in plain English."""
        # Extract nodes
        node_pattern = r'\((\w+):(\w+)\)'
        nodes = re.findall(node_pattern, pattern)
        
        # Extract relationships
        rel_pattern = r'-\[(\w*):?(\w*)\]-'
        rels = re.findall(rel_pattern, pattern)
        
        if not nodes:
            return "Search the database for a pattern"
        
        if len(nodes) == 1:
            var, label = nodes[0]
            return f"Find all {label} nodes (calling them '{var}')"
        
        if len(nodes) >= 2 and rels:
            var1, label1 = nodes[0]
            var2, label2 = nodes[1]
            rel_type = rels[0][1] if rels[0][1] else "related to"
            
            direction = "->" if "->" in pattern else "<-" if "<-" in pattern else "-"
            
            if direction == "->":
                return f"Find {label1} nodes ('{var1}') that point to {label2} nodes ('{var2}') via '{rel_type}' relationships"
            elif direction == "<-":
                return f"Find {label1} nodes ('{var1}') that receive connections from {label2} nodes ('{var2}') via '{rel_type}' relationships"
            else:
                return f"Find {label1} nodes ('{var1}') connected to {label2} nodes ('{var2}') via '{rel_type}' relationships (any direction)"
        
        return "Search for a complex pattern in the database"

    def _explain_where_conditions(self, conditions: str) -> str:
        """Explain WHERE conditions in plain English."""
        conditions_clean = conditions.strip()
        
        # Check for CONTAINS
        if "CONTAINS" in conditions_clean.upper():
            match = re.search(r'(\w+\.\w+)\s+CONTAINS\s+[\'"]([^\'"]+)[\'"]', conditions_clean, re.IGNORECASE)
            if match:
                property_name, value = match.groups()
                return f"Filter to only include items where {property_name} contains '{value}'"
        
        # Check for IN
        if " IN " in conditions_clean.upper():
            match = re.search(r'(\w+\.\w+)\s+IN\s+\[(.*?)\]', conditions_clean, re.IGNORECASE)
            if match:
                property_name, values = match.groups()
                return f"Filter to only include items where {property_name} is one of: {values}"
        
        # Check for equals
        if "=" in conditions_clean and "!=" not in conditions_clean:
            match = re.search(r'(\w+\.\w+)\s*=\s*[\'"]?([^\'"]+)[\'"]?', conditions_clean)
            if match:
                property_name, value = match.groups()
                return f"Filter to only include items where {property_name} equals '{value.strip()}'"
        
        # Check for comparison
        if ">" in conditions_clean or "<" in conditions_clean:
            return f"Filter based on numeric comparison: {conditions_clean}"
        
        # Check for AND/OR
        if " AND " in conditions_clean.upper():
            count = len(re.findall(r'\bAND\b', conditions_clean, re.IGNORECASE))
            return f"Apply {count + 1} filters (all must be true)"
        
        if " OR " in conditions_clean.upper():
            count = len(re.findall(r'\bOR\b', conditions_clean, re.IGNORECASE))
            return f"Apply {count + 1} filters (at least one must be true)"
        
        return f"Apply filter: {conditions_clean}"

    def _explain_return_clause(self, returns: str) -> str:
        """Explain RETURN clause in plain English."""
        returns_clean = returns.strip()
        
        # Count what's being returned
        items = [item.strip() for item in returns_clean.split(',')]
        
        if len(items) == 1:
            if "count(" in items[0].lower():
                return "Count the total number of results"
            elif "distinct" in items[0].lower():
                return f"Return unique values of {items[0].replace('DISTINCT', '').strip()}"
            else:
                return f"Return the property: {items[0]}"
        else:
            return f"Return {len(items)} properties: {', '.join(items[:3])}{'...' if len(items) > 3 else ''}"

    def _assess_complexity(self, query: str) -> Dict[str, any]:
        """Assess query complexity."""
        query_lower = query.lower()
        
        # Count operations
        match_count = len(re.findall(r'\bmatch\b', query_lower))
        where_count = len(re.findall(r'\bwhere\b', query_lower))
        optional_count = len(re.findall(r'\boptional\b', query_lower))
        
        # Calculate complexity score
        score = 1
        score += match_count * 2
        score += where_count * 1.5
        score += optional_count * 3
        
        if score <= 4:
            level = "Simple"
            description = "Easy to understand and fast to execute"
            color = "🟢"
        elif score <= 8:
            level = "Moderate"
            description = "Standard complexity, good performance expected"
            color = "🟡"
        else:
            level = "Complex"
            description = "Advanced query, may take longer to execute"
            color = "🟠"
        
        return {
            "level": level,
            "score": round(score, 1),
            "description": description,
            "color": color
        }

    def _check_for_issues(self, query: str) -> List[Dict[str, str]]:
        """Check for common query issues and suggest improvements."""
        warnings = []
        query_lower = query.lower()
        
        # Check for missing LIMIT
        if "limit" not in query_lower and "count(" not in query_lower:
            warnings.append({
                "type": "Performance",
                "severity": "warning",
                "message": "No LIMIT clause found. Query might return too many results.",
                "suggestion": "Add 'LIMIT 10' or 'LIMIT 100' to the end of your query",
                "icon": "⚠️"
            })
        
        # Check for missing WHERE with relationships
        if "match" in query_lower and "-[" in query_lower and "where" not in query_lower:
            if "limit" not in query_lower:
                warnings.append({
                    "type": "Optimization",
                    "severity": "info",
                    "message": "Relationship query without filters might be broad",
                    "suggestion": "Consider adding WHERE clause to narrow results",
                    "icon": "💡"
                })
        
        # Check for property existence
        property_pattern = r'(\w+)\.(\w+)'
        properties = re.findall(property_pattern, query)
        if properties:
            warnings.append({
                "type": "Tip",
                "severity": "info",
                "message": f"Query accesses {len(set(properties))} different properties",
                "suggestion": "Make sure these properties exist in your database",
                "icon": "ℹ️"
            })
        
        # Check for multiple MATCH clauses
        match_count = len(re.findall(r'\bmatch\b', query_lower))
        if match_count > 2:
            warnings.append({
                "type": "Complexity",
                "severity": "info",
                "message": f"Query has {match_count} MATCH clauses",
                "suggestion": "Consider combining patterns for better performance",
                "icon": "🔄"
            })
        
        return warnings

    def _create_visual_diagram(self, query: str) -> str:
        """Create an ASCII diagram of the query pattern."""
        # Extract nodes
        node_pattern = r'\((\w+):(\w+)\)'
        nodes = re.findall(node_pattern, query)
        
        # Extract relationships
        rel_pattern = r'-\[(\w*):?(\w*)\]-[>]?'
        rels = re.findall(rel_pattern, query)
        
        if not nodes:
            return "No pattern to visualize"
        
        # Build simple diagram
        if len(nodes) == 1:
            var, label = nodes[0]
            return f"({label})"
        
        if len(nodes) >= 2 and rels:
            var1, label1 = nodes[0]
            var2, label2 = nodes[1]
            rel_type = rels[0][1] if rels[0][1] else "RELATED"
            
            # Check direction
            if "->" in query:
                return f"({label1}) --[{rel_type}]--> ({label2})"
            elif "<-" in query:
                return f"({label1}) <--[{rel_type}]-- ({label2})"
            else:
                return f"({label1}) --[{rel_type}]-- ({label2})"
        
        # Multi-node diagram
        diagram = f"({nodes[0][1]})"
        for i in range(1, len(nodes)):
            rel_type = rels[i-1][1] if i-1 < len(rels) and rels[i-1][1] else "?"
            diagram += f" --[{rel_type}]--> ({nodes[i][1]})"
        
        return diagram

    def _estimate_result_size(self, query: str) -> Dict[str, str]:
        """Estimate the potential result size."""
        query_lower = query.lower()
        
        # Check for LIMIT
        limit_match = re.search(r'limit\s+(\d+)', query_lower)
        if limit_match:
            limit = int(limit_match.group(1))
            return {
                "estimate": f"Maximum {limit} results",
                "reasoning": f"LIMIT {limit} clause restricts output",
                "icon": "✅"
            }
        
        # Check for COUNT
        if "count(" in query_lower:
            return {
                "estimate": "1 result (count)",
                "reasoning": "COUNT returns a single number",
                "icon": "✅"
            }
        
        # Check for WHERE clauses
        where_count = len(re.findall(r'\bwhere\b', query_lower))
        if where_count > 0:
            return {
                "estimate": "Moderate (filtered)",
                "reasoning": f"{where_count} filter(s) will narrow results",
                "icon": "🟡"
            }
        
        # No filters or limits
        return {
            "estimate": "Potentially large",
            "reasoning": "No LIMIT or filters - could return many results",
            "icon": "⚠️"
        }