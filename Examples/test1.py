#! /usr/bin/env python3
#
# Basic PDF export using the subprocess runner.
#
# Install:
#   python3 -m venv .venv
#   source .venv/bin/activate        # Linux/macOS
#   .venv\Scripts\activate           # Windows
#   pip install majorsilence-reporting
#
# Download RdlCmd from https://github.com/majorsilence/Reporting/releases
#   Linux/macOS : *-rdlcmd-aot-linux-x64.zip or *-rdlcmd-aot-osx.zip
#   Windows     : *-rdlcmd-aot-windows.zip
# Extract the zip and set RDLCMD_PATH to the RdlCmd (or RdlCmd.exe) binary.
#
# Run:
#   RDLCMD_PATH=/path/to/RdlCmd \
#   DB_PATH=/path/to/northwindEF.db \
#   REPORT_PATH=/path/to/SimpleTest1.rdl \
#   python3 test1.py

import os
from majorsilence_reporting import Report

# ── Configuration ─────────────────────────────────────────────────────────────
_here = os.path.dirname(os.path.abspath(__file__))
RDLCMD_PATH = os.environ.get('RDLCMD_PATH', '/path/to/RdlCmd')
DB_PATH     = os.environ.get('DB_PATH',     os.path.join(_here, 'northwindEF.db'))
REPORT_PATH = os.environ.get('REPORT_PATH', os.path.join(_here, 'SimpleTest1.rdl'))
# ──────────────────────────────────────────────────────────────────────────────

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
os.makedirs(output_dir, exist_ok=True)

rpt = Report(REPORT_PATH, RDLCMD_PATH)
rpt.set_connection_string('Data Source=' + DB_PATH)
rpt.export('pdf', os.path.join(output_dir, 'test1.pdf'))
print('Written: output/test1.pdf')
