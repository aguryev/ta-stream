from datetime import datetime
from typing import Any


class Candle:
    base_attrs = [
        "timestamp",
        "open",
        "close",
        "high",
        "low",
        "volume",
    ]

    def __init__(self, **kwargs):
        missing_attrs = [attr for attr in self.base_attrs if attr not in kwargs]
        if missing_attrs:
            raise TypeError(f"Missing {len(missing_attrs)} required positional arguments: " + ", ".join(missing_attrs))

        self.data = kwargs

    def __getattr__(self, attr: str) -> Any:
        try:
            return self.data[attr]
        except KeyError:
            raise AttributeError(f"object '{self.__class__.__name__}' has no attribute '{attr}'")

    @classmethod
    def from_price(cls, timestamp: int, price: float):
        kwargs = {attr: price for attr in cls.base_attrs}
        kwargs["timestamp"] = timestamp
        kwargs["volume"] = 0.0

        return cls(**kwargs)

    @property
    def time(self) -> datetime:
        return datetime.fromtimestamp(self.data["timestamp"])

    def merge(self, candle) -> None:
        self.data["volume"] = candle.data["volume"]
        self.data["close"] = candle.data["close"]
        self.data["high"] = max(self.data["high"], candle.data["high"])
        self.data["low"] = min(self.data["low"], candle.data["low"])

    def tick_price(self, price: float) -> None:
        self.data["high"] = max(self.data["high"], price)
        self.data["low"] = min(self.data["low"], price)
        self.data["close"] = price

    def add_attr(self, attr: str, value: float) -> None:
        self.data[attr] = value

    def replace(self, **kwargs):
        data = {key: (kwargs[key] if key in kwargs else value) for key, value in self.data.items()}
        return self.__class__(**data)
