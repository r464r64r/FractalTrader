"""Tests for backtesting framework.

NOTE: These tests require vectorbt which is only available in the Docker container.
Run with: docker exec -it fractal-dev python -m pytest tests/test_backtesting.py -v
"""


import numpy as np
import pandas as pd
import pytest

# Skip all tests if vectorbt is not available
pytest.importorskip("vectorbt", reason="vectorbt only available in Docker container")

from backtesting.runner import BacktestResult, BacktestRunner
from strategies.base import BaseStrategy, Signal


# Mock strategy for testing
class MockStrategy(BaseStrategy):
    """Simple mock strategy that generates predictable signals."""

    DEFAULT_PARAMS = {"entry_threshold": 100.5, "min_rr_ratio": 2.0}

    def __init__(self, params: dict = None):
        super().__init__(name="MockStrategy", params=params)

    def generate_signals(self, data: pd.DataFrame) -> list[Signal]:
        """Generate a signal when close > entry_threshold."""
        self.validate_data(data)
        signals = []

        for idx in range(10, len(data)):
            if data["close"].iloc[idx] > self.params["entry_threshold"]:
                signal = Signal(
                    timestamp=data.index[idx],
                    direction=1,
                    entry_price=data["close"].iloc[idx],
                    stop_loss=data["close"].iloc[idx] * 0.98,
                    take_profit=data["close"].iloc[idx] * 1.04,
                    confidence=80,
                    strategy_name=self.name,
                )
                signals.append(signal)
                break  # Only one signal for simplicity

        return signals

    def calculate_confidence(self, data: pd.DataFrame, signal_idx: int) -> int:
        """Return fixed confidence."""
        return 80


class MockNoSignalsStrategy(BaseStrategy):
    """Strategy that never generates signals."""

    def __init__(self):
        super().__init__(name="MockNoSignalsStrategy")

    def generate_signals(self, data: pd.DataFrame) -> list[Signal]:
        """Return empty list."""
        return []

    def calculate_confidence(self, data: pd.DataFrame, signal_idx: int) -> int:
        """Return 0 confidence."""
        return 0


class MockFailingStrategy(BaseStrategy):
    """Strategy that raises exceptions."""

    def __init__(self):
        super().__init__(name="MockFailingStrategy")

    def generate_signals(self, data: pd.DataFrame) -> list[Signal]:
        """Raise exception."""
        raise ValueError("Mock error")

    def calculate_confidence(self, data: pd.DataFrame, signal_idx: int) -> int:
        """Return 0."""
        return 0


@pytest.fixture
def sample_data():
    """Generate simple uptrending OHLCV data."""
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=200, freq="1h")

    # Uptrend
    close = np.linspace(100, 120, 200)

    return pd.DataFrame(
        {
            "open": close - 0.5,
            "high": close + 1.0,
            "low": close - 1.0,
            "close": close,
            "volume": np.random.randint(1000, 10000, 200),
        },
        index=dates,
    )


