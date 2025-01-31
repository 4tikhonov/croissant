"""graph_test module."""

import json
import os

from etils import epath
import pytest
from rdflib import term

from mlcroissant._src.core.issues import Issues
from mlcroissant._src.structure_graph.nodes.metadata import Metadata

Literal = term.Literal


_DATASETS_FOLDER = (
    epath.Path(__file__).parent.parent.parent.parent.parent.parent / "datasets"
)
_JSON_LD_PATHS = [
    path
    for path in _DATASETS_FOLDER.glob("*/*.json")
    if not os.fspath(path).endswith("_by_openml_converter.json")
]


# If this test fails, you probably manually updated a dataset in datasets/.
# Please, use scripts/migrations/migrate.py to migrate datasets.
@pytest.mark.parametrize(
    ["path"],
    [[path] for path in _JSON_LD_PATHS],
)
def test_jsonld_to_python_to_jsonld(path):
    with path.open() as f:
        json_ld = json.load(f)
    issues = Issues()
    metadata = Metadata.from_file(issues, path)
    result = metadata.to_json()
    # `distribution` may not be in the right order:
    if "distribution" in result:
        distribution = result.pop("distribution")
        distribution = {file["name"]: file for file in distribution}
        expected_distribution = json_ld.pop("distribution")
        expected_distribution = {file["name"]: file for file in expected_distribution}
        assert distribution == expected_distribution
    # Check the expected JSON-LD:
    assert result == json_ld
    assert not issues.errors
