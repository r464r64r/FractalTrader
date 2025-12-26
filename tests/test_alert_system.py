"""Tests for alert system and trade journal."""

import pytest
import pandas as pd
from datetime import datetime, timezone
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from notebooks.alert_system import AlertSystem, AlertLevel, Alert, TradeJournal


class TestAlert:
    """Test Alert dataclass."""

    def test_alert_creation(self):
        """Test creating an alert."""
        alert = Alert(
            timestamp=datetime.now(timezone.utc),
            level=AlertLevel.HIGH,
            title="Test Alert",
            message="This is a test",
            confidence=75,
            timeframe="1h"
        )

        assert alert.level == AlertLevel.HIGH
        assert alert.title == "Test Alert"
        assert alert.confidence == 75
        assert alert.timeframe == "1h"

    def test_alert_string_representation(self):
        """Test alert string output."""
        alert = Alert(
            timestamp=datetime.now(timezone.utc),
            level=AlertLevel.CRITICAL,
            title="Critical Setup",
            message="High confidence trade",
            confidence=90,
            timeframe="4h"
        )

        str_repr = str(alert)

        assert "CRITICAL" in str_repr
        assert "Critical Setup" in str_repr
        assert "90%" in str_repr
        assert "4h" in str_repr


class TestAlertSystem:
    """Test suite for AlertSystem."""

    @pytest.fixture
    def alert_system(self):
        """Create alert system for testing."""
        return AlertSystem(
            min_confidence=70,
            enable_sound=False,  # Disable sound for tests
            max_history=10
        )

    def test_initialization(self, alert_system):
        """Test alert system initialization."""
        assert alert_system.min_confidence == 70
        assert alert_system.enable_sound is False
        assert alert_system.max_history == 10
        assert len(alert_system.alerts) == 0

    def test_setup_detected_high_confidence(self, alert_system):
        """Test detecting high confidence setup."""
        alert_system.setup_detected(
            title="Liquidity Sweep",
            message="BTC swept liquidity",
            confidence=85,
            timeframe="1h"
        )

        # Check alert was created
        assert len(alert_system.alerts) == 1

        alert = alert_system.alerts[0]
        assert alert.level == AlertLevel.CRITICAL  # 85% = critical
        assert alert.title == "Liquidity Sweep"
        assert alert.confidence == 85

    def test_setup_detected_medium_confidence(self, alert_system):
        """Test detecting medium confidence setup."""
        alert_system.setup_detected(
            title="Order Block",
            message="Testing OB",
            confidence=75,
            timeframe="4h"
        )

        alert = alert_system.alerts[0]
        assert alert.level == AlertLevel.HIGH  # 75% = high

    def test_setup_below_threshold(self, alert_system):
        """Test setup below confidence threshold is ignored."""
        alert_system.setup_detected(
            title="Weak Setup",
            message="Low confidence",
            confidence=65,  # Below 70% threshold
            timeframe="15m"
        )

        # Should not create alert
        assert len(alert_system.alerts) == 0

    def test_info_alert(self, alert_system):
        """Test info-level alert."""
        alert_system.info(
            title="Market Update",
            message="Volatility increased"
        )

        assert len(alert_system.alerts) == 1
        assert alert_system.alerts[0].level == AlertLevel.INFO

    def test_callback_registration(self, alert_system):
        """Test callback registration and triggering."""
        callback_data = {'called': False, 'alert': None}

        def test_callback(alert):
            callback_data['called'] = True
            callback_data['alert'] = alert

        alert_system.on_alert(test_callback)

        # Trigger alert
        alert_system.info("Test", "Testing callback")

        assert callback_data['called'] is True
        assert callback_data['alert'] is not None
        assert callback_data['alert'].title == "Test"

    def test_max_history_limit(self):
        """Test that history is limited to max_history."""
        alert_system = AlertSystem(max_history=5)

        # Create 10 alerts
        for i in range(10):
            alert_system.info(f"Alert {i}", f"Message {i}")

        # Should only keep last 5
        assert len(alert_system.alerts) == 5
        assert alert_system.alerts[-1].title == "Alert 9"
        assert alert_system.alerts[0].title == "Alert 5"

    def test_get_recent_alerts(self, alert_system):
        """Test getting recent alerts."""
        # Create alerts
        for i in range(5):
            alert_system.info(f"Alert {i}", "Test")

        recent = alert_system.get_recent_alerts(limit=3)

        assert len(recent) == 3
        # Should be newest first
        assert recent[0].title == "Alert 4"
        assert recent[-1].title == "Alert 2"

    def test_get_alert_summary(self, alert_system):
        """Test getting alert statistics."""
        # Create different types of alerts
        alert_system.info("Info", "Test")
        alert_system.setup_detected("Setup 1", "Test", 75, "1h")
        alert_system.setup_detected("Setup 2", "Test", 90, "1h")

        summary = alert_system.get_alert_summary()

        assert summary['info'] == 1
        assert summary['high'] == 1
        assert summary['critical'] == 1

    def test_clear_history(self, alert_system):
        """Test clearing alert history."""
        alert_system.info("Test", "Message")
        alert_system.info("Test 2", "Message")

        assert len(alert_system.alerts) == 2

        alert_system.clear_history()

        assert len(alert_system.alerts) == 0


