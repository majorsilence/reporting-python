#! /usr/bin/env python3
#
# Feed data directly into a report from Python — no database required.
# Uses the in-process native library (no subprocess, no .NET runtime).
#
# Install:
#   python3 -m venv .venv
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
#   REPORT_PATH=/path/to/SalesReport.rdl \
#   python3 test5-set-data-from-code.py
#
# Note: dict keys must exactly match the <Field Name="..."> values in the RDL.
# No connection string is needed — SkipDatabaseSchemaValidation is set automatically.

import os
from majorsilence_reporting import load_bundled_library
from majorsilence_reporting.report_native import load_library, Report

# ── Configuration ─────────────────────────────────────────────────────────────
_here = os.path.dirname(os.path.abspath(__file__))
REPORT_PATH = os.environ.get('REPORT_PATH', os.path.join(_here, 'SalesReport.rdl'))
# ──────────────────────────────────────────────────────────────────────────────

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
os.makedirs(output_dir, exist_ok=True)

# Use the library bundled with the platform wheel; fall back to a manual path.
if 'RDLNATIVE_LIB' in os.environ:
    lib = load_library(os.environ['RDLNATIVE_LIB'])
else:
    lib = load_bundled_library()

# DATA — keys must match <Field Name="..."> in SalesReport.rdl exactly
sales_data = [
    {'Product': 'Chai',                   'Region': 'North America', 'Amount': '1250.00', 'Quantity': '50'},
    {'Product': 'Chang',                  'Region': 'North America', 'Amount':  '980.50', 'Quantity': '42'},
    {'Product': 'Aniseed Syrup',          'Region': 'Europe',        'Amount':  '432.00', 'Quantity': '24'},
    {'Product': "Chef Anton's Cajun",     'Region': 'Europe',        'Amount': '1875.25', 'Quantity': '75'},
    {'Product': "Grandma's Boysenberry",  'Region': 'Asia Pacific',  'Amount':  '640.00', 'Quantity': '32'},
    {'Product': "Uncle Bob's Organic",    'Region': 'North America', 'Amount':  '315.60', 'Quantity': '18'},
    {'Product': 'Northwoods Cranberry',   'Region': 'North America', 'Amount':  '560.00', 'Quantity': '20'},
    {'Product': 'Mishi Kobe Niku',        'Region': 'Asia Pacific',  'Amount': '4500.00', 'Quantity': '30'},
    {'Product': 'Ikura',                  'Region': 'Asia Pacific',  'Amount': '1980.00', 'Quantity': '36'},
    {'Product': 'Queso Cabrales',         'Region': 'Europe',        'Amount':  '850.00', 'Quantity': '25'},
    {'Product': 'Queso Manchego La',      'Region': 'Europe',        'Amount':  '720.00', 'Quantity': '30'},
    {'Product': 'Konbu',                  'Region': 'Asia Pacific',  'Amount':  '180.00', 'Quantity': '24'},
    {'Product': 'Tofu',                   'Region': 'Asia Pacific',  'Amount':  '560.00', 'Quantity': '40'},
    {'Product': 'Genen Shouyu',           'Region': 'Asia Pacific',  'Amount':  '310.00', 'Quantity': '26'},
    {'Product': 'Pavlova',                'Region': 'Asia Pacific',  'Amount':  '825.00', 'Quantity': '55'},
    {'Product': 'Alice Mutton',           'Region': 'Europe',        'Amount': '2340.00', 'Quantity': '26'},
    {'Product': 'Carnarvon Tigers',       'Region': 'Asia Pacific',  'Amount': '6200.00', 'Quantity': '31'},
    {'Product': 'Teatime Biscuits',       'Region': 'Europe',        'Amount':  '291.60', 'Quantity': '36'},
    {'Product': "Sir Rodney's Marmalade", 'Region': 'Europe',        'Amount': '1245.00', 'Quantity': '45'},
    {"Product": "Sir Rodney's Scones",    'Region': 'Europe',        'Amount':  '350.00', 'Quantity': '50'},
]

rpt = Report(lib, REPORT_PATH)
rpt.add_data('Data', sales_data)

out_path = os.path.join(output_dir, 'sales-report.pdf')
rpt.export('pdf', out_path)
print('Written: output/sales-report.pdf')
