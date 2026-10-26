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
- automated tests, GitHub Actions CI, Docker, and a Jenkins pipeline.

## Project structure

```text
src/curriculum_graph_tool/   Python package
tests/                       Unit and integration tests
data/sample_curriculum.json  Demonstration fixture
Dockerfile                   Test and runtime container stages
Jenkinsfile                  Jenkins CI pipeline
compose.jenkins.yml          Local Jenkins and Docker-in-Docker stack
jenkins/Dockerfile           Jenkins image with Docker CLI and plugins
.github/workflows/ci.yml     Hosted CI and container verification
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

The [CI workflow](.github/workflows/ci.yml) runs compilation, Ruff static checks, and all fourteen tests on Python 3.11 and 3.12. A dependent container job validates the Jenkins Compose file, builds the Docker test and runtime stages, repeats the quality checks inside Docker, and runs the packaged CLI as a smoke test. See [GitHub Actions](https://github.com/aluakrr/neo4j-curriculum-research-tool/actions) for run results.

## Docker

Build and run the minimal runtime image:

```bash
docker build --target runtime -t curriculum-graph:latest .
docker run --rm curriculum-graph:latest
```

Run the full verification suite inside the test image:

```bash
docker build --target test -t curriculum-graph:test .
docker run --rm --entrypoint sh curriculum-graph:test -c "python -m compileall -q src && ruff check src tests && pytest"
```

## Jenkins

Start the local Jenkins controller and its isolated Docker daemon:

```bash
docker compose -f compose.jenkins.yml up -d --build
```

Open `http://localhost:8080`, complete the initial setup, create a Pipeline job from SCM, set the repository URL to this repository, and keep `Jenkinsfile` as the script path. Every run checks out the revision, builds the test image, compiles and lints the source, runs the tests, builds the runtime image, and performs a container smoke test.

Stop the local stack without deleting its persistent volumes:

```bash
docker compose -f compose.jenkins.yml down
```

## Repository link

Maintained by Alua Koishybay ([aluakrr](https://github.com/aluakrr)).

[Public repository](https://github.com/aluakrr/neo4j-curriculum-research-tool)

Report bugs or suggest improvements through [GitHub Issues](https://github.com/aluakrr/neo4j-curriculum-research-tool/issues).

## License

MIT License. See [LICENSE](LICENSE).
