from curriculum_graph_tool.normalizer import split_elective_entry


def test_split_elective_entry():
    assert split_elective_entry("Introduction to Finance / Software Design Patterns") == (
        "Introduction to Finance",
        "Software Design Patterns",
    )


def test_split_removes_empty_values_and_case_insensitive_duplicates():
    assert split_elective_entry(" AI /  / ai / Reliability ") == ("AI", "Reliability")

