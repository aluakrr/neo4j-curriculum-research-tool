"""Curriculum relationship validation for Neo4j research prototypes."""

from .graph import Course, CurriculumGraph, ElectiveGroup, load_graph

__all__ = ["Course", "CurriculumGraph", "ElectiveGroup", "load_graph"]
__version__ = "0.1.0"

