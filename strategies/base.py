"""
Base strategy class for Smart Money Concepts trading strategies.

All strategies inherit from BaseStrategy and implement the signal generation logic.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import pandas as pd


@dataclass
class Signal:
    """
    Trading signal with all necessary information for execution.

    Attributes:
        timestamp: When the signal was generated
        direction: 1 for long, -1 for short
        entry_price: Suggested entry price
        stop_loss: Stop loss price
        take_profit: Optional take profit price
        confidence: Confidence score 0-100
        strategy_name: Name of the strategy that generated this signal
        metadata: Additional strategy-specific data
    """

    timestamp: pd.Timestamp
    direction: int  # 1 = long, -1 = short
    entry_price: float
    stop_loss: float
    take_profit: float | None = None
    confidence: int = 50
    strategy_name: str = ""
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate signal parameters."""
        if self.direction not in (1, -1):
            raise ValueError(f"Direction must be 1 or -1, got {self.direction}")
        if not 0 <= self.confidence <= 100:
            raise ValueError(f"Confidence must be 0-100, got {self.confidence}")
        if self.entry_price <= 0:
            raise ValueError(f"Entry price must be positive, got {self.entry_price}")
        if self.stop_loss <= 0:
            raise ValueError(f"Stop loss must be positive, got {self.stop_loss}")

    @property
    def risk_reward_ratio(self) -> float | None:
        """Calculate risk:reward ratio if take profit is set."""
        if self.take_profit is None:
            return None

        risk = abs(self.entry_price - self.stop_loss)
        if risk == 0:
            return None

        reward = abs(self.take_profit - self.entry_price)
        return reward / risk

    @property
    def risk_percent(self) -> float:
        """Calculate risk as percentage of entry price."""
        return abs(self.entry_price - self.stop_loss) / self.entry_price * 100

    def is_valid_rr(self, min_rr: float = 1.5) -> bool:
        """Check if signal meets minimum risk:reward ratio."""
        rr = self.risk_reward_ratio
        if rr is None:
            return False
        return rr >= min_rr


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.

    Subclasses must implement:
    - generate_signals(): Produce trading signals from OHLCV data
    - calculate_confidence(): Score the confidence of a signal

    Example:
        >>> class MyStrategy(BaseStrategy):
        ...     def generate_signals(self, data):
        ...         # Implementation
        ...         return signals
        ...     def calculate_confidence(self, data, signal_idx):
        ...         return 60
    """

    DEFAULT_PARAMS: dict = {}

    def __init__(self, name: str, params: dict | None = None):
        """
        Initialize the strategy.

        Args:
            name: Strategy identifier
            params: Strategy parameters (merged with DEFAULT_PARAMS)
        """
        self.name = name
        self.params = {**self.DEFAULT_PARAMS, **(params or {})}

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> list[Signal]:
        """
        Generate trading signals from OHLCV data.

        Args:
            data: DataFrame with columns [open, high, low, close, volume]
                  Index should be DatetimeIndex

        Returns:
            List of Signal objects
        """
        pass

    @abstractmethod
    def calculate_confidence(self, data: pd.DataFrame, signal_idx: int) -> int:
        """
        Calculate confidence score for a specific signal.

        Args:
            data: Full OHLCV DataFrame
            signal_idx: Integer index position of the signal bar

        Returns:
            Confidence score 0-100
        """
        pass

    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate that data has required columns and format.

        Args:
            data: Input DataFrame

        Returns:
            True if valid, raises ValueError otherwise
        """
        required_columns = ["open", "high", "low", "close", "volume"]

        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"Missing required column: {col}")

        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("Data index must be DatetimeIndex")

        if len(data) == 0:
            raise ValueError("Data cannot be empty")

        return True

    def filter_signals_by_rr(self, signals: list[Signal], min_rr: float = 1.5) -> list[Signal]:
        """
        Filter signals by minimum risk:reward ratio.

        Args:
            signals: List of signals to filter
            min_rr: Minimum risk:reward ratio

        Returns:
            Filtered list of signals meeting RR criteria
        """
        return [s for s in signals if s.is_valid_rr(min_rr)]

    def filter_signals_by_confidence(
        self, signals: list[Signal], min_confidence: int = 40
    ) -> list[Signal]:
        """
        Filter signals by minimum confidence score.

        Args:
            signals: List of signals to filter
            min_confidence: Minimum confidence score (0-100)

        Returns:
            Filtered list of signals meeting confidence criteria
        """
        return [s for s in signals if s.confidence >= min_confidence]

    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range.

        Args:
            data: OHLCV DataFrame
            period: ATR period

        Returns:
            Series of ATR values
        """
        high = data["high"]
        low = data["low"]
        close = data["close"]

        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))

        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()

        return atr

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', params={self.params})"
