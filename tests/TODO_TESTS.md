# Fractal Trader - Test Requirements Checklist

This document consolidates all test requirements from the codebase. Each module's TEST REQUIREMENTS section has been collected here for systematic test implementation.

**Status Legend:**
- [ ] Not implemented
- [x] Implemented and passing

---

## Risk Management

### risk/confidence.py (9 tests)

- [ ] test_confidence_score_zero_by_default
- [ ] test_confidence_score_max_100
- [ ] test_htf_alignment_adds_30_points
- [ ] test_pattern_strength_adds_30_points
- [ ] test_volume_confirmation_adds_20_points
- [ ] test_market_regime_adds_20_points
- [ ] test_multiple_confluences_capped_at_20
- [ ] test_total_score_capped_at_100
- [ ] test_all_factors_true_equals_100

### risk/position_sizing.py (19 tests)

- [ ] test_position_size_respects_max_percent
- [ ] test_low_confidence_returns_zero
- [ ] test_below_min_confidence_returns_zero
- [ ] test_volatility_adjustment_scales_correctly
- [ ] test_high_volatility_reduces_size
- [ ] test_low_volatility_increases_size (capped at 1.5x)
- [ ] test_consecutive_wins_reduces_size
- [ ] test_consecutive_losses_reduces_size
- [ ] test_zero_risk_per_unit_returns_zero
- [ ] test_stop_equals_entry_returns_zero
- [ ] test_negative_portfolio_value_returns_zero
- [ ] test_negative_entry_price_returns_zero
- [ ] test_negative_stop_loss_returns_zero
- [ ] test_invalid_confidence_returns_zero
- [ ] test_negative_atr_returns_zero
- [ ] test_negative_streaks_return_zero
- [ ] test_position_value_calculation
- [ ] test_risk_percent_calculation
- [ ] test_zero_portfolio_value_in_risk_percent

---

## Backtesting

### backtesting/runner.py (19 tests)

- [ ] test_backtest_runner_initialization
- [ ] test_run_with_valid_strategy
- [ ] test_run_with_no_signals_returns_empty_result
- [ ] test_empty_result_has_zero_metrics
- [ ] test_empty_result_preserves_initial_cash
- [ ] test_signals_to_arrays_creates_boolean_series
- [ ] test_signals_to_arrays_matches_signal_timestamps
- [ ] test_extract_results_handles_nan_values
- [ ] test_extract_results_calculates_win_rate
- [ ] test_extract_results_calculates_profit_factor
- [ ] test_profit_factor_zero_when_no_losses
- [ ] test_avg_trade_duration_calculated
- [ ] test_optimize_returns_sorted_dataframe
- [ ] test_optimize_tests_all_param_combinations
- [ ] test_optimize_skips_failed_combinations
- [ ] test_optimize_returns_empty_df_when_all_fail
- [ ] test_fees_and_slippage_applied
- [ ] test_equity_curve_generated
- [ ] test_trades_dataframe_populated

---

## Core Detection Algorithms

### core/imbalance.py (17 tests)

- [ ] test_find_fair_value_gaps_detects_bullish_fvg
- [ ] test_find_fair_value_gaps_detects_bearish_fvg
- [ ] test_bullish_fvg_requires_gap_between_high_and_low
- [ ] test_bearish_fvg_requires_gap_between_low_and_high
- [ ] test_min_gap_percent_filters_small_gaps
- [ ] test_returns_empty_dataframe_when_no_gaps
- [ ] test_returns_empty_for_insufficient_data
- [ ] test_fvg_dataframe_has_required_columns
- [ ] test_check_fvg_fill_detects_full_fill
- [ ] test_check_fvg_fill_detects_partial_fill
- [ ] test_partial_fill_respects_percent_threshold
- [ ] test_fvg_marked_as_filled_after_fill
- [ ] test_fill_idx_recorded_correctly
- [ ] test_get_active_fvgs_returns_unfilled_only
- [ ] test_get_active_fvgs_respects_max_age
- [ ] test_calculate_fvg_size_returns_percentages
- [ ] test_calculate_fvg_size_handles_empty_input

### core/order_blocks.py (21 tests)

