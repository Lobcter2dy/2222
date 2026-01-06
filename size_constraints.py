#!/usr/bin/env python3
"""
Система ограничений размеров для элементов
Предотвращает создание слишком маленьких элементов
"""
from typing import Dict, Tuple, Optional
from .utils.logger import get_logger

log = get_logger('SizeConstraints')


class SizeConstraints:
    """
    Система логических ограничений размеров элементов.
    
    Определяет минимальные и максимальные размеры для разных типов элементов,
    учитывая их функциональное назначение.
    """
    
    # Минимальные размеры по типам элементов
    MINIMUM_SIZES = {
        # Базовые элементы
        'button': {'width': 60, 'height': 24},
        'panel': {'width': 50, 'height': 50},
        'frame': {'width': 40, 'height': 40},
        'text': {'width': 20, 'height': 16},
        'image': {'width': 32, 'height': 32},
        'scroll_area': {'width': 100, 'height': 100},
        'state_switcher': {'width': 80, 'height': 40},
        
        # Артефакты (функциональные компоненты)
        'file_browser': {'width': 250, 'height': 300},
        'code_editor': {'width': 400, 'height': 250},
        'directory_browser': {'width': 220, 'height': 280},
        'image_viewer': {'width': 300, 'height': 200},
        'text_editor': {'width': 350, 'height': 200},
        'calculator': {'width': 200, 'height': 300},
        'color_picker': {'width': 280, 'height': 320},
        'chart_viewer': {'width': 400, 'height': 300},
        
        # Специальные элементы
        'menu': {'width': 150, 'height': 100},
        'toolbar': {'width': 200, 'height': 32},
        'statusbar': {'width': 200, 'height': 24},
        'tabbar': {'width': 150, 'height': 32},
        
        # Контейнеры
        'window': {'width': 300, 'height': 200},
        'dialog': {'width': 250, 'height': 150},
        'popup': {'width': 100, 'height': 50},
        
        # По умолчанию
        'default': {'width': 50, 'height': 50}
    }
    
    # Максимальные размеры (для предотвращения огромных элементов)
    MAXIMUM_SIZES = {
        'default': {'width': 5000, 'height': 5000}
    }
    
    # Рекомендуемые размеры (для подсказок пользователю)
    RECOMMENDED_SIZES = {
        'button': {'width': 120, 'height': 32},
        'panel': {'width': 200, 'height': 150},
        'frame': {'width': 300, 'height': 200},
        'text': {'width': 100, 'height': 20},
        'image': {'width': 200, 'height': 150},
        'scroll_area': {'width': 250, 'height': 200},
        
        # Артефакты
        'file_browser': {'width': 300, 'height': 400},
        'code_editor': {'width': 600, 'height': 400},
        'directory_browser': {'width': 280, 'height': 350},
        
        'default': {'width': 150, 'height': 100}
    }
    
    # Соотношения сторон (для некоторых элементов)
    ASPECT_RATIO_CONSTRAINTS = {
        'button': {'min_ratio': 0.2, 'max_ratio': 8.0},  # Не слишком вытянутые
        'image': {'min_ratio': 0.1, 'max_ratio': 10.0},  # Гибкие пропорции
        'text': {'min_ratio': 0.5, 'max_ratio': 20.0},   # Может быть длинной строкой
    }
    
    @classmethod
    def get_min_size(cls, element_type: str) -> Dict[str, int]:
        """
        Возвращает минимальные размеры для типа элемента.
        
        Args:
            element_type: Тип элемента
            
        Returns:
            Dict с ключами 'width' и 'height'
        """
        return cls.MINIMUM_SIZES.get(element_type, cls.MINIMUM_SIZES['default']).copy()
    
    @classmethod
    def get_max_size(cls, element_type: str) -> Dict[str, int]:
        """Возвращает максимальные размеры для типа элемента"""
        return cls.MAXIMUM_SIZES.get(element_type, cls.MAXIMUM_SIZES['default']).copy()
    
    @classmethod
    def get_recommended_size(cls, element_type: str) -> Dict[str, int]:
        """Возвращает рекомендуемые размеры для типа элемента"""
        return cls.RECOMMENDED_SIZES.get(element_type, cls.RECOMMENDED_SIZES['default']).copy()
    
    @classmethod
    def constrain_size(cls, element_type: str, width: int, height: int) -> Tuple[int, int]:
        """
        Применяет ограничения к размерам элемента.
        
        Args:
            element_type: Тип элемента
            width, height: Исходные размеры
            
        Returns:
            Tuple (width, height) с примененными ограничениями
        """
        min_size = cls.get_min_size(element_type)
        max_size = cls.get_max_size(element_type)
        
        # Применяем минимальные ограничения
        width = max(width, min_size['width'])
        height = max(height, min_size['height'])
        
        # Применяем максимальные ограничения
        width = min(width, max_size['width'])
        height = min(height, max_size['height'])
        
        # Проверяем соотношения сторон
        if element_type in cls.ASPECT_RATIO_CONSTRAINTS:
            ratio_limits = cls.ASPECT_RATIO_CONSTRAINTS[element_type]
            current_ratio = width / height if height > 0 else 1.0
            
            if current_ratio < ratio_limits['min_ratio']:
                # Слишком узкий - увеличиваем ширину
                width = int(height * ratio_limits['min_ratio'])
            elif current_ratio > ratio_limits['max_ratio']:
                # Слишком широкий - увеличиваем высоту
                height = int(width / ratio_limits['max_ratio'])
        
        return width, height
    
    @classmethod
    def validate_size(cls, element_type: str, width: int, height: int) -> Tuple[bool, Optional[str]]:
        """
        Проверяет допустимость размеров элемента.
        
        Args:
            element_type: Тип элемента
            width, height: Размеры для проверки
            
        Returns:
            Tuple (is_valid, error_message)
        """
        min_size = cls.get_min_size(element_type)
        max_size = cls.get_max_size(element_type)
        
        # Проверка минимальных размеров
        if width < min_size['width']:
            return False, f"Ширина слишком мала (мин. {min_size['width']}px)"
        
        if height < min_size['height']:
            return False, f"Высота слишком мала (мин. {min_size['height']}px)"
        
        # Проверка максимальных размеров
        if width > max_size['width']:
            return False, f"Ширина слишком велика (макс. {max_size['width']}px)"
        
        if height > max_size['height']:
            return False, f"Высота слишком велика (макс. {max_size['height']}px)"
        
        # Проверка соотношений сторон
        if element_type in cls.ASPECT_RATIO_CONSTRAINTS:
            ratio_limits = cls.ASPECT_RATIO_CONSTRAINTS[element_type]
            current_ratio = width / height if height > 0 else 1.0
            
            if current_ratio < ratio_limits['min_ratio']:
                return False, f"Элемент слишком узкий (соотношение {current_ratio:.2f})"
            
            if current_ratio > ratio_limits['max_ratio']:
                return False, f"Элемент слишком широкий (соотношение {current_ratio:.2f})"
        
        return True, None
    
    @classmethod
    def get_size_hint(cls, element_type: str) -> str:
        """
        Возвращает подсказку о размерах для пользователя.
        
        Args:
            element_type: Тип элемента
            
        Returns:
            Строка с информацией о размерах
        """
        min_size = cls.get_min_size(element_type)
        rec_size = cls.get_recommended_size(element_type)
        
        hint = f"Мин: {min_size['width']}×{min_size['height']}, "
        hint += f"Рек: {rec_size['width']}×{rec_size['height']}"
        
        if element_type in cls.ASPECT_RATIO_CONSTRAINTS:
            ratio_limits = cls.ASPECT_RATIO_CONSTRAINTS[element_type]
            hint += f", Пропорции: {ratio_limits['min_ratio']:.1f}-{ratio_limits['max_ratio']:.1f}"
        
        return hint
    
    @classmethod
    def get_constrained_creation_size(cls, element_type: str, 
                                     requested_width: int, requested_height: int,
                                     canvas_constraints: Optional[Dict] = None) -> Tuple[int, int]:
        """
        Возвращает размеры для создания элемента с учетом всех ограничений.
        
        Args:
            element_type: Тип элемента
            requested_width, requested_height: Запрошенные размеры
            canvas_constraints: Ограничения холста (размеры, границы)
            
        Returns:
            Tuple (width, height) итоговых размеров
        """
        # Применяем базовые ограничения
        width, height = cls.constrain_size(element_type, requested_width, requested_height)
        
        # Применяем ограничения холста если есть
        if canvas_constraints:
            max_canvas_width = canvas_constraints.get('max_width', 5000)
            max_canvas_height = canvas_constraints.get('max_height', 5000)
            
            width = min(width, max_canvas_width)
            height = min(height, max_canvas_height)
        
        log.debug(f"Размеры {element_type}: {requested_width}×{requested_height} → {width}×{height}")
        
        return width, height
    
    @classmethod
    def get_resize_constraints(cls, element_type: str, 
                              current_width: int, current_height: int,
                              delta_width: int, delta_height: int) -> Tuple[int, int]:
        """
        Применяет ограничения при изменении размеров существующего элемента.
        
        Args:
            element_type: Тип элемента
            current_width, current_height: Текущие размеры
            delta_width, delta_height: Изменение размеров
            
        Returns:
            Tuple (new_width, new_height) с примененными ограничениями
        """
        new_width = current_width + delta_width
        new_height = current_height + delta_height
        
        return cls.constrain_size(element_type, new_width, new_height)


# Интеграция с ElementManager
def apply_size_constraints_to_element_manager():
    """Применяет систему ограничений к ElementManager"""
    from .elements.element_manager import ElementManager
    
    # Добавляем метод проверки размеров
    original_create_element = ElementManager.create_element
    
    def create_element_with_constraints(self, element_type, x, y, width, height):
        """Создание элемента с применением ограничений размеров"""
        # Применяем ограничения
        constrained_width, constrained_height = SizeConstraints.constrain_size(
            element_type, width, height
        )
        
        # Логируем если размеры изменились
        if constrained_width != width or constrained_height != height:
            log.info(f"Размеры {element_type} скорректированы: "
                    f"{width}×{height} → {constrained_width}×{constrained_height}")
        
        # Вызываем оригинальный метод
        return original_create_element(self, element_type, x, y, constrained_width, constrained_height)
    
    # Заменяем метод
    ElementManager.create_element = create_element_with_constraints
    
    log.info("Система ограничений размеров применена к ElementManager")
