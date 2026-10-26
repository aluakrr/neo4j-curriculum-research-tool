"""Check actual CLI outputs captured from the packaged runtime image."""

import hashlib
import json
import os
from pathlib import Path

root = Path("/evidence")
stats = json.loads((root / "stats.json").read_text())
assert stats == {
    "courses": 6,
    "elective_groups": 2,
    "HAS_OPTION": 4,
    "PREREQUISITE_OF": 5,
    "POSTREQUISITE_OF": 4,
}, stats
score = json.loads((root / "score.json").read_text())
assert score == {"score": 1.0, "missing": []}, score
options = json.loads((root / "available.json").read_text())
assert options == {"EG1": ["FIN101", "SE201"], "EG2": ["AI301", "REL301"]}, options
cypher = (root / "import.cypher").read_bytes()
assert b"HAS_OPTION" in cypher and b"PREREQUISITE_OF" in cypher
assert cypher == (root / "import-repeat.cypher").read_bytes()
manifest = {
    "status": "pass",
    "commit": os.environ["GIT_COMMIT"],
    "dataset_sha256": hashlib.sha256(Path("data/sample_curriculum.json").read_bytes()).hexdigest(),
    "cypher_sha256": hashlib.sha256(cypher).hexdigest(),
    "checks": ["statistics", "prerequisite_score", "elective_options", "deterministic_cypher"],
}
print(json.dumps(manifest, indent=2))
