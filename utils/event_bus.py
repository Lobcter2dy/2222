"""
Централизованная шина событий (Event Bus)
Реализует паттерн Pub/Sub для уменьшения связанности модулей
"""

from typing import Dict, List, Callable, Any, Optional
import threading
from collections import defaultdict


class EventBus:
    """
    Шина событий для обмена сообщениями между модулями.
    
    Использование:
        from modules.utils.event_bus import event_bus
        
        # Подписка на событие
        def on_element_selected(element):
            print(f"Selected: {element.id}")
        
        event_bus.on('element:selected', on_element_selected)
        
        # Публикация события
        event_bus.emit('element:selected', element)
        
        # Отписка
        event_bus.off('element:selected', on_element_selected)
        
        # Одноразовая подписка
        event_bus.once('app:ready', lambda: print("App is ready!"))
    """
    
    # Стандартные события
    EVENTS = {
        # Элементы
        'element:created': 'Создан новый элемент',
        'element:selected': 'Выбран элемент',
        'element:deselected': 'Снято выделение с элемента',
        'element:moved': 'Элемент перемещён',
        'element:resized': 'Изменён размер элемента',
        'element:deleted': 'Элемент удалён',
        'element:properties_changed': 'Изменены свойства элемента',
        
        # Механизмы
        'mechanism:created': 'Создан новый механизм',
        'mechanism:started': 'Механизм запущен',
        'mechanism:stopped': 'Механизм остановлен',
        'mechanism:paused': 'Механизм на паузе',
        'mechanism:deleted': 'Механизм удалён',
        
        # UI
        'ui:tab_changed': 'Переключена вкладка',
        'ui:zoom_changed': 'Изменён масштаб',
        'ui:grid_toggled': 'Переключена сетка',
        'ui:theme_changed': 'Изменена тема',
        
        # Проект
        'project:new': 'Создан новый проект',
        'project:opened': 'Открыт проект',
        'project:saved': 'Проект сохранён',
        'project:modified': 'Проект изменён',
        
        # Приложение
        'app:ready': 'Приложение готово',
        'app:closing': 'Приложение закрывается',
    }
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._once_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._lock = threading.Lock()
        self._enabled = True
        
    def on(self, event: str, handler: Callable, priority: int = 0) -> 'EventBus':
        """
        Подписывается на событие.
        
        Args:
            event: Имя события
            handler: Функция-обработчик
            priority: Приоритет (выше = раньше выполнится)
            
        Returns:
            self для цепочки вызовов
        """
        with self._lock:
            # Храним как (priority, handler)
            self._handlers[event].append((priority, handler))
            # Сортируем по приоритету (больше = раньше)
            self._handlers[event].sort(key=lambda x: -x[0])
        return self
        
    def off(self, event: str, handler: Optional[Callable] = None) -> 'EventBus':
        """
        Отписывается от события.
        
        Args:
            event: Имя события
            handler: Функция-обработчик (если None - отписывает всех)
            
        Returns:
            self для цепочки вызовов
        """
        with self._lock:
            if handler is None:
                # Удаляем всех
                self._handlers[event].clear()
                self._once_handlers[event].clear()
            else:
                # Удаляем конкретный обработчик
                self._handlers[event] = [
                    (p, h) for p, h in self._handlers[event] if h != handler
                ]
                self._once_handlers[event] = [
                    (p, h) for p, h in self._once_handlers[event] if h != handler
                ]
        return self
        
    def once(self, event: str, handler: Callable, priority: int = 0) -> 'EventBus':
        """
        Подписывается на событие с автоматической отпиской после первого срабатывания.
        
        Args:
            event: Имя события
            handler: Функция-обработчик
            priority: Приоритет
            
        Returns:
            self для цепочки вызовов
        """
        with self._lock:
            self._once_handlers[event].append((priority, handler))
            self._once_handlers[event].sort(key=lambda x: -x[0])
        return self
        
    def emit(self, event: str, *args, **kwargs) -> bool:
        """
        Публикует событие.
        
        Args:
            event: Имя события
            *args, **kwargs: Аргументы для обработчиков
            
        Returns:
            True если событие обработано хотя бы одним обработчиком
        """
        if not self._enabled:
            return False
            
        handled = False
        
        with self._lock:
            # Копируем списки чтобы избежать проблем при модификации во время итерации
            handlers = list(self._handlers.get(event, []))
            once_handlers = list(self._once_handlers.get(event, []))
            
            # Очищаем once обработчики
            self._once_handlers[event].clear()
            
        # Вызываем обычные обработчики
        for priority, handler in handlers:
            try:
                handler(*args, **kwargs)
                handled = True
            except Exception as e:
                print(f"[EventBus] Error in handler for '{event}': {e}")
                
        # Вызываем once обработчики
        for priority, handler in once_handlers:
            try:
                handler(*args, **kwargs)
                handled = True
            except Exception as e:
                print(f"[EventBus] Error in once handler for '{event}': {e}")
                
        return handled
        
    def enable(self):
        """Включает шину событий"""
        self._enabled = True
        
    def disable(self):
        """Отключает шину событий (события игнорируются)"""
        self._enabled = False
        
    def clear(self):
        """Очищает все подписки"""
        with self._lock:
            self._handlers.clear()
            self._once_handlers.clear()
            
    def get_handlers_count(self, event: str) -> int:
        """Возвращает количество обработчиков для события"""
        with self._lock:
            return len(self._handlers.get(event, [])) + len(self._once_handlers.get(event, []))
            
    def list_events(self) -> List[str]:
        """Возвращает список всех событий с подписчиками"""
        with self._lock:
            events = set(self._handlers.keys()) | set(self._once_handlers.keys())
            return list(events)


# Глобальный экземпляр шины событий
event_bus = EventBus()


# Удобные функции
def on(event: str, handler: Callable, priority: int = 0) -> EventBus:
    """Подписывается на событие (глобальная шина)"""
    return event_bus.on(event, handler, priority)


def off(event: str, handler: Optional[Callable] = None) -> EventBus:
    """Отписывается от события (глобальная шина)"""
    return event_bus.off(event, handler)


def emit(event: str, *args, **kwargs) -> bool:
    """Публикует событие (глобальная шина)"""
    return event_bus.emit(event, *args, **kwargs)


def once(event: str, handler: Callable, priority: int = 0) -> EventBus:
    """Одноразовая подписка (глобальная шина)"""
    return event_bus.once(event, handler, priority)

