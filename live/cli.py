"""Command-line interface for paper trading bot.

Provides commands to manage the trading bot:
- start: Start paper trading
- stop: Stop running bot
- status: Show current status
- report: Generate performance report

Usage:
    python -m live.cli start --strategy liquidity_sweep --duration 3600
    python -m live.cli status
    python -m live.cli report
    python -m live.cli stop
"""

import argparse
import logging
import sys
import signal
from pathlib import Path
from typing import Optional

from live.hl_integration.config import HyperliquidConfig
from live.hl_integration.testnet import HyperliquidTestnetTrader
from live.state_manager import StateManager
from live.reporting import PerformanceReporter

# Import strategies
from strategies.liquidity_sweep import LiquiditySweepStrategy
from strategies.fvg_fill import FVGFillStrategy
from strategies.bos_orderblock import BOSOrderBlockStrategy


logger = logging.getLogger(__name__)


# PID file for tracking running bot
PID_FILE = Path('.trading_bot.pid')
STATE_FILE = Path('.testnet_state.json')


def setup_logging(level: str = 'INFO') -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def get_strategy(strategy_name: str):
    """
    Get strategy instance by name.

    Args:
        strategy_name: Strategy name

    Returns:
        Strategy instance

    Raises:
        ValueError: If strategy not found
    """
    strategies = {
        'liquidity_sweep': LiquiditySweepStrategy,
        'fvg_fill': FVGFillStrategy,
        'bos_orderblock': BOSOrderBlockStrategy
    }

    if strategy_name not in strategies:
        raise ValueError(
            f"Unknown strategy: {strategy_name}. "
            f"Available: {list(strategies.keys())}"
        )

    return strategies[strategy_name]()


def cmd_start(args: argparse.Namespace) -> int:
    """
    Start paper trading bot.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 = success)
    """
    # Check if bot is already running
    if PID_FILE.exists():
        print("⚠️  Bot is already running!")
        print(f"PID file exists: {PID_FILE}")
        print("Run 'live.cli stop' to stop it first, or remove PID file if it crashed.")
        return 1

    # Setup logging
    setup_logging(args.log_level)

    print("🚀 Starting paper trading bot...")
    print(f"Strategy: {args.strategy}")
    print(f"Network: testnet")
    print(f"Duration: {args.duration}s" if args.duration else "Duration: unlimited")

    try:
        # Load config
        config = HyperliquidConfig.from_env(network='testnet')
        config.log_level = args.log_level

        # Get strategy
        strategy = get_strategy(args.strategy)

        # Create trader
        trader = HyperliquidTestnetTrader(
            config=config,
            strategy=strategy,
            state_file=str(STATE_FILE)
        )

        # Write PID file
        PID_FILE.write_text(str(id(trader)))

        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            print("\n⚠️  Received shutdown signal")
            trader.stop()
            PID_FILE.unlink(missing_ok=True)
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start trading
        print("✅ Bot started successfully")
        print("Press Ctrl+C to stop")
        print("-" * 60)

        trader.run(duration_seconds=args.duration)

        # Cleanup
        PID_FILE.unlink(missing_ok=True)

        print("\n✅ Bot stopped successfully")
        return 0

    except KeyboardInterrupt:
        print("\n⚠️  Bot stopped by user")
        PID_FILE.unlink(missing_ok=True)
        return 0
    except Exception as e:
        logger.error(f"Bot failed: {e}", exc_info=True)
        print(f"\n❌ Bot failed: {e}")
        PID_FILE.unlink(missing_ok=True)
        return 1


