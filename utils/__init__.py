"""
Утилиты проекта
"""

from .safe_exec import SafeExecutor, safe_exec
from .logger import Logger, get_logger
from .event_bus import EventBus, event_bus, on, off, emit, once
from .debounce import (
    Debouncer, Throttler, TkDebouncer, TkThrottler,
    debounce, throttle,
    DEBOUNCE_UI, DEBOUNCE_SEARCH, DEBOUNCE_SAVE, DEBOUNCE_RESIZE,
    THROTTLE_SCROLL, THROTTLE_DRAG, THROTTLE_MOUSE
)
from .hotkeys import HotkeyManager, init_hotkeys, get_hotkey_manager

__all__ = [
    # Safe exec
    'SafeExecutor',
    'safe_exec',
    # Logger
    'Logger',
    'get_logger',
    # Event bus
    'EventBus',
    'event_bus',
    'on',
    'off', 
    'emit',
    'once',
    # Debounce/Throttle
    'Debouncer',
    'Throttler',
    'TkDebouncer',
    'TkThrottler',
    'debounce',
    'throttle',
    'DEBOUNCE_UI',
    'DEBOUNCE_SEARCH',
    'DEBOUNCE_SAVE',
    'DEBOUNCE_RESIZE',
    'THROTTLE_SCROLL',
    'THROTTLE_DRAG',
    'THROTTLE_MOUSE',
    # Hotkeys
    'HotkeyManager',
    'init_hotkeys',
    'get_hotkey_manager',
]

