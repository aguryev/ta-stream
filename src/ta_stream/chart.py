from .candle import Candle
from .indicators import AbstractIndicator
from .indicators.exceptions import IndicatorNotSetupError


class Chart:
    def __init__(
        self,
        precision: int,
        chart_period: int,
        indicators: list[AbstractIndicator] = [],
        initial_history: list[Candle] = [],
        candle_stream_period: int = 1,
        max_history_length=200,
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
        try:
            if len(self.history) == 0 or self.should_be_next_candle(candle.timestamp):
                self.update_indicators()
                self.append_candle(candle)
            else:
                self.merge_candle(candle)
        except KeyError:
            self.append_candle(candle)

        self.history = self.history[-self.max_length :]

    def update_indicators(self) -> None:
        for _ind in self.indicators:
            try:
                _ind.update(self.history[-1])
            except IndicatorNotSetupError:
                _ind.setup(self.history)

            self.history[-1].add_attr(_ind.name, round(_ind.value, self.precision))

    def json(self):
        return [candle.data for candle in self.history]
