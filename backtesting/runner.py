"""
Backtesting framework using vectorbt.

This module provides fast vectorized backtesting for trading strategies,
with comprehensive performance metrics and result analysis.
"""

from dataclasses import dataclass
from itertools import product

import pandas as pd
import vectorbt as vbt

from risk.position_sizing import RiskParameters
from strategies.base import BaseStrategy, Signal


@dataclass
class BacktestResult:
    """
    Results from a backtest run.

    Contains comprehensive performance metrics and detailed trade data.

    Attributes:
        total_return: Total return as decimal (0.5 = 50%)
        sharpe_ratio: Risk-adjusted return metric
        sortino_ratio: Downside risk-adjusted return
        max_drawdown: Maximum peak-to-trough decline (0.2 = 20%)
        win_rate: Percentage of winning trades (0.55 = 55%)
        profit_factor: Gross profit / gross loss ratio
        total_trades: Number of completed trades
        avg_trade_duration: Average time in trade
        equity_curve: Series of portfolio value over time
        trades: DataFrame with trade details
        signals: List of original Signal objects

    Example:
        >>> result = runner.run(data, strategy)
        >>> print(f"Sharpe: {result.sharpe_ratio:.2f}")
        >>> print(f"Win Rate: {result.win_rate:.1%}")
    """

    total_return: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    avg_trade_duration: pd.Timedelta

    # Detailed data
    equity_curve: pd.Series
    trades: pd.DataFrame
    signals: list[Signal]


