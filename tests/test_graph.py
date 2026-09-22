from pathlib import Path

import pytest

from curriculum_graph_tool.graph import Course, CurriculumGraph, ElectiveGroup, load_graph

DATASET = Path(__file__).parents[1] / "data" / "sample_curriculum.json"


def test_fixture_is_valid():
    graph = load_graph(DATASET)
    assert graph.validate() == []
    assert len(graph.courses) == 6
    assert len(graph.elective_groups) == 2


def test_relationship_counts():
    graph = load_graph(DATASET)
    assert graph.relationship_counts() == {
        "HAS_OPTION": 4,
        "PREREQUISITE_OF": 5,
        "POSTREQUISITE_OF": 4,
    }


@pytest.mark.parametrize(
    ("completed", "expected_score", "expected_missing"),
    [
        ([], 0.0, ("CS101", "CS201")),
        (["CS101"], 0.5, ("CS201",)),
        (["CS101", "CS201"], 1.0, ()),
    ],
)
def test_prerequisite_satisfaction(completed, expected_score, expected_missing):
    graph = load_graph(DATASET)
    score, missing = graph.prerequisite_satisfaction("AI301", completed)
    assert score == expected_score
    assert missing == expected_missing


def test_course_without_prerequisites_is_available():
    graph = load_graph(DATASET)
    assert graph.is_available("FIN101", [])


def test_available_options_preserve_group_context():
    graph = load_graph(DATASET)
    result = graph.available_options(["CS101", "CS201"])
    assert result == {"EG1": ["FIN101", "SE201"], "EG2": ["AI301", "REL301"]}


def test_unknown_relationship_is_reported():
    graph = CurriculumGraph(
        courses={"A": Course("A", "A", prerequisites=("UNKNOWN",))},
        elective_groups={"G": ElectiveGroup("G", "G", ("A", "UNKNOWN"))},
    )
    errors = graph.validate()
    assert len(errors) == 2
    assert all("UNKNOWN" in error for error in errors)

