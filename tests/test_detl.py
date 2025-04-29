"""Contains unit tests for the `detl` package"""
import datetime
import pathlib
import unittest

import numpy
import pandas

import detl

dir_testfiles = pathlib.Path(pathlib.Path(__file__).absolute().parent, "testfiles")

v4_testfiles = [
    pathlib.Path(dir_testfiles, "v4_NT-WMB-2.Control.csv"),
    pathlib.Path(dir_testfiles, "v4_20180726.Control.csv"),
]
v4_nreactors = [4, 4]
v4_trackdata_nrows = [
    [5461, 5460, 5460, 5459],
    [1371, 1370, 1370, 1370],
]

v5_testfiles = [
    pathlib.Path(dir_testfiles, "v5_short_CTPC06280.Control.csv"),
    pathlib.Path(dir_testfiles, "v5_medium_CTPC06110.20181219.Control.csv"),
    pathlib.Path(dir_testfiles, "v5_long_CTPC06110.20190218.Control.csv"),
]
v5_nreactors = [
    4,
    4,
    4,
]
v5_trackdata_nrows = [
    [14111, 14112, 14108, 14112],
    [16936, 16936, 16935, 16936],
    [52245, 52245, 52245, 52245],
]


class TestParserSelection(unittest.TestCase):
    def test_v4_detection(self):
        parser = detl.get_parser(pathlib.Path(dir_testfiles, "v4_20180726.Control.csv"))
        self.assertIsNotNone(parser)
        self.assertIsInstance(parser, detl.core.DASwareParser)
        self.assertIsInstance(parser, detl.parsing.dw4.DASware4Parser)
        return

    def test_v5_detection(self):
        parser = detl.get_parser(pathlib.Path(dir_testfiles, "v5_short_CTPC06280.Control.csv"))
        self.assertIsNotNone(parser)
        self.assertIsInstance(parser, detl.core.DASwareParser)
        self.assertIsInstance(parser, detl.parsing.dw5.DASware5Parser)
        return

    def test_invalid_detection(self):
        with self.assertRaises(NotImplementedError):
            _ = detl.get_parser(pathlib.Path(dir_testfiles, "invalid.csv"))
        return


