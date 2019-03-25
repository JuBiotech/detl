import pathlib

from .. import core


class DASware4Parser(core.DASwareParser):
    def parse(self, filepath:pathlib.Path) -> core.DWData:
        """Parses the provided DASware CSV file into a data object.

        Args:
            filepath (str or pathlib.Path): path pointing to the file of interest
        """
        raise NotImplementedError()

