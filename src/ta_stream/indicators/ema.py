from functools import cached_property

from ta_stream import Candle

from .abstract import AbstractIndicator


class EMAIndicator(AbstractIndicator):
    def __init__(self, period: int, price_atr: str = "close", name: str = "") -> None:
        super().__init__(name or f"ema_{period}", period)
        self.price_attr = price_atr

    @cached_property
    def alpha(self) -> float:
        return 2 / (self.period + 1)

    def _get_candle_price(self, candle: Candle) -> float:
        return getattr(candle, self.price_attr)

    def get_first_value(self, setup_history: list[Candle]) -> float:
        return sum(map(self._get_candle_price, setup_history)) / len(setup_history)

    def get_next_value(self, candle: Candle) -> float:
        return self._get_candle_price(candle) * self.alpha + self.value * (1 - self.alpha)