class TestCommonParsing(unittest.TestCase):
    def test_split_blocks_v5(self):
        with self.assertRaises(ValueError):
            detl.parsing.common.split_blocks(["bla"])

        filepath = pathlib.Path(dir_testfiles, "v5_short_CTPC06280.Control.csv")

        scoped_blocks = detl.parsing.common.split_blocks(filepath)
        self.assertEqual(len(scoped_blocks), 5)
        self.assertTrue(None in scoped_blocks)
        self.assertTrue(1 in scoped_blocks)
        self.assertTrue(2 in scoped_blocks)
        self.assertTrue(3 in scoped_blocks)
        self.assertTrue(4 in scoped_blocks)
        self.assertTrue("TrackData" not in scoped_blocks)
        self.assertTrue("Events" in scoped_blocks[None])
        self.assertTrue("Fb-Pro" in scoped_blocks[None])
        self.assertTrue("Procedure" in scoped_blocks[None])
        self.assertTrue("Profile Columns" in scoped_blocks[None])
        self.assertTrue("Plant" in scoped_blocks[None])
        self.assertTrue("Units" in scoped_blocks[None])
        self.assertTrue("Sensors" in scoped_blocks[None])
        self.assertTrue("Modules" in scoped_blocks[None])
        self.assertTrue("External Servers" in scoped_blocks[None])
        self.assertTrue("External Values" in scoped_blocks[None])
        self.assertTrue("Internal Values" in scoped_blocks[None])
        self.assertTrue("Setups" in scoped_blocks[None])
        for r in {1, 2, 3, 4}:
            self.assertTrue("TrackData" in scoped_blocks[r])
            self.assertTrue("Setup" in scoped_blocks[r])
            self.assertTrue("Unit" in scoped_blocks[r])
            self.assertTrue("Requirements" in scoped_blocks[r])
            self.assertTrue("Sensor Elements" in scoped_blocks[r])
            self.assertTrue("Device Channels" in scoped_blocks[r])
            self.assertTrue("Profiles" in scoped_blocks[r])
            self.assertTrue("Profiles" in scoped_blocks[r])
        return

    def test_parse_generic(self):
        filepath = pathlib.Path(dir_testfiles, "v5_short_CTPC06280.Control.csv")
        scoped_blocks = detl.parsing.common.split_blocks(filepath)
        attr, df = detl.parsing.common.parse_generic(
            "Info", scoped_blocks[None]["Info"], scope=None
        )
        self.assertEqual(attr, "_info")
        self.assertIsInstance(df, pandas.DataFrame)
        self.assertEqual(len(df), 71)
        self.assertEqual(len(df.columns), 7)

    def test_parse_generic_T(self):
        filepath = pathlib.Path(dir_testfiles, "v5_short_CTPC06280.Control.csv")
        scoped_blocks = detl.parsing.common.split_blocks(filepath)
        attr, df = detl.parsing.common.parse_generic_T(
            "Info", scoped_blocks[None]["Info"], scope=None
        )
        self.assertEqual(attr, "_info")
        self.assertIsInstance(df, pandas.DataFrame)
        self.assertEqual(len(df), 7)
        self.assertEqual(len(df.columns), 71)

    def test_transform_to_dwdata_v5(self):
        filepath = pathlib.Path(dir_testfiles, "v5_short_CTPC06280.Control.csv")
        scoped_blocks = detl.parsing.common.split_blocks(filepath)
        dd = detl.parsing.common.transform_to_dwdata(
            scoped_blocks, detl.parsing.dw5.BLOCKPARSERS, detl.DASwareVersion.V5
        )
        self.assertIsInstance(dd, detl.DWData)
        self.assertIsInstance(dd, dict)
        self.assertEqual(dd.version, detl.DASwareVersion.V5)

    def test_inoculation_times(self):
        filepath = pathlib.Path(dir_testfiles, "v4_NT-WMB-2.Control.csv")
        dd = detl.parse(
            filepath,
            inoculation_times={
                1: datetime.datetime(2016, 3, 9, 16, 38, 31, tzinfo=datetime.timezone.utc),
                2: datetime.datetime(2016, 3, 9, 16, 50, 31, tzinfo=datetime.timezone.utc),
            },
        )
        self.assertEqual(dd[1].dataframe.process_time[0], 0)
        self.assertTrue(numpy.isnan(dd[3].dataframe.process_time[0]))
        self.assertTrue(numpy.isnan(dd[2].dataframe.process_time[0]))
        return


class TestDW4Parsing(unittest.TestCase):
    def test_trackdata_row_count(self):
        for fp, row_counts, nunits in zip(v4_testfiles, v4_trackdata_nrows, v4_nreactors):
            ddata = detl.parse(fp)
            for r, nrows in zip(range(1, nunits + 1), row_counts):
                self.assertTrue(r in ddata)
                self.assertIsNotNone(ddata[r].trackdata)
                self.assertEqual(len(ddata[r].trackdata), nrows)
        return

    def test_trackdata_transformation(self):
        ddata = detl.parse(v4_testfiles[0])

        assert "pump_a_rate_sp" in ddata[1].dataframe.columns
        assert "pump_b_rate_sp" in ddata[1].dataframe.columns

        self.assertAlmostEqual(ddata[1].dataframe.loc[2798, "duration"], 23.325, places=3)
        self.assertAlmostEqual(ddata[1].dataframe.loc[2798, "process_time"], 8.74667, places=3)
        self.assertAlmostEqual(ddata[2].dataframe.loc[4513, "off-gas_pv"], 31.675, places=3)
        self.assertAlmostEqual(ddata[3].dataframe.loc[1472, "temperature_pv"], 30.011, places=3)
        self.assertAlmostEqual(ddata[4].dataframe.loc[3475, "pump_a_volume_pv"], 0.622, places=3)
        self.assertEqual(
            ddata[4].dataframe.loc[2878, "timestamp"],
            datetime.datetime(2016, 3, 10, 16, 38, 8, tzinfo=datetime.timezone.utc),
        )

    def test_timestamp_parsing(self):
        ddata = detl.parse(pathlib.Path(dir_testfiles, "v4_NT-WMB-2.Control.csv"))
        self.assertEqual(
            ddata[1].dataframe.loc[0, "timestamp"],
            datetime.datetime(2016, 3, 9, 16, 38, 31, tzinfo=datetime.timezone.utc),
        )

        ddata = detl.parse(pathlib.Path(dir_testfiles, "v4_20180726.Control.csv"))
        self.assertEqual(
            ddata[1].dataframe.loc[0, "timestamp"],
            datetime.datetime(2018, 7, 26, 11, 53, 36, tzinfo=datetime.timezone.utc),
        )

        return


