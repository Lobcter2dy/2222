#!/usr/bin/env python3
"""
UI ограничения и валидация
Обеспечивает логичные ограничения для всех UI компонентов
"""
from typing import Tuple, Dict, Any, Optional
from .size_constraints import SizeConstraints
from .utils.logger import get_logger

log = get_logger('UIConstraints')


class UIConstraints:
    """
    Система UI ограничений.
    
    Обеспечивает:
    - Логичные размеры элементов
    - Предотвращение коллизий
    - Валидацию позиций
    - Ограничения взаимодействия
    """
    
    # Минимальные расстояния между элементами
    MIN_ELEMENT_SPACING = 2
    
    # Минимальные отступы от границ холста
    MIN_CANVAS_MARGIN = 5
    
    @classmethod
    def validate_element_creation(cls, element_type: str, x: int, y: int, 
                                 width: int, height: int,
                                 canvas_bounds: Optional[Tuple[int, int]] = None,
                                 existing_elements: Optional[list] = None) -> Tuple[bool, Optional[str], Dict[str, int]]:
        """
        Валидирует создание элемента.
        
        Args:
            element_type: Тип элемента
            x, y: Позиция
            width, height: Размеры
            canvas_bounds: Размеры холста (width, height)
            existing_elements: Список существующих элементов
            
        Returns:
            Tuple (is_valid, error_message, corrected_params)
        """
        corrected = {'x': x, 'y': y, 'width': width, 'height': height}
        
        # 1. Проверяем размеры элемента
        is_size_valid, size_error = SizeConstraints.validate_size(element_type, width, height)
        if not is_size_valid:
            # Корректируем размеры автоматически
            corrected_width, corrected_height = SizeConstraints.constrain_size(element_type, width, height)
            corrected['width'] = corrected_width
            corrected['height'] = corrected_height
            log.info(f"Размеры {element_type} скорректированы: {width}×{height} → {corrected_width}×{corrected_height}")
        
        # 2. Проверяем границы холста
        if canvas_bounds:
            canvas_width, canvas_height = canvas_bounds
            
            # Корректируем позицию если выходит за границы
            if x < cls.MIN_CANVAS_MARGIN:
                corrected['x'] = cls.MIN_CANVAS_MARGIN
            if y < cls.MIN_CANVAS_MARGIN:
                corrected['y'] = cls.MIN_CANVAS_MARGIN
                
            # Корректируем размер если не помещается
            max_width = canvas_width - corrected['x'] - cls.MIN_CANVAS_MARGIN
            max_height = canvas_height - corrected['y'] - cls.MIN_CANVAS_MARGIN
            
            if corrected['width'] > max_width:
                corrected['width'] = max(max_width, SizeConstraints.get_min_size(element_type)['width'])
            if corrected['height'] > max_height:
                corrected['height'] = max(max_height, SizeConstraints.get_min_size(element_type)['height'])
        
        # 3. Проверяем коллизии с существующими элементами (опционально)
        if existing_elements and cls._has_collision(corrected, existing_elements):
            # Находим свободное место
            free_pos = cls._find_free_position(corrected, canvas_bounds, existing_elements)
            if free_pos:
                corrected['x'], corrected['y'] = free_pos
        
        # 4. Специальные правила для функциональных элементов
        if element_type in ['code_editor', 'file_browser']:
            # Функциональные элементы не могут быть слишком маленькими
            min_functional_size = SizeConstraints.get_min_size(element_type)
            if corrected['width'] < min_functional_size['width']:
                corrected['width'] = min_functional_size['width']
            if corrected['height'] < min_functional_size['height']:
                corrected['height'] = min_functional_size['height']
        
        return True, None, corrected
    
    @classmethod
    def _has_collision(cls, new_element: Dict[str, int], existing_elements: list) -> bool:
        """Проверяет коллизию с существующими элементами"""
        new_x1, new_y1 = new_element['x'], new_element['y']
        new_x2, new_y2 = new_x1 + new_element['width'], new_y1 + new_element['height']
        
        for element in existing_elements:
            if not hasattr(element, 'x') or not hasattr(element, 'y'):
                continue
                
            ex1, ey1 = element.x, element.y
            ex2, ey2 = ex1 + element.width, ey1 + element.height
            
            # Проверяем пересечение прямоугольников
            if (new_x1 < ex2 and new_x2 > ex1 and new_y1 < ey2 and new_y2 > ey1):
                return True
        
        return False
    
    @classmethod
    def _find_free_position(cls, element: Dict[str, int], 
                           canvas_bounds: Optional[Tuple[int, int]], 
                           existing_elements: list) -> Optional[Tuple[int, int]]:
        """Находит свободную позицию для элемента"""
        if not canvas_bounds:
            return None
        
        canvas_width, canvas_height = canvas_bounds
        width, height = element['width'], element['height']
        
        # Пробуем разные позиции
        step = 20
        for y in range(cls.MIN_CANVAS_MARGIN, canvas_height - height - cls.MIN_CANVAS_MARGIN, step):
            for x in range(cls.MIN_CANVAS_MARGIN, canvas_width - width - cls.MIN_CANVAS_MARGIN, step):
                test_element = {'x': x, 'y': y, 'width': width, 'height': height}
                if not cls._has_collision(test_element, existing_elements):
                    return (x, y)
        
        return None
    
    @classmethod
    def validate_element_resize(cls, element_type: str, 
                               current_x: int, current_y: int,
                               new_width: int, new_height: int,
                               canvas_bounds: Optional[Tuple[int, int]] = None) -> Tuple[int, int]:
        """
        Валидирует изменение размеров элемента.
        
        Args:
            element_type: Тип элемента
            current_x, current_y: Текущая позиция
            new_width, new_height: Новые размеры
            canvas_bounds: Границы холста
            
        Returns:
            Tuple (validated_width, validated_height)
        """
        # Применяем базовые ограничения размеров
        validated_width, validated_height = SizeConstraints.constrain_size(
            element_type, new_width, new_height
        )
        
        # Проверяем границы холста
        if canvas_bounds:
            canvas_width, canvas_height = canvas_bounds
            
            max_width = canvas_width - current_x - cls.MIN_CANVAS_MARGIN
            max_height = canvas_height - current_y - cls.MIN_CANVAS_MARGIN
            
            validated_width = min(validated_width, max_width)
            validated_height = min(validated_height, max_height)
            
            # Убеждаемся что не меньше минимума
            min_size = SizeConstraints.get_min_size(element_type)
            validated_width = max(validated_width, min_size['width'])
            validated_height = max(validated_height, min_size['height'])
        
        return validated_width, validated_height
    
    @classmethod
    def validate_element_position(cls, element_width: int, element_height: int,
                                 x: int, y: int,
                                 canvas_bounds: Optional[Tuple[int, int]] = None) -> Tuple[int, int]:
        """
        Валидирует позицию элемента.
        
        Args:
            element_width, element_height: Размеры элемента
            x, y: Запрашиваемая позиция
            canvas_bounds: Границы холста
            
        Returns:
            Tuple (validated_x, validated_y)
        """
        validated_x, validated_y = x, y
        
        # Проверяем границы холста
        if canvas_bounds:
            canvas_width, canvas_height = canvas_bounds
            
            # Минимальные отступы
            validated_x = max(validated_x, cls.MIN_CANVAS_MARGIN)
            validated_y = max(validated_y, cls.MIN_CANVAS_MARGIN)
            
            # Максимальные границы
            max_x = canvas_width - element_width - cls.MIN_CANVAS_MARGIN
            max_y = canvas_height - element_height - cls.MIN_CANVAS_MARGIN
            
            validated_x = min(validated_x, max_x)
            validated_y = min(validated_y, max_y)
        
        return validated_x, validated_y
    
    @classmethod
    def get_ui_hints_for_element(cls, element_type: str) -> Dict[str, Any]:
        """
        Возвращает UI подсказки для типа элемента.
        
        Args:
            element_type: Тип элемента
            
        Returns:
            Dict с информацией для UI
        """
        min_size = SizeConstraints.get_min_size(element_type)
        rec_size = SizeConstraints.get_recommended_size(element_type)
        
        hints = {
            'size_hint': SizeConstraints.get_size_hint(element_type),
            'min_size': min_size,
            'recommended_size': rec_size,
            'creation_cursor': 'crosshair',
            'resize_cursor': 'sizing'
        }
        
        # Специальные подсказки для разных типов
        if element_type == 'code_editor':
            hints['description'] = "Редактор кода с подсветкой синтаксиса"
            hints['creation_cursor'] = 'hand2'
        elif element_type == 'file_browser':
            hints['description'] = "Браузер файлов для навигации"
            hints['creation_cursor'] = 'hand2'
        elif element_type == 'button':
            hints['description'] = "Интерактивная кнопка с функциями"
        elif element_type == 'image':
            hints['description'] = "Элемент для отображения изображений"
        
        return hints
