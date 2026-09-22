"""Command-line interface for the curriculum graph tool."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .cypher import generate_cypher
from .graph import load_graph


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path, help="Curriculum JSON file")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("stats", help="Print graph statistics")

    score = subparsers.add_parser("score", help="Evaluate prerequisite satisfaction")
    score.add_argument("course_code")
    score.add_argument("--completed", nargs="*", default=[])

    available = subparsers.add_parser("available", help="List available options by group")
    available.add_argument("--completed", nargs="*", default=[])

    cypher = subparsers.add_parser("cypher", help="Generate an idempotent Cypher script")
    cypher.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    graph = load_graph(args.dataset)
    if args.command == "stats":
        payload = {
            "courses": len(graph.courses),
            "elective_groups": len(graph.elective_groups),
            **graph.relationship_counts(),
        }
        print(json.dumps(payload, indent=2))
    elif args.command == "score":
        score, missing = graph.prerequisite_satisfaction(args.course_code, args.completed)
        print(json.dumps({"score": score, "missing": list(missing)}, indent=2))
    elif args.command == "available":
        print(json.dumps(graph.available_options(args.completed), indent=2))
    elif args.command == "cypher":
        content = generate_cypher(graph)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content, encoding="utf-8")
        else:
            print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