class TestDW5Parsing(unittest.TestCase):
    def test_trackdata_row_count(self):
        for fp, row_counts, nunits in zip(v5_testfiles, v5_trackdata_nrows, v5_nreactors):
            ddata = detl.parse(fp)
            for r, nrows in zip(range(1, nunits + 1), row_counts):
                self.assertTrue(r in ddata)
                self.assertIsNotNone(ddata[r].trackdata)
                self.assertEqual(len(ddata[r].trackdata), nrows)
        return

    def test_trackdata_transformation(self):
        ddata = detl.parse(v5_testfiles[1])

        assert "pump_a_rate_sp" in ddata[1].dataframe.columns
        assert "pump_b_rate_sp" in ddata[1].dataframe.columns

        self.assertAlmostEqual(ddata[1].dataframe.loc[11359, "aeration_x_co2_pv"], 0.034, places=3)
        self.assertAlmostEqual(ddata[2].dataframe.loc[4128, "stirrer_speed_pv"], 1059.382, places=3)
        self.assertAlmostEqual(ddata[3].dataframe.loc[13387, "duration"], 37.238, places=3)
        self.assertAlmostEqual(ddata[3].dataframe.loc[13387, "process_time"], 36.3028, places=3)
        self.assertAlmostEqual(ddata[4].dataframe.loc[9400, "do_sp"], 30.0, places=3)

    def test_timestamp_parsing(self):
        ddata = detl.parse(pathlib.Path(dir_testfiles, "v5_short_CTPC06280.Control.csv"))
        self.assertEqual(
            ddata[1].dataframe.loc[0, "timestamp"],
            datetime.datetime(2019, 2, 6, 10, 46, 52, tzinfo=datetime.timezone.utc),
        )
        return


class TestClosestDataLookup(unittest.TestCase):
    def test_dw4(self):
        ddata = detl.parse(v4_testfiles[0])
        points = numpy.array([0, 5, 15, 1999])
        expected_output = numpy.array([1000.027, 1003.670, 1026.961, 1034.168])

        looked_up_data = ddata[1].get_closest_data(points)
        [
            self.assertAlmostEqual(i, o, places=3)
            for i, o in zip(looked_up_data["volume_pv"], expected_output)
        ]

    def test_dw5(self):
        ddata = detl.parse(v5_testfiles[0])
        points = numpy.array([0, 4, 16, 100])
        expected_output = numpy.array([0, 0.291, 5.481, 26.343])

        looked_up_data = ddata[4].get_closest_data(points, reference="duration")
        [
            self.assertAlmostEqual(i, o, places=3)
            for i, o in zip(looked_up_data["ctr_pv"], expected_output)
        ]


class TestGetNarrowData(unittest.TestCase):
    def test_with_process_time(self):
        ddata = detl.parse(v4_testfiles[0])
        nd = ddata.get_narrow_data()
        self.assertAlmostEqual(nd.loc[5643]["value"], 1030.005, places=3)
        self.assertAlmostEqual(nd.loc[25146]["time"], 23.8967, places=3)

    def test_with_duration(self):
        ddata = detl.parse(v4_testfiles[0])
        nd = ddata.get_narrow_data(kdim="duration")
        self.assertAlmostEqual(nd.loc[20456]["value"], 29.889, places=3)
        self.assertAlmostEqual(nd.loc[15643]["time"], 39.35, places=3)

    def test_kdim_setting(self):
        ddata = detl.parse(v4_testfiles[0])
        with self.assertRaises(KeyError):
            ddata.get_narrow_data(kdim="volume_pv")


class TestReactorDataProps(unittest.TestCase):
    def test_reactor_data(self):
        ddata = detl.parse(v4_testfiles[0])
        rdata = list(ddata.values())[0]
        self.assertIsInstance(rdata, detl.core.ReactorData)

        # check properties
        rdata.id
        rdata.setup
        rdata.unit
        rdata.requirements
        rdata.sensor_elements
        rdata.device_channels
        rdata.profiles
        rdata.trackdata
        rdata.dataframe


if __name__ == "__main__":
    unittest.main()
