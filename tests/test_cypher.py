from pathlib import Path

from curriculum_graph_tool.cypher import generate_cypher
from curriculum_graph_tool.graph import load_graph

DATASET = Path(__file__).parents[1] / "data" / "sample_curriculum.json"


def test_cypher_contains_constraints_and_relationships():
    cypher = generate_cypher(load_graph(DATASET))
    assert "CREATE CONSTRAINT course_code IF NOT EXISTS" in cypher
    assert "[:HAS_OPTION]" in cypher
    assert "[:PREREQUISITE_OF]" in cypher
    assert "[:POSTREQUISITE_OF]" in cypher


def test_cypher_is_deterministic():
    graph = load_graph(DATASET)
    assert generate_cypher(graph) == generate_cypher(graph)

