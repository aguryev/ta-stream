import csv
import pathlib
from collections.abc import Generator

import pytest

from ta_stream import Candle


def csv_iterator(data_name: str) -> Generator:
    path_to_csv = pathlib.Path(__file__).parent.joinpath("data", f"{data_name}.csv")
    with open(path_to_csv) as f:
        csv_reader = csv.DictReader(f)
        yield from csv_reader


@pytest.fixture
def candle_generator(data_name: str) -> Generator:
    return (
        Candle(timestamp=int(_row["time"]), volume=100.0, **{_k: float(_v) for _k, _v in _row.items() if _k != "time"})
        for _row in csv_iterator(data_name)
    )
