"""Performance reporting for paper trading bot.

Generates daily/weekly reports with key metrics:
- PnL (absolute and percentage)
- Win rate
- Confidence distribution
- Trade statistics
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
from pathlib import Path


logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Trading performance metrics."""

    # Period
    period_start: str
    period_end: str
    duration_hours: float

    # Portfolio
    starting_balance: float
    ending_balance: float
    pnl: float
    pnl_percent: float

    # Trades
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float

    # Confidence
    avg_confidence: float
    min_confidence: float
    max_confidence: float

    # Positions
    open_positions: int
    max_concurrent_positions: int

    # Risk
    max_drawdown: float
    avg_trade_pnl: float
    best_trade: float
    worst_trade: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'period': {
                'start': self.period_start,
                'end': self.period_end,
                'duration_hours': round(self.duration_hours, 2)
            },
            'portfolio': {
                'starting_balance': round(self.starting_balance, 2),
                'ending_balance': round(self.ending_balance, 2),
                'pnl': round(self.pnl, 2),
                'pnl_percent': round(self.pnl_percent, 4)
            },
            'trades': {
                'total': self.total_trades,
                'winning': self.winning_trades,
                'losing': self.losing_trades,
                'win_rate': round(self.win_rate, 4)
            },
            'confidence': {
                'avg': round(self.avg_confidence, 2),
                'min': round(self.min_confidence, 2),
                'max': round(self.max_confidence, 2)
            },
            'positions': {
                'open': self.open_positions,
                'max_concurrent': self.max_concurrent_positions
            },
            'risk': {
                'max_drawdown': round(self.max_drawdown, 4),
                'avg_trade_pnl': round(self.avg_trade_pnl, 2),
                'best_trade': round(self.best_trade, 2),
                'worst_trade': round(self.worst_trade, 2)
            }
        }


