from abc import ABC, abstractmethod

from ta_stream import Candle

from .exceptions import IndicatorNotSetupError


class AbstractIndicator(ABC):
    def __init__(self, name: str, period: int = 2) -> None:
        self.name: str = name
        self.period = period
        self.value: float | None = None

    @property
    def setup_period(self) -> int:
        return self.period

    def setup(self, history: list[Candle]) -> None:
        if len(history) < self.period:
            raise TypeError(f"The setup data is shorter then {self.setup_period}.")

        self.value = self.get_first_value(history[: self.setup_period])
        for candle in history[self.setup_period :]:
            self.update(candle)

    def update(self, candle: Candle) -> None:
        try:
            value = self.get_next_value(candle)
            self.value = value
        except TypeError:
            raise IndicatorNotSetupError()

    @abstractmethod
    def get_first_value(self, setup_history: list[Candle]) -> float:
        pass

    @abstractmethod
    def get_next_value(self, candle: Candle) -> float:
        pass
