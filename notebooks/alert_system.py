"""Alert system for trading setups - visual and audio notifications."""

import logging
from typing import Optional, Callable, List, Dict
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum
import pandas as pd

# Audio support (optional - works in Jupyter)
try:
    from IPython.display import Audio, display, HTML
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False


logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"       # FYI - low importance
    SETUP = "setup"     # Valid setup detected
    HIGH = "high"       # High confidence setup (>70%)
    CRITICAL = "critical"  # Extremely high confidence (>85%)


@dataclass
class Alert:
    """Trading setup alert."""
    timestamp: datetime
    level: AlertLevel
    title: str
    message: str
    confidence: Optional[float] = None
    timeframe: Optional[str] = None
    metadata: Optional[dict] = None

    def __str__(self):
        """String representation."""
        conf_str = f" [{self.confidence:.0f}%]" if self.confidence else ""
        tf_str = f" ({self.timeframe})" if self.timeframe else ""
        return f"[{self.level.value.upper()}]{tf_str} {self.title}{conf_str}: {self.message}"


class AlertSystem:
    """
    Trading alert system with visual and audio notifications.

    Features:
    - Multiple alert levels (info, setup, high, critical)
    - Audio notifications (optional)
    - Alert history tracking
    - Configurable thresholds
    - Jupyter-friendly output

    Example:
        >>> alerts = AlertSystem(min_confidence=70, enable_sound=True)
        >>> alerts.setup_detected(
        ...     title="Liquidity Sweep Setup",
        ...     message="BTC swept H1 liquidity, now testing H4 order block",
        ...     confidence=78,
        ...     timeframe="H1"
        ... )
        🔔 [HIGH] (H1) Liquidity Sweep Setup [78%]: BTC swept...
    """

    def __init__(
        self,
        min_confidence: float = 70,
        enable_sound: bool = True,
        max_history: int = 100
    ):
        """
        Initialize alert system.

        Args:
            min_confidence: Minimum confidence to trigger alerts (0-100)
            enable_sound: Enable audio notifications
            max_history: Max alerts to keep in history
        """
        self.min_confidence = min_confidence
        self.enable_sound = enable_sound and AUDIO_AVAILABLE
        self.max_history = max_history

        # Alert history
        self.alerts: List[Alert] = []

        # Callbacks for custom handling
        self._callbacks: List[Callable[[Alert], None]] = []

        logger.info(
            f"AlertSystem initialized: min_confidence={min_confidence}%, "
            f"sound={'enabled' if self.enable_sound else 'disabled'}"
        )

    def on_alert(self, callback: Callable[[Alert], None]):
        """
        Register callback for new alerts.

        Args:
            callback: Function to call when alert is triggered
                     Receives Alert object
        """
        self._callbacks.append(callback)

    def setup_detected(
        self,
        title: str,
        message: str,
        confidence: float,
        timeframe: str,
        metadata: Optional[dict] = None
    ):
        """
        Notify about detected trading setup.

        Args:
            title: Alert title (e.g., "Liquidity Sweep Setup")
            message: Detailed message
            confidence: Setup confidence (0-100)
            timeframe: Timeframe where setup detected
            metadata: Additional data (price levels, etc.)
        """
        # Determine alert level based on confidence
        if confidence >= 85:
            level = AlertLevel.CRITICAL
        elif confidence >= 70:
            level = AlertLevel.HIGH
        else:
            level = AlertLevel.SETUP

        # Only alert if meets minimum confidence
        if confidence < self.min_confidence:
            logger.debug(f"Setup ignored (confidence {confidence}% < {self.min_confidence}%)")
            return

        self._trigger_alert(
            level=level,
            title=title,
            message=message,
            confidence=confidence,
            timeframe=timeframe,
            metadata=metadata
        )

    def info(self, title: str, message: str, **kwargs):
        """Trigger info-level alert."""
        self._trigger_alert(AlertLevel.INFO, title, message, **kwargs)

    def _trigger_alert(
        self,
        level: AlertLevel,
        title: str,
        message: str,
        confidence: Optional[float] = None,
        timeframe: Optional[str] = None,
        metadata: Optional[dict] = None
    ):
        """
        Internal: trigger an alert.

        Args:
            level: Alert severity
            title: Alert title
            message: Alert message
            confidence: Setup confidence (optional)
            timeframe: Timeframe (optional)
            metadata: Additional data (optional)
        """
        alert = Alert(
            timestamp=datetime.now(timezone.utc),
            level=level,
            title=title,
            message=message,
            confidence=confidence,
            timeframe=timeframe,
            metadata=metadata or {}
        )

        # Add to history
        self.alerts.append(alert)
        if len(self.alerts) > self.max_history:
            self.alerts.pop(0)

        # Display alert
        self._display_alert(alert)

        # Play sound
        if self.enable_sound and level in [AlertLevel.HIGH, AlertLevel.CRITICAL]:
            self._play_sound(level)

        # Call callbacks
        for callback in self._callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")

        logger.info(f"Alert triggered: {alert}")

    def _display_alert(self, alert: Alert):
        """Display alert in Jupyter notebook."""
        # Color based on level
        colors = {
            AlertLevel.INFO: "#3b82f6",      # Blue
            AlertLevel.SETUP: "#10b981",     # Green
            AlertLevel.HIGH: "#f59e0b",      # Orange
            AlertLevel.CRITICAL: "#ef4444"   # Red
        }

        # Emoji based on level
        emojis = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.SETUP: "✅",
            AlertLevel.HIGH: "🔔",
            AlertLevel.CRITICAL: "🚨"
        }

        color = colors.get(alert.level, "#6b7280")
        emoji = emojis.get(alert.level, "📢")

        # Format confidence
        conf_badge = ""
        if alert.confidence is not None:
            conf_badge = f'<span style="background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 4px; font-size: 0.85em; margin-left: 8px;">{alert.confidence:.0f}%</span>'

        # Format timeframe
        tf_badge = ""
        if alert.timeframe:
            tf_badge = f'<span style="opacity: 0.8; font-size: 0.85em; margin-left: 8px;">({alert.timeframe})</span>'

        # Format timestamp
        time_str = alert.timestamp.strftime("%H:%M:%S")

        html = f'''
        <div style="
            background: linear-gradient(135deg, {color}15 0%, {color}05 100%);
            border-left: 4px solid {color};
            padding: 12px 16px;
            margin: 8px 0;
            border-radius: 6px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <span style="font-size: 1.2em; margin-right: 8px;">{emoji}</span>
                <strong style="color: {color}; font-size: 1.05em;">{alert.title}</strong>
                {conf_badge}
                {tf_badge}
                <span style="margin-left: auto; opacity: 0.6; font-size: 0.85em;">{time_str}</span>
            </div>
            <div style="margin-left: 32px; opacity: 0.9; line-height: 1.5;">
                {alert.message}
            </div>
        </div>
        '''

        if AUDIO_AVAILABLE:
            display(HTML(html))
        else:
            # Fallback to plain print
            print(f"\n{emoji} {alert}\n")

    def _play_sound(self, level: AlertLevel):
        """Play notification sound."""
        if not self.enable_sound:
            return

        try:
            # Generate simple beep sound
            import numpy as np

            # Different frequencies for different levels
            freq = 800 if level == AlertLevel.CRITICAL else 600
            duration = 0.2
            sample_rate = 22050

            t = np.linspace(0, duration, int(sample_rate * duration))
            # Simple sine wave
            wave = np.sin(2 * np.pi * freq * t)
            # Fade out to avoid clicks
            fade = np.linspace(1, 0, len(wave))
            wave = wave * fade

            if AUDIO_AVAILABLE:
                display(Audio(wave, rate=sample_rate, autoplay=True))

        except Exception as e:
            logger.debug(f"Sound playback failed: {e}")

    def get_recent_alerts(self, limit: int = 10) -> List[Alert]:
        """
        Get recent alerts.

        Args:
            limit: Max number of alerts to return

        Returns:
            List of recent alerts (newest first)
        """
        return list(reversed(self.alerts[-limit:]))

    def get_alert_summary(self) -> Dict[str, int]:
        """
        Get alert statistics.

        Returns:
            Dict with counts per level
        """
        summary = {level.value: 0 for level in AlertLevel}
        for alert in self.alerts:
            summary[alert.level.value] += 1
        return summary

    def clear_history(self):
        """Clear alert history."""
        self.alerts.clear()
        logger.info("Alert history cleared")