class PerformanceReporter:
    """
    Generate performance reports from trading data.

    Example:
        >>> reporter = PerformanceReporter(starting_balance=100000)
        >>> reporter.add_trades(trade_history)
        >>> metrics = reporter.calculate_metrics()
        >>> reporter.print_report(metrics)
        >>> reporter.save_report(metrics, 'daily_report.json')
    """

    def __init__(
        self,
        starting_balance: float,
        open_positions: Optional[Dict] = None,
        trade_history: Optional[List[Dict]] = None,
        session_start: Optional[str] = None
    ):
        """
        Initialize performance reporter.

        Args:
            starting_balance: Starting portfolio value
            open_positions: Dict of open positions
            trade_history: List of trades
            session_start: Session start time (ISO format)
        """
        self.starting_balance = starting_balance
        self.open_positions = open_positions or {}
        self.trade_history = trade_history or []
        self.session_start = session_start or datetime.now().isoformat()

    def calculate_metrics(
        self,
        current_balance: float,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None
    ) -> PerformanceMetrics:
        """
        Calculate performance metrics.

        Args:
            current_balance: Current portfolio value
            period_start: Start of reporting period (defaults to session start)
            period_end: End of reporting period (defaults to now)

        Returns:
            PerformanceMetrics object
        """
        # Parse dates
        start_dt = datetime.fromisoformat(period_start or self.session_start)
        end_dt = datetime.fromisoformat(period_end or datetime.now().isoformat())

        duration_hours = (end_dt - start_dt).total_seconds() / 3600

        # Filter trades in period
        trades_in_period = self._filter_trades_by_period(period_start, period_end)

        # Calculate PnL
        pnl = current_balance - self.starting_balance
        pnl_percent = (pnl / self.starting_balance) if self.starting_balance > 0 else 0

        # Trade statistics
        total_trades = len(trades_in_period)
        winning_trades = sum(1 for t in trades_in_period if t.get('pnl', 0) > 0)
        losing_trades = sum(1 for t in trades_in_period if t.get('pnl', 0) < 0)
        win_rate = (winning_trades / total_trades) if total_trades > 0 else 0

        # Confidence statistics
        confidences = [t.get('confidence', 50) for t in trades_in_period]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        min_confidence = min(confidences) if confidences else 0
        max_confidence = max(confidences) if confidences else 0

        # Position statistics
        open_count = len(self.open_positions)
        max_concurrent = self._calculate_max_concurrent_positions()

        # Risk statistics
        max_drawdown = self._calculate_max_drawdown()
        pnls = [t.get('pnl', 0) for t in trades_in_period if 'pnl' in t]
        avg_trade_pnl = sum(pnls) / len(pnls) if pnls else 0
        best_trade = max(pnls) if pnls else 0
        worst_trade = min(pnls) if pnls else 0

        return PerformanceMetrics(
            period_start=start_dt.isoformat(),
            period_end=end_dt.isoformat(),
            duration_hours=duration_hours,
            starting_balance=self.starting_balance,
            ending_balance=current_balance,
            pnl=pnl,
            pnl_percent=pnl_percent,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            avg_confidence=avg_confidence,
            min_confidence=min_confidence,
            max_confidence=max_confidence,
            open_positions=open_count,
            max_concurrent_positions=max_concurrent,
            max_drawdown=max_drawdown,
            avg_trade_pnl=avg_trade_pnl,
            best_trade=best_trade,
            worst_trade=worst_trade
        )

    def print_report(self, metrics: PerformanceMetrics) -> None:
        """
        Print formatted performance report.

        Args:
            metrics: Performance metrics to print
        """
        print("=" * 60)
        print("📊 TRADING PERFORMANCE REPORT")
        print("=" * 60)

        print(f"\n⏱️  PERIOD")
        print(f"  Start: {metrics.period_start}")
        print(f"  End: {metrics.period_end}")
        print(f"  Duration: {metrics.duration_hours:.1f} hours")

        print(f"\n💰 PORTFOLIO")
        print(f"  Starting Balance: ${metrics.starting_balance:,.2f}")
        print(f"  Ending Balance: ${metrics.ending_balance:,.2f}")
        pnl_sign = "+" if metrics.pnl >= 0 else ""
        print(f"  P&L: {pnl_sign}${metrics.pnl:,.2f} ({pnl_sign}{metrics.pnl_percent:.2%})")

        print(f"\n📈 TRADES")
        print(f"  Total: {metrics.total_trades}")
        print(f"  Winning: {metrics.winning_trades} ({metrics.win_rate:.1%})")
        print(f"  Losing: {metrics.losing_trades}")

        print(f"\n🎯 CONFIDENCE")
        print(f"  Average: {metrics.avg_confidence:.1f}")
        print(f"  Range: {metrics.min_confidence:.0f} - {metrics.max_confidence:.0f}")

        print(f"\n📊 POSITIONS")
        print(f"  Currently Open: {metrics.open_positions}")
        print(f"  Max Concurrent: {metrics.max_concurrent_positions}")

        print(f"\n⚠️  RISK METRICS")
        print(f"  Max Drawdown: {metrics.max_drawdown:.2%}")
        print(f"  Avg Trade P&L: ${metrics.avg_trade_pnl:,.2f}")
        print(f"  Best Trade: ${metrics.best_trade:,.2f}")
        print(f"  Worst Trade: ${metrics.worst_trade:,.2f}")

        print("=" * 60)

    def save_report(
        self,
        metrics: PerformanceMetrics,
        filepath: str,
        format: str = 'json'
    ) -> None:
        """
        Save report to file.

        Args:
            metrics: Performance metrics
            filepath: Output file path
            format: Output format ('json' or 'csv')
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        if format == 'json':
            with open(path, 'w') as f:
                json.dump(metrics.to_dict(), f, indent=2)
            logger.info(f"Report saved to {filepath}")
        elif format == 'csv':
            self._save_csv_report(metrics, path)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _save_csv_report(self, metrics: PerformanceMetrics, path: Path) -> None:
        """Save report as CSV."""
        data = metrics.to_dict()

        # Flatten nested dict
        rows = []
        for category, values in data.items():
            for key, value in values.items():
                rows.append(f"{category}_{key},{value}")

        with open(path, 'w') as f:
            f.write("metric,value\n")
            f.write("\n".join(rows))

        logger.info(f"CSV report saved to {path}")

    def _filter_trades_by_period(
        self,
        period_start: Optional[str],
        period_end: Optional[str]
    ) -> List[Dict]:
        """Filter trades within reporting period."""
        if not period_start and not period_end:
            return self.trade_history

        start_dt = datetime.fromisoformat(period_start or "1970-01-01")
        end_dt = datetime.fromisoformat(period_end or datetime.now().isoformat())

        filtered = []
        for trade in self.trade_history:
            trade_time_str = trade.get('timestamp')
            if not trade_time_str:
                continue

            # Handle both datetime objects and ISO strings
            if isinstance(trade_time_str, datetime):
                trade_dt = trade_time_str
            else:
                try:
                    trade_dt = datetime.fromisoformat(trade_time_str)
                except:
                    continue

            if start_dt <= trade_dt <= end_dt:
                filtered.append(trade)

        return filtered

    def _calculate_max_concurrent_positions(self) -> int:
        """Calculate maximum concurrent positions held."""
        # Simplified: just return current open positions
        # TODO: Track this over time for accurate max
        return len(self.open_positions)

    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown during period."""
        # Simplified: calculate from trade history
        if not self.trade_history:
            return 0.0

        balance = self.starting_balance
        peak = balance
        max_dd = 0.0

        for trade in self.trade_history:
            pnl = trade.get('pnl', 0)
            balance += pnl

            if balance > peak:
                peak = balance

            dd = (peak - balance) / peak if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd

        return max_dd
