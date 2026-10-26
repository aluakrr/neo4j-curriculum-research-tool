# Neo4j Curriculum Research Tool

A small reproducible Python module for validating curriculum relationship data before it is loaded into Neo4j. The tool supports the dissertation project **Modeling Relationships in Neo4j for Curriculum Knowledge Extraction**.

## Research purpose

Human-oriented curriculum documents often encode elective alternatives as slash-separated text. The package includes a helper for splitting these entries. The CLI reads JSON with explicitly defined courses and elective groups, validates their references, evaluates prerequisite satisfaction, returns available options per group, and generates deterministic Cypher statements for a Neo4j property graph.

## Features

- explicit `Course` and `ElectiveGroup` domain objects;
- `HAS_OPTION`, `PREREQUISITE_OF`, and `POSTREQUISITE_OF` relationship export;
- prerequisite satisfaction score from `0.0` to `1.0`;
- course and elective-group availability checks;
- deterministic Cypher generation;
- command-line interface;
- automated tests and GitHub Actions CI.

## Project structure

```text
src/curriculum_graph_tool/   Python package
tests/                       Unit and integration tests
data/sample_curriculum.json  Demonstration fixture
.github/workflows/ci.yml     Continuous integration workflow
.github/ISSUE_TEMPLATE/      Issue templates
```

## Installation

Requires Python 3.11 or newer. Run the commands from the repository root.

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Usage

Show graph statistics:

```bash
curriculum-graph data/sample_curriculum.json stats
```

Evaluate a course for a set of completed courses:

```bash
curriculum-graph data/sample_curriculum.json score AI301 --completed CS101 CS201
```

List available options by elective group:

```bash
curriculum-graph data/sample_curriculum.json available --completed CS101 CS201
```

Generate Cypher:

```bash
curriculum-graph data/sample_curriculum.json cypher --output build/import.cypher
```

## Testing

```bash
pytest
```

The [CI workflow](.github/workflows/ci.yml) runs compilation, Ruff static checks, and the full test suite on Python 3.11 and 3.12 for pushes to `main` and pull requests targeting `main`. It can also be started manually. See [GitHub Actions](https://github.com/aluakrr/neo4j-curriculum-research-tool/actions) for run results.

## Repository link

Maintained by Alua Koishybay ([aluakrr](https://github.com/aluakrr)).

[Public repository](https://github.com/aluakrr/neo4j-curriculum-research-tool)

Report bugs or suggest improvements through [GitHub Issues](https://github.com/aluakrr/neo4j-curriculum-research-tool/issues).

## Assignment 5: Docker and Jenkins

The `assignment5-devops` branch adds a Dockerfile, a Jenkins pipeline with JUnit reports,
container smoke checks, and automatic batch execution in a local test environment.
See [the ordered setup guide](docs/assignment5.md) and [Jenkinsfile](Jenkinsfile).

## License

MIT License. See [LICENSE](LICENSE).

