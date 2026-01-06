#!/usr/bin/env python3
"""
PanelWithControl - Модульная система создания интерфейсов
=========================================================

Структура модулей:
- config: Конфигурация и константы
- ui_builder: Построение интерфейса
- tab_system: Система вкладок
- elements: Элементы холста (Frame, Panel, Button, Image)
- mechanisms: Механизмы анимации (MoveTrack, Rotator)
- dialogs: Диалоговые окна настроек
- tabs: Вкладки боковой панели
"""

# Базовая конфигурация
from .config import Config

# Система компонентов
from .component_system import Component, ComponentManager, ArtifactManager

# Системы
from .grid_system import GridSystem
from .selection_system import SelectionSystem
from .selection_tool import SelectionTool
from .ui_builder import UIBuilder
from .tab_system import TabSystem
from .zoom_system import ZoomSystem
from .main_canvas import MainCanvas
from .code_generator import CodeGenerator
from .project_manager import ProjectManager
# Обработчики событий и колбэки
from .event_handlers import EventHandlers
from .app_callbacks import AppCallbacks
from .loading_overlay import LoadingOverlay, LoadingContext
from .ai_assistant import AIAssistant, AIModelType, get_ai_assistant
from .window_manager import WindowManager, WindowConfig, get_window_manager
from .button_functions import (
    ButtonFunctions, ButtonAction, 
    button_functions, get_button_functions,
    call_button_function, register_button_function, get_available_functions
)

# Элементы
from .elements import (
    ElementManager,
    ElementBase,
    FrameElement,
    PanelElement,
    ButtonElement,
    ImageElement,
    TextElement,
    ScrollAreaElement
)

# Механизмы
from .mechanisms import (
    MechanismManager,
    MechanismBase,
    MoveTrackMechanism,
    RotatorMechanism,
    ScaleMechanism,
    FadeMechanism,
    ShakeMechanism,
    PathMechanism,
    PulseMechanism
)

# Диалоги
from .dialogs import (
    ButtonConfigDialog,
    FrameConfigDialog,
    PanelConfigDialog,
    ImageConfigDialog,
    ActionConfigDialog,
    show_button_config,
    show_frame_config,
    show_panel_config,
    show_image_config,
    show_action_config
)
