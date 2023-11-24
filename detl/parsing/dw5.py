import logging
import pathlib

import numpy
import pandas

from .. import core
from . import common

logger = logging.getLogger("detl.parsing.dw5")


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
    "volume_pv": "\\.V\\d+\\.VPV",
    "temperature_sp": "\\.T\\d+\\.SP",
    "temperature_pv": "\\.\\.T\\d+\\.PV",
    "temperature_out": "\\.T\\d+\\.Out",
    "stirrer_speed_sp": "\\.N\\d+\\.SP",
    "stirrer_speed_pv": "\\.N\\d+\\.PV",
    "stirrer_torque_pv": "\\.N\\d+\\.TStirPV",
    "aeration_sp": "\\.F\\d+\\.SP",
    "aeration_pv": "\\.F\\d+\\.PV",
    "aeration_air_pv": "\\.FAir\\d+\\.PV",
    "aeration_co2_pv": "\\.FCO2\\d+\\.PV",
    "aeration_o2_pv": "\\.FO2\\d+\\.PV",
    "aeration_n2_pv": "\\.FN2\\d+\\.PV",
    "aeration_x_co2_pv": "\\.XCO2\\d+\\.PV",
    "aeration_x_o2_pv": "\\.XO2\\d+\\.PV",
    "ph_sp": "\\.pH\\d+\\.SP",
    "ph_pv": "\\.pH\\d+\\.PV",
    "ph_out": "\\.pH\\d+\\.Out",
    "do_sp": "\\.DO\\d+\\.SP",
    "do_pv": "\\.DO\\d+\\.PV",
    "do_out": "\\.DO\\d+\\.Out",
    "off-gas_pv": "\\.F\\d+\\.Out",
    "off-gas_x_o2_pv": "\\.XO2\\d+\\.Out",
    "off-gas_x_co2_pv": "\\.XCO2\\d+\\.Out",
    "otr_pv": "\\.OTR\\d+",
    "vot_pv": "\\.VOT\\d+",
    "ctr_pv": "\\.CTR\\d+",
    "vct_pv": "\\.VCT\\d+",
    "rq_pv": "\\.RQ\\d+",
    "pump_a_rate_sp": "\\.FA\\d+\\.SP",
    "pump_a_rate_pv": "\\.FA\\d+\\.PV",
    "pump_a_volume_pv": "\\.VA\\d+\\.PV",
    "pump_b_rate_sp": "\\.FB\\d+\\.SP",
    "pump_b_rate_pv": "\\.FB\\d+\\.PV",
    "pump_b_volume_pv": "\\.VB\\d+\\.PV",
    "pump_c_rate_sp": "\\.FC\\d+\\.SP",
    "pump_c_rate_pv": "\\.FC\\d+\\.PV",
    "pump_c_volume_pv": "\\.VC\\d+\\.PV",
    "pump_d_rate_sp": "\\.FD\\d+\\.SP",
    "pump_d_rate_pv": "\\.FD\\d+\\.PV",
    "pump_d_volume_pv": "\\.VD\\d+\\.PV",
    "absorption_pv": "\\.ODAU\\d+\\.PV",
    "turbidity_pv": "\\.ODCX\\d+\\.PV",
    "level_pv": "\\.Lvl\\d+\\.PV",
    "offline_a": "\\.OfflineA\\d+\\.OfflineA",
    "offline_b": "\\.OfflineB\\d+\\.OfflineB",
    "offline_c": "\\.OfflineC\\d+\\.OfflineC",
    "offline_d": "\\.OfflineD\\d+\\.OfflineD",
    "offline_e": "\\.OfflineE\\d+\\.OfflineE",
    "offline_f": "\\.OfflineF\\d+\\.OfflineF",
    "offline_g": "\\.OfflineG\\d+\\.OfflineG",
    "offline_h": "\\.OfflineH\\d+\\.OfflineH",
    "offline_i": "\\.OfflineI\\d+\\.OfflineI",
    "offline_j": "\\.OfflineJ\\d+\\.OfflineJ",
    "offline_k": "\\.OfflineK\\d+\\.OfflineK",
    "offline_l": "\\.OfflineL\\d+\\.OfflineL",
    "offline_m": "\\.OfflineM\\d+\\.OfflineM",
    "offline_n": "\\.OfflineN\\d+\\.OfflineN",
    "offline_o": "\\.OfflineO\\d+\\.OfflineO",
    "offline_p": "\\.OfflineP\\d+\\.OfflineP",
    "offline_q": "\\.OfflineQ\\d+\\.OfflineQ",
    "offline_r": "\\.OfflineR\\d+\\.OfflineR",
    "offline_s": "\\.OfflineS\\d+\\.OfflineS",
    "offline_t": "\\.OfflineT\\d+\\.OfflineT",
    "offline_u": "\\.OfflineU\\d+\\.OfflineU",
    "offline_v": "\\.OfflineV\\d+\\.OfflineV",
    "offline_w": "\\.OfflineW\\d+\\.OfflineW",
    "offline_x": "\\.OfflineX\\d+\\.OfflineX",
    "offline_y": "\\.OfflineY\\d+\\.OfflineY",
    "offline_z": "\\.OfflineZ\\d+\\.OfflineZ",
    "loop_a_sp": "\\.LoopA\\d+\\.SP",
    "loop_a_pv": "\\.LoopA\\d+\\.PV",
    "loop_a_out": "\\.LoopA\\d+\\.Out",
    "loop_b_sp": "\\.LoopB\\d+\\.SP",
    "loop_b_pv": "\\.LoopB\\d+\\.PV",
    "loop_b_out": "\\.LoopB\\d+\\.Out",
    "loop_c_sp": "\\.LoopC\\d+\\.SP",
    "loop_c_pv": "\\.LoopC\\d+\\.PV",
    "loop_c_out": "\\.LoopC\\d+\\.Out",
    "loop_d_sp": "\\.LoopD\\d+\\.SP",
    "loop_d_pv": "\\.LoopD\\d+\\.PV",
    "loop_d_out": "\\.LoopD\\d+\\.Out",
    "internal_a_start_oszillation": "\\.InternalA\\d+\\.Start Oszillation",
}


class DASware5Parser(core.DASwareParser):
    def parse(self, filepath: pathlib.Path) -> core.DWData:
        """Parses the provided DASware CSV file into a data object.

        Args:
            filepath (str or pathlib.Path): path pointing to the file of interest
        """
        scoped_blocks = common.split_blocks(filepath)
        scoped_blocks = {
            key: value for (key, value) in scoped_blocks.items() if "TrackData" in list(value)
        }
        dd = common.transform_to_dwdata(scoped_blocks, BLOCKPARSERS, version=core.DASwareVersion.V5)

        for _, reactor in dd.items():
            reactor._dataframe = common.transform_trackdata(
                reactor.trackdata, columnmapping, core.DASwareVersion.V5
            )

        return dd
