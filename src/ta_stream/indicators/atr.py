from ta_stream import Candle

from .abstract import AbstractIndicator


class ATRIndicator(AbstractIndicator):
    def __init__(self, period: int = 14, name: str = "") -> None:
        super().__init__(name or f"atr_{period}", period)
        self._candle: Candle | None = None

    def setup(self, history: list[Candle]) -> None:
        self._candle = history[0]
        super().setup(history[1:])

    @staticmethod
    def get_tr(candle: Candle, prev_close: float) -> float:
        return max(
            candle.high - candle.low,
            abs(candle.high - prev_close),
            abs(candle.low - prev_close),
        )

    def get_average(self, value: float) -> float:
        return (self.value * (self.period - 1) + value) / self.period

    def _calculate_tr(self, candle) -> tuple[float]:
        tr = self.get_tr(candle, self._candle.close)
        self._candle = candle

        return tr

    def get_first_value(self, setup_history: list[Candle]) -> float:
        return sum(map(self._calculate_tr, setup_history)) / self.period

    def get_next_value(self, candle: Candle) -> float:
        tr = self._calculate_tr(candle)
        return self.get_average(tr)