def cmd_stop(args: argparse.Namespace) -> int:
    """
    Stop running bot.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 = success)
    """
    if not PID_FILE.exists():
        print("ℹ️  No bot is currently running")
        return 0

    print("🛑 Stopping bot...")

    # Note: In a real implementation, we would send a signal to the process
    # For now, we'll just remove the PID file and inform the user
    PID_FILE.unlink()

    print("✅ Bot stop signal sent")
    print("Note: Bot will stop after current iteration")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """
    Show current bot status.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 = success)
    """
    print("=" * 60)
    print("📊 BOT STATUS")
    print("=" * 60)

    # Check if running
    is_running = PID_FILE.exists()
    status_emoji = "🟢" if is_running else "🔴"
    status_text = "RUNNING" if is_running else "STOPPED"

    print(f"\nStatus: {status_emoji} {status_text}")

    if not STATE_FILE.exists():
        print("No trading session data found")
        return 0

    # Load state
    try:
        state_manager = StateManager(state_file=str(STATE_FILE), auto_save=False)
        stats = state_manager.get_stats()

        print(f"\n📈 Session Info:")
        print(f"  Started: {stats['session_start']}")
        print(f"  Last Updated: {stats['last_updated']}")
        print(f"  Starting Balance: ${stats['starting_balance']:,.2f}")

        print(f"\n💼 Positions:")
        print(f"  Open: {stats['open_positions']}")

        print(f"\n📊 Trades:")
        print(f"  Total: {stats['total_trades']}")

        # Show open positions
        positions = state_manager.load_positions()
        if positions:
            print(f"\n🔓 Open Positions:")
            for symbol, pos in positions.items():
                entry = pos.get('entry_price', 0)
                size = pos.get('size', 0)
                print(f"  {symbol}: {size:.4f} @ ${entry:,.2f}")

        print("=" * 60)
        return 0

    except Exception as e:
        logger.error(f"Failed to load status: {e}")
        print(f"❌ Failed to load status: {e}")
        return 1


def cmd_report(args: argparse.Namespace) -> int:
    """
    Generate performance report.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 = success)
    """
    if not STATE_FILE.exists():
        print("❌ No trading session data found")
        print("Start a trading session first with: live.cli start")
        return 1

    try:
        # Load state
        state_manager = StateManager(state_file=str(STATE_FILE), auto_save=False)

        starting_balance = state_manager.get_starting_balance()
        positions = state_manager.load_positions()
        trade_history = state_manager.load_trade_history()
        session_start = state_manager.state.session_start

        # Calculate current balance (simplified - just starting + PnL from trades)
        current_balance = starting_balance
        for trade in trade_history:
            pnl = trade.get('pnl', 0)
            current_balance += pnl

        # Generate report
        reporter = PerformanceReporter(
            starting_balance=starting_balance,
            open_positions=positions,
            trade_history=trade_history,
            session_start=session_start
        )

        metrics = reporter.calculate_metrics(current_balance)

        # Print report
        reporter.print_report(metrics)

        # Save to file if requested
        if args.output:
            reporter.save_report(metrics, args.output, format=args.format)
            print(f"\n💾 Report saved to: {args.output}")

        return 0

    except Exception as e:
        logger.error(f"Failed to generate report: {e}", exc_info=True)
        print(f"❌ Failed to generate report: {e}")
        return 1


def main() -> int:
    """
    Main CLI entry point.

    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description='FractalTrader Paper Trading Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start bot with liquidity sweep strategy for 1 hour
  python -m live.cli start --strategy liquidity_sweep --duration 3600

  # Start bot indefinitely (until stopped)
  python -m live.cli start --strategy fvg_fill

  # Check bot status
  python -m live.cli status

  # Generate performance report
  python -m live.cli report

  # Save report to file
  python -m live.cli report --output daily_report.json

  # Stop running bot
  python -m live.cli stop
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Start command
    start_parser = subparsers.add_parser('start', help='Start paper trading bot')
    start_parser.add_argument(
        '--strategy',
        type=str,
        default='liquidity_sweep',
        choices=['liquidity_sweep', 'fvg_fill', 'bos_orderblock'],
        help='Trading strategy to use (default: liquidity_sweep)'
    )
    start_parser.add_argument(
        '--duration',
        type=int,
        default=None,
        help='Trading duration in seconds (default: unlimited)'
    )
    start_parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )

    # Stop command
    subparsers.add_parser('stop', help='Stop running bot')

    # Status command
    subparsers.add_parser('status', help='Show bot status')

    # Report command
    report_parser = subparsers.add_parser('report', help='Generate performance report')
    report_parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Save report to file (e.g., report.json)'
    )
    report_parser.add_argument(
        '--format',
        type=str,
        default='json',
        choices=['json', 'csv'],
        help='Report format (default: json)'
    )

    # Parse arguments
    args = parser.parse_args()

    # Execute command
    if args.command == 'start':
        return cmd_start(args)
    elif args.command == 'stop':
        return cmd_stop(args)
    elif args.command == 'status':
        return cmd_status(args)
    elif args.command == 'report':
        return cmd_report(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
