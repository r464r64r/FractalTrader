"""State persistence for paper trading bot.

This module handles saving and loading trading state to survive restarts.
Critical for Sprint 3 success criteria: "Can stop/restart without losing state"
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict, field
from copy import deepcopy
from filelock import FileLock, Timeout


logger = logging.getLogger(__name__)


@dataclass
class TradingState:
    """
    Complete trading state for persistence.

    Attributes:
        open_positions: Dict of currently open positions
        trade_history: List of all executed trades
        starting_balance: Initial portfolio value
        session_start: When trading session started
        last_updated: Last state update timestamp
        metadata: Additional state information
    """
    open_positions: Dict[str, Any] = field(default_factory=dict)
    trade_history: List[Dict[str, Any]] = field(default_factory=list)
    starting_balance: float = 0.0
    session_start: str = ""
    last_updated: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradingState':
        """Create state from dictionary."""
        return cls(**data)


class StateManager:
    """
    Manages trading state persistence.

    Features:
    - Automatic state saving
    - Graceful recovery from corrupted files
    - Backup rotation (keeps last N states)
    - Thread-safe operations

    Example:
        >>> manager = StateManager('trading_state.json')
        >>> manager.save_position('BTC', position_data)
        >>> positions = manager.load_positions()
        >>> manager.save_trade(trade_data)
        >>> history = manager.load_trade_history()
    """

    def __init__(
        self,
        state_file: str = '.trading_state.json',
        backup_count: int = 5,
        auto_save: bool = True
    ):
        """
        Initialize state manager.

        Args:
            state_file: Path to state file (relative or absolute)
            backup_count: Number of backup files to keep
            auto_save: If True, save state after each update
        """
        self.state_file = Path(state_file)
        self.backup_count = backup_count
        self.auto_save = auto_save

        # Ensure parent directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing state or create new
        self.state = self._load_or_create_state()

        logger.info(f"StateManager initialized: {self.state_file}")

    def save_position(
        self,
        symbol: str,
        position_data: Dict[str, Any]
    ) -> None:
        """
        Save or update an open position.

        Args:
            symbol: Trading symbol (e.g., 'BTC')
            position_data: Position information dict
        """
        self.state.open_positions[symbol] = self._serialize_position(position_data)
        self.state.last_updated = datetime.now().isoformat()

        if self.auto_save:
            self._save_state()

        logger.debug(f"Saved position: {symbol}")

    def remove_position(self, symbol: str) -> None:
        """
        Remove a closed position.

        Args:
            symbol: Trading symbol to remove
        """
        if symbol in self.state.open_positions:
            del self.state.open_positions[symbol]
            self.state.last_updated = datetime.now().isoformat()

            if self.auto_save:
                self._save_state()

            logger.debug(f"Removed position: {symbol}")

    def load_positions(self) -> Dict[str, Any]:
        """
        Load all open positions.

        Returns:
            Dictionary of open positions (deep copy)
        """
        return deepcopy(self.state.open_positions)

    def save_trade(self, trade_data: Dict[str, Any]) -> None:
        """
        Save a trade to history.

        Args:
            trade_data: Trade information dict
        """
        serialized_trade = self._serialize_trade(trade_data)
        self.state.trade_history.append(serialized_trade)
        self.state.last_updated = datetime.now().isoformat()

        if self.auto_save:
            self._save_state()

        logger.debug(f"Saved trade: {serialized_trade.get('symbol')}")

    def load_trade_history(self) -> List[Dict[str, Any]]:
        """
        Load complete trade history.

        Returns:
            List of all trades (deep copy)
        """
        return deepcopy(self.state.trade_history)

    def set_starting_balance(self, balance: float) -> None:
        """
        Set starting balance for the session.

        Args:
            balance: Starting portfolio value
        """
        self.state.starting_balance = balance
        self.state.session_start = datetime.now().isoformat()
        self.state.last_updated = datetime.now().isoformat()

        if self.auto_save:
            self._save_state()

        logger.info(f"Set starting balance: ${balance:,.2f}")

    def get_starting_balance(self) -> float:
        """
        Get starting balance for the session.

        Returns:
            Starting balance
        """
        return self.state.starting_balance

    def save_metadata(self, key: str, value: Any) -> None:
        """
        Save custom metadata.

        Args:
            key: Metadata key
            value: Metadata value (must be JSON-serializable)
        """
        self.state.metadata[key] = value
        self.state.last_updated = datetime.now().isoformat()

        if self.auto_save:
            self._save_state()

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get custom metadata.

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default
        """
        return self.state.metadata.get(key, default)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get trading session statistics.

        Returns:
            Dictionary with stats:
            - total_trades: Number of trades
            - open_positions: Number of open positions
            - session_start: Session start time
            - last_updated: Last update time
        """
        return {
            'total_trades': len(self.state.trade_history),
            'open_positions': len(self.state.open_positions),
            'session_start': self.state.session_start,
            'last_updated': self.state.last_updated,
            'starting_balance': self.state.starting_balance
        }

    def force_save(self) -> None:
        """Force save state immediately."""
        self._save_state()
        logger.info("State saved manually")

    def reset_state(self, confirm: bool = False) -> None:
        """
        Reset state (clear all data).

        Args:
            confirm: Must be True to actually reset

        Raises:
            ValueError: If confirm is False
        """
        if not confirm:
            raise ValueError("Must set confirm=True to reset state")

        # Backup current state before reset
        self._create_backup()

        # Create new empty state
        self.state = TradingState()
        self._save_state()

        logger.warning("State reset complete")

    def _load_or_create_state(self) -> TradingState:
        """Load existing state or create new one."""
        if self.state_file.exists():
            lock_file = f"{self.state_file}.lock"
            lock = FileLock(lock_file, timeout=10)

            try:
                with lock:
                    with open(self.state_file, 'r') as f:
                        data = json.load(f)
                    logger.info(f"Loaded state from {self.state_file}")
                    return TradingState.from_dict(data)
            except Timeout:
                logger.error(f"Failed to acquire file lock for {self.state_file} (timeout)")
                logger.warning("Creating new state")
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
                logger.warning("Creating new state")

                # Try to recover from backup
                if self._try_recover_from_backup():
                    return self._load_or_create_state()

        # Create new state
        logger.info("Creating new state")
        return TradingState()

    def _save_state(self) -> None:
        """Save current state to file."""
        lock_file = f"{self.state_file}.lock"
        lock = FileLock(lock_file, timeout=10)

        try:
            with lock:
                # Create backup before saving
                if self.state_file.exists():
                    self._create_backup()

                # Write state to file
                with open(self.state_file, 'w') as f:
                    json.dump(self.state.to_dict(), f, indent=2)

                logger.debug(f"State saved to {self.state_file}")
        except Timeout:
            logger.error(f"Failed to acquire file lock for {self.state_file} (timeout)")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def _create_backup(self) -> None:
        """Create backup of current state file."""
        if not self.state_file.exists():
            return

        try:
            # Rotate backups
            for i in range(self.backup_count - 1, 0, -1):
                old_backup = self.state_file.with_suffix(f'.json.bak{i}')
                new_backup = self.state_file.with_suffix(f'.json.bak{i+1}')

                if old_backup.exists():
                    old_backup.rename(new_backup)

            # Create new backup
            backup_path = self.state_file.with_suffix('.json.bak1')
            self.state_file.rename(backup_path)

            # Restore original (we just renamed it)
            backup_path.rename(self.state_file)

            # Copy to backup
            import shutil
            shutil.copy2(self.state_file, backup_path)

            logger.debug(f"Backup created: {backup_path}")
        except Exception as e:
            logger.warning(f"Backup creation failed: {e}")

    def _try_recover_from_backup(self) -> bool:
        """
        Try to recover from backup files.

        Returns:
            True if recovery successful
        """
        lock_file = f"{self.state_file}.lock"
        lock = FileLock(lock_file, timeout=10)

        for i in range(1, self.backup_count + 1):
            backup_path = self.state_file.with_suffix(f'.json.bak{i}')

            if not backup_path.exists():
                continue

            try:
                with lock:
                    with open(backup_path, 'r') as f:
                        data = json.load(f)

                    # Backup is valid, restore it
                    with open(self.state_file, 'w') as f:
                        json.dump(data, f, indent=2)

                    logger.info(f"Recovered from backup: {backup_path}")
                    return True
            except Timeout:
                logger.error(f"Failed to acquire file lock for recovery (timeout)")
                continue
            except Exception as e:
                logger.warning(f"Backup {backup_path} corrupted: {e}")
                continue

        logger.error("No valid backups found")
        return False

    def _serialize_position(self, position_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Serialize position data for JSON storage.

        Converts datetime objects and other non-JSON types to strings.
        """
        serialized = position_data.copy()

        for key, value in serialized.items():
            if isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif hasattr(value, 'to_dict'):
                serialized[key] = value.to_dict()

        return serialized

    def _serialize_trade(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Serialize trade data for JSON storage.

        Converts datetime objects and other non-JSON types to strings.
        """
        serialized = trade_data.copy()

        for key, value in serialized.items():
            if isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif hasattr(value, 'to_dict'):
                serialized[key] = value.to_dict()

        return serialized
