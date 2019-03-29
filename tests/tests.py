"""Contains unit tests for the `detl` package"""
import numpy
import pathlib
import pandas
import unittest

import detl

basic_parsing_testfiles = [
    pathlib.Path('tests', 'testfiles', 'v4_NT-WMB-2.Control.csv'),
    pathlib.Path('tests', 'testfiles', 'v4_20180726.Control.csv'),
    pathlib.Path('tests', 'testfiles', 'long_CTPC06110.20190218.Control.csv'),
]
basic_parsing_nreactors = [4, 4, 4]
basic_parsing_trackdata_nrows = [
    [5461, 5460, 5460, 5459],
    [1371, 1370, 1370, 1370],
    [52245, 52245, 52245, 52245],
]


class TestParserSelection(unittest.TestCase):
    def test_v4_detection(self):
        parser = detl.get_parser(pathlib.Path('tests', 'testfiles', 'v4_20180726.Control.csv'))
        self.assertIsNotNone(parser)
        self.assertIsInstance(parser, detl.core.DASwareParser)
        self.assertIsInstance(parser, detl.parsing.dw4.DASware4Parser)
        return
    
    def test_v5_detection(self):
        parser = detl.get_parser(pathlib.Path('tests', 'testfiles', 'short_CTPC06280.Control.csv'))
        self.assertIsNotNone(parser)
        self.assertIsInstance(parser, detl.core.DASwareParser)
        self.assertIsInstance(parser, detl.parsing.dw5.DASware5Parser)
        return

    def test_invalid_detection(self):
        with self.assertRaises(NotImplementedError):
            _ = detl.get_parser(pathlib.Path('tests', 'testfiles', 'invalid.csv'))
        return


class TestCommonParsing(unittest.TestCase):
    def test_split_blocks(self):
        with self.assertRaises(ValueError):
            detl.parsing.common.split_blocks(['bla'])

        filepath = pathlib.Path('tests', 'testfiles', 'short_CTPC06280.Control.csv')
        
        scoped_blocks = detl.parsing.common.split_blocks(filepath)
        self.assertEqual(len(scoped_blocks), 5)
        self.assertTrue(None in scoped_blocks)
        self.assertTrue(1 in scoped_blocks)
        self.assertTrue(2 in scoped_blocks)
        self.assertTrue(3 in scoped_blocks)
        self.assertTrue(4 in scoped_blocks)
        self.assertTrue('TrackData' not in scoped_blocks)
        self.assertTrue('Events' in scoped_blocks[None])
        self.assertTrue('Fb-Pro' in scoped_blocks[None])
        self.assertTrue('Procedure' in scoped_blocks[None])
        self.assertTrue('Profile Columns' in scoped_blocks[None])
        self.assertTrue('Plant' in scoped_blocks[None])
        self.assertTrue('Units' in scoped_blocks[None])
        self.assertTrue('Sensors' in scoped_blocks[None])
        self.assertTrue('Modules' in scoped_blocks[None])
        self.assertTrue('External Servers' in scoped_blocks[None])
        self.assertTrue('External Values' in scoped_blocks[None])
        self.assertTrue('Internal Values' in scoped_blocks[None])
        self.assertTrue('Setups' in scoped_blocks[None])
        for r in {1,2,3,4}:
            self.assertTrue('TrackData' in scoped_blocks[r])
            self.assertTrue('Setup' in scoped_blocks[r])
            self.assertTrue('Unit' in scoped_blocks[r])
            self.assertTrue('Requirements' in scoped_blocks[r])
            self.assertTrue('Sensor Elements' in scoped_blocks[r])
            self.assertTrue('Device Channels' in scoped_blocks[r])
            self.assertTrue('Profiles' in scoped_blocks[r])
            self.assertTrue('Profiles' in scoped_blocks[r])
        return

    def test_parse_generic(self):
        filepath = pathlib.Path('tests', 'testfiles', 'short_CTPC06280.Control.csv')
        scoped_blocks = detl.parsing.common.split_blocks(filepath)
        attr, df = detl.parsing.common.parse_generic('Info', scoped_blocks[None]['Info'], scope=None)
        self.assertEqual(attr, '_info')
        self.assertIsInstance(df, pandas.DataFrame)
        self.assertEqual(len(df), 71)
        self.assertEqual(len(df.columns), 7)
    
    def test_parse_generic_T(self):
        filepath = pathlib.Path('tests', 'testfiles', 'short_CTPC06280.Control.csv')
        scoped_blocks = detl.parsing.common.split_blocks(filepath)
        attr, df = detl.parsing.common.parse_generic_T('Info', scoped_blocks[None]['Info'], scope=None)
        self.assertEqual(attr, '_info')
        self.assertIsInstance(df, pandas.DataFrame)
        self.assertEqual(len(df), 7)
        self.assertEqual(len(df.columns), 71)
    
    def test_transform_to_dwdata(self):
        filepath = pathlib.Path('tests', 'testfiles', 'short_CTPC06280.Control.csv')
        scoped_blocks = detl.parsing.common.split_blocks(filepath)
        dd = detl.parsing.common.transform_to_dwdata(scoped_blocks, detl.parsing.dw4.BLOCKPARSERS, detl.DASwareVersion.V4)
        self.assertIsInstance(dd, detl.DWData)
        self.assertIsInstance(dd, dict)
        self.assertEqual(dd.version, detl.DASwareVersion.V4)


class TestDW4Parsing(unittest.TestCase):
    def test_trackdata_row_count(self):
        for fp, row_counts, nunits in zip(basic_parsing_testfiles, basic_parsing_trackdata_nrows, basic_parsing_nreactors):
            ddata = detl.parse(fp)
            for r, nrows in zip(range(1, nunits + 1), row_counts):
                self.assertTrue(r in ddata)
                self.assertIsNotNone(ddata[r].trackdata)
                self.assertEqual(len(ddata[r].trackdata), nrows)
        return



if __name__ == '__main__':
    unittest.main()