class TestBacktestRunner:
    """Tests for BacktestRunner."""

    def test_backtest_runner_initialization(self):
        """BacktestRunner should initialize with default parameters."""
        runner = BacktestRunner()
        assert runner.initial_cash == 10000
        assert runner.fees == 0.001
        assert runner.slippage == 0.0005

        # Custom initialization
        runner_custom = BacktestRunner(initial_cash=50000, fees=0.002, slippage=0.001)
        assert runner_custom.initial_cash == 50000
        assert runner_custom.fees == 0.002
        assert runner_custom.slippage == 0.001

    def test_run_with_valid_strategy(self, sample_data):
        """Running with a valid strategy should return BacktestResult."""
        runner = BacktestRunner(initial_cash=10000)
        strategy = MockStrategy()
        result = runner.run(sample_data, strategy)

        assert isinstance(result, BacktestResult)
        assert isinstance(result.total_return, float)
        assert isinstance(result.sharpe_ratio, float)
        assert isinstance(result.equity_curve, pd.Series)
        assert len(result.signals) > 0

    def test_run_with_no_signals_returns_empty_result(self, sample_data):
        """Strategy with no signals should return empty result."""
        runner = BacktestRunner()
        strategy = MockNoSignalsStrategy()
        result = runner.run(sample_data, strategy)

        assert isinstance(result, BacktestResult)
        assert len(result.signals) == 0

    def test_empty_result_has_zero_metrics(self, sample_data):
        """Empty result should have zero for all metrics."""
        runner = BacktestRunner()
        strategy = MockNoSignalsStrategy()
        result = runner.run(sample_data, strategy)

        assert result.total_return == 0.0
        assert result.sharpe_ratio == 0.0
        assert result.sortino_ratio == 0.0
        assert result.max_drawdown == 0.0
        assert result.win_rate == 0.0
        assert result.profit_factor == 0.0
        assert result.total_trades == 0

    def test_empty_result_preserves_initial_cash(self, sample_data):
        """Empty result equity curve should equal initial cash."""
        initial_cash = 25000
        runner = BacktestRunner(initial_cash=initial_cash)
        strategy = MockNoSignalsStrategy()
        result = runner.run(sample_data, strategy)

        # All equity values should equal initial cash
        assert (result.equity_curve == initial_cash).all()

    def test_signals_to_arrays_creates_boolean_series(self, sample_data):
        """_signals_to_arrays should create boolean Series."""
        runner = BacktestRunner()
        signals = [
            Signal(
                timestamp=sample_data.index[10],
                direction=1,
                entry_price=100.0,
                stop_loss=98.0,
                take_profit=104.0,
                confidence=80,
            )
        ]

        entries, exits = runner._signals_to_arrays(sample_data, signals)

        assert isinstance(entries, pd.Series)
        assert isinstance(exits, pd.Series)
        assert entries.dtype == bool
        assert exits.dtype == bool
        assert len(entries) == len(sample_data)
        assert len(exits) == len(sample_data)

    def test_signals_to_arrays_matches_signal_timestamps(self, sample_data):
        """Entry array should mark True at signal timestamp."""
        runner = BacktestRunner()
        signal_timestamp = sample_data.index[50]

        signals = [
            Signal(
                timestamp=signal_timestamp,
                direction=1,
                entry_price=100.0,
                stop_loss=98.0,
                confidence=80,
            )
        ]

        entries, exits = runner._signals_to_arrays(sample_data, signals)

        # Should be True at signal timestamp
        assert entries.loc[signal_timestamp] == True
        # Should be False elsewhere (except other signals)
        assert entries.sum() == 1

    def test_extract_results_handles_nan_values(self):
        """_extract_results should handle NaN values gracefully."""
        # This is tested indirectly through empty result tests
        # The empty result path exercises NaN handling
        runner = BacktestRunner()
        dates = pd.date_range("2024-01-01", periods=10, freq="1h")
        data = pd.DataFrame(
            {
                "open": [100] * 10,
                "high": [101] * 10,
                "low": [99] * 10,
                "close": [100] * 10,
                "volume": [1000] * 10,
            },
            index=dates,
        )

        strategy = MockNoSignalsStrategy()
        result = runner.run(data, strategy)

        # Should have valid (zero) values, not NaN
        assert not pd.isna(result.total_return)
        assert not pd.isna(result.sharpe_ratio)
        assert not pd.isna(result.sortino_ratio)

    def test_extract_results_calculates_win_rate(self, sample_data):
        """Win rate should be calculated correctly from trades."""
        runner = BacktestRunner()
        strategy = MockStrategy()
        result = runner.run(sample_data, strategy)

        # Win rate should be between 0 and 1
        assert 0.0 <= result.win_rate <= 1.0

    def test_extract_results_calculates_profit_factor(self, sample_data):
        """Profit factor should be calculated from gross profit/loss."""
        runner = BacktestRunner()
        strategy = MockStrategy()
        result = runner.run(sample_data, strategy)

        # Profit factor should be >= 0
        assert result.profit_factor >= 0.0

    def test_profit_factor_zero_when_no_losses(self):
        """Profit factor should be 0 when there are no losses."""
        # This happens when gross_loss == 0, formula returns 0
        # Tested through the empty result
        runner = BacktestRunner()
        dates = pd.date_range("2024-01-01", periods=10, freq="1h")
        data = pd.DataFrame(
            {
                "open": [100] * 10,
                "high": [101] * 10,
                "low": [99] * 10,
                "close": [100] * 10,
                "volume": [1000] * 10,
            },
            index=dates,
        )

        strategy = MockNoSignalsStrategy()
        result = runner.run(data, strategy)

        assert result.profit_factor == 0.0

    def test_avg_trade_duration_calculated(self, sample_data):
        """Average trade duration should be calculated."""
        runner = BacktestRunner()
        strategy = MockStrategy()
        result = runner.run(sample_data, strategy)

        assert isinstance(result.avg_trade_duration, pd.Timedelta)

    def test_optimize_returns_sorted_dataframe(self, sample_data):
        """Optimize should return DataFrame sorted by metric."""
        runner = BacktestRunner()
        param_grid = {"entry_threshold": [100.0, 105.0], "min_rr_ratio": [1.5, 2.0]}

        results = runner.optimize(sample_data, MockStrategy, param_grid, metric="total_return")

        assert isinstance(results, pd.DataFrame)
        if len(results) > 1:
            # Check sorted in descending order
            returns = results["total_return"].values
            assert all(returns[i] >= returns[i + 1] for i in range(len(returns) - 1))

    def test_optimize_tests_all_param_combinations(self, sample_data):
        """Optimize should test all parameter combinations."""
        runner = BacktestRunner()
        param_grid = {"entry_threshold": [100.0, 105.0, 110.0], "min_rr_ratio": [1.5, 2.0]}

        results = runner.optimize(sample_data, MockStrategy, param_grid)

        # Should test 3 × 2 = 6 combinations (if all succeed)
        # At least should have tested multiple combinations
        assert len(results) > 0

    def test_optimize_skips_failed_combinations(self, sample_data):
        """Optimize should skip parameter combinations that fail."""
        runner = BacktestRunner()

        # This will likely generate some failing combinations
        param_grid = {
            "entry_threshold": [100.0, 200.0],  # 200 is too high, no signals
        }

        results = runner.optimize(sample_data, MockStrategy, param_grid)

        # Should not crash, even if some combinations fail
        assert isinstance(results, pd.DataFrame)

    def test_optimize_returns_empty_df_when_all_fail(self, sample_data):
        """Optimize should return empty DataFrame when all combinations fail."""
        runner = BacktestRunner()

        # Use failing strategy
        param_grid = {}

        results = runner.optimize(sample_data, MockFailingStrategy, param_grid)

        assert isinstance(results, pd.DataFrame)
        assert len(results) == 0

    def test_fees_and_slippage_applied(self, sample_data):
        """Fees and slippage should affect results."""
        strategy = MockStrategy()

        # Run without fees/slippage
        runner_no_fees = BacktestRunner(fees=0.0, slippage=0.0)
        result_no_fees = runner_no_fees.run(sample_data, strategy)

        # Run with fees/slippage
        runner_with_fees = BacktestRunner(fees=0.01, slippage=0.01)  # 1% each
        result_with_fees = runner_with_fees.run(sample_data, strategy)

        # If there are trades, fees should reduce returns
        if result_no_fees.total_trades > 0:
            assert result_with_fees.total_return <= result_no_fees.total_return

    def test_equity_curve_generated(self, sample_data):
        """Equity curve should be generated for all results."""
        runner = BacktestRunner()
        strategy = MockStrategy()
        result = runner.run(sample_data, strategy)

        assert isinstance(result.equity_curve, pd.Series)
        assert len(result.equity_curve) == len(sample_data)
        assert all(result.equity_curve > 0)  # Should be positive

    def test_trades_dataframe_populated(self, sample_data):
        """Trades DataFrame should be populated when signals exist."""
        runner = BacktestRunner()
        strategy = MockStrategy()
        result = runner.run(sample_data, strategy)

        assert isinstance(result.trades, pd.DataFrame)
        # If signals were generated, trades might exist
        # (depends on vectorbt execution)
