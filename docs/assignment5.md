# Assignment 5: Docker and Jenkins

Author: Alua Koishybay. Research: Modeling Relationships in Neo4j for Curriculum Knowledge Extraction.

## 1. Initial setup

Use Docker Desktop in Linux-container mode and Git. Clone the `assignment5-devops`
branch of https://github.com/aluakrr/neo4j-curriculum-research-tool.
The original Python module and its 14 tests are retained. The synthetic fixture contains
6 courses, 2 elective groups, 4 HAS_OPTION, 5 PREREQUISITE_OF, and 4 POSTREQUISITE_OF edges.
These counts describe this fixture, not the larger dissertation dataset.

## 2. Required work

### 2.1 Dockerfile

The multi-stage Dockerfile shares a digest-pinned Python base between `test` and
`runtime`. Development dependencies are pinned in `requirements-ci.txt` and omitted
from the final runtime stage. Both images run as UID 10001; caches go to `/tmp`.

```sh
docker build --target test -t curriculum-tests .
docker run --rm curriculum-tests
docker build --target runtime -t curriculum-graph:local .
docker run --rm curriculum-graph:local
docker run --rm curriculum-graph:local data/sample_curriculum.json cypher
```

### 2.2 Jenkins server

Copy `jenkins/.env.example` to `jenkins/.env`, replace the placeholder with a unique
password, and run these commands from the repository root:

```sh
docker compose --env-file jenkins/.env -f jenkins/compose.yaml up -d --build
```

Open http://localhost:8085. Sign in as `admin` using the password in your local `.env`.
The `curriculum-research-ci` pipeline job is created by the initialization script.
Click **Build Now** once to register the Jenkinsfile trigger. Afterwards Jenkins polls
the configured branch every minute and builds a detected new revision automatically.
Multiple changes made between polls can be grouped in one build; allow a completed
build between demonstration commits. A public shared installation should use webhooks.

The controller is a local teaching environment. Its Docker socket can control the
local Docker engine, so only trusted code should be built here. Anonymous read access
is enabled for viewing evidence, with the web port bound to localhost only. For a
shared server use isolated agents and authenticated access. No inbound agent port is exposed.
The password file is ignored by Git and must not be included in a submission archive.

### 2.3 CI pipeline

1. Checkout the Git branch; record the full commit and Docker version.
2. Build the test stage, run Ruff and 14 tests, and publish JUnit XML.
3. Build the runtime image with the 12-character commit tag and full revision label.
4. Exercise all four CLI commands in the runtime image. Validate counts, scoring,
   elective options, and identical repeated Cypher. Archive dataset/output SHA-256.
5. Optionally push the same image to Docker Hub; this is off by default.
6. Automatically execute the tested runtime image on the local Docker test host.
   Capture the exit state and exported Cypher, then compare it with the validated output.

Test failures stop image delivery. The pipeline stores logs and artifacts for the last
20 builds. Source/image identity is recorded; this is not a claim of bit-identical image
rebuilds. Jenkins plugin versions are resolved during controller build; the actual
installed list is retained with submission evidence.

Docker Hub publishing requires a Jenkins username/password credential named `dockerhub`
(username plus access token), the `DOCKERHUB_NAMESPACE` parameter, and `PUSH_DOCKER_HUB=true`.
No registry publication is needed for the local demonstration.

### 2.4 Optional CD

`DEPLOY_TEST=true` runs a fresh batch container on the local Docker test host after all
checks pass. This is appropriate for a CLI research tool: it completes and returns an
artifact instead of serving HTTP. It is a local container test deployment, not a
Kubernetes deployment or a live Neo4j import. Kubernetes would use a Job for this task;
a real database import additionally needs credentials, a disposable database and checks.

## 3. Submitted materials

The report and original Jenkins screenshots are supplied separately in the ASDP
submission folder. Jenkins stores JUnit XML, image metadata, the commit, JSON results,
Cypher exports and the deployment state under each build's **Artifacts**.

## Stop and restart

```sh
docker compose --env-file jenkins/.env -f jenkins/compose.yaml stop
docker compose --env-file jenkins/.env -f jenkins/compose.yaml start
```

The named volume preserves builds. Do not use `down -v` if build history is needed.
