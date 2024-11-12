import pytest

from ta_stream.indicators import ADXIndicator, ATRIndicator, EMAIndicator, PSARIndicator, SMAIndicator


@pytest.mark.parametrize("data_name, data_field, eps, period", [("cocoa", "sma_12", 0.01, 12)])
def test_sma_indicator(candle_generator, data_field, eps, period):
    sma = SMAIndicator(period)
    assert sma.period == period
    assert sma.name == f"sma_{period}"
    assert sma.price_attr == "close"
    assert not sma._price_cache

    sma.setup([next(candle_generator) for _ix in range(period + 2)])
    assert len(sma._price_cache) == period

    for candle in candle_generator:
        sma.update(candle)

        assert len(sma._price_cache) == period
        assert abs(getattr(candle, data_field) - sma.value) <= eps


@pytest.mark.parametrize("data_name, data_field, eps, period", [("cocoa", "ema_20", 0.01, 20)])
def test_ema_indicator(candle_generator, data_field, eps, period):
    ema = EMAIndicator(period)
    assert ema.period == period
    assert ema.name == f"ema_{period}"
    assert ema.price_attr == "close"

    ema.setup([next(candle_generator) for _ix in range(period + 2)])

    for candle in candle_generator:
        ema.update(candle)

        assert abs(getattr(candle, data_field) - ema.value) <= eps


@pytest.mark.parametrize("data_name, data_field, eps", [("cocoa", "psar", 0.01)])
def test_psar_indicator(candle_generator, data_field, eps):
    psar = PSARIndicator()
    assert psar.period == 2
    assert psar._af_start == 0.02
    assert psar._af_stop == 0.2
    assert psar._af_step == 0.02

    psar.setup([next(candle_generator) for _ix in range(4)])

    for candle in candle_generator:
        psar.update(candle)

        assert abs(getattr(candle, data_field) - psar.value) <= eps


@pytest.mark.parametrize("data_name, data_field, eps, period", [("cocoa", "atr", 0.01, 14)])
def test_atr_indicator(candle_generator, data_field, eps, period):
    atr = ATRIndicator(period)
    assert atr.period == period
    assert atr.name == f"atr_{period}"
    assert atr._candle is None

    atr.setup([next(candle_generator) for _ix in range(period + 2)])

    for candle in candle_generator:
        atr.update(candle)

        assert abs(getattr(candle, data_field) - atr.value) <= eps


@pytest.mark.parametrize("data_name, data_field, eps, period, setup_period", [("cocoa", "adx", 0.01, 14, 27)])
def test_adx_indicator(candle_generator, data_field, eps, period, setup_period):
    adx = ADXIndicator(period)
    assert adx.period == period
    assert adx.setup_period == setup_period
    assert adx.name == f"adx_{period}"
    assert adx._candle is None

    adx.setup([next(candle_generator) for _ix in range(2 * period + 2)])

    for candle in candle_generator:
        adx.update(candle)

        assert abs(getattr(candle, data_field) - adx.value) <= eps
