from ta_stream import Candle

from .abstract import AbstractIndicator


class SMAIndicator(AbstractIndicator):
    def __init__(self, period: int, price_atr: str = "close", name: str = "") -> None:
        super().__init__(name or f"sma_{period}", period)
        self.price_attr = price_atr
        self._price_cache: list[float] = []

    def _get_candle_price(self, candle: Candle) -> float:
        return getattr(candle, self.price_attr)

    def _get_value(self) -> float:
        return sum(self._price_cache) / self.period

    def get_first_value(self, setup_history: list[Candle]) -> float:
        self._price_cache = list(map(self._get_candle_price, setup_history))
        return self._get_value()

    def get_next_value(self, candle: Candle) -> float:
        self._price_cache = self._price_cache[1:] + [self._get_candle_price(candle)]
        return self._get_value()
