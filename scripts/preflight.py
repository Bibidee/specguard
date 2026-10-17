"""Fail-closed local release gate for the SpecGuard contract package."""

import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "specguard.py"
SOURCES = sorted((ROOT / "contracts").glob("*.py"))
if SOURCES != [CONTRACT]:
    raise SystemExit(f"Expected exactly contracts/specguard.py; found {[p.name for p in SOURCES]}")

ast.parse(CONTRACT.read_text(encoding="utf-8"), filename=str(CONTRACT))
candidate = Path(sys.executable).with_name("genvm-lint.exe" if os.name == "nt" else "genvm-lint")
# Prefer the linter installed beside the interpreter running this release gate;
# a globally installed linter can target a different SDK/runtime.
lint = str(candidate) if candidate.exists() else (shutil.which("genvm-lint") or shutil.which("genvm-lint.exe"))
if not lint:
    raise SystemExit("genvm-lint not found; install pinned requirements")

env = os.environ.copy()
env["GENVM_VERSION"] = "v0.2.16"
local_genvm_root = ROOT / ".genvmroot"
local_runner = local_genvm_root / "runners" / "py-lib-genlayer-std" / "src" / "genlayer"
if local_runner.is_dir():
    # An explicitly provisioned SDK cache can be used on constrained hosts.
    # It is ignored and never part of the release artifact.
    env["GENVMROOT"] = str(local_genvm_root)

def run(command):
    print("+", " ".join(map(str, command)), flush=True)
    subprocess.run(command, cwd=ROOT, env=env, check=True)

run([sys.executable, "-m", "compileall", "-q", "contracts", "tests"])
run([sys.executable, "-m", "pytest", "tests", "-q"])
run([lint, "check", str(CONTRACT), "--json"])

target = ROOT / "artifacts" / "specguard.abi.json"
with tempfile.TemporaryDirectory(prefix="specguard-abi-", dir=ROOT) as temporary:
    generated = Path(temporary) / "specguard.abi.json"
    run([lint, "schema", str(CONTRACT), "--output", str(generated)])
    expected = generated.read_bytes().replace(b"\r\n", b"\n")
    actual = target.read_bytes().replace(b"\r\n", b"\n") if target.exists() else b""
    if expected != actual:
        raise SystemExit("Generated ABI/schema differs from committed artifacts/specguard.abi.json")
    if not isinstance(json.loads(expected.decode("utf-8")), dict):
        raise SystemExit("Generated ABI/schema is invalid")

print("SpecGuard preflight PASS: deployable-source count, syntax, tests, lint, and ABI/schema")
