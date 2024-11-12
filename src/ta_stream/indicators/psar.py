from ta_stream import Candle

from .abstract import AbstractIndicator


class PSARIndicator(AbstractIndicator):
    def __init__(self, start: float = 0.02, stop: float = 0.2, step: float = 0.02, name: str = "psar") -> None:
        super().__init__(name)
        self._af_start = start
        self._af_stop = stop
        self._af_step = step
        self.reset_af()

    def reset_af(self):
        self.af = self._af_start

    def _get_next_psar(self) -> float:
        return self.value + self.af * (self.ep - self.value)

    def _reset_ep(
        self,
        candle: Candle | None = None,
        high: float | None = None,
        low: float | None = None,
    ) -> None:
        try:
            _high = candle.high
            _low = candle.low
        except AttributeError:
            _high = high
            _low = low

        self.ep = _high if self.uptrend else _low

    def _reset_value(self, high: float, low: float) -> None:
        self.value = low if self.uptrend else high

    def get_first_value(self, setup_history: list[Candle]) -> float:
        self.uptrend = setup_history[0].open < setup_history[-1].close
        high = max(_cnd.high for _cnd in setup_history)
        low = min(_cnd.low for _cnd in setup_history)

        self._reset_value(high=high, low=low)
        self._reset_ep(high=high, low=low)
        return self._get_next_psar()

    def get_next_value(self, candle: Candle) -> float:
        if (self.uptrend and candle.low < self.value) or (not self.uptrend and candle.high > self.value):
            self._stop_and_reverse(candle)

        elif (self.uptrend and self.ep < candle.high) or (not self.uptrend and self.ep > candle.low):
            self._reset_ep(candle)
            self.af = min(self.af + self._af_step, self._af_stop)

        return self._get_next_psar()

    def _stop_and_reverse(self, candle: Candle) -> None:
        self.uptrend = not self.uptrend
        self._reset_value(high=max(self.ep, candle.high), low=min(self.ep, candle.low))
        self._reset_ep(candle)
        self.reset_af()