class TestTradeJournal:
    """Test suite for TradeJournal."""

    @pytest.fixture
    def journal(self):
        """Create trade journal for testing."""
        return TradeJournal()

    def test_initialization(self, journal):
        """Test journal initialization."""
        assert len(journal.entries) == 0

    def test_log_setup(self, journal):
        """Test logging a setup."""
        timestamp = datetime.now(timezone.utc)

        journal.log_setup(
            timestamp=timestamp,
            symbol='BTC',
            timeframe='1h',
            setup_type='Liquidity Sweep',
            confidence=78,
            price=50000.0,
            metadata={'stop_loss': 49500}
        )

        assert len(journal.entries) == 1

        entry = journal.entries[0]
        assert entry['symbol'] == 'BTC'
        assert entry['timeframe'] == '1h'
        assert entry['confidence'] == 78
        assert entry['price'] == 50000.0

    def test_to_dataframe(self, journal):
        """Test converting journal to DataFrame."""
        # Log multiple setups
        for i in range(5):
            journal.log_setup(
                timestamp=datetime.now(timezone.utc),
                symbol='BTC',
                timeframe='1h',
                setup_type=f'Setup {i}',
                confidence=70 + i,
                price=50000 + i * 100
            )

        df = journal.to_dataframe()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5
        assert 'symbol' in df.columns
        assert 'confidence' in df.columns
        assert isinstance(df.index, pd.DatetimeIndex)

    def test_empty_dataframe(self, journal):
        """Test DataFrame when journal is empty."""
        df = journal.to_dataframe()

        assert isinstance(df, pd.DataFrame)
        assert df.empty

    def test_get_statistics(self, journal):
        """Test getting journal statistics."""
        # Log setups with different properties
        journal.log_setup(
            datetime.now(timezone.utc),
            'BTC', '1h', 'Type A', 80, 50000
        )
        journal.log_setup(
            datetime.now(timezone.utc),
            'BTC', '4h', 'Type A', 90, 51000
        )
        journal.log_setup(
            datetime.now(timezone.utc),
            'ETH', '1h', 'Type B', 70, 3000
        )

        stats = journal.get_statistics()

        assert stats['total_setups'] == 3
        assert stats['avg_confidence'] == 80.0
        assert stats['by_timeframe']['1h'] == 2
        assert stats['by_timeframe']['4h'] == 1
        assert stats['by_type']['Type A'] == 2
        assert stats['by_type']['Type B'] == 1

    def test_empty_statistics(self, journal):
        """Test statistics when journal is empty."""
        stats = journal.get_statistics()

        assert stats['total_setups'] == 0
        assert stats['avg_confidence'] == 0
        assert stats['by_timeframe'] == {}
        assert stats['by_type'] == {}

    def test_get_recent_entries(self, journal):
        """Test getting recent journal entries."""
        # Log setups
        for i in range(10):
            journal.log_setup(
                datetime.now(timezone.utc),
                'BTC', '1h', f'Setup {i}', 70 + i, 50000
            )

        recent = journal.get_recent_entries(limit=5)

        assert len(recent) == 5
        # Should be most recent
        assert recent.iloc[-1]['setup_type'] == 'Setup 9'

    def test_clear_journal(self, journal):
        """Test clearing journal."""
        journal.log_setup(
            datetime.now(timezone.utc),
            'BTC', '1h', 'Test', 75, 50000
        )

        assert len(journal.entries) == 1

        journal.clear()

        assert len(journal.entries) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
