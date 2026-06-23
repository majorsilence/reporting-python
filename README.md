# Majorsilence Reporting — Python Wrappers

Three wrappers are provided for generating reports from Python. Pick the one that matches how you deploy the reporting engine:

| Wrapper | Mechanism | Requires |
|---|---|---|
| `majorsilence_reporting.Report` | subprocess → RdlCmd (.NET DLL) | .NET runtime on the host |
| `majorsilence_reporting.ReportAot` | subprocess → RdlCmd (self-contained or AOT binary) | nothing extra |
| `majorsilence_reporting.report_native.Report` | in-process ctypes FFI → rdlnative shared library | nothing extra |

**Python 3.10 or later** is required (union type hints `X | Y` are used throughout).

No pip packages are needed at runtime. All three wrappers use the Python standard library only.

---

## Setup

### Install Python

Python 3.10 or later is required.

- **Linux (Debian/Ubuntu):**
  ```bash
  sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv
  python3 --version
  ```
- **macOS** (via Homebrew):
  ```bash
  brew install python
  python3 --version
  ```
- **Windows** — download the installer from [python.org](https://www.python.org/downloads/) and ensure "Add Python to PATH" is checked, or install via winget:
  ```powershell
  winget install Python.Python.3.13
  python --version
  ```

### Create a virtual environment (recommended)

```bash
python3 -m venv .venv

# Activate — Linux/macOS:
source .venv/bin/activate

# Activate — Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

### Install the package

From the repo root:

```bash
pip install -e .                   # editable install from source
# or
pip install -e ".[dev]"            # also installs pytest
```

Or without installing, add `src/` to your `sys.path`:

```python
import sys, os
sys.path.insert(0, '/path/to/reporting-python/src')
```

---

## Option 1 — `Report` (subprocess, .NET runtime required)

Use this when you have the .NET runtime installed on the host and want to run `RdlCmd.dll` through `dotnet`.

```python
from majorsilence_reporting import Report

rpt = Report(
    report_path    = "/path/to/report.rdl",
    rdl_cmd_path   = "/path/to/RdlCmd.dll",   # or RdlCmd.exe on Windows
    path_to_dotnet = "dotnet",                  # omit on Windows with a native exe
)
rpt.set_connection_string("Data Source=/path/to/northwindEF.db")
rpt.set_parameter("Country", "Germany")

# Export to a file
rpt.export("pdf", "/tmp/output.pdf")

# Export to memory (bytes for binary formats, str for text formats)
data = rpt.export_to_memory("pdf")
```

### Windows

```python
rpt = Report(
    report_path  = r"C:\reports\report.rdl",
    rdl_cmd_path = r"C:\RdlCmd\RdlCmd.exe",
)
```

---

## Option 2 — `ReportAot` (subprocess, no runtime required)

Use this with an AOT-compiled or self-contained RdlCmd binary. No `path_to_dotnet` argument — the binary runs directly.

Download the appropriate binary from the release:
- `majorsilence-reporting-rdlcmd-aot-linux.zip` → `linux-x64/` or `linux-arm64/`
- `majorsilence-reporting-rdlcmd-aot-osx.zip` → `osx-x64/` or `osx-arm64/`
- `majorsilence-reporting-rdlcmd-aot-windows.zip` → `win-x64/` or `win-arm64/`

Or use the self-contained (non-AOT) build from `majorsilence-reporting-rdlcmd-self-contained.zip`.

```python
from majorsilence_reporting import ReportAot

rpt = ReportAot(
    report_path  = "/path/to/report.rdl",
    rdl_cmd_path = "/path/to/RdlCmd",   # RdlCmd.exe on Windows
)
rpt.set_connection_string("Data Source=/path/to/northwindEF.db")
rpt.set_parameter("Country", "Germany")

rpt.export("pdf", "/tmp/output.pdf")
data = rpt.export_to_memory("xlsx")
```

On Linux/macOS, make the binary executable:

```bash
chmod +x /path/to/RdlCmd
```

---

## Option 3 — `report_native.Report` (in-process FFI, no subprocess)

Use this for the lowest overhead: the reporting engine runs inside the Python process via `ctypes`. No subprocess is spawned.

Download the native shared library from the release (`majorsilence-reporting-rdlnative-linux.zip`, `-osx.zip`, or `-windows.zip`) and extract it. The directory will contain the shared library and all its sibling libraries.

| Platform | Library filename |
|---|---|
| Linux | `librdlnative.so` |
| macOS | `librdlnative.dylib` |
| Windows | `rdlnative.dll` |

```python
from majorsilence_reporting.report_native import load_library, Report

# Load once per process — pass the full path to the shared library.
# All sibling libraries in the same directory are loaded automatically.
lib = load_library("/path/to/librdlnative.so")

rpt = Report(lib, "/path/to/report.rdl")
rpt.set_connection_string("Data Source=/path/to/northwindEF.db")
rpt.set_parameter("Country", "Germany")

# Export to a file
rpt.export("pdf", "/tmp/output.pdf")

# Export to memory — returns bytes directly from the native buffer (no temp file)
data = rpt.export_to_memory("pdf")
```

`load_library()` sets `RDLNATIVE_LIB_DIR` and pre-loads sibling `.so`/`.dylib` files with `RTLD_GLOBAL` so that .NET's P/Invoke resolver can find them. Call it once at startup before creating any `Report` instances.

---

## Supported export formats

All three wrappers accept the same format strings:

| Format | Description |
|---|---|
| `pdf` | PDF (default if unrecognised format given) |
| `csv` | Comma-separated values |
| `xlsx` | Excel workbook |
| `xlsx_table` | Excel workbook (table style) |
| `xml` | XML |
| `rtf` | Rich Text Format |
| `tif` | TIFF image |
| `tifb` | TIFF image (black & white) |
| `html` | HTML |
| `mht` | MHTML |

---

## Running the tests

The test suite (`tests/test_report_native.py`) covers `report_native`. It requires a published `rdlnative` shared library and is skipped automatically if the library is not found.

```bash
# Build the native library first (from the main Reporting repo)
dotnet publish RdlNative -c Release-DrawingCompat -r linux-x64 -f net10.0 \
    --self-contained true -p:PublishAot=true \
    -o /tmp/rdlnative-pub

# Run tests (set REPORTING_REPO_ROOT to the Reporting repo clone)
RDLNATIVE_LIB=/tmp/rdlnative-pub/librdlnative.so \
REPORTING_REPO_ROOT=/path/to/Reporting \
    python -m pytest -v
```

On macOS replace `linux-x64` with `osx-arm64` (or `osx-x64`) and `librdlnative.so` with `librdlnative.dylib`.

---

## Examples

See the `Examples/` subdirectory for runnable scripts:

- `test1.py` — basic PDF export to file
- `test2-parameters.py` — passing report parameters
- `test3-streaming.py` — exporting to memory for streaming responses
