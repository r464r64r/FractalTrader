"""Real-time setup detection pipeline for live trading."""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timezone

from strategies.liquidity_sweep import LiquiditySweepStrategy
from strategies.imbalance import calculate_confidence_factors


logger = logging.getLogger(__name__)


class SetupDetector:
    """
    Real-time trading setup detector.

    Analyzes live market data and identifies high-probability setups
    using SMC methodology.

    Features:
    - Multi-timeframe analysis
    - Confidence scoring
    - Setup validation
    - Metadata extraction

    Example:
        >>> detector = SetupDetector(min_confidence=70)
        >>> setups = detector.scan_for_setups(data)
        >>> for setup in setups:
        ...     print(f"{setup['type']}: {setup['confidence']}%")
    """

    def __init__(
        self,
        min_confidence: float = 70,
        primary_timeframe: str = '1h',
        higher_timeframes: List[str] = ['4h']
    ):
        """
        Initialize setup detector.

        Args:
            min_confidence: Minimum confidence to report setups
            primary_timeframe: Main timeframe for entry signals
            higher_timeframes: HTF for bias/confirmation
        """
        self.min_confidence = min_confidence
        self.primary_timeframe = primary_timeframe
        self.higher_timeframes = higher_timeframes

        # Initialize strategy
        self.strategy = LiquiditySweepStrategy()

        logger.info(
            f"SetupDetector initialized: min_confidence={min_confidence}%, "
            f"primary={primary_timeframe}, HTF={higher_timeframes}"
        )

    def scan_for_setups(
        self,
        data: Dict[str, pd.DataFrame],
        current_price: Optional[float] = None
    ) -> List[Dict]:
        """
        Scan market data for trading setups.

        Args:
            data: Dict of {timeframe: DataFrame}
            current_price: Current market price (optional)

        Returns:
            List of detected setups with metadata
        """
        setups = []

        # Check if we have required data
        if self.primary_timeframe not in data:
            logger.warning(f"Primary timeframe {self.primary_timeframe} not in data")
            return setups

        primary_df = data[self.primary_timeframe]

        if primary_df.empty:
            return setups

        # Get current price
        if current_price is None:
            current_price = float(primary_df['close'].iloc[-1])

        # Detect liquidity sweep setups
        liq_setups = self._detect_liquidity_sweeps(data, current_price)
        setups.extend(liq_setups)

        # Detect order block bounces
        ob_setups = self._detect_order_block_bounces(data, current_price)
        setups.extend(ob_setups)

        # Filter by confidence
        setups = [s for s in setups if s['confidence'] >= self.min_confidence]

        # Sort by confidence
        setups.sort(key=lambda x: x['confidence'], reverse=True)

        logger.debug(f"Detected {len(setups)} setups (min conf: {self.min_confidence}%)")

        return setups

    def _detect_liquidity_sweeps(
        self,
        data: Dict[str, pd.DataFrame],
        current_price: float
    ) -> List[Dict]:
        """
        Detect liquidity sweep setups.

        Args:
            data: Multi-timeframe data
            current_price: Current price

        Returns:
            List of liquidity sweep setups
        """
        setups = []

        primary_df = data[self.primary_timeframe]

        # Use strategy to find setups
        try:
            signals = self.strategy.generate_signals(primary_df)

            if signals.empty or 'signal' not in signals.columns:
                return setups

            # Check for new signals in last few candles
            recent_signals = signals.tail(5)
            active_signals = recent_signals[recent_signals['signal'] != 0]

            for idx, row in active_signals.iterrows():
                signal_type = "LONG" if row['signal'] > 0 else "SHORT"

                # Calculate confidence
                confidence = self._calculate_setup_confidence(
                    data=data,
                    signal_type=signal_type,
                    entry_price=current_price
                )

                # Get HTF bias
                htf_bias = self._get_htf_bias(data)

                setup = {
                    'type': f"Liquidity Sweep {signal_type}",
                    'timeframe': self.primary_timeframe,
                    'confidence': confidence,
                    'entry_price': current_price,
                    'direction': signal_type,
                    'timestamp': datetime.now(timezone.utc),
                    'htf_bias': htf_bias,
                    'metadata': {
                        'signal_time': idx,
                        'signal_value': row['signal']
                    }
                }

                setups.append(setup)

        except Exception as e:
            logger.error(f"Error detecting liquidity sweeps: {e}")

        return setups

    def _detect_order_block_bounces(
        self,
        data: Dict[str, pd.DataFrame],
        current_price: float
    ) -> List[Dict]:
        """
        Detect order block bounce setups.

        Args:
            data: Multi-timeframe data
            current_price: Current price

        Returns:
            List of order block setups
        """
        setups = []

        primary_df = data[self.primary_timeframe]

        # Import detection module
        try:
            from detection.order_blocks import detect_order_blocks

            # Detect order blocks
            ob_df = detect_order_blocks(primary_df)

            if ob_df.empty:
                return setups

            # Find untested order blocks near current price
            tolerance = 0.02  # 2% price tolerance

            for idx, ob in ob_df.iterrows():
                ob_price = (ob['top'] + ob['bottom']) / 2
                price_diff = abs(current_price - ob_price) / ob_price

                # Check if price near order block
                if price_diff > tolerance:
                    continue

                # Determine direction
                signal_type = "LONG" if ob['type'] == 'bullish' else "SHORT"

                # Calculate confidence
                confidence = self._calculate_setup_confidence(
                    data=data,
                    signal_type=signal_type,
                    entry_price=current_price
                )

                # Boost confidence if aligned with HTF
                htf_bias = self._get_htf_bias(data)
                if htf_bias == signal_type:
                    confidence *= 1.1  # 10% boost

                confidence = min(100, confidence)  # Cap at 100

                setup = {
                    'type': f"Order Block {signal_type}",
                    'timeframe': self.primary_timeframe,
                    'confidence': confidence,
                    'entry_price': current_price,
                    'direction': signal_type,
                    'timestamp': datetime.now(timezone.utc),
                    'htf_bias': htf_bias,
                    'metadata': {
                        'ob_top': ob['top'],
                        'ob_bottom': ob['bottom'],
                        'ob_strength': ob.get('strength', 0)
                    }
                }

                setups.append(setup)

        except Exception as e:
            logger.error(f"Error detecting order block bounces: {e}")

        return setups

    def _calculate_setup_confidence(
        self,
        data: Dict[str, pd.DataFrame],
        signal_type: str,
        entry_price: float
    ) -> float:
        """
        Calculate confidence score for a setup.

        Args:
            data: Multi-timeframe data
            signal_type: "LONG" or "SHORT"
            entry_price: Entry price

        Returns:
            Confidence score (0-100)
        """
        try:
            primary_df = data[self.primary_timeframe]

            # Use confidence factors from strategy
            factors = calculate_confidence_factors(
                df=primary_df,
                entry_type=signal_type.lower()
            )

            # Base confidence from factors
            confidence = factors['total_score']

            # Add HTF alignment bonus
            htf_bias = self._get_htf_bias(data)
            if htf_bias == signal_type:
                confidence += 5  # Bonus for HTF alignment

            # Add volume confirmation
            if self._check_volume_confirmation(primary_df):
                confidence += 3

            return min(100, max(0, confidence))

        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0

    def _get_htf_bias(self, data: Dict[str, pd.DataFrame]) -> Optional[str]:
        """
        Get higher timeframe bias.

        Args:
            data: Multi-timeframe data

        Returns:
            "LONG", "SHORT", or None
        """
        if not self.higher_timeframes:
            return None

        htf = self.higher_timeframes[0]

        if htf not in data or data[htf].empty:
            return None

        try:
            from detection.market_structure import detect_market_structure

            structure = detect_market_structure(data[htf])

            if structure.get('trend') == 'bullish':
                return "LONG"
            elif structure.get('trend') == 'bearish':
                return "SHORT"

        except Exception as e:
            logger.debug(f"HTF bias detection failed: {e}")

        return None

    def _check_volume_confirmation(self, df: pd.DataFrame) -> bool:
        """
        Check if volume confirms setup.

        Args:
            df: Price data

        Returns:
            True if volume confirms
        """
        if 'volume' not in df.columns or df.empty:
            return False

        try:
            # Check if recent volume above average
            recent_vol = df['volume'].iloc[-1]
            avg_vol = df['volume'].tail(20).mean()

            return recent_vol > avg_vol * 1.2  # 20% above average

        except Exception:
            return False


