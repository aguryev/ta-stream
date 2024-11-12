from datetime import datetime

import pytest

from ta_stream import Candle


#
# Utils
#
def get_candle(timestamp: int, open: float, high: float, low: float, close: float, volume: float = 0.0) -> Candle:
    return Candle(
        timestamp=timestamp,
        open=open,
        high=high,
        low=low,
        close=close,
        volume=volume,
    )


#
# Tests
#
@pytest.mark.parametrize(
    "timestamp, open, high, low, close, volume, new_value",
    [
        (1722594600, 3143.120, 3148.350, 3138.060, 3146.135, 29318, 123.4),
        (1724416440, 7685.0, 7690.0, 7684.0, 7690.0, 112.0, 12.34),
        (1724845020, 1.11287, 1.113, 1.11287, 1.11295, 456.0, 1.234),
    ],
)
def test_candle_init(timestamp, open, high, low, close, volume, new_value):
    candle = get_candle(timestamp, open, high, low, close, volume)

    assert candle.timestamp == timestamp
    assert candle.open == open
    assert candle.high == high
    assert candle.low == low
    assert candle.close == close
    assert candle.volume == volume

    assert isinstance(candle.time, datetime)
    assert candle.time.timestamp() == timestamp

    assert not hasattr(candle, "new_attr")
    candle.add_attr("new_attr", new_value)
    assert candle.new_attr == new_value


@pytest.mark.parametrize("timestamp, price", [(1727643720, 0.93206), (1728291900, 63342.0)])
def test_candle_from_price(timestamp, price):
    candle = Candle.from_price(timestamp, price)

    assert candle.timestamp == timestamp
    assert candle.open == price
    assert candle.high == price
    assert candle.low == price
    assert candle.close == price
    assert candle.volume == 0.0


@pytest.mark.parametrize(
    "candle_one, candle_two, expected",
    [
        ((1, 12.3, 13.2, 11.5, 12.4, 123), (2, 12.0, 12.2, 11.9, 12.1, 321), (13.2, 11.5)),
        ((123, 1.23, 1.32, 1.15, 1.24, 9.8), (234, 1.2, 2.1, 1.1, 2.05, 8.9), (2.1, 1.1)),
    ],
)
def test_candle_merge(candle_one, candle_two, expected):
    candle = get_candle(*candle_one)
    candle.merge(get_candle(*candle_two))

    assert candle.timestamp == candle_one[0]
    assert candle.open == candle_one[1]
    assert candle.high == expected[0]
    assert candle.low == expected[1]
    assert candle.close == candle_two[4]
    assert candle.volume == candle_two[5]


@pytest.mark.parametrize(
    "candle_data, price, expected",
    [
        ((0.123, 0.234, 0.111, 0.125), 0.120, (0.234, 0.111)),
        ((1.23, 2.34, 1.11, 1.25), 3.0, (3.0, 1.11)),
        ((12.3, 23.4, 11.1, 12.5), 10.1, (23.4, 10.1)),
    ],
)
def test_candle_tick_price(candle_data, price, expected):
    candle = get_candle(123, *candle_data)
    candle.tick_price(price)

    assert candle.open == candle_data[0]
    assert candle.high == expected[0]
    assert candle.low == expected[1]
    assert candle.close == price


@pytest.mark.parametrize(
    "candle_data, replace_data",
    [
        ((17225946, 3143.120, 3148.350, 3138.060, 3146.135, 293), (17244164, 7685.0, 7690.0, 7684.0, 7690.0, 112.0)),
        ((1234, 0.123, 0.234, 0.111, 0.125, 123), (2345, 1.23, 2.34, 1.11, 1.25, 987)),
    ],
)
def test_candle_replace(candle_data, replace_data):
    candle = get_candle(*candle_data)

    candle_one = candle.replace(timestamp=replace_data[0])
    assert isinstance(candle_one, Candle)
    assert candle_one.timestamp == replace_data[0]
    assert candle_one.open == candle_data[1]
    assert candle_one.high == candle_data[2]
    assert candle_one.low == candle_data[3]
    assert candle_one.close == candle_data[4]
    assert candle_one.volume == candle_data[5]

    candle_two = candle.replace(open=replace_data[1], close=replace_data[4], volume=replace_data[5])
    assert isinstance(candle_two, Candle)
    assert candle_two.timestamp == candle_data[0]
    assert candle_two.open == replace_data[1]
    assert candle_two.high == candle_data[2]
    assert candle_two.low == candle_data[3]
    assert candle_two.close == replace_data[4]
    assert candle_two.volume == replace_data[5]

    candle_three = candle.replace(high=replace_data[2], low=replace_data[3])
    assert isinstance(candle_three, Candle)
    assert candle_three.timestamp == candle_data[0]
    assert candle_three.open == candle_data[1]
    assert candle_three.high == replace_data[2]
    assert candle_three.low == replace_data[3]
    assert candle_three.close == candle_data[4]
    assert candle_three.volume == candle_data[5]
