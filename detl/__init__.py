from . import parsing
from .core import DASwareParser, DASwareVersion, DWData

__version__ = "1.1.2"

parsers = {
    DASwareVersion.V4: parsing.dw4.DASware4Parser,
    DASwareVersion.V5: parsing.dw5.DASware5Parser,
}


def get_parser(filepath) -> DASwareParser:
    """Analyzes a raw DASware CSV file and selects an appropiate parser.

    Args:
        filepath (str or pathlib.Path): path pointing to the file of interest

    Returns:
        DWDParser: a parser that can be used for the provided file type

    Raises:
        NotImlementedError: when the file contents do not match with a known DASware CSV style
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(filepath, "r", encoding="latin-1") as f:
            lines = f.readlines()

    version = None

    if len(lines) > 2 and lines[2].startswith('"FngArchiv";"4.0.1"'):
        version = DASwareVersion.V4
    elif len(lines) > 2 and lines[2].startswith('"FngArchiv";"5.0.0"'):
        version = DASwareVersion.V5
    else:
        raise NotImplementedError("Unsupported file version")

    # select a parser for this version
    parser_cls = parsers[version]
    return parser_cls()


def parse(filepath, *, inoculation_times: dict = None) -> DWData:
    """Parses a raw DASware CSV file into a DWData object.

    Args:
        filepath (str or pathlib.Path): path pointing to the file of interest
        inoculation_times (dict or None): optional overrides for inoculation timepoints
            key (int): reactor number
            value (datetime.datetime): timezone-aware datetime object of the real inoculation time (computer clock!)

    Returns:
        DWData: parsed data object

    Raises:
        NotImlementedError: when the file contents do not match with a known DASware CSV style
    """
    parser = get_parser(filepath)
    data = parser.parse(filepath)

    if inoculation_times:
        for r, dt_inoculate in inoculation_times.items():
            new_process_time = (
                data[r].dataframe["timestamp"] - dt_inoculate
            ).dt.total_seconds() / 3600
            new_process_time[new_process_time < 0] = float("nan")
            data[r].dataframe["process_time"] = new_process_time

    return data
