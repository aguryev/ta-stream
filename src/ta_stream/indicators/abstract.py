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

    def _split_setup_data(self, history: list[Candle]) -> tuple:
        return history[: self.setup_period], history[self.setup_period :]

    def setup(self, history: list[Candle]) -> None:
        if len(history) < self.setup_period:
            raise TypeError(f"The setup data is shorter then {self.setup_period}.")

        setup_history, other_history = self._split_setup_data(history)

        self.value = self.get_first_value(setup_history)
        for candle in other_history:
            self.update(candle)

    def update(self, candle: Candle) -> None:
        if self.value is not None:
            value = self.get_next_value(candle)
            self.value = value
            return

        raise IndicatorNotSetupError()

    @abstractmethod
    def get_first_value(self, setup_history: list[Candle]) -> float:
        pass

    @abstractmethod
    def get_next_value(self, candle: Candle) -> float:
        pass
