"""
Timer logic module for Pomodoro timer functionality.
Uses Qt signals for non-blocking timer updates.
"""

from PySide6.QtCore import QObject, Signal, QTimer
from enum import Enum
from dataclasses import dataclass
from typing import Optional
import time


class TimerState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    BREAK = "break"
    BREAK_PAUSED = "break_paused"


@dataclass
class TimerConfig:
    work_duration: int = 25 * 60  # 25 minutes in seconds
    short_break: int = 5 * 60     # 5 minutes
    long_break: int = 15 * 60     # 15 minutes
    sessions_before_long_break: int = 4


class PomodoroTimer(QObject):
    """
    Non-blocking Pomodoro timer using Qt's event loop.
    Emits signals for UI updates without blocking animations.
    """
    
    # Signals for UI updates
    tick = Signal(int)  # Emits remaining seconds
    state_changed = Signal(TimerState)
    session_completed = Signal(int)  # Emits total sessions completed
    break_completed = Signal()
    timer_finished = Signal()  # Emits when work session ends
    
    def __init__(self, config: Optional[TimerConfig] = None):
        super().__init__()
        self.config = config or TimerConfig()
        self._state = TimerState.IDLE
        self._remaining_seconds = self.config.work_duration
        self._sessions_completed = 0
        self._current_task_id: Optional[int] = None
        self._session_start_time: Optional[float] = None
        
        # Qt Timer for non-blocking updates (1 second interval)
        self._qt_timer = QTimer(self)
        self._qt_timer.setInterval(1000)
        self._qt_timer.timeout.connect(self._on_tick)
    
    @property
    def state(self) -> TimerState:
        return self._state
    
    @property
    def remaining_seconds(self) -> int:
        return self._remaining_seconds
    
    @property
    def remaining_formatted(self) -> str:
        minutes = self._remaining_seconds // 60
        seconds = self._remaining_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    @property
    def progress(self) -> float:
        """Returns progress as 0.0 to 1.0"""
        if self._state in (TimerState.BREAK, TimerState.BREAK_PAUSED):
            total = self._get_break_duration()
        else:
            total = self.config.work_duration
        return 1.0 - (self._remaining_seconds / total) if total > 0 else 0.0
    
    @property
    def sessions_completed(self) -> int:
        return self._sessions_completed
    
    @property
    def is_running(self) -> bool:
        return self._state in (TimerState.RUNNING, TimerState.BREAK)
    
    @property
    def is_break(self) -> bool:
        return self._state in (TimerState.BREAK, TimerState.BREAK_PAUSED)
    
    def set_task(self, task_id: Optional[int]):
        """Set the current task for this timer session."""
        self._current_task_id = task_id
    
    def get_current_task_id(self) -> Optional[int]:
        return self._current_task_id
    
    def start(self):
        """Start or resume the timer."""
        if self._state == TimerState.IDLE:
            self._remaining_seconds = self.config.work_duration
            self._state = TimerState.RUNNING
            self._session_start_time = time.time()
        elif self._state == TimerState.PAUSED:
            self._state = TimerState.RUNNING
        elif self._state == TimerState.BREAK_PAUSED:
            self._state = TimerState.BREAK
        
        self._qt_timer.start()
        self.state_changed.emit(self._state)
    
    def pause(self):
        """Pause the timer."""
        if self._state == TimerState.RUNNING:
            self._state = TimerState.PAUSED
        elif self._state == TimerState.BREAK:
            self._state = TimerState.BREAK_PAUSED
        
        self._qt_timer.stop()
        self.state_changed.emit(self._state)
    
    def toggle(self):
        """Toggle between running and paused states."""
        if self.is_running:
            self.pause()
        else:
            self.start()
    
    def reset(self):
        """Reset timer to initial state."""
        self._qt_timer.stop()
        self._state = TimerState.IDLE
        self._remaining_seconds = self.config.work_duration
        self._session_start_time = None
        self.state_changed.emit(self._state)
        self.tick.emit(self._remaining_seconds)
    
    def skip_to_break(self):
        """Skip current work session and start break."""
        self._qt_timer.stop()
        self._start_break()
    
    def skip_break(self):
        """Skip break and start new work session."""
        self._qt_timer.stop()
        self._state = TimerState.IDLE
        self._remaining_seconds = self.config.work_duration
        self.state_changed.emit(self._state)
        self.tick.emit(self._remaining_seconds)
    
    def set_work_duration(self, minutes: int):
        """Set work duration in minutes."""
        self.config.work_duration = minutes * 60
        if self._state == TimerState.IDLE:
            self._remaining_seconds = self.config.work_duration
            self.tick.emit(self._remaining_seconds)
    
    def set_break_duration(self, minutes: int):
        """Set short break duration in minutes."""
        self.config.short_break = minutes * 60
    
    def set_long_break_duration(self, minutes: int):
        """Set long break duration in minutes."""
        self.config.long_break = minutes * 60
    
    def get_elapsed_seconds(self) -> int:
        """Get elapsed seconds in current session."""
        if self._state in (TimerState.BREAK, TimerState.BREAK_PAUSED):
            total = self._get_break_duration()
        else:
            total = self.config.work_duration
        return total - self._remaining_seconds
    
    def _on_tick(self):
        """Called every second by Qt timer."""
        if self._remaining_seconds > 0:
            self._remaining_seconds -= 1
            self.tick.emit(self._remaining_seconds)
        else:
            self._qt_timer.stop()
            self._handle_timer_complete()
    
    def _handle_timer_complete(self):
        """Handle timer completion for work/break sessions."""
        if self._state == TimerState.RUNNING:
            # Work session completed
            self._sessions_completed += 1
            self.session_completed.emit(self._sessions_completed)
            self.timer_finished.emit()
            self._start_break()
        elif self._state == TimerState.BREAK:
            # Break completed
            self.break_completed.emit()
            self._state = TimerState.IDLE
            self._remaining_seconds = self.config.work_duration
            self.state_changed.emit(self._state)
            self.tick.emit(self._remaining_seconds)
    
    def _start_break(self):
        """Start break timer."""
        self._remaining_seconds = self._get_break_duration()
        self._state = TimerState.BREAK
        self._qt_timer.start()
        self.state_changed.emit(self._state)
        self.tick.emit(self._remaining_seconds)
    
    def _get_break_duration(self) -> int:
        """Get break duration based on sessions completed."""
        if self._sessions_completed % self.config.sessions_before_long_break == 0:
            return self.config.long_break
        return self.config.short_break
