import os
import shutil
import subprocess
import tempfile

VALID_TYPES  = frozenset({"pdf", "csv", "xlsx", "xlsx_table", "xml", "rtf", "tif", "tifb", "html", "mht"})
BINARY_TYPES = frozenset({"pdf", "tif", "tifb", "rtf", "xlsx", "xlsx_table"})


class ReportAot:
    """
    Generates reports via the AOT or self-contained RdlCmd binary.

    Unlike Report, this class does not accept a path_to_dotnet argument —
    rdl_cmd_path must point directly to the native executable (e.g. RdlCmd on
    Linux/macOS, RdlCmd.exe on Windows).  No .NET runtime is required.

    Usage::

        from majorsilence_reporting import ReportAot

        rpt = ReportAot(
            report_path  = '/path/to/report.rdl',
            rdl_cmd_path = '/path/to/RdlCmd',
        )
        rpt.set_connection_string('Data Source=/path/to/db.sqlite')
        rpt.set_parameter('Country', 'Germany')

        rpt.export('pdf', '/tmp/output.pdf')
        data = rpt.export_to_memory('pdf')   # bytes for binary, str for text

    Supported formats: pdf, csv, xlsx, xlsx_table, xml, rtf, tif, tifb, html, mht
    """

    def __init__(self, report_path: str, rdl_cmd_path: str) -> None:
        self._report_path    = report_path
        self._rdl_cmd_path   = rdl_cmd_path
        self._connection_string: str | None = None
        self._parameters: dict[str, str] = {}

    def set_parameter(self, name: str, value: str) -> None:
        """Set a report parameter value."""
        self._parameters[name] = value

    def set_connection_string(self, connection_string: str) -> None:
        """Override the connection string defined in the RDL."""
        self._connection_string = connection_string

    def export(self, format: str, export_path: str) -> None:
        """Render the report and save it to export_path.

        format      -- output format; defaults to "pdf" if unrecognised
        export_path -- destination file path
        """
        if format not in VALID_TYPES:
            format = "pdf"

        fd, tmp = tempfile.mkstemp()
        os.close(fd)
        tmp_dir = os.path.dirname(tmp)
        shutil.copyfile(self._report_path, tmp)

        rdl_arg = f"/f{tmp}"
        for i, (key, val) in enumerate(self._parameters.items()):
            rdl_arg += ("?" if i == 0 else "&") + f"{key}={val}"

        cmd = [self._rdl_cmd_path, rdl_arg, f"/t{format}", f"/o{tmp_dir}"]
        if self._connection_string:
            cmd.append(f"/c{self._connection_string}")

        subprocess.run(cmd, check=True)

        tmp_out = os.path.join(tmp_dir, os.path.basename(tmp) + f".{format}")
        shutil.copyfile(tmp_out, export_path)
        os.remove(tmp)
        os.remove(tmp_out)

    def export_to_memory(self, format: str) -> bytes | str:
        """Render the report and return the output.

        Returns bytes for binary formats (pdf, tif, tifb, rtf, xlsx, xlsx_table)
        and str for text formats.  format defaults to "pdf" if unrecognised.
        """
        if format not in VALID_TYPES:
            format = "pdf"

        fd, tmp = tempfile.mkstemp()
        os.close(fd)
        self.export(format, tmp)

        with open(tmp, "rb" if format in BINARY_TYPES else "r") as f:
            data = f.read()
        os.remove(tmp)
        return data
