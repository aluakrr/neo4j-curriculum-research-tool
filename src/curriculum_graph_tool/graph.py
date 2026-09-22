"""Domain model and validation logic for curriculum knowledge graphs."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Course:
    """A canonical academic course."""

    code: str
    name: str
    prerequisites: tuple[str, ...] = ()
    postrequisites: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ElectiveGroup:
    """A curriculum slot in which one option must be selected."""

    group_id: str
    name: str
    options: tuple[str, ...]


@dataclass(slots=True)
class CurriculumGraph:
    """In-memory representation used before Neo4j import."""

    courses: dict[str, Course] = field(default_factory=dict)
    elective_groups: dict[str, ElectiveGroup] = field(default_factory=dict)

    def validate(self) -> list[str]:
        """Return structural validation errors without mutating the graph."""
        errors: list[str] = []
        for code, course in self.courses.items():
            if code != course.code:
                errors.append(f"Course key {code!r} does not match code {course.code!r}")
            for related in (*course.prerequisites, *course.postrequisites):
                if related not in self.courses:
                    errors.append(f"Course {code} references unknown course {related}")
        for group in self.elective_groups.values():
            if len(group.options) < 2:
                errors.append(f"Elective group {group.group_id} has fewer than two options")
            for option in group.options:
                if option not in self.courses:
                    errors.append(f"Elective group {group.group_id} references unknown course {option}")
        return errors

    def prerequisite_satisfaction(
        self, course_code: str, completed: Iterable[str]
    ) -> tuple[float, tuple[str, ...]]:
        """Return satisfaction score and missing prerequisites for one course."""
        course = self.courses[course_code]
        required = set(course.prerequisites)
        if not required:
            return 1.0, ()
        completed_set = set(completed)
        missing = tuple(sorted(required - completed_set))
        score = (len(required) - len(missing)) / len(required)
        return round(score, 4), missing

    def is_available(self, course_code: str, completed: Iterable[str]) -> bool:
        """Return True when all prerequisites are completed."""
        score, _ = self.prerequisite_satisfaction(course_code, completed)
        return score == 1.0

    def available_options(self, completed: Iterable[str]) -> dict[str, list[str]]:
        """Return available course codes for each elective group."""
        completed_set = set(completed)
        return {
            group.group_id: [
                code for code in group.options if self.is_available(code, completed_set)
            ]
            for group in self.elective_groups.values()
        }

    def relationship_counts(self) -> dict[str, int]:
        """Return aggregate relationship counts for validation and reporting."""
        return {
            "HAS_OPTION": sum(len(group.options) for group in self.elective_groups.values()),
            "PREREQUISITE_OF": sum(len(course.prerequisites) for course in self.courses.values()),
            "POSTREQUISITE_OF": sum(len(course.postrequisites) for course in self.courses.values()),
        }


def load_graph(path: str | Path) -> CurriculumGraph:
    """Load and validate a graph fixture from JSON."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    courses = {
        item["code"]: Course(
            code=item["code"],
            name=item["name"],
            prerequisites=tuple(item.get("prerequisites", [])),
            postrequisites=tuple(item.get("postrequisites", [])),
        )
        for item in raw["courses"]
    }
    groups = {
        item["group_id"]: ElectiveGroup(
            group_id=item["group_id"],
            name=item["name"],
            options=tuple(item["options"]),
        )
        for item in raw["elective_groups"]
    }
    graph = CurriculumGraph(courses=courses, elective_groups=groups)
    errors = graph.validate()
    if errors:
        raise ValueError("Invalid curriculum graph:\n- " + "\n- ".join(errors))
    return graph

