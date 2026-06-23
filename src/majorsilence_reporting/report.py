import os
import shutil
import subprocess
import tempfile

VALID_TYPES = frozenset({"pdf", "csv", "xlsx", "xml", "rtf", "tif", "html"})


class Report:
    """
    Generates reports via the RdlCmd .NET command-line tool.

    Requires a .NET runtime on the host.  For self-contained or AOT builds
    that need no runtime, use ReportAot instead.

    Usage::

        from majorsilence_reporting import Report

        rpt = Report(
            report_path    = '/path/to/report.rdl',
            rdl_cmd_path   = '/path/to/RdlCmd.dll',
            path_to_dotnet = 'dotnet',   # omit on Windows with a native exe
        )
        rpt.set_connection_string('Data Source=/path/to/db.sqlite')
        rpt.set_parameter('Country', 'Germany')

        rpt.export('pdf', '/tmp/output.pdf')
        data = rpt.export_to_memory('pdf')   # bytes for binary, str for text

    Supported formats: pdf, csv, xlsx, xml, rtf, tif, html
    """

    def __init__(
        self,
        report_path: str,
        rdl_cmd_path: str,
        path_to_dotnet: str | None = None,
    ) -> None:
        self._report_path      = report_path
        self._rdl_cmd_path     = rdl_cmd_path
        self._path_to_dotnet   = path_to_dotnet
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

        cmd: list[str] = []
        if self._path_to_dotnet:
            cmd.append(self._path_to_dotnet)
        cmd += [self._rdl_cmd_path, rdl_arg, f"/t{format}", f"/o{tmp_dir}"]
        if self._connection_string:
            cmd.append(f"/c{self._connection_string}")

        subprocess.run(cmd, check=True)

        tmp_out = os.path.join(tmp_dir, os.path.basename(tmp) + f".{format}")
        shutil.copyfile(tmp_out, export_path)
        os.remove(tmp)
        os.remove(tmp_out)

    def export_to_memory(self, format: str) -> bytes | str:
        """Render the report and return the output.

        Returns bytes for binary formats (pdf, tif, rtf) and str for text formats.
        format -- output format; defaults to "pdf" if unrecognised
        """
        if format not in VALID_TYPES:
            format = "pdf"

        fd, tmp = tempfile.mkstemp()
        os.close(fd)
        self.export(format, tmp)

        binary_types = {"pdf", "tif", "rtf"}
        with open(tmp, "rb" if format in binary_types else "r") as f:
            data = f.read()
        os.remove(tmp)
        return data
