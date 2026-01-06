#!/usr/bin/env python3
"""
Модуль элементов интерфейса
Каждый элемент - отдельная папка со своей структурой
"""
from .element_base import ElementBase
from .element_manager import ElementManager
from .frame import FrameElement
from .panel import PanelElement
from .button import ButtonElement
from .image import ImageElement
from .text import TextElement
from .scroll_area import ScrollAreaElement
from .state_switcher import StateSwitcherElement, ElementState
from .artifact import ArtifactElement
