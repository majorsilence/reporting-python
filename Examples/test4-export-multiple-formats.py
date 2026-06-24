#! /usr/bin/env python
#
# Export a report to multiple formats using the in-process native library.
# No subprocess is spawned; no .NET runtime is required.
#
# Install:
#   python -m venv .venv
#   source .venv/bin/activate        # Linux/macOS
#   .venv\Scripts\activate           # Windows
#   pip install majorsilence-reporting
#
# The platform-specific wheel (Linux x64/arm64, Windows x64, macOS arm64)
# bundles rdlnative and load_bundled_library() finds it automatically.
#
# On an unsupported platform, download rdlnative manually from
# https://github.com/majorsilence/Reporting/releases (*-rdlnative-*.zip),
# extract it, and set RDLNATIVE_LIB to the shared library path:
#   Linux   : RDLNATIVE_LIB=/path/to/librdlnative.so
#   macOS   : RDLNATIVE_LIB=/path/to/librdlnative.dylib
#   Windows : RDLNATIVE_LIB=C:\path\to\rdlnative.dll
#
# Run:
#   DB_PATH=/path/to/sqlitetestdb2.db \
#   REPORT_PATH=/path/to/Orders.rdl \
#   python test4-export-multiple-formats.py

import os
from majorsilence_reporting import load_bundled_library
from majorsilence_reporting.report_native import load_library, Report

# ── Configuration ─────────────────────────────────────────────────────────────
_here = os.path.dirname(os.path.abspath(__file__))
DB_PATH     = os.environ.get('DB_PATH',     os.path.join(_here, 'sqlitetestdb2.db'))
REPORT_PATH = os.environ.get('REPORT_PATH', os.path.join(_here, 'Orders.rdl'))
# ──────────────────────────────────────────────────────────────────────────────

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
os.makedirs(output_dir, exist_ok=True)

# Use the library bundled with the platform wheel; fall back to a manual path.
if 'RDLNATIVE_LIB' in os.environ:
    lib = load_library(os.environ['RDLNATIVE_LIB'])
else:
    lib = load_bundled_library()

rpt = Report(lib, REPORT_PATH)
rpt.set_connection_string('Data Source=' + DB_PATH)

formats = [
    ('orders.pdf',  'pdf'),
    ('orders.xlsx', 'xlsx'),
    ('orders.csv',  'csv'),
    ('orders.html', 'html'),
]

for filename, fmt in formats:
    out_path = os.path.join(output_dir, filename)
    rpt.export(fmt, out_path)
    print(f'Written: output/{filename}')
