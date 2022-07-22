import datetime
from itertools import chain
from pathlib import Path
from typing import Union, List

from jhack.utils.file_peeker import FilePeeker
import parse


class DebugLogInterlacer:
    """Helper to interlace debug-logs

    Yields the chronologically next row across one or more debug log files, keeping track of
    progress so that successive calls to readline will progress through the monitored files.

    # TODO: Cleanup file peekers and their pointers?
    """
    line_pattern = parse.compile("{_}: {timestamp:ti} {_}")
    line_pattern_no_date = parse.compile("{_}: {timestamp:tt} {_}")

    def __init__(self, files: List[Union[Path, str]]):
        self.files = [Path(f) for f in files]
        self.file_peekers = [FilePeeker(f) for f in self.files]

    def readline(self):
        """Returns the chronologically next line from the collection log files"""
        next_line_timestamp = None
        next_line_file_index = None

        for i, file_peeker in enumerate(self.file_peekers):
            try:
                line = file_peeker.peekline()

                # Skip blank lines
                if line.strip() == "":
                    continue

                if match := self.line_pattern.parse(line):
                    this_timestamp = match.named["timestamp"]
                    if next_line_timestamp is None or this_timestamp < next_line_timestamp:
                        next_line_timestamp = this_timestamp
                        next_line_file_index = i
                else:
                    if self.line_pattern_no_date.parse(line):
                        raise ValueError(
                            f"Could not parse line from file {file_peeker.filename}, no full "
                            f"datetime found.  Did you export with `juju debug-log --date`?"
                        )
                    else:
                        raise ValueError(
                            f"Cannot parse line {line} from file {file_peeker.filename} for "
                            f"unknown reasons."
                        )
            except StopIteration:
                continue

        if next_line_file_index is not None:
            return self.file_peekers[next_line_file_index].readline()
        else:
            return ''


# class DebugLogSequencer:
#     """Helper to sequence debug-logs
#
#     Yields the rows of a bunch of files, sorted by the first timestamp we
#     can find in them.
#
#     """
#     line_pattern = parse.compile("{_}: {timestamp:ti} {_}")
#     line_pattern_no_date = parse.compile("{_}: {timestamp:tt} {_}")
#
#     def __init__(self, files: List[Union[Path, str]]):
#         self.files = [Path(f) for f in files]
#         sorted_files = sorted(files, key=self.by_timestamp)
#
#         from jhack.utils.tail_charms import logger
#         logger.debug(f"files sorted by timestamp: {sorted_files}")
#         peekers = map(FilePeeker, sorted_files)
#         self._line_iterator = iter(chain(*peekers))
#
#     def by_timestamp(self, file: Path):
#         with open(file, 'r') as f:
#             first_line = f.readline()
#         match = self.line_pattern.parse(first_line)
#         if match and (tstamp := match.named.get('timestamp')):
#             timestamp: datetime.datetime = tstamp
#             return tstamp
#         elif time := self.line_pattern_no_date.parse(first_line):
#             timestamp: datetime.time = time.named.get('timestamp')
#             dt = datetime.datetime.now().replace(hour=timestamp.hour,
#                                                  minute=timestamp.minute,
#                                                  second=timestamp.second)  # assume it's today
#             return dt
#         raise ValueError(
#             f'first line of {file} matches no known pattern;'
#             f'{first_line[:20]!r}. Is this a juju debug-log line?'
#         )
#
#     def readline(self):
#         """Returns the chronologically next line from the collection log files"""
#         try:
#             return next(self._line_iterator)
#         except StopIteration:  # conform to file.readline() behaviour
#             return ""
