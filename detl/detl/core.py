"""Specifies the base types for parsing and representing DASware data."""
import abc
import enum
import pathlib


class DWData(object):
    pass


class DASwareParser(object):
    """Abstract type for parsers that read DASware CSV files."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def parse(self, filepath:pathlib.Path) -> DWData:
        """Parses the provided DASware CSV file into a data object.

        Args:
            filepath (str or pathlib.Path): path pointing to the file of interest
        """
        raise NotImplementedError('Whoever implemented {} screwed up.'.format(self.__class__.__name__))


class DASwareVersion(enum.Enum):
    V4 = 'v4'
    V5 = 'v5'
