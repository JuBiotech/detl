import datetime
import logging
import pathlib

import numpy
import pandas
import pytz

from .. import core
from . import common

logger = logging.getLogger("detl.parsing.dw4")


BLOCKPARSERS = {
    "Info": common.parse_generic,
    "CoreInfo": common.parse_generic,
    "ProjectInfo": common.parse_generic_T,
    "TrackInfo": common.parse_generic_T,
    "TrackData": common.parse_generic,
    "Setup": common.parse_generic,
    "Unit": common.parse_generic,
    "Requirements": common.parse_requirements,
    "Sensor Elements": common.parse_generic,
    "Device Channels": common.parse_generic,
    "Profiles": common.parse_profiles,
    "Events": common.parse_generic,
    "Fb-Pro": common.parse_generic,
    "Procedure": common.parse_generic,
    "Profile Columns": common.parse_profile_columns,
    "Plant": common.parse_generic,
    "Units": common.parse_generic,
    "Sensors": common.parse_generic,
    "Modules": common.parse_generic,
    "External Servers": common.parse_generic,
    "External Values": common.parse_generic,
    "Internal Values": common.parse_generic,
    "Setups": common.parse_generic,
}

columnmapping = {
    "volume_pv": "V\\d\\.PV",
    "temperature_sp": "T\\d\\.SP",
    "temperature_pv": "T\\d\\.PV",
    "temperature_out": "T\\d\\.Out",
    "stirrer_speed_sp": "N\\d\\.SP",
    "stirrer_speed_pv": "N\\d\\.PV",
    "stirrer_torque_pv": "Torque\\d\\.PV",
    "aeration_sp": "F\\d\\.SP",
    "aeration_pv": "F\\d\\.PV",
    "aeration_x_o2_sp": "XO2 \\d\\.SP",
    "aeration_x_o2_pv": "XO2 \\d\\.PV",
    "aeration_x_co2_sp": "XCO2 \\d\\.SP",
    "aeration_x_co2_pv": "XCO2 \\d\\.PV",
    "ph_sp": "pH\\d\\.SP",
    "ph_pv": "pH\\d\\.PV",
    "ph_out": "pH\\d\\.Out",
    "do_sp": "DO\\d\\.SP",
    "do_pv": "DO\\d\\.PV",
    "do_out": "DO\\d\\.Out",
    "off-gas_pv": "F\\d\\.Out",
    "off-gas_x_o2_pv": "XO2 \\d\\.Out",
    "off-gas_x_co2_pv": "XCO2 \\d\\.Out",
    "otr_pv": "OTR\\d",
    "vot_pv": "VOT\\d",
    "ctr_pv": "CTR\\d",
    "vct_pv": "VCT\\d",
    "rq_pv": "RQ\\d",
    "pump_a_rate_sp": "FA\\d\\.SP",
    "pump_a_rate_pv": "FA\\d\\.PV",
    "pump_a_volume_pv": "VA\\d\\.PV",
    "pump_b_rate_sp": "FB\\d\\.SP",
    "pump_b_rate_pv": "FB\\d\\.PV",
    "pump_b_volume_pv": "VB\\d\\.PV",
    "pump_c_rate_sp": "FC\\d\\.SP",
    "pump_c_rate_pv": "FC\\d\\.PV",
    "pump_c_volume_pv": "VC\\d\\.PV",
    "pump_d_rate_sp": "FD\\d\\.SP",
    "pump_d_rate_pv": "FD\\d\\.PV",
    "pump_d_volume_pv": "VD\\d\\.PV",
    "absorption_pv": "AU\\d",
    "turbidity_pv": "CX\\d",
    "level_pv": "Level\\d\\.PV",
    "redox_sp": "RD\\d\\.SP",
    "redox_pv": "RD\\d\\.PV",
    "redox_out": "RD\\d\\.Out",
    "offline_a": "Offline\\d\\.A",
    "offline_b": "Offline\\d\\.B",
    "offline_c": "Offline\\d\\.C",
    "offline_d": "Offline\\d\\.D",
    "opc_a": "OPC\\d\\.A",
    "opc_b": "OPC\\d\\.B",
    "opc_c": "OPC\\d\\.C",
    "opc_d": "OPC\\d\\.D",
    "balance_a_p": "MA\\d\\.PV",
    "balance_b_pv": "MB\\d\\.PV",
    "balance_c_pv": "MC\\d\\.PV",
    "balance_d_pv": "MD\\d\\.PV",
    "external_a_pv": "External\\d\\.A",
    "external_b_pv": "External\\d\\.B",
    "external_c_pv": "External\\d\\.C",
    "external_d_pv": "External\\d\\.D",
}


class DASware4Parser(core.DASwareParser):
    def parse(self, filepath) -> core.DWData:
        """Parses the provided DASware CSV file into a data object.

        Args:
            filepath (str or pathlib.Path): path pointing to the file of interest
        """
        scoped_blocks = common.split_blocks(filepath)
        dd = common.transform_to_dwdata(scoped_blocks, BLOCKPARSERS, version=core.DASwareVersion.V5)

        for _, reactor in dd.items():
            reactor._dataframe = common.transform_trackdata(
                reactor.trackdata, columnmapping, core.DASwareVersion.V4
            )

        return dd
