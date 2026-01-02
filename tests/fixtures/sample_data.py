"""Sample data fixtures for testing."""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_ohlcv():
    """Generate sample OHLCV data with clear structure for testing."""
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=100, freq="1h")

    # Create uptrend with pullbacks
    close = [100.0]
    for i in range(1, 100):
        if i % 10 < 5:  # Rally phase
            close.append(close[-1] * 1.005)
        else:  # Pullback phase
            close.append(close[-1] * 0.997)

    close = np.array(close)

    return pd.DataFrame(
        {
            "open": close * 0.999,
            "high": close * 1.005,
            "low": close * 0.995,
            "close": close,
            "volume": np.random.randint(1000, 10000, 100),
        },
        index=dates,
    )


@pytest.fixture
def trending_data():
    """Generate uptrending OHLCV data."""
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=200, freq="1h")

    # Uptrend with noise
    trend = np.linspace(100, 150, 200)
    noise = np.random.randn(200) * 2
    close = trend + noise

    return pd.DataFrame(
        {
            "open": close - np.random.rand(200),
            "high": close + np.random.rand(200) * 2,
            "low": close - np.random.rand(200) * 2,
            "close": close,
            "volume": np.random.randint(1000, 10000, 200),
        },
        index=dates,
    )


@pytest.fixture
def downtrending_data():
    """Generate downtrending OHLCV data."""
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=200, freq="1h")

    # Downtrend with noise
    trend = np.linspace(150, 100, 200)
    noise = np.random.randn(200) * 2
    close = trend + noise

    return pd.DataFrame(
        {
            "open": close + np.random.rand(200),
            "high": close + np.random.rand(200) * 2,
            "low": close - np.random.rand(200) * 2,
            "close": close,
            "volume": np.random.randint(1000, 10000, 200),
        },
        index=dates,
    )


@pytest.fixture
def ranging_data():
    """Generate ranging/sideways OHLCV data."""
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=200, freq="1h")

    # Ranging with oscillation
    base = 100
    oscillation = np.sin(np.linspace(0, 4 * np.pi, 200)) * 5
    noise = np.random.randn(200) * 1
    close = base + oscillation + noise

    return pd.DataFrame(
        {
            "open": close - np.random.rand(200) * 0.5,
            "high": close + np.random.rand(200) * 1.5,
            "low": close - np.random.rand(200) * 1.5,
            "close": close,
            "volume": np.random.randint(1000, 10000, 200),
        },
        index=dates,
    )


@pytest.fixture
def liquidity_sweep_data():
    """Generate data with a clear liquidity sweep pattern."""
    dates = pd.date_range("2024-01-01", periods=20, freq="1h")

    # Build up with equal lows, then sweep and reversal
    data = pd.DataFrame(
        {
            "high": [
                100,
                101,
                100,
                101,
                100,
                101,
                100,
                99,
                103,
                105,
                106,
                107,
                108,
                109,
                110,
                111,
                112,
                113,
                114,
                115,
            ],
            "low": [
                98,
                99,
                98,
                99,
                98,
                99,
                98,
                95,
                99,
                101,
                102,
                103,
                104,
                105,
                106,
                107,
                108,
                109,
                110,
                111,
            ],
            "close": [
                99,
                100,
                99,
                100,
                99,
                100,
                99,
                96,
                102,
                104,
                105,
                106,
                107,
                108,
                109,
                110,
                111,
                112,
                113,
                114,
            ],
            "open": [
                99,
                99,
                100,
                99,
                100,
                99,
                100,
                99,
                97,
                102,
                104,
                105,
                106,
                107,
                108,
                109,
                110,
                111,
                112,
                113,
            ],
            "volume": [1000] * 20,
        },
        index=dates,
    )

    return data


@pytest.fixture
def fvg_data():
    """Generate data with a clear Fair Value Gap pattern."""
    dates = pd.date_range("2024-01-01", periods=10, freq="1h")

    # Bullish FVG: Gap between candle 1 high and candle 3 low
    data = pd.DataFrame(
        {
            "open": [100, 101, 106, 107, 108, 109, 108, 107, 108, 109],
            "high": [101, 102, 108, 109, 110, 110, 109, 108, 109, 110],
            "low": [99, 100, 105, 106, 107, 108, 107, 106, 107, 108],
            "close": [101, 102, 107, 108, 109, 109, 108, 107, 108, 109],
            "volume": [1000] * 10,
        },
        index=dates,
    )

    return data
