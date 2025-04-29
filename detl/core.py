"""Specifies the base types for parsing and representing DASware data."""
import abc
import enum
import pathlib
from typing import Dict

import numpy
import pandas


class DASwareVersion(enum.Enum):
    V4 = "v4"
    V5 = "v5"


class ReactorData(object):
    """Data structure containing data from one reactor."""

    def __init__(self, id: int):
        self._id = id
        self._setup = None
        self._unit = None
        self._requirements = None
        self._sensor_elements = None
        self._device_channels = None
        self._profiles = None
        self._trackdata = None
        self._dataframe = None

    @property
    def id(self) -> int:
        """Number of the reactor."""
        return self._id

    @property
    def setup(self) -> pandas.DataFrame:
        """Dataframe of overall process information."""
        return self._setup

    @property
    def unit(self) -> pandas.DataFrame:
        """Properties of the reactor."""
        return self._unit

    @property
    def requirements(self) -> pandas.DataFrame:
        return self._requirements

    @property
    def sensor_elements(self) -> pandas.DataFrame:
        """Table of connected sensors."""
        return self._sensor_elements

    @property
    def device_channels(self) -> pandas.DataFrame:
        return self._device_channels

    @property
    def profiles(self) -> pandas.DataFrame:
        return self._profiles

    @property
    def trackdata(self) -> pandas.DataFrame:
        """Contains timeseries of mass flows."""
        return self._trackdata

    @property
    def dataframe(self) -> pandas.DataFrame:
        """Primary table of setpoint (SP) and actual (PV) control parameters."""
        return self._dataframe

    def get_closest_data(
        self, points: numpy.array, reference: str = "process_time"
    ) -> pandas.DataFrame:
        """Returns a subset of the reactor data at points closest to the given ones.

        Args:
            points (numpy.array): the data from readings closest to these points will be returned
            reference (str): name of the column to look for points

        Returns:
            filtered_data: DataFrame containing data closest to the given points

        Raises:
            KeyError: when the reference column is not in the DataFrame
        """
        if reference not in self.dataframe.columns:
            raise KeyError("Reference column not in DataFrame")

        idx = [abs(self.dataframe.loc[:, reference] - p).idxmin() for p in points]

        return self.dataframe.loc[idx]


class DWData(Dict[str, ReactorData]):
    """Standardized data type for DASGIP data."""

    def __init__(self, version: DASwareVersion):
        self._version = version
        self._info = None
        self._coreinfo = None
        self._projectinfo = None
        self._trackinfo = None
        self._events = None
        self._fb_pro = None
        self._procedure = None
        self._profile_columns = None
        self._plant = None
        self._units = None
        self._sensors = None
        self._modules = None
        self._external_servers = None
        self._external_values = None
        self._internal_values = None

    @property
    def version(self) -> DASwareVersion:
        """Specifies which DASWARE version was used."""
        return self._version

    @property
    def info(self) -> pandas.DataFrame:
        """Contains version numbers of software modules."""
        return self._info

    @property
    def coreinfo(self) -> pandas.DataFrame:
        """Information about DASWARE and timezone settings."""
        return self._coreinfo

    @property
    def projectinfo(self) -> pandas.DataFrame:
        return self._projectinfo

    @property
    def tracks(self) -> pandas.DataFrame:
        """Metadata about logging settings."""
        return self._trackinfo

    @property
    def events(self) -> pandas.DataFrame:
        """Table of events that happened during the process."""
        return self._events

    @property
    def fb_pro(self) -> pandas.DataFrame:
        return self._fb_pro

    @property
    def procedure(self) -> pandas.DataFrame:
        """Metadata of the experiment"""
        return self._procedure

    @property
    def profile_columns(self) -> pandas.DataFrame:
        return self._profile_columns

    @property
    def plant(self) -> pandas.DataFrame:
        """Metadata of the hardware"""
        return self._plant

    @property
    def units(self) -> pandas.DataFrame:
        """Metadata of the reactor units"""
        return self._units

    @property
    def sensors(self) -> pandas.DataFrame:
        """Metadata of the connected sensors"""
        return self._sensors

    @property
    def modules(self) -> pandas.DataFrame:
        return self._modules

    @property
    def external_servers(self) -> pandas.DataFrame:
        return self._external_servers

    @property
    def external_values(self) -> pandas.DataFrame:
        return self._external_values

    @property
    def internal_values(self) -> pandas.DataFrame:
        return self._internal_values

    def get_narrow_data(self, kdim: str = "process_time"):
        """Returns all data in a narrow DataFrame.

        Args:
            kdim (str): name of the time axis which will be the time axis in the new format.
                        Can be 'timestamp', 'duration', or 'process_time'. 'process_time' will
                        drop all data before valid time information is available.
                        'duration' and 'process_time' will drop the timestamp information to get a clean
                        float-type value column.

        Returns:
            narrow_data: DataFrame containing all data in a narrow format

        Raises:
            KeyError: when the reference column is not in the DataFrame
        """
        if kdim not in {"timestamp", "duration", "process_time"}:
            raise KeyError("kdim must be 'timestamp', 'duration', or 'process_time'.")

        narrow_data = pandas.DataFrame()
        for reactor_id in self:
            if kdim == "process_time":
                _df = (
                    self[reactor_id]
                    .dataframe.dropna()
                    .drop("timestamp", axis="columns")
                    .melt(id_vars=kdim)
                )
            elif kdim == "duration":
                _df = (
                    self[reactor_id].dataframe.drop("timestamp", axis="columns").melt(id_vars=kdim)
                )
            else:
                _df = self[reactor_id].dataframe.melt(id_vars=kdim)

            _df["reactor"] = reactor_id
            _df = _df.astype({"value": float})
            narrow_data = pandas.concat([narrow_data, _df], ignore_index=True)

        narrow_data = narrow_data.rename({kdim: "time"}, axis="columns")[
            ["reactor", "time", "variable", "value"]
        ]

        return narrow_data


class DASwareParser(object):
    """Abstract type for parsers that read DASware CSV files."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def parse(self, filepath: pathlib.Path) -> DWData:
        """Parses the provided DASware CSV file into a data object.

        Args:
            filepath (str or pathlib.Path): path pointing to the file of interest
        """
        raise NotImplementedError(
            "Whoever implemented {} screwed up.".format(self.__class__.__name__)
        )
