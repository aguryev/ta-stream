from .candle import Candle
from .indicators import AbstractIndicator


class Chart:
    def __init__(
        self,
        precision: int,
        chart_period: int,
        indicators: list[AbstractIndicator] = [],
        initial_history: list[Candle] = [],
        candle_stream_period: int = 1,
        max_history_length: int | None = 200,
    ) -> None:
        self.precision = precision
        self.period = chart_period
        self.indicators = indicators
        self.stream_period = candle_stream_period
        self.max_length = max_history_length

        self.setup_history(initial_history)

    def setup_history(self, history: list[Candle], indicators: list = []) -> None:
        self.history: list[Candle] = []
        for candle in history:
            self.update(candle)

    def get_actual_timestamp(self, timestamp: int) -> int:
        return timestamp - (timestamp % (self.period * 60))

    def should_be_next_candle(self, timestamp: int) -> bool:
        recent_timestamp = self.history[-1].timestamp
        return self.get_actual_timestamp(timestamp) > recent_timestamp

    def append_candle(self, candle: Candle) -> None:
        timestamp = self.get_actual_timestamp(candle.timestamp)
        self.history.append(candle.replace(timestamp=timestamp))

    def merge_candle(self, candle: Candle) -> None:
        self.history[-1].merge(candle)

    def tick_price(self, timestamp: int, price: float) -> bool:
        try:
            if self.should_be_next_candle(timestamp):
                candle = Candle.from_price(self.get_actual_timestamp(timestamp), price)
                self.update(candle)
                return True
            else:
                self.history[-1].tick_price(price)
        except IndexError:
            pass

        return False

    def update(self, candle: Candle) -> None:
        if len(self.history) == 0 or self.should_be_next_candle(candle.timestamp):
            for _ind in self.indicators:
                self._update_indicator(_ind)

            self.append_candle(candle)
        else:
            self.merge_candle(candle)

        if self.max_length is not None:
            self.history = self.history[-self.max_length :]

    def _update_indicator(self, indicator: AbstractIndicator) -> None:
        if indicator.value is not None:
            indicator.update(self.history[-1])
        elif len(self.history) >= indicator.setup_period:
            indicator.setup(self.history)
        else:
            return

        self.history[-1].add_attr(indicator.name, round(indicator.value, self.precision))

    def json(self):
        return [candle.data for candle in self.history]
