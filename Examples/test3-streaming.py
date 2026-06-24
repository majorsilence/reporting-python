#! /usr/bin/env python
#
# Export to memory (bytes) for streaming HTTP responses.
#
# Install:
#   python -m venv .venv
#   source .venv/bin/activate        # Linux/macOS
#   .venv\Scripts\activate           # Windows
#   pip install majorsilence-reporting
#
# Download RdlCmd from https://github.com/majorsilence/Reporting/releases
#   Linux/macOS : *-rdlcmd-aot-linux-x64.zip or *-rdlcmd-aot-osx.zip
#   Windows     : *-rdlcmd-aot-windows.zip
# Extract and set RDLCMD_PATH to the RdlCmd (or RdlCmd.exe) binary.
#
# Run:
#   RDLCMD_PATH=/path/to/RdlCmd \
#   DB_PATH=/path/to/northwindEF.db \
#   REPORT_PATH=/path/to/SimpleTest1.rdl \
#   python test3-streaming.py

import os
from majorsilence_reporting import Report

# ── Configuration ─────────────────────────────────────────────────────────────
RDLCMD_PATH = os.environ.get('RDLCMD_PATH', '/path/to/RdlCmd')
DB_PATH     = os.environ.get('DB_PATH',     '/path/to/northwindEF.db')
REPORT_PATH = os.environ.get('REPORT_PATH', '/path/to/SimpleTest1.rdl')
# ──────────────────────────────────────────────────────────────────────────────

rpt = Report(REPORT_PATH, RDLCMD_PATH)
rpt.set_connection_string('Data Source=' + DB_PATH)
data = rpt.export_to_memory('pdf')

# data is bytes — pass directly to your HTTP response:
#   Flask  : return Response(data, mimetype='application/pdf')
#   Django : return HttpResponse(data, content_type='application/pdf')
#   WSGI   : start_response('200 OK', [('Content-Type', 'application/pdf')]); yield data
print(f'Rendered {len(data):,} bytes')
