import collections
import logging
import numpy
import pathlib
import pandas
import re
from io import StringIO
import warnings

from .. import core

logger = logging.getLogger('detl.parsing.common')


def split_blocks(filepath:pathlib.Path) -> dict:
    """Reads a CSV file and splits its contents into scoped blocks.

    Args:
        filepath (pathlib.Path): path to the raw CSV

    Returns:
        scoped_blocks (dict): dicationary mapping scope to dictionary of blocks
    """
    if not isinstance(filepath, (str, pathlib.Path)):
        raise ValueError('Please provide filepath either as str or pathlib.Path object')

    # split the entire file into table-blocks
    blocks = [[]]
    with pathlib.Path(filepath).open(mode='r', errors='replace') as file:
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
        setup_matches = re.findall(r'"\[Setup(\d)\]"', blockheader)
        track_matches = re.findall(r'"\[TrackData(\d)\]"', blockheader)
        if len(track_matches) == 1:
            scope = int(track_matches[0])
        elif blockheader == '"[Events]"':
            scope = None
        elif len(setup_matches) == 1:
            scope = int(setup_matches[0])
        blockheader = blockheader[2:-2]
        if scope:
            blockheader = blockheader.strip(str(scope))
        scoped_blocks[scope][blockheader] = ''.join(blocklines[1:]).strip()
    return scoped_blocks


def transform_to_dwdata(scoped_blocks:dict, blockparsers:dict, version:core.DASwareVersion) -> core.DWData:
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
                except:
                    logger.warning(f'scope {scope}: Failed to parse block "{header}"')
    return dd


def parse_generic(header, block, scope):
    df = pandas.read_csv(StringIO(block), sep=';')
    attr = '_' + header.lower().replace(' ', '_').replace('-', '_')
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
