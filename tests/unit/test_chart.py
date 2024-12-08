import pytest

from ta_stream import Chart


@pytest.mark.parametrize(
    "data_name, precision, period, expected",
    [
        ("cocoa", 0, 15, (1729874700, 7814.0, 7814.0, 7765.0, 7799.0)),
        ("cocoa", 0, 30, (1729873800, 7835.0, 7845.0, 7765.0, 7799.0)),
        ("cocoa", 0, 60, (1729872000, 7823.0, 7888.0, 7765.0, 7799.0)),
    ],
)
def test_chart_setup(candle_generator, precision, period, expected):
    chart = Chart(
        precision=precision,
        chart_period=period,
        initial_history=list(candle_generator),
    )
    assert chart.precision == precision
    assert chart.period == period
    assert chart.indicators == []
    assert chart.stream_period == 1
    assert chart.max_length == 200

    last_candle = chart.history[-1]
    assert last_candle.timestamp == expected[0]
    assert last_candle.open == expected[1]
    assert last_candle.high == expected[2]
    assert last_candle.low == expected[3]
    assert last_candle.close == expected[4]
