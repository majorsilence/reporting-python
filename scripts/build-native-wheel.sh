#!/usr/bin/env bash
# =============================================================================
# build-native-wheel.sh — Build and smoke-test a local wheel with bundled
#                          rdlnative libraries.
#
# Usage:
#   ./scripts/build-native-wheel.sh [RELEASE_TAG]
#
#   RELEASE_TAG  GitHub release tag to download native libs from.
#                Defaults to the latest release of majorsilence/Reporting.
#
# Examples:
#   ./scripts/build-native-wheel.sh           # use latest rdlnative release
#   ./scripts/build-native-wheel.sh 26.0.0    # use a specific release
#
# Prerequisites:
#   pip install build wheel
#   gh (GitHub CLI) — https://cli.github.com — must be authenticated
#
# What this script does:
#   1. Downloads the rdlnative zip for your platform from majorsilence/Reporting
#   2. Unpacks native libs into src/majorsilence_reporting/native/
#   3. Builds the wheel and verifies native libs are inside it
#   4. Creates a temporary venv, installs the wheel
#   5. Runs Examples/test5-set-data-from-code.py as a smoke test
#
# To install the built wheel in your own project afterwards:
#   pip install dist/majorsilence_reporting-*.whl --force-reinstall
# =============================================================================

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NATIVE_DIR="$REPO_ROOT/src/majorsilence_reporting/native"
EXAMPLES_DIR="$REPO_ROOT/Examples"
WORK_DIR="/tmp/rdlnative-build-$$"
TEST_VENV="$WORK_DIR/test-venv"

cleanup() { rm -rf "$WORK_DIR"; }
trap cleanup EXIT

# ── Resolve release tag ───────────────────────────────────────────────────────
echo "=== Resolving rdlnative release ==="
if [[ $# -ge 1 ]]; then
    RELEASE_TAG="$1"
else
    echo "No release tag specified — fetching latest from majorsilence/Reporting..."
    RELEASE_TAG=$(gh release view --repo majorsilence/Reporting --json tagName -q .tagName)
fi
echo "Using release: $RELEASE_TAG"

# ── Detect platform asset ─────────────────────────────────────────────────────
OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
    Linux)
        case "$ARCH" in
            x86_64)  ASSET_PATTERN="*-majorsilence-reporting-rdlnative-linux-x64.zip" ;;
            aarch64) ASSET_PATTERN="*-majorsilence-reporting-rdlnative-linux-arm64.zip" ;;
            *)       echo "Unsupported Linux arch: $ARCH"; exit 1 ;;
        esac ;;
    Darwin)
        ASSET_PATTERN="*-majorsilence-reporting-rdlnative-osx.zip" ;;
    *)
        echo "Unsupported OS: $OS (run this script on Linux or macOS)"
        exit 1 ;;
esac
echo "Asset pattern: $ASSET_PATTERN"

# ── Download native libs ──────────────────────────────────────────────────────
echo ""
echo "=== Downloading native libs ==="
mkdir -p "$WORK_DIR"
gh release download "$RELEASE_TAG" \
    --repo majorsilence/Reporting \
    --pattern "$ASSET_PATTERN" \
    --dir "$WORK_DIR"

# ── Extract ───────────────────────────────────────────────────────────────────
mkdir -p "$WORK_DIR/unpacked"
ASSET=$(ls "$WORK_DIR"/*.zip | head -1)
echo "Extracting: $(basename "$ASSET")"
unzip -q "$ASSET" -d "$WORK_DIR/unpacked"
echo "Zip contents:"
find "$WORK_DIR/unpacked" -type f

# ── Copy into package ─────────────────────────────────────────────────────────
echo ""
echo "=== Copying native libs into package ==="
find "$NATIVE_DIR" -maxdepth 1 -type f ! -name '.gitkeep' ! -name '.gitignore' -delete
find "$WORK_DIR/unpacked" -type f -exec cp -v {} "$NATIVE_DIR/" \;
echo "native/ contents:"
ls -lh "$NATIVE_DIR/"

# ── Create venv with build tools ─────────────────────────────────────────────
echo ""
echo "=== Setting up build venv ==="
python3 -m venv "$TEST_VENV"
"$TEST_VENV/bin/pip" install --quiet build wheel

# ── Build wheel ───────────────────────────────────────────────────────────────
echo ""
echo "=== Building wheel ==="
cd "$REPO_ROOT"
mkdir -p dist
"$TEST_VENV/bin/python" -m build --wheel --outdir dist/

# ── Verify wheel contains native libs ────────────────────────────────────────
echo ""
echo "=== Verifying wheel ==="
WHEEL=$(ls dist/majorsilence_reporting-*.whl | tail -1)
NATIVE_FILES=$("$TEST_VENV/bin/python" -m zipfile -l "$WHEEL" | grep native/ || true)
if [[ -z "$NATIVE_FILES" ]]; then
    echo "ERROR: no native/ files found in wheel — packaging fix needed"
    exit 1
fi
echo "$NATIVE_FILES"
echo "Wheel: $WHEEL ($(du -sh "$WHEEL" | cut -f1))"

# ── Install wheel into the same venv for smoke test ──────────────────────────
echo ""
echo "=== Installing wheel ==="
"$TEST_VENV/bin/pip" install --quiet "$WHEEL"

echo ""
echo "=== Running smoke test (test5-set-data-from-code.py) ==="
echo "─────────────────────────────────────────────────────────"
REPORT_PATH="$EXAMPLES_DIR/SalesReport.rdl" \
    "$TEST_VENV/bin/python" "$EXAMPLES_DIR/test5-set-data-from-code.py"
echo "─────────────────────────────────────────────────────────"

echo ""
echo "All done. Smoke test passed."
echo ""
echo "To install in your own project:"
echo "  pip install \"$WHEEL\" --force-reinstall"
