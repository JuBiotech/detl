import collections
import datetime
import logging
import pathlib
import re
import warnings
from io import StringIO

import numpy
import pandas

from .. import core
from . import utils

logger = logging.getLogger("detl.parsing.common")


def split_blocks(filepath: pathlib.Path) -> dict:
    """Reads a CSV file and splits its contents into scoped blocks.

    Args:
        filepath (pathlib.Path): path to the raw CSV

    Returns:
        scoped_blocks (dict): dicationary mapping scope to dictionary of blocks
    """
    if not isinstance(filepath, (str, pathlib.Path)):
        raise ValueError("Please provide filepath either as str or pathlib.Path object")

    # split the entire file into table-blocks
    blocks = [[]]
    with pathlib.Path(filepath).open(mode="r", errors="replace") as file:
        for line in file:
            if len(line) == 1:
                blocks.append([])
            else:
                blocks[-1].append(line)
    # drop empty blocks
    blocks = [block for block in blocks if len(block) > 1]

    # group blocks by scope (None or reactor-number)
    scoped_blocks = collections.defaultdict(dict)
    scope = None
    for blocklines in blocks:
        blockheader = blocklines[0].strip()
        setup_matches = re.findall(r'"\[Setup(\d+)\]"', blockheader)
        track_matches = re.findall(r'"\[TrackData(\d+)\]"', blockheader)
        if len(track_matches) == 1:
            scope = int(track_matches[0])
        elif blockheader == '"[Events]"':
            scope = None
        elif len(setup_matches) == 1:
            scope = int(setup_matches[0])
        blockheader = blockheader[2:-2]
        if scope:
            blockheader = blockheader.strip(str(scope))
        scoped_blocks[scope][blockheader] = "".join(blocklines[1:]).strip()
    return scoped_blocks


def transform_to_dwdata(
    scoped_blocks: dict, blockparsers: dict, version: core.DASwareVersion
) -> core.DWData:
    dd = core.DWData(version)
    for scope, blocks in scoped_blocks.items():
        if scope is not None and not scope in dd:
            dd[scope] = core.ReactorData(scope)
        for header, block in blocks.items():
            if not header in blockparsers:
                logger.warn(f'No parser found for block "{header}"')
                continue
            blockparser = blockparsers[header]
            if blockparser is not None:
                try:
                    attr, df = blockparser(header, block, scope)
                    if scope is None:
                        setattr(dd, attr, df)
                    else:
                        setattr(dd[scope], attr, df)
                except NotImplementedError as ex:
                    logger.debug(
                        f'scope {scope}: Parsing function for "{header}" is not implemented'
                    )
                except:
                    logger.warning(f'scope {scope}: Failed to parse block "{header}"')
    return dd


def parse_generic(header, block, scope):
    df = pandas.read_csv(StringIO(block), sep=";")
    attr = "_" + header.lower().replace(" ", "_").replace("-", "_")
    return (attr, df)


def parse_generic_T(header, block, scope):
    attr, df = parse_generic(header, block, scope)
    return (attr, df.T)


def parse_requirements(header, block, scope):
    raise NotImplementedError()


def parse_profiles(header, block, scope):
    raise NotImplementedError()


def parse_profile_columns(header, block, scope):
    raise NotImplementedError()


def transform_trackdata(
    trackdata: pandas.DataFrame, columnmapping: dict, version: core.DASwareVersion
) -> pandas.DataFrame:
    """Parses trackdata to an useful DataFrame.

    Args:
        trackdata (pandas.DataFrame): Trackdata derived from DASGIP raw data file
        columnmapping (dict): Mapping from trackdata column names to reasonable column names
        version (core.DASwareVersion): inform about the DASware version of the file that is being processed

    Returns:
        transformed_data (pandas.DataFrame): DataFrame with structured data
    """
    transformed_data = pandas.DataFrame(
        index=trackdata.index,
        columns=["timestamp", "duration", "process_time"],
    )
    transformed_data["timestamp"] = [utils.dwtimestamp_to_utc(t) for t in trackdata["Timestamp"]]
    transformed_data["duration"] = trackdata["Duration"] * 24

    magic_time = datetime.datetime.strptime("1899-12-30 00:00:00", "%Y-%m-%d %H:%M:%S")
    switch = False
    if version == core.DASwareVersion.V4:
        ser = trackdata.filter(regex=".*Inoculation Time.*", axis="columns").squeeze()
    elif version == core.DASwareVersion.V5:
        ser = trackdata.filter(regex=".*InoculationTime.*", axis="columns").squeeze()
    else:
        raise NotImplementedError(f"Unknown DASwareVersion: {version}")
    process_time = numpy.full(len(ser), numpy.nan)

    if not ser.empty:
        for i in range(len(ser)):
            if pandas.notna(ser[i]):
                td = datetime.datetime.strptime(ser[i], "%Y-%m-%d %H:%M:%S") - magic_time

                if (not switch) and (td.total_seconds() > 0):
                    switch = True
                    process_time[i - 1] = float(0)

                if switch:
                    process_time[i] = td.total_seconds() / 3600

    transformed_data["process_time"] = process_time

    for key, reg in columnmapping.items():
        new_data = trackdata.filter(regex=reg, axis="columns").squeeze()
        if (not new_data.empty) and (not new_data.isnull().all()):
            transformed_data.loc[:, key] = new_data

    transformed_data = transformed_data.fillna(method="ffill")

    return transformed_data
