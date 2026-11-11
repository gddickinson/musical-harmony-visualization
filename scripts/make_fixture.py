"""Write tests/fixtures/harmony_reference.json: the repo's Python code run on every style progression plus a custom one.

The node tests (web/static/*.test.mjs) and the Verify page compare the browser engine against this file;
tests/test_web.py checks that it is still current (numbers compared with a tolerance).

Run: python scripts/make_fixture.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from web.reference import reference_cases  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "harmony_reference.json"


def main():
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE.write_text(json.dumps(reference_cases(), separators=(",", ":")))
    print(f"wrote {FIXTURE.relative_to(ROOT)} ({FIXTURE.stat().st_size / 1e3:.0f} kB)")


if __name__ == "__main__":
    main()
