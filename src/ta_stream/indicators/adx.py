from ta_stream import Candle

from .atr import ATRIndicator


class ADXIndicator(ATRIndicator):
    def __init__(self, period: int = 14, name: str = "") -> None:
        super().__init__(period, name or f"adx_{period}")

    @property
    def setup_period(self) -> int:
        return 2 * self.period

    @staticmethod
    def get_dm(candle, prev_candle) -> tuple[float]:
        _plus = max(candle.high - prev_candle.high, 0.0)
        _minus = max(prev_candle.low - candle.low, 0.0)

        return (
            _plus if _plus > _minus else 0.0,
            _minus if _minus > _plus else 0.0,
        )

    @staticmethod
    def get_dx(di_plus, di_minus) -> float:
        return 100 * abs(di_plus - di_minus) / (di_plus + di_minus)

    def _get_base_indicators(self, candle) -> tuple[float]:
        tr = self.get_tr(candle, self._candle.close)
        dm = self.get_dm(candle, self._candle)

        self._candle = candle

        return (tr, *dm)

    def _cache_indicators(self, *values: float) -> None:
        self._xtr = values[0]
        self._xdm_plus = values[1]
        self._xdm_minus = values[2]

        self.di_plus = 100 * self._xdm_plus / self._xtr
        self.di_minus = 100 * self._xdm_minus / self._xtr

    def _calculate_next_dx(self, candle) -> float:
        base_indicators = map(
            self._smooth,
            zip(["xtr", "xdm_plus", "xdm_minus"], self._get_base_indicators(candle), strict=False),
        )
        self._cache_indicators(*base_indicators)

        return self.get_dx(self.di_plus, self.di_minus)

    def _smooth(self, indicator: tuple[str, float]) -> float:
        return getattr(self, f"_{indicator[0]}") * (self.period - 1) / self.period + indicator[1]

    def get_first_value(self, setup_history: list[Candle]) -> float:
        _indicators = map(self._get_base_indicators, setup_history[: self.period])
        self._cache_indicators(*[sum(_val) for _val in zip(*_indicators, strict=False)])

        xdx = self.get_dx(self.di_plus, self.di_minus) + sum(map(self._calculate_next_dx, setup_history[self.period :]))
        return xdx / self.period

    def get_next_value(self, candle: Candle):
        dx = self._calculate_next_dx(candle)
        return self.get_average(dx)
