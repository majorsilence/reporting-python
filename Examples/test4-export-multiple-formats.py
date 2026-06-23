#! /usr/bin/env python
#
# ExportMultipleFormats — render Orders.rdl to PDF, Excel, CSV, and HTML
# using the rdlnative in-process library (no subprocess / .NET runtime required).
#
# Build the native library first:
#   dotnet publish RdlNative/Majorsilence.Reporting.RdlNative.csproj \
#       -p:PublishAot=true -o /tmp/rdlnative-pub
#
# Run:
#   RDLNATIVE_LIB=/tmp/rdlnative-pub/librdlnative.so python test4-export-multiple-formats.py
#
# Output: orders.pdf / orders.xlsx / orders.csv / orders.html in the output directory

import sys
import os
import platform

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from majorsilence_reporting.report_native import load_library, Report

# SETUP
current_directory = os.path.dirname(os.path.abspath(__file__))
base_directory = os.path.abspath(os.path.join(current_directory, '..', '..', '..'))

db_path = os.path.abspath(os.path.join(base_directory, 'Examples', 'ExportMultipleFormats', 'sqlitetestdb2.db'))
report_path = os.path.abspath(os.path.join(base_directory, 'Examples', 'ExportMultipleFormats', 'Orders.rdl'))

if platform.system() == 'Windows':
    lib_name = 'rdlnative.dll'
elif platform.system() == 'Darwin':
    lib_name = 'librdlnative.dylib'
else:
    lib_name = 'librdlnative.so'

lib_path = os.environ.get(
    'RDLNATIVE_LIB',
    os.path.join(base_directory, 'RdlNative', 'bin', 'Release', 'net10.0', lib_name),
)

output_directory = os.path.join(current_directory, 'output')
os.makedirs(output_directory, exist_ok=True)

# REPORT EXAMPLE
lib = load_library(lib_path)
rpt = Report(lib, report_path)
rpt.set_connection_string('Data Source=' + db_path)

formats = [
    ('orders.pdf',  'pdf'),
    ('orders.xlsx', 'xlsx'),
    ('orders.csv',  'csv'),
    ('orders.html', 'html'),
]

for filename, fmt in formats:
    out_path = os.path.join(output_directory, filename)
    rpt.export(fmt, out_path)
    print(f'Written: {out_path}')
