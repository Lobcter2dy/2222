"""
Контроллеры приложения
Отвечают за координацию между модулями
"""

from .app_controller import AppController
from .canvas_controller import CanvasController
from .element_controller import ElementController
from .ui_controller import UIController

__all__ = [
    'AppController',
    'CanvasController', 
    'ElementController',
    'UIController',
]

