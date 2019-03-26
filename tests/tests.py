"""Contains unit tests for the `detl` package"""
import numpy
import pathlib
import pandas
import unittest

import detl


class TestParserSelection(unittest.TestCase):
    def test_v4_detection(self):
        parser = detl.get_parser(pathlib.Path('data', 'v4_20180726.Control.csv'))
        self.assertIsNotNone(parser)
        self.assertIsInstance(parser, detl.core.DASwareParser)
        self.assertIsInstance(parser, detl.parsing.dw4.DASware4Parser)
        return
    
    def test_v5_detection(self):
        parser = detl.get_parser(pathlib.Path('data', 'short_CTPC06280.Control.csv'))
        self.assertIsNotNone(parser)
        self.assertIsInstance(parser, detl.core.DASwareParser)
        self.assertIsInstance(parser, detl.parsing.dw5.DASware5Parser)
        return

    def test_invalid_detection(self):
        with self.assertRaises(NotImplementedError):
            parser = detl.get_parser(pathlib.Path('data', 'invalid.csv'))
        return


if __name__ == '__main__':
    unittest.main()