- [ ] test_find_order_blocks_detects_bullish_ob
- [ ] test_find_order_blocks_detects_bearish_ob
- [ ] test_bullish_ob_is_down_candle_before_impulse
- [ ] test_bearish_ob_is_up_candle_before_impulse
- [ ] test_min_impulse_percent_filters_small_moves
- [ ] test_returns_empty_dataframe_when_no_obs
- [ ] test_returns_empty_for_insufficient_data
- [ ] test_ob_dataframe_has_required_columns
- [ ] test_check_ob_retest_detects_price_entering_zone
- [ ] test_ob_invalidated_when_price_breaks_zone
- [ ] test_bullish_ob_invalidated_below_low
- [ ] test_bearish_ob_invalidated_above_high
- [ ] test_retest_count_increments
- [ ] test_get_valid_order_blocks_filters_invalidated
- [ ] test_get_valid_order_blocks_respects_max_age
- [ ] test_get_nearest_order_block_finds_below
- [ ] test_get_nearest_order_block_finds_above
- [ ] test_get_nearest_returns_none_when_no_valid
- [ ] test_calculate_ob_strength_considers_retests
- [ ] test_calculate_ob_strength_considers_size
- [ ] test_ob_strength_capped_at_100

---

## Strategies

### strategies/fvg_fill.py (15 tests)

- [ ] test_strategy_generates_signals_on_fvg_fill
- [ ] test_bullish_fvg_creates_long_signal
- [ ] test_bearish_fvg_creates_short_signal
- [ ] test_stop_loss_below_fvg_for_long
- [ ] test_stop_loss_above_fvg_for_short
- [ ] test_take_profit_uses_2_1_rr
- [ ] test_filters_by_min_rr_ratio
- [ ] test_confidence_calculation
- [ ] test_confidence_considers_trend
- [ ] test_confidence_considers_volume
- [ ] test_confidence_considers_volatility
- [ ] test_no_signals_when_no_fvgs
- [ ] test_respects_max_gap_age
- [ ] test_partial_fill_parameter
- [ ] test_min_gap_percent_filters

### strategies/bos_orderblock.py (16 tests)

- [ ] test_strategy_requires_bos_confirmation
- [ ] test_bullish_bos_creates_long_setup
- [ ] test_bearish_bos_creates_short_setup
- [ ] test_finds_recent_ob_before_bos
- [ ] test_waits_for_ob_retest_after_bos
- [ ] test_stop_loss_below_ob_for_long
- [ ] test_stop_loss_above_ob_for_short
- [ ] test_take_profit_uses_3_1_rr_minimum
- [ ] test_filters_by_min_rr_ratio
- [ ] test_confidence_weighted_for_bos
- [ ] test_confidence_considers_trend_consistency
- [ ] test_confidence_considers_volume
- [ ] test_no_signals_without_bos
- [ ] test_no_signals_without_ob
- [ ] test_respects_ob_validity_bars
- [ ] test_ob_retest_detected_correctly

---

## Summary

**Total Test Requirements: 116 tests**

| Module | Tests Required |
|--------|----------------|
| risk/confidence.py | 9 |
| risk/position_sizing.py | 19 |
| backtesting/runner.py | 19 |
| core/imbalance.py | 17 |
| core/order_blocks.py | 21 |
| strategies/fvg_fill.py | 15 |
| strategies/bos_orderblock.py | 16 |

**Currently Passing: 37 tests** (from core/market_structure.py and core/liquidity.py implemented by Opus)

**Remaining to Implement: 116 tests** (for Sonnet-implemented modules)

---

## Testing Priority

### High Priority (Core Functionality)
1. Risk management tests (28 tests) - Critical for position sizing
2. Backtesting runner tests (19 tests) - Needed for strategy validation
3. Core detection tests (38 tests) - Foundation for strategies

### Medium Priority (Strategy Validation)
4. Strategy tests (31 tests) - Validate signal generation logic

### Recommended Testing Workflow

1. **Start with risk management** - these are foundational
   ```bash
   python -m pytest tests/test_risk.py -v
   ```

2. **Then backtesting framework** - enables strategy testing
   ```bash
   python -m pytest tests/test_backtesting.py -v
   ```

3. **Core detection algorithms** - validates patterns
   ```bash
   python -m pytest tests/test_imbalance.py tests/test_order_blocks.py -v
   ```

4. **Finally strategies** - end-to-end validation
   ```bash
   python -m pytest tests/test_strategies.py -v
   ```

---

## Notes for Test Implementation

- All modules include comprehensive docstrings - use them for test design
- Edge cases are explicitly documented in position_sizing.py
- Use the existing test fixtures from tests/fixtures/sample_data.py
- Follow the testing patterns from test_market_structure.py and test_liquidity.py
- Aim for >80% code coverage across all modules

---

**Generated:** Sprint completion (Sonnet autonomous session)
**Next Step:** Implement tests systematically following the priority order above
