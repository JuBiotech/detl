import logging
import numpy
import pathlib
import pandas

from .. import core
from . import common

logger = logging.getLogger('detl.parsing.dw5')


BLOCKPARSERS = {
    'Info': common.parse_generic,
    'CoreInfo': common.parse_generic,
    'ProjectInfo': common.parse_generic_T,
    'TrackInfo': common.parse_generic_T,
    'TrackData': common.parse_generic,
    'Setup': common.parse_generic,
    'Unit': common.parse_generic,
    'Requirements': common.parse_generic,
    'Sensor Elements': common.parse_generic,
    'Device Channels': common.parse_generic,
    'Profiles': common.parse_generic,
    'Events': common.parse_generic,
    'Fb-Pro': common.parse_generic,
    'Procedure': common.parse_generic,
    'Profile Columns': common.parse_generic,
    'Plant': common.parse_generic,
    'Units': common.parse_generic,
    'Sensors': common.parse_generic,
    'Modules': common.parse_generic,
    'External Servers': common.parse_generic,
    'External Values': common.parse_generic,
    'Internal Values': common.parse_generic,
    'Setups': common.parse_generic,
}

class DASware5Parser(core.DASwareParser):
    def parse(self, filepath:pathlib.Path) -> core.DWData:
        """Parses the provided DASware CSV file into a data object.

        Args:
            filepath (str or pathlib.Path): path pointing to the file of interest
        """
        scoped_blocks = common.split_blocks(filepath)
        dd = common.transform_to_dwdata(scoped_blocks, BLOCKPARSERS, version=core.DASwareVersion.V5)
        return dd
