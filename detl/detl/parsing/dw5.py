import pathlib
import pandas
import re
from io import StringIO

from .. import core


class DASware5Parser(core.DASwareParser):
    def parse(self, filepath:pathlib.Path) -> core.DWData:
        """Parses the provided DASware CSV file into a data object.

        Args:
            filepath (str or pathlib.Path): path pointing to the file of interest
        """
        if isinstance(filepath, str):
            fpath = pathlib.Path(filepath)
        elif isinstance(filepath, pathlib.Path):
            fpath = filepath
        else:
            raise ValueError('Please provide filepath either as str or pathlib.Path object')
        
        string_collection = dict()
        reactor_pattern = re.compile(r'\[TrackData(\d)\]')
        global_end_pattern = re.compile(r'\[Events\]')
        on_record = None

        with fpath.open(mode='r', errors='replace') as fobject:
            for line in fobject:
                if on_record is None:
                    find_reactor = re.findall(reactor_pattern, line)
                    find_global_end = re.match(global_end_pattern, line)
                    
                    if find_reactor != []:
                        on_record = int(find_reactor[0])
                        string_collection.update({on_record: StringIO()})
                    elif find_global_end is not None:
                        break
                else:
                    if line.rstrip() == (len(line.rstrip()) * line[0]):
                        string_collection[on_record].seek(0)
                        on_record = None
                    else:
                        string_collection[on_record].write(line)

        df_collection = dict()
        for key, sobject in string_collection.items():
            df_collection.update({
                key: pandas.read_csv(sobject, sep=';')
            })

        return core.DWData(df_collection, core.DASwareVersion.V5)
