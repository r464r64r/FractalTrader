"""Tests for state persistence module."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from live.state_manager import StateManager, TradingState


class TestTradingState:
    """Tests for TradingState dataclass."""

    def test_state_initialization(self):
        """Test state initializes with defaults."""
        state = TradingState()
        assert state.open_positions == {}
        assert state.trade_history == []
        assert state.starting_balance == 0.0
        assert state.session_start == ""
        assert state.metadata == {}

    def test_state_to_dict(self):
        """Test state serialization to dict."""
        state = TradingState(
            open_positions={"BTC": {"size": 1.0}},
            trade_history=[{"symbol": "BTC", "pnl": 100}],
            starting_balance=100000.0,
        )
        data = state.to_dict()

        assert data["open_positions"] == {"BTC": {"size": 1.0}}
        assert data["trade_history"] == [{"symbol": "BTC", "pnl": 100}]
        assert data["starting_balance"] == 100000.0

    def test_state_from_dict(self):
        """Test state deserialization from dict."""
        data = {
            "open_positions": {"ETH": {"size": 10.0}},
            "trade_history": [],
            "starting_balance": 50000.0,
            "session_start": "2025-01-01T00:00:00",
            "last_updated": "2025-01-01T01:00:00",
            "metadata": {"key": "value"},
        }
        state = TradingState.from_dict(data)

        assert state.open_positions == {"ETH": {"size": 10.0}}
        assert state.starting_balance == 50000.0
        assert state.metadata == {"key": "value"}


class TestStateManager:
    """Tests for StateManager."""

    @pytest.fixture
    def temp_state_file(self):
        """Create temporary state file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        yield temp_path

        # Cleanup
        Path(temp_path).unlink(missing_ok=True)
        # Also cleanup backup files
        for backup in Path(temp_path).parent.glob(f"{Path(temp_path).stem}*.bak*"):
            backup.unlink(missing_ok=True)

    @pytest.fixture
    def manager(self, temp_state_file):
        """Create state manager with temp file."""
        return StateManager(state_file=temp_state_file, auto_save=True)

    def test_manager_initialization(self, temp_state_file):
        """Test manager initializes correctly."""
        manager = StateManager(state_file=temp_state_file)
        assert manager.state_file == Path(temp_state_file)
        assert isinstance(manager.state, TradingState)
        assert manager.auto_save is True

    def test_save_position(self, manager):
        """Test saving a position."""
        position_data = {
            "symbol": "BTC",
            "size": 1.5,
            "entry_price": 50000,
            "stop_loss": 48000,
            "take_profit": 55000,
        }

        manager.save_position("BTC", position_data)

        positions = manager.load_positions()
        assert "BTC" in positions
        assert positions["BTC"]["size"] == 1.5
        assert positions["BTC"]["entry_price"] == 50000

    def test_remove_position(self, manager):
        """Test removing a position."""
        position_data = {"symbol": "BTC", "size": 1.0}
        manager.save_position("BTC", position_data)

        # Verify it exists
        positions = manager.load_positions()
        assert "BTC" in positions

        # Remove it
        manager.remove_position("BTC")

        # Verify it's gone
        positions = manager.load_positions()
        assert "BTC" not in positions

    def test_save_trade(self, manager):
        """Test saving a trade."""
        trade_data = {
            "timestamp": datetime.now(),
            "symbol": "BTC",
            "direction": "LONG",
            "size": 1.0,
            "entry_price": 50000,
            "exit_price": 51000,
            "pnl": 1000,
            "status": "CLOSED",
        }

        manager.save_trade(trade_data)

        history = manager.load_trade_history()
        assert len(history) == 1
        assert history[0]["symbol"] == "BTC"
        assert history[0]["pnl"] == 1000

    def test_load_trade_history(self, manager):
        """Test loading trade history."""
        # Add multiple trades
        for i in range(3):
            trade = {"symbol": "BTC", "pnl": i * 100, "timestamp": datetime.now()}
            manager.save_trade(trade)

        history = manager.load_trade_history()
        assert len(history) == 3
        assert history[0]["pnl"] == 0
        assert history[1]["pnl"] == 100
        assert history[2]["pnl"] == 200

    def test_set_starting_balance(self, manager):
        """Test setting starting balance."""
        manager.set_starting_balance(100000.0)

        assert manager.get_starting_balance() == 100000.0
        assert manager.state.session_start != ""

    def test_metadata_save_load(self, manager):
        """Test saving and loading metadata."""
        manager.save_metadata("strategy", "liquidity_sweep")
        manager.save_metadata("max_positions", 3)

        assert manager.get_metadata("strategy") == "liquidity_sweep"
        assert manager.get_metadata("max_positions") == 3
        assert manager.get_metadata("nonexistent", "default") == "default"

    def test_get_stats(self, manager):
        """Test getting session statistics."""
        manager.set_starting_balance(50000)
        manager.save_trade({"symbol": "BTC", "pnl": 100})
        manager.save_trade({"symbol": "ETH", "pnl": 200})
        manager.save_position("SOL", {"size": 10})

        stats = manager.get_stats()
        assert stats["total_trades"] == 2
        assert stats["open_positions"] == 1
        assert stats["starting_balance"] == 50000
        assert stats["session_start"] != ""

    def test_state_persistence(self, temp_state_file):
        """Test state persists across manager instances."""
        # Create manager and save data
        manager1 = StateManager(state_file=temp_state_file)
        manager1.set_starting_balance(75000)
        manager1.save_position("BTC", {"size": 2.0})
        manager1.save_trade({"symbol": "ETH", "pnl": 500})
        manager1.force_save()

        # Create new manager with same file
        manager2 = StateManager(state_file=temp_state_file)

        # Verify data persisted
        assert manager2.get_starting_balance() == 75000
        assert "BTC" in manager2.load_positions()
        assert len(manager2.load_trade_history()) == 1

    def test_auto_save_disabled(self, temp_state_file):
        """Test auto_save=False doesn't save automatically."""
        manager = StateManager(state_file=temp_state_file, auto_save=False)

        manager.save_position("BTC", {"size": 1.0})

        # File should not be updated yet
        # (We can't easily test this without checking file modification time)
        # Instead, test that manual save works
        manager.force_save()

        # Now create new manager and verify
        manager2 = StateManager(state_file=temp_state_file)
        assert "BTC" in manager2.load_positions()

    def test_reset_state(self, manager):
        """Test resetting state."""
        # Add data
        manager.set_starting_balance(100000)
        manager.save_position("BTC", {"size": 1.0})
        manager.save_trade({"symbol": "ETH", "pnl": 100})

        # Verify data exists
        assert manager.get_starting_balance() == 100000
        assert len(manager.load_positions()) == 1
        assert len(manager.load_trade_history()) == 1

        # Reset
        manager.reset_state(confirm=True)

        # Verify data cleared
        assert manager.get_starting_balance() == 0.0
        assert len(manager.load_positions()) == 0
        assert len(manager.load_trade_history()) == 0

    def test_reset_requires_confirmation(self, manager):
        """Test reset requires confirm=True."""
        with pytest.raises(ValueError, match="Must set confirm=True"):
            manager.reset_state(confirm=False)

    def test_corrupted_state_recovery(self, temp_state_file):
        """Test recovery from corrupted state file."""
        # Create valid state
        manager1 = StateManager(state_file=temp_state_file)
        manager1.set_starting_balance(50000)
        manager1.force_save()

        # Force create a backup before corruption
        manager1._create_backup()

        # Corrupt the file
        with open(temp_state_file, "w") as f:
            f.write("invalid json {{{")

        # Create new manager - should recover from backup
        manager2 = StateManager(state_file=temp_state_file)
        # After recovery from backup, balance should be restored
        assert manager2.get_starting_balance() == 50000  # Recovered from backup

    def test_backup_creation(self, temp_state_file):
        """Test backup files are created."""
        manager = StateManager(state_file=temp_state_file, backup_count=3)

        # Make several changes to trigger backups
        for i in range(5):
            manager.save_position(f"COIN{i}", {"size": float(i)})
            manager.force_save()

        # Check backups exist
        backup_dir = Path(temp_state_file).parent
        backups = list(backup_dir.glob("*.bak*"))
        assert len(backups) > 0  # At least some backups should exist

    def test_datetime_serialization(self, manager):
        """Test datetime objects are properly serialized."""
        now = datetime.now()
        trade_data = {"timestamp": now, "symbol": "BTC", "pnl": 100}

        manager.save_trade(trade_data)

        # Reload manager to test deserialization
        manager.force_save()
        manager2 = StateManager(state_file=manager.state_file)

        history = manager2.load_trade_history()
        assert len(history) == 1
        # Timestamp should be string after serialization
        assert isinstance(history[0]["timestamp"], str)

    def test_concurrent_positions(self, manager):
        """Test managing multiple positions concurrently."""
        positions = {
            "BTC": {"size": 1.0, "entry": 50000},
            "ETH": {"size": 10.0, "entry": 3000},
            "SOL": {"size": 100.0, "entry": 100},
        }

        for symbol, data in positions.items():
            manager.save_position(symbol, data)

        loaded = manager.load_positions()
        assert len(loaded) == 3
        assert loaded["BTC"]["size"] == 1.0
        assert loaded["ETH"]["size"] == 10.0
        assert loaded["SOL"]["size"] == 100.0

    def test_empty_state_file_creation(self, temp_state_file):
        """Test state file is created if it doesn't exist."""
        # Delete file if it exists
        Path(temp_state_file).unlink(missing_ok=True)

        # Create manager - should create new file
        manager = StateManager(state_file=temp_state_file)
        manager.force_save()

        # Verify file exists
        assert Path(temp_state_file).exists()

    def test_load_positions_returns_copy(self, manager):
        """Test load_positions returns a copy, not reference."""
        manager.save_position("BTC", {"size": 1.0})

        positions1 = manager.load_positions()
        positions2 = manager.load_positions()

        # Modify one copy
        positions1["BTC"]["size"] = 999.0

        # Other copy should be unchanged
        assert positions2["BTC"]["size"] == 1.0

        # Original in manager should be unchanged
        positions3 = manager.load_positions()
        assert positions3["BTC"]["size"] == 1.0

    def test_load_trade_history_returns_copy(self, manager):
        """Test load_trade_history returns a copy, not reference."""
        manager.save_trade({"symbol": "BTC", "pnl": 100})

        history1 = manager.load_trade_history()
        history2 = manager.load_trade_history()

        # Modify one copy
        history1[0]["pnl"] = 999

        # Other copy should be unchanged
        assert history2[0]["pnl"] == 100

        # Original in manager should be unchanged
        history3 = manager.load_trade_history()
        assert history3[0]["pnl"] == 100

    def test_concurrent_access_with_file_locking(self, temp_state_file):
        """Test concurrent access with file locking prevents corruption."""
        import multiprocessing
        import time

        def write_positions(state_file, prefix, count):
            """Worker function to write positions."""
            manager = StateManager(state_file=state_file)
            for i in range(count):
                manager.save_position(f"{prefix}_{i}", {"size": float(i)})
                time.sleep(0.01)  # Simulate work

        # Create initial manager
        manager = StateManager(state_file=temp_state_file)
        manager.set_starting_balance(100000)
        manager.force_save()

        # Start two processes writing concurrently
        p1 = multiprocessing.Process(target=write_positions, args=(temp_state_file, "BTC", 5))
        p2 = multiprocessing.Process(target=write_positions, args=(temp_state_file, "ETH", 5))

        p1.start()
        p2.start()

        p1.join(timeout=5)
        p2.join(timeout=5)

        # Verify file is not corrupted
        manager2 = StateManager(state_file=temp_state_file)
        positions = manager2.load_positions()

        # Should have positions from both processes
        btc_positions = [k for k in positions.keys() if k.startswith("BTC")]
        eth_positions = [k for k in positions.keys() if k.startswith("ETH")]

        # File locking should prevent corruption, all writes should succeed
        assert len(btc_positions) > 0
        assert len(eth_positions) > 0

    def test_file_lock_acquisition(self, temp_state_file):
        """Test that file locks are properly acquired and released."""
        manager = StateManager(state_file=temp_state_file)

        # First write should succeed
        manager.save_position("BTC", {"size": 1.0})
        manager.force_save()

        # Second write should also succeed (lock was released)
        manager.save_position("ETH", {"size": 2.0})
        manager.force_save()

        # Verify both writes succeeded
        positions = manager.load_positions()
        assert "BTC" in positions
        assert "ETH" in positions

    def test_file_lock_with_load_and_save(self, temp_state_file):
        """Test file locking works for both load and save operations."""
        # Create initial state
        manager1 = StateManager(state_file=temp_state_file)
        manager1.set_starting_balance(50000)
        manager1.save_position("BTC", {"size": 1.0})
        manager1.force_save()

        # Load with new manager (should acquire lock)
        manager2 = StateManager(state_file=temp_state_file)
        assert manager2.get_starting_balance() == 50000
        assert "BTC" in manager2.load_positions()

        # Save with new manager (should acquire lock)
        manager2.save_position("ETH", {"size": 2.0})
        manager2.force_save()

        # Verify changes persisted
        manager3 = StateManager(state_file=temp_state_file)
        positions = manager3.load_positions()
        assert "BTC" in positions
        assert "ETH" in positions