class LiveSetupMonitor:
    """
    Continuously monitor for new setups and trigger alerts.

    Integrates SetupDetector with AlertSystem for real-time notifications.
    """

    def __init__(
        self,
        detector: SetupDetector,
        alert_system,
        journal
    ):
        """
        Initialize live setup monitor.

        Args:
            detector: SetupDetector instance
            alert_system: AlertSystem instance
            journal: TradeJournal instance
        """
        self.detector = detector
        self.alerts = alert_system
        self.journal = journal

        # Track seen setups to avoid duplicates
        self._seen_setups = set()

        logger.info("LiveSetupMonitor initialized")

    def check_for_setups(
        self,
        data: Dict[str, pd.DataFrame],
        symbol: str,
        current_price: Optional[float] = None
    ):
        """
        Check for new setups and trigger alerts.

        Args:
            data: Multi-timeframe data
            symbol: Trading symbol
            current_price: Current price (optional)
        """
        setups = self.detector.scan_for_setups(data, current_price)

        for setup in setups:
            # Create unique ID for this setup
            setup_id = (
                setup['type'],
                setup['timeframe'],
                int(setup['entry_price'])  # Round to avoid float issues
            )

            # Skip if already seen
            if setup_id in self._seen_setups:
                continue

            self._seen_setups.add(setup_id)

            # Trigger alert
            self.alerts.setup_detected(
                title=setup['type'],
                message=self._format_setup_message(setup, symbol),
                confidence=setup['confidence'],
                timeframe=setup['timeframe'],
                metadata=setup.get('metadata', {})
            )

            # Log to journal
            self.journal.log_setup(
                timestamp=setup['timestamp'],
                symbol=symbol,
                timeframe=setup['timeframe'],
                setup_type=setup['type'],
                confidence=setup['confidence'],
                price=setup['entry_price'],
                metadata=setup.get('metadata', {})
            )

            logger.info(f"New setup detected: {setup['type']} @ {setup['confidence']}%")

        # Cleanup old seen setups (keep last 50)
        if len(self._seen_setups) > 50:
            self._seen_setups = set(list(self._seen_setups)[-50:])

    def _format_setup_message(self, setup: Dict, symbol: str) -> str:
        """
        Format setup message for alert.

        Args:
            setup: Setup dict
            symbol: Trading symbol

        Returns:
            Formatted message string
        """
        direction = setup['direction']
        entry = setup['entry_price']
        htf = setup.get('htf_bias', 'neutral')

        msg = f"{symbol} {direction} setup at ${entry:,.2f}"

        if htf and htf == direction:
            msg += f" | HTF aligned ({htf})"
        elif htf:
            msg += f" | HTF {htf} (counter-trend)"

        return msg
