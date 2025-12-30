from datetime import datetime
from decimal import Decimal

from app.models import OnHoldPositions, Position, Tick, StrategyStats


class StateSaverMixin:
    _start_date: datetime
    _open_positions: list[Position]
    _max_onhold_positions: OnHoldPositions | None
    _max_sell_percent: Decimal
    _max_sell_percent_tick: int
    _ticks_history: list[Tick]
    _first_open_position_rate: Decimal
    _actual_qty_balance: Decimal
    _stats: StrategyStats = StrategyStats()
    _last_closed_deal: Position | None = None

    def get_state_for_save(self) -> dict:
        return {
            '_actual_qty_balance': self._actual_qty_balance,
            '_start_date': self._start_date,
            '_open_positions': self._open_positions,
            '_max_onhold_positions': self._max_onhold_positions,
            '_max_sell_percent': self._max_sell_percent,
            '_max_sell_percent_tick': self._max_sell_percent_tick,
            '_ticks_history': self._ticks_history,
            '_first_open_position_rate': self._first_open_position_rate,
            '_stats': self._stats,
            '_last_closed_deal': self._last_closed_deal,
        }

    def restore_state_from(self, saved_state: dict) -> None:
        self._actual_qty_balance = saved_state.get('_actual_qty_balance') or Decimal(0)
        self._start_date = saved_state.get('_start_date') or datetime.utcnow()
        self._open_positions = saved_state.get('_open_positions') or []
        self._max_onhold_positions = saved_state.get('_max_onhold_positions')
        self._max_sell_percent = saved_state.get('_max_sell_percent') or Decimal(0)
        self._max_sell_percent_tick = saved_state.get('_max_sell_percent_tick') or 0
        self._ticks_history = saved_state.get('_ticks_history') or []
        self._first_open_position_rate = saved_state.get('_first_open_position_rate') or Decimal(0)
        self._stats = saved_state.get('_stats') or StrategyStats()
        self._last_closed_deal = saved_state.get('_last_closed_deal') or None
