"""
Interactive multi-timeframe dashboard for Jupyter notebooks.

Provides synchronized 3-panel charts with SMC pattern overlays and confidence scoring.
"""

from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from core.order_blocks import find_order_blocks
from risk.confidence import ConfidenceFactors


class FractalDashboard:
    """
    Interactive dashboard for visualizing Smart Money Concepts across multiple timeframes.

    Creates a synchronized 3-panel view (typically H4/H1/M15) with:
    - Candlestick charts
    - Auto-detected order blocks
    - Confidence scoring breakdown

    Example:
        >>> dashboard = FractalDashboard(
        ...     pair='BTC/USDT',
        ...     timeframes=['4h', '1h', '15m']
        ... )
        >>> dashboard.load_data('data/samples/btc_90d.csv')
        >>> dashboard.detect_patterns()
        >>> dashboard.show()

    Attributes:
        pair: Trading pair symbol (e.g., 'BTC/USDT')
        timeframes: List of timeframe strings (e.g., ['4h', '1h', '15m'])
        data: Dict mapping timeframe -> OHLCV DataFrame
        order_blocks: Dict mapping timeframe -> (bullish_ob, bearish_ob) DataFrames
    """

    def __init__(
        self,
        pair: str,
        timeframes: List[str],
        min_impulse_percent: float = 0.01
    ):
        """
        Initialize FractalDashboard.

        Args:
            pair: Trading pair symbol
            timeframes: List of timeframe strings (max 3 for optimal display)
            min_impulse_percent: Minimum impulse size for order block detection (default 1%)

        Raises:
            ValueError: If timeframes list is empty or > 3 panels
        """
        if not timeframes or len(timeframes) > 3:
            raise ValueError("Timeframes must contain 1-3 entries")

        self.pair = pair
        self.timeframes = timeframes
        self.min_impulse_percent = min_impulse_percent

        # Data storage
        self.data: Dict[str, pd.DataFrame] = {}
        self.order_blocks: Dict[str, tuple[pd.DataFrame, pd.DataFrame]] = {}

    def load_data(self, csv_path: str) -> None:
        """
        Load OHLCV data from CSV file.

        For Sprint 1 MVP, loads single dataset and resamples to different timeframes.
        Sprint 2 will fetch live data per timeframe.

        Args:
            csv_path: Path to CSV file with columns: timestamp, open, high, low, close, volume

        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If CSV is missing required columns
        """
        # Load base data
        try:
            df = pd.read_csv(csv_path, parse_dates=['timestamp'], index_col='timestamp')
        except FileNotFoundError:
            raise FileNotFoundError(f"Data file not found: {csv_path}")
        except Exception as e:
            raise ValueError(f"Error loading CSV: {e}")

        # Validate columns
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise ValueError(f"CSV missing columns: {missing}")

        # Resample to each timeframe
        timeframe_map = {
            '15m': '15min',
            '1h': '1h',
            '4h': '4h',
            '1d': '1D'
        }

        for tf in self.timeframes:
            if tf not in timeframe_map:
                raise ValueError(f"Unsupported timeframe: {tf}")

            # Resample OHLCV
            resampled = df.resample(timeframe_map[tf]).agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()

            self.data[tf] = resampled

    def detect_patterns(self) -> None:
        """
        Detect SMC patterns (order blocks) on all loaded timeframes.

        Uses core/order_blocks.py detection algorithm.
        Results stored in self.order_blocks.

        Raises:
            RuntimeError: If called before load_data()
        """
        if not self.data:
            raise RuntimeError("Must call load_data() before detect_patterns()")

        for tf, df in self.data.items():
            bullish_ob, bearish_ob = find_order_blocks(
                open_price=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                min_impulse_percent=self.min_impulse_percent
            )
            self.order_blocks[tf] = (bullish_ob, bearish_ob)

    def calculate_confidence(
        self,
        timeframe: str,
        ob_index: pd.Timestamp,
        ob_type: str = 'bullish'
    ) -> Tuple[int, ConfidenceFactors]:
        """
        Calculate confidence score for a specific order block setup.

        Args:
            timeframe: Timeframe of the order block
            ob_index: Timestamp index of the order block
            ob_type: 'bullish' or 'bearish'

        Returns:
            Tuple of (confidence_score, ConfidenceFactors instance)

        Raises:
            RuntimeError: If called before detect_patterns()
            ValueError: If timeframe or OB not found
        """
        if not self.order_blocks:
            raise RuntimeError("Must call detect_patterns() before calculate_confidence()")

        if timeframe not in self.order_blocks:
            raise ValueError(f"Timeframe {timeframe} not found")

        # Get order block data
        bullish_ob, bearish_ob = self.order_blocks[timeframe]
        ob_df = bullish_ob if ob_type == 'bullish' else bearish_ob

        if ob_index not in ob_df.index:
            raise ValueError(f"Order block at {ob_index} not found")

        ob_data = ob_df.loc[ob_index]
        df = self.data[timeframe]

        # Calculate confidence factors
        factors = ConfidenceFactors()

        # 1. HTF alignment - check if higher timeframe confirms
        if len(self.timeframes) > 1:
            htf_idx = max(0, self.timeframes.index(timeframe) - 1)
            if htf_idx < self.timeframes.index(timeframe):
                htf = self.timeframes[htf_idx]
                htf_bullish, htf_bearish = self.order_blocks[htf]
                # Simple check: HTF has same direction OBs
                if ob_type == 'bullish' and len(htf_bullish) > 0:
                    factors.htf_trend_aligned = True
                elif ob_type == 'bearish' and len(htf_bearish) > 0:
                    factors.htf_trend_aligned = True

        # 2. Pattern clean - check if OB hasn't been heavily retested (invalidated)
        if not ob_data['invalidated']:
            factors.pattern_clean = True

        # 3. Multiple confluences - retest count as confluence
        factors.multiple_confluences = min(int(ob_data['retest_count']), 4)

        # 4. Volume spike - check volume at OB formation
        try:
            ob_volume = df.loc[ob_index, 'volume']
            avg_volume = df['volume'].rolling(window=20).mean().loc[ob_index]
            if ob_volume > avg_volume * 1.5:  # 50% above average
                factors.volume_spike = True
        except (KeyError, ValueError):
            pass

        # 5. Market regime - check if trending
        # Simple trend check: price above/below 50-period MA
        try:
            ma50 = df['close'].rolling(window=50).mean()
            current_price = df['close'].iloc[-1]
            ma50_value = ma50.iloc[-1]

            if ob_type == 'bullish' and current_price > ma50_value:
                factors.trending_market = True
            elif ob_type == 'bearish' and current_price < ma50_value:
                factors.trending_market = True
        except (KeyError, ValueError):
            pass

        # 6. Low volatility - check ATR (simple version using high-low range)
        try:
            atr = (df['high'] - df['low']).rolling(window=14).mean()
            recent_atr = atr.iloc[-14:].mean()
            historical_atr = atr.mean()

            if recent_atr < historical_atr * 1.2:  # Within 120% of avg
                factors.low_volatility = True
        except (KeyError, ValueError):
            pass

        score = factors.calculate_score()
        return score, factors

    def render(
        self,
        height: int = 800,
        show_invalidated: bool = False,
        max_order_blocks: int = 50,
        show_confidence_for: Optional[Tuple[str, pd.Timestamp, str]] = None
    ) -> go.Figure:
        """
        Create synchronized multi-timeframe chart with SMC overlays.

        Args:
            height: Total figure height in pixels
            show_invalidated: Whether to show invalidated order blocks
            max_order_blocks: Max order blocks to render per timeframe (performance limit)
            show_confidence_for: Optional tuple (timeframe, ob_timestamp, ob_type) to show confidence panel

        Returns:
            Plotly Figure object ready to display

        Raises:
            RuntimeError: If called before detect_patterns()
        """
        if not self.order_blocks:
            raise RuntimeError("Must call detect_patterns() before render()")

        n_panels = len(self.timeframes)

        # Create subplots with shared x-axis
        fig = make_subplots(
            rows=n_panels,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            subplot_titles=[f"{tf.upper()} (FractalTrader)" for tf in self.timeframes],
            row_heights=self._calculate_row_heights()
        )

        # Add candlesticks and order blocks for each timeframe
        for i, tf in enumerate(self.timeframes, 1):
            df = self.data[tf]
            bullish_ob, bearish_ob = self.order_blocks[tf]

            # Add candlestick trace
            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name=tf.upper(),
                    showlegend=False
                ),
                row=i,
                col=1
            )

            # Add order block overlays
            self._add_order_blocks(
                fig=fig,
                row=i,
                order_blocks=bullish_ob,
                color="rgba(0, 255, 0, 0.2)",
                border_color="green",
                ob_type="bullish",
                show_invalidated=show_invalidated,
                max_blocks=max_order_blocks
            )

            self._add_order_blocks(
                fig=fig,
                row=i,
                order_blocks=bearish_ob,
                color="rgba(255, 0, 0, 0.2)",
                border_color="red",
                ob_type="bearish",
                show_invalidated=show_invalidated,
                max_blocks=max_order_blocks
            )

        # Update layout
        fig.update_layout(
            height=height,
            title=f"{self.pair} - Multi-Timeframe Analysis",
            showlegend=False,
            xaxis_rangeslider_visible=False,
            hovermode='x unified'
        )

        # Hide rangeslider on bottom subplot
        fig.update_xaxes(rangeslider_visible=False)

        # Add confidence panel if requested
        if show_confidence_for:
            self._add_confidence_panel(fig, *show_confidence_for)

        return fig

    def show(
        self,
        height: int = 800,
        show_invalidated: bool = False,
        max_order_blocks: int = 50,
        show_confidence_for: Optional[Tuple[str, pd.Timestamp, str]] = None
    ) -> None:
        """
        Render and display dashboard in Jupyter notebook.

        Args:
            height: Total figure height in pixels
            show_invalidated: Whether to show invalidated order blocks
            max_order_blocks: Max order blocks per timeframe
            show_confidence_for: Optional tuple (timeframe, ob_timestamp, ob_type) to show confidence panel
        """
        fig = self.render(
            height=height,
            show_invalidated=show_invalidated,
            max_order_blocks=max_order_blocks,
            show_confidence_for=show_confidence_for
        )
        fig.show()

    def _calculate_row_heights(self) -> List[float]:
        """
        Calculate optimal row heights for subplots.

        Higher timeframes get more space (macro context more important).

        Returns:
            List of relative heights summing to 1.0
        """
        n = len(self.timeframes)
        if n == 1:
            return [1.0]
        elif n == 2:
            return [0.6, 0.4]  # 60/40 split
        else:  # n == 3
            return [0.4, 0.3, 0.3]  # Top panel gets most space

    def _add_confidence_panel(
        self,
        fig: go.Figure,
        timeframe: str,
        ob_index: pd.Timestamp,
        ob_type: str = 'bullish'
    ) -> None:
        """
        Add confidence breakdown panel as annotation.

        Args:
            fig: Plotly figure to modify
            timeframe: Timeframe of the order block
            ob_index: Timestamp of the order block
            ob_type: 'bullish' or 'bearish'
        """
        # Calculate confidence
        score, factors = self.calculate_confidence(timeframe, ob_index, ob_type)

        # Build text for annotation
        direction = "BUY" if ob_type == "bullish" else "SELL"
        signal = "✓ ENTRY" if score >= 70 else "⚠ CAUTION" if score >= 50 else "✗ SKIP"
        signal_color = "green" if score >= 70 else "orange" if score >= 50 else "red"

        breakdown_lines = [
            f"<b>Setup: {ob_type.upper()} OB Retest</b>",
            f"<b>Confidence: {score}/100 {signal}</b>",
            "",
            "<b>Breakdown:</b>"
        ]

        # Add factor breakdown
        if factors.htf_trend_aligned:
            breakdown_lines.append("  HTF alignment:  +15 ✓")
        else:
            breakdown_lines.append("  HTF alignment:   0 ✗")

        if factors.htf_structure_clean:
            breakdown_lines.append("  HTF structure:  +15 ✓")
        else:
            breakdown_lines.append("  HTF structure:   0 ✗")

        if factors.pattern_clean:
            breakdown_lines.append("  Pattern clean:  +10 ✓")
        else:
            breakdown_lines.append("  Pattern clean:   0 ✗")

        confluence_points = min(factors.multiple_confluences * 5, 20)
        breakdown_lines.append(f"  Confluences:    +{confluence_points} ({factors.multiple_confluences}x)")

        if factors.volume_spike:
            breakdown_lines.append("  Volume spike:   +10 ✓")
        else:
            breakdown_lines.append("  Volume spike:    0 ✗")

        if factors.volume_divergence:
            breakdown_lines.append("  Volume div:     +10 ✓")
        else:
            breakdown_lines.append("  Volume div:      0 ✗")

        if factors.trending_market:
            breakdown_lines.append("  Trending:       +10 ✓")
        else:
            breakdown_lines.append("  Trending:        0 ✗")

        if factors.low_volatility:
            breakdown_lines.append("  Low volatility: +10 ✓")
        else:
            breakdown_lines.append("  Low volatility:  0 ✗")

        text = "<br>".join(breakdown_lines)

        # Add annotation (top-right corner of first panel)
        fig.add_annotation(
            text=text,
            xref="paper",
            yref="paper",
            x=0.98,
            y=0.98,
            xanchor="right",
            yanchor="top",
            showarrow=False,
            bgcolor="rgba(0, 0, 0, 0.8)",
            bordercolor=signal_color,
            borderwidth=2,
            borderpad=10,
            font=dict(
                family="Courier New, monospace",
                size=11,
                color="white"
            ),
            align="left"
        )

    def _add_order_blocks(
        self,
        fig: go.Figure,
        row: int,
        order_blocks: pd.DataFrame,
        color: str,
        border_color: str,
        ob_type: str,
        show_invalidated: bool,
        max_blocks: int
    ) -> None:
        """
        Add order block shapes to a subplot.

        Args:
            fig: Plotly figure to modify
            row: Subplot row number
            order_blocks: DataFrame with columns [ob_high, ob_low, invalidated, retest_count]
            color: Fill color (rgba format)
            border_color: Border line color
            ob_type: 'bullish' or 'bearish'
            show_invalidated: Whether to render invalidated blocks
            max_blocks: Maximum blocks to render
        """
        # Filter blocks
        if not show_invalidated:
            blocks = order_blocks[~order_blocks['invalidated']]
        else:
            blocks = order_blocks

        # Limit number of blocks (performance)
        if len(blocks) > max_blocks:
            # Sort by retest_count (most tested = most important)
            blocks = blocks.nlargest(max_blocks, 'retest_count')

        # Add each block as a shape
        for idx, row_data in blocks.iterrows():
            # Determine x-coordinates (time range)
            # For MVP, extend to end of chart
            x0 = idx
            x1 = self.data[self.timeframes[row - 1]].index[-1]

            fig.add_shape(
                type="rect",
                x0=x0,
                x1=x1,
                y0=row_data['ob_low'],
                y1=row_data['ob_high'],
                fillcolor=color,
                line=dict(color=border_color, width=1),
                opacity=0.8 if not row_data['invalidated'] else 0.3,
                row=row,
                col=1
            )

            # Add label annotation
            fig.add_annotation(
                x=x0,
                y=row_data['ob_high'] if ob_type == "bullish" else row_data['ob_low'],
                text=f"OB ({row_data['retest_count']} retests)",
                showarrow=False,
                font=dict(size=8, color=border_color),
                xanchor="left",
                yanchor="bottom" if ob_type == "bullish" else "top",
                row=row,
                col=1
            )
