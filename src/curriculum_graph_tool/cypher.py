"""Deterministic Cypher generation for Neo4j import."""

from __future__ import annotations

from .graph import CurriculumGraph


def _quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def generate_cypher(graph: CurriculumGraph) -> str:
    """Generate idempotent constraints, nodes, and relationships."""
    lines = [
        "CREATE CONSTRAINT course_code IF NOT EXISTS FOR (c:Course) REQUIRE c.code IS UNIQUE;",
        "CREATE CONSTRAINT elective_group_id IF NOT EXISTS FOR (g:ElectiveGroup) REQUIRE g.id IS UNIQUE;",
        "",
    ]
    for course in sorted(graph.courses.values(), key=lambda item: item.code):
        lines.append(
            "MERGE (c:Course {code: '"
            + _quote(course.code)
            + "'}) SET c.name = '"
            + _quote(course.name)
            + "';"
        )
    lines.append("")
    for group in sorted(graph.elective_groups.values(), key=lambda item: item.group_id):
        lines.append(
            "MERGE (g:ElectiveGroup {id: '"
            + _quote(group.group_id)
            + "'}) SET g.name = '"
            + _quote(group.name)
            + "';"
        )
        for option in sorted(group.options):
            lines.append(
                f"MATCH (g:ElectiveGroup {{id: '{_quote(group.group_id)}'}}), "
                f"(c:Course {{code: '{_quote(option)}'}}) MERGE (g)-[:HAS_OPTION]->(c);"
            )
    lines.append("")
    for course in sorted(graph.courses.values(), key=lambda item: item.code):
        for prerequisite in sorted(course.prerequisites):
            lines.append(
                f"MATCH (p:Course {{code: '{_quote(prerequisite)}'}}), "
                f"(c:Course {{code: '{_quote(course.code)}'}}) "
                "MERGE (p)-[:PREREQUISITE_OF]->(c);"
            )
        for postrequisite in sorted(course.postrequisites):
            lines.append(
                f"MATCH (c:Course {{code: '{_quote(course.code)}'}}), "
                f"(p:Course {{code: '{_quote(postrequisite)}'}}) "
                "MERGE (c)-[:POSTREQUISITE_OF]->(p);"
            )
    return "\n".join(lines).strip() + "\n"

