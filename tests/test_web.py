"""Web interface tests: every exported endpoint answers, the static build is complete, and the JS engine tests pass.

Run: python -m pytest -q tests/test_web.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from web.app import STATIC, STATIC_ENDPOINTS, app  # noqa: E402

client = TestClient(app)


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200 and "static/main.js" in r.text


@pytest.mark.parametrize("path", STATIC_ENDPOINTS)
def test_endpoint(path):
    r = client.get("/api" + path)
    assert r.status_code == 200, r.text
    assert r.json() is not None


def test_static_build(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_static
    build_static.build(tmp_path / "site")
    assert (tmp_path / "site" / "index.html").read_text().count("APP_STATIC") == 1
    for path in STATIC_ENDPOINTS:
        assert (tmp_path / "site" / "api" / (path.strip("/") + ".json")).exists()


def test_static_assets_referenced_exist():
    html = (STATIC / "index.html").read_text()
    for name in ("style.css", "main.js"):
        assert f"static/{name}" in html and (STATIC / name).exists()


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_js_engine():
    tests = sorted(STATIC.glob("*.test.mjs"))
    for t in tests:
        r = subprocess.run(["node", str(t)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr


# --- project-specific ------------------------------------------------------------------------------------------------
import json  # noqa: E402

import numpy as np  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "harmony_reference.json"


def _close(a, b, path=""):
    """Recursive comparison: numbers with rtol 1e-9 (libm differs across platforms), everything else exact."""
    if isinstance(a, dict):
        assert set(a) == set(b), path
        for k in a:
            _close(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list):
        assert len(a) == len(b), path
        for i, (x, y) in enumerate(zip(a, b)):
            _close(x, y, f"{path}[{i}]")
    elif isinstance(a, float) or isinstance(b, float):
        assert np.isclose(a, b, rtol=1e-9, atol=1e-12), f"{path}: {a} vs {b}"
    elif path.endswith((".pcm_sum", ".pcm_abs_sum")):
        assert abs(a - b) <= 1e-6 * max(1, abs(a)), f"{path}: {a} vs {b}"
    elif "].pcm[" in path:
        assert abs(a - b) <= 1, f"{path}: {a} vs {b}"
    else:
        assert a == b, f"{path}: {a!r} vs {b!r}"


def test_fixture_current():
    """tests/fixtures/harmony_reference.json matches the Python code (rerun scripts/make_fixture.py if not)."""
    from web.reference import reference_cases
    _close(json.loads(json.dumps(reference_cases())), json.loads(FIXTURE.read_text()))


def test_theory_endpoint_matches_python():
    from theory import CHORD_TYPES, ProgressionStyle, get_style_progression
    t = client.get("/api/theory").json()
    assert list(t["chord_types"]) == list(CHORD_TYPES)
    assert [s["name"] for s in t["styles"]] == [s.value for s in ProgressionStyle]
    assert t["styles"][0]["progression"] == [list(p) for p in get_style_progression(ProgressionStyle.JAZZ)]
    assert t == json.loads(FIXTURE.read_text())["theory"]


def test_check_matches_fixture_case():
    ref = json.loads(FIXTURE.read_text())["cases"][-1]
    r = client.post("/api/check", json={"progression": ref["progression"], "config": ref["config"]})
    assert r.status_code == 200
    _close(r.json(), {k: v for k, v in ref.items() if k != "name"})


@pytest.mark.parametrize("body", [
    {"progression": [["H4", "major", 1]]},
    {"progression": [["C4", "nope", 1]]},
    {"progression": [["C4", "major", -1]]},
    {"progression": [["C4", "major", 1]] * 65},
    {"progression": [["C4", "major", 400]]},
    {"progression": [["C4", "major", 1]], "config": {"tempo_bpm": 5}},
])
def test_check_rejects_bad_input(body):
    assert client.post("/api/check", json=body).status_code in (400, 422)


def test_figures_render_pngs():
    r = client.post("/api/figures", json={"progression": [["C4", "major7", 2], ["G4", "dominant7", 2]], "style": "jazz"})
    assert r.status_code == 200
    import base64
    for kind in ("motion", "advanced_analysis"):
        assert base64.b64decode(r.json()[kind])[:8] == b"\x89PNG\r\n\x1a\n"
