import json
from pathlib import Path

from curriculum_graph_tool.cli import main

DATASET = Path(__file__).parents[1] / "data" / "sample_curriculum.json"


def test_stats_command(capsys):
    assert main([str(DATASET), "stats"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["courses"] == 6
    assert payload["HAS_OPTION"] == 4


def test_cypher_output_file(tmp_path):
    target = tmp_path / "import.cypher"
    assert main([str(DATASET), "cypher", "--output", str(target)]) == 0
    assert "MERGE (c:Course" in target.read_text(encoding="utf-8")