class TradeJournal:
    """
    Trade journal for logging setups and tracking performance.

    Tracks:
    - All detected setups
    - Confidence scores over time
    - Setup frequency per timeframe
    - Performance metrics (if trades executed)
    """

    def __init__(self):
        """Initialize trade journal."""
        self.entries: List[Dict] = []

        logger.info("TradeJournal initialized")

    def log_setup(
        self,
        timestamp: datetime,
        symbol: str,
        timeframe: str,
        setup_type: str,
        confidence: float,
        price: float,
        metadata: Optional[dict] = None
    ):
        """
        Log a detected setup.

        Args:
            timestamp: When setup detected
            symbol: Trading symbol
            timeframe: Setup timeframe
            setup_type: Type of setup (e.g., "Liquidity Sweep")
            confidence: Setup confidence
            price: Current price
            metadata: Additional data
        """
        entry = {
            'timestamp': timestamp,
            'symbol': symbol,
            'timeframe': timeframe,
            'setup_type': setup_type,
            'confidence': confidence,
            'price': price,
            'metadata': metadata or {}
        }

        self.entries.append(entry)
        logger.debug(f"Journal entry: {setup_type} on {symbol} {timeframe} @ {confidence}%")

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert journal to DataFrame.

        Returns:
            DataFrame with all entries
        """
        if not self.entries:
            return pd.DataFrame()

        df = pd.DataFrame(self.entries)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)

        return df

    def get_statistics(self) -> dict:
        """
        Get journal statistics.

        Returns:
            Dict with statistics
        """
        if not self.entries:
            return {
                'total_setups': 0,
                'avg_confidence': 0,
                'by_timeframe': {},
                'by_type': {}
            }

        df = self.to_dataframe()

        return {
            'total_setups': len(df),
            'avg_confidence': df['confidence'].mean(),
            'by_timeframe': df.groupby('timeframe').size().to_dict(),
            'by_type': df.groupby('setup_type').size().to_dict(),
            'confidence_distribution': {
                'min': df['confidence'].min(),
                'max': df['confidence'].max(),
                'median': df['confidence'].median()
            }
        }

    def get_recent_entries(self, limit: int = 10) -> pd.DataFrame:
        """
        Get recent journal entries.

        Args:
            limit: Max number of entries

        Returns:
            DataFrame with recent entries
        """
        df = self.to_dataframe()
        if df.empty:
            return df
        return df.tail(limit)

    def clear(self):
        """Clear journal."""
        self.entries.clear()
        logger.info("Journal cleared")
