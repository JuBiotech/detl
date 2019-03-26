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

basic_parsing_number_of_dfs = [4, 4, 4]

basic_parsing_row_counts = [
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


class TestBasicParsing(unittest.TestCase):
    def test_dataframes(self):
        for fp in basic_parsing_testfiles:
            ddata = detl.parse(fp)
            for _, item in ddata.data.items():
                self.assertIsInstance(item, pandas.DataFrame)
        return
    
    def test_number_of_dataframes(self):
        for idx, fp in enumerate(basic_parsing_testfiles):
            ddata = detl.parse(fp)
            self.assertEqual(len(ddata.data), basic_parsing_number_of_dfs[idx])
        return
    
    def test_dataframe_row_count(self):
        for idx, fp in enumerate(basic_parsing_testfiles):
            ddata = detl.parse(fp)
            for u_idx, item in ddata.data.items():
                self.assertEqual(
                    len(item.index), 
                    basic_parsing_row_counts[idx][u_idx-1]
                )
        return



if __name__ == '__main__':
    unittest.main()
