import importlib.metadata
import pathlib
import sys
import warnings
from typing import overload

from . import parsing
from .core import DASwareParser, DASwareVersion, DWData, Source, read_source

if sys.version_info >= (3, 13):
    from warnings import deprecated
else:
    from typing_extensions import deprecated


__version__ = importlib.metadata.version(__package__ or __name__)

parsers = {
    DASwareVersion.V4: parsing.dw4.DASware4Parser,
    DASwareVersion.V5: parsing.dw5.DASware5Parser,
}


def get_parser(source: Source) -> DASwareParser:
    """Analyzes a raw DASware CSV file and selects an appropiate parser.

    Args:
        source (pathlib.Path, str, bytes or binary stream): Path to the file of interest, its content as bytes, or a binary stream

    Returns:
        DWDParser: a parser that can be used for the provided file type

    Raises:
        NotImlementedError: when the file contents do not match with a known DASware CSV style
    """
    content = read_source(source)
    try:
        lines = content.decode("utf-8").splitlines()
    except UnicodeDecodeError:
        lines = content.decode("latin-1").splitlines()

    if len(lines) > 2 and lines[2].startswith('"FngArchiv";"4.0.1"'):
        version = DASwareVersion.V4
    elif len(lines) > 2 and lines[2].startswith('"FngArchiv";"5.0.0"'):
        version = DASwareVersion.V5
    else:
        raise NotImplementedError("Unsupported file version")

    # select a parser for this version
    parser_cls = parsers[version]
    return parser_cls()


@overload
def parse(source: Source, *, inoculation_times: dict | None = None) -> DWData: ...


@overload
@deprecated("'filepath' is deprecated. Use 'source' instead.")
def parse(*, filepath, inoculation_times: dict | None = None) -> DWData: ...


def parse(
    source: Source | None = None,
    filepath: str | pathlib.Path | None = None,
    *,
    inoculation_times: dict | None = None,
) -> DWData:
    """Parses a raw DASware CSV file into a DWData object.

    Parameters:
    -----------
        source: pathlib.Path | str | bytes
            Path pointing to the file of interest, its content as bytes, or a binary stream. A ``str`` is always interpreted as a path. Streams must be opened in binary mode;\n
            they are read from their current position and are not closed.
        inoculation_times: dict | None
            optional overrides for inoculation timepoints
                key (int): reactor number
                value (datetime.datetime): timezone-aware datetime object of the real inoculation time (computer clock!)

    Returns:
    --------
        DWData: parsed data object

    Raises:
        NotImlementedError: when the file contents do not match with a known DASware CSV style
    """
    if filepath is not None:
        if source is not None:
            raise TypeError("parse() got both 'source' and 'filepath'")
        # @deprecated on an overload only informs type checkers, so warn at runtime too
        warnings.warn(
            "'filepath' is deprecated, use 'source' instead.", DeprecationWarning, stacklevel=2
        )
        source = filepath
    elif source is None:
        raise TypeError("parse() missing required argument: 'source'")

    # Read once, so streams are consumed only once by detection and parsing
    content = read_source(source)

    parser = get_parser(content)
    data = parser.parse(content)

    if inoculation_times:
        for r, dt_inoculate in inoculation_times.items():
            new_process_time = (
                data[r].dataframe["timestamp"] - dt_inoculate
            ).dt.total_seconds() / 3600
            new_process_time[new_process_time < 0] = float("nan")
            data[r].dataframe["process_time"] = new_process_time

    return data