class BacktestRunner:
    """
    Run backtests using vectorbt.

    Converts strategy signals into vectorbt format and executes
    fast vectorized backtests with realistic fees and slippage.

    Example:
        >>> runner = BacktestRunner(initial_cash=10000, fees=0.001)
        >>> strategy = LiquiditySweepStrategy()
        >>> result = runner.run(btc_data, strategy)
        >>> print(f"Total return: {result.total_return:.2%}")
    """

    def __init__(
        self,
        initial_cash: float = 10000,
        fees: float = 0.001,  # 0.1% per trade
        slippage: float = 0.0005,  # 0.05% slippage
    ):
        """
        Initialize the backtest runner.

        Args:
            initial_cash: Starting portfolio value
            fees: Trading fees as decimal (0.001 = 0.1%)
            slippage: Slippage as decimal (0.0005 = 0.05%)
        """
        self.initial_cash = initial_cash
        self.fees = fees
        self.slippage = slippage

    def run(
        self,
        data: pd.DataFrame,
        strategy: BaseStrategy,
        risk_params: RiskParameters | None = None,
    ) -> BacktestResult:
        """
        Run backtest for a strategy.

        Args:
            data: OHLCV DataFrame with DatetimeIndex
            strategy: Strategy instance to test
            risk_params: Risk parameters (uses defaults if None)

        Returns:
            BacktestResult with performance metrics

        Example:
            >>> from strategies.liquidity_sweep import LiquiditySweepStrategy
            >>> strategy = LiquiditySweepStrategy()
            >>> result = runner.run(data, strategy)
        """
        risk_params = risk_params or RiskParameters()

        # Generate signals
        signals = strategy.generate_signals(data)

        if not signals:
            return self._empty_result(data.index)

        # Convert to vectorbt format
        entries, exits = self._signals_to_arrays(data, signals)

        # Run vectorbt backtest
        portfolio = vbt.Portfolio.from_signals(
            close=data["close"],
            entries=entries,
            exits=exits,
            init_cash=self.initial_cash,
            fees=self.fees,
            slippage=self.slippage,
            freq="1h",  # Adjust based on data timeframe
        )

        return self._extract_results(portfolio, signals, data.index)

    def optimize(
        self,
        data: pd.DataFrame,
        strategy_class: type,
        param_grid: dict,
        metric: str = "sharpe_ratio",
    ) -> pd.DataFrame:
        """
        Optimize strategy parameters.

        Tests all combinations of parameters and ranks by chosen metric.

        Args:
            data: OHLCV DataFrame
            strategy_class: Strategy class to optimize (not instance)
            param_grid: Dict of param_name -> list of values
            metric: Metric to optimize ('sharpe_ratio', 'total_return', etc.)

        Returns:
            DataFrame with results for all parameter combinations, sorted by metric

        Example:
            >>> param_grid = {
            ...     'swing_period': [3, 5, 7],
            ...     'min_rr_ratio': [1.5, 2.0, 2.5]
            ... }
            >>> results = runner.optimize(data, LiquiditySweepStrategy, param_grid)
            >>> best_params = results.iloc[0]
        """
        results = []

        # Generate all combinations
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())

        for values in product(*param_values):
            params = dict(zip(param_names, values))

            try:
                strategy = strategy_class(params)
                result = self.run(data, strategy)

                results.append(
                    {
                        **params,
                        "total_return": result.total_return,
                        "sharpe_ratio": result.sharpe_ratio,
                        "sortino_ratio": result.sortino_ratio,
                        "max_drawdown": result.max_drawdown,
                        "win_rate": result.win_rate,
                        "profit_factor": result.profit_factor,
                        "total_trades": result.total_trades,
                    }
                )
            except Exception:
                # Skip parameter combinations that fail
                continue

        if not results:
            return pd.DataFrame()

        df = pd.DataFrame(results)
        return df.sort_values(metric, ascending=False)

    def _signals_to_arrays(
        self, data: pd.DataFrame, signals: list[Signal]
    ) -> tuple[pd.Series, pd.Series]:
        """
        Convert Signal objects to vectorbt entry/exit arrays.

        Args:
            data: OHLCV DataFrame
            signals: List of Signal objects

        Returns:
            entries: Boolean Series marking entry bars
            exits: Boolean Series marking exit bars
        """
        entries = pd.Series(False, index=data.index)
        exits = pd.Series(False, index=data.index)

        for signal in signals:
            if signal.timestamp in data.index:
                if signal.direction == 1:
                    entries.loc[signal.timestamp] = True
                else:  # direction == -1
                    entries.loc[signal.timestamp] = True  # vectorbt handles shorts

                # For now, use simple exit logic
                # In production, this would be more sophisticated
                # (stop loss, take profit, trailing stop, etc.)

        return entries, exits

    def _extract_results(
        self, portfolio: vbt.Portfolio, signals: list[Signal], index: pd.Index
    ) -> BacktestResult:
        """
        Extract performance metrics from vectorbt portfolio.

        Args:
            portfolio: vectorbt Portfolio object
            signals: Original signals
            index: Data index

        Returns:
            BacktestResult with all metrics
        """
        # Calculate metrics
        total_return = portfolio.total_return()
        sharpe_ratio = portfolio.sharpe_ratio()
        max_drawdown = portfolio.max_drawdown()

        # Handle potential NaN values
        # Modified from DEVELOPMENT.md: Added NaN handling for edge cases
        if pd.isna(total_return):
            total_return = 0.0
        if pd.isna(sharpe_ratio):
            sharpe_ratio = 0.0
        if pd.isna(max_drawdown):
            max_drawdown = 0.0

        # Sortino ratio
        try:
            sortino_ratio = portfolio.sortino_ratio()
            if pd.isna(sortino_ratio):
                sortino_ratio = 0.0
        except Exception:
            sortino_ratio = 0.0

        # Trade statistics
        trades_df = portfolio.trades.records_readable
        total_trades = len(trades_df)

        if total_trades > 0:
            # Win rate
            winning_trades = (trades_df["PnL"] > 0).sum()
            win_rate = winning_trades / total_trades

            # Profit factor
            gross_profit = trades_df[trades_df["PnL"] > 0]["PnL"].sum()
            gross_loss = abs(trades_df[trades_df["PnL"] < 0]["PnL"].sum())
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0

            # Average trade duration
            if "Duration" in trades_df.columns:
                avg_duration = trades_df["Duration"].mean()
            else:
                avg_duration = pd.Timedelta(0)
        else:
            win_rate = 0.0
            profit_factor = 0.0
            avg_duration = pd.Timedelta(0)

        # Equity curve
        equity_curve = portfolio.value()

        return BacktestResult(
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=total_trades,
            avg_trade_duration=avg_duration,
            equity_curve=equity_curve,
            trades=trades_df,
            signals=signals,
        )

    def _empty_result(self, index: pd.Index) -> BacktestResult:
        """
        Return empty result when no signals generated.

        Args:
            index: Data index for equity curve

        Returns:
            BacktestResult with zero values
        """
        equity_curve = pd.Series(self.initial_cash, index=index)

        return BacktestResult(
            total_return=0.0,
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
            max_drawdown=0.0,
            win_rate=0.0,
            profit_factor=0.0,
            total_trades=0,
            avg_trade_duration=pd.Timedelta(0),
            equity_curve=equity_curve,
            trades=pd.DataFrame(),
            signals=[],
        )


# =============================================================================
# TEST REQUIREMENTS
# =============================================================================
# [ ] test_backtest_runner_initialization
# [ ] test_run_with_valid_strategy
# [ ] test_run_with_no_signals_returns_empty_result
# [ ] test_empty_result_has_zero_metrics
# [ ] test_empty_result_preserves_initial_cash
# [ ] test_signals_to_arrays_creates_boolean_series
# [ ] test_signals_to_arrays_matches_signal_timestamps
# [ ] test_extract_results_handles_nan_values
# [ ] test_extract_results_calculates_win_rate
# [ ] test_extract_results_calculates_profit_factor
# [ ] test_profit_factor_zero_when_no_losses
# [ ] test_avg_trade_duration_calculated
# [ ] test_optimize_returns_sorted_dataframe
# [ ] test_optimize_tests_all_param_combinations
# [ ] test_optimize_skips_failed_combinations
# [ ] test_optimize_returns_empty_df_when_all_fail
# [ ] test_fees_and_slippage_applied
# [ ] test_equity_curve_generated
# [ ] test_trades_dataframe_populated
# =============================================================================
