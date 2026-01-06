#!/usr/bin/env python3
"""
Менеджер окон (панелей)
Управляет созданием, открытием, закрытием окон
Окно = Panel элемент с определёнными свойствами
"""
import tkinter as tk


class WindowConfig:
    """Конфигурация окна"""
    
    def __init__(self, window_id):
        self.window_id = window_id
        self.title = ""
        self.x = 100
        self.y = 100
        self.width = 300
        self.height = 200
        
        # Поведение
        self.modal = False           # Модальное окно (блокирует остальные)
        self.closable = True         # Можно закрыть
        self.draggable = True        # Можно перетаскивать
        self.resizable = True        # Можно менять размер
        
        # Анимация
        self.animate_open = True     # Анимация открытия
        self.animate_close = True    # Анимация закрытия
        self.animation_duration = 300  # Длительность анимации (мс)
        
        # Связанные элементы
        self.content_elements = []   # ID элементов содержимого
        self.close_button_id = None  # ID кнопки закрытия
        
        # Механизмы
        self.fade_mechanism_id = None  # Механизм прозрачности
        
        # Состояние
        self.is_open = False
        self.z_index = 0
    
    def to_dict(self):
        return {
            'window_id': self.window_id,
            'title': self.title,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'modal': self.modal,
            'closable': self.closable,
            'draggable': self.draggable,
            'resizable': self.resizable,
            'animate_open': self.animate_open,
            'animate_close': self.animate_close,
            'animation_duration': self.animation_duration,
            'content_elements': self.content_elements,
            'close_button_id': self.close_button_id,
            'fade_mechanism_id': self.fade_mechanism_id,
            'is_open': self.is_open,
            'z_index': self.z_index,
        }
    
    @classmethod
    def from_dict(cls, data):
        config = cls(data.get('window_id', ''))
        config.title = data.get('title', '')
        config.x = data.get('x', 100)
        config.y = data.get('y', 100)
        config.width = data.get('width', 300)
        config.height = data.get('height', 200)
        config.modal = data.get('modal', False)
        config.closable = data.get('closable', True)
        config.draggable = data.get('draggable', True)
        config.resizable = data.get('resizable', True)
        config.animate_open = data.get('animate_open', True)
        config.animate_close = data.get('animate_close', True)
        config.animation_duration = data.get('animation_duration', 300)
        config.content_elements = data.get('content_elements', [])
        config.close_button_id = data.get('close_button_id')
        config.fade_mechanism_id = data.get('fade_mechanism_id')
        config.is_open = data.get('is_open', False)
        config.z_index = data.get('z_index', 0)
        return config


class WindowManager:
    """Менеджер окон"""
    
    def __init__(self):
        self._windows = {}  # window_id -> WindowConfig
        self._element_manager = None
        self._mechanism_manager = None
        self._z_index_counter = 100
        
        # Модальное окно (если есть)
        self._modal_window = None
        
        # Callbacks
        self._on_window_open = None
        self._on_window_close = None
        
        # Активные таймеры (для очистки)
        self._active_timers = []

    def set_element_manager(self, manager):
        self._element_manager = manager

    def set_mechanism_manager(self, manager):
        self._mechanism_manager = manager

    def set_callbacks(self, on_open=None, on_close=None):
        self._on_window_open = on_open
        self._on_window_close = on_close

    # === Регистрация окон ===
    
    def register_window(self, panel_element_id, config: WindowConfig = None):
        """
        Регистрирует панель как окно
        
        Args:
            panel_element_id: ID элемента Panel
            config: конфигурация окна (опционально)
        """
        if config is None:
            config = WindowConfig(panel_element_id)
        
        config.window_id = panel_element_id
        self._windows[panel_element_id] = config
        
        # Изначально скрываем
        if self._element_manager:
            element = self._element_manager.get_element_by_id(panel_element_id)
            if element:
                element.hide()
                
                # Скрываем содержимое
                for child_id in config.content_elements:
                    child = self._element_manager.get_element_by_id(child_id)
                    if child:
                        child.hide()
        
        return config

    def unregister_window(self, window_id):
        """Удаляет окно из регистрации"""
        if window_id in self._windows:
            del self._windows[window_id]

    def get_window(self, window_id):
        """Возвращает конфигурацию окна"""
        return self._windows.get(window_id)

    def get_all_windows(self):
        """Возвращает список всех окон"""
        return list(self._windows.values())

    # === Управление окнами ===
    
    def open_window(self, window_id, params=None):
        """Открывает окно"""
        params = params or {}
        config = self._windows.get(window_id)
        
        if not config:
            print(f"[WindowManager] Окно {window_id} не найдено")
            return False
        
        if config.is_open:
            # Уже открыто - поднимаем наверх
            self.bring_to_front(window_id)
            return True
        
        # Проверяем модальность
        if self._modal_window and config.modal:
            print(f"[WindowManager] Уже есть модальное окно")
            return False
        
        if config.modal:
            self._modal_window = window_id
        
        # Получаем элемент
        if not self._element_manager:
            return False
        
        element = self._element_manager.get_element_by_id(window_id)
        if not element:
            return False
        
        # Устанавливаем z-index
        config.z_index = self._z_index_counter
        self._z_index_counter += 1
        
        # Позиция (если передана)
        if 'x' in params:
            element.x = params['x']
        if 'y' in params:
            element.y = params['y']
        
        # Анимация открытия
        if config.animate_open and config.fade_mechanism_id:
            mech = self._mechanism_manager.get_mechanism_by_id(config.fade_mechanism_id)
            if mech and hasattr(mech, 'fade_in'):
                element.show()
                mech.fade_in(config.animation_duration)
            else:
                element.show()
        else:
            element.show()
        
        # Показываем содержимое
        for child_id in config.content_elements:
            child = self._element_manager.get_element_by_id(child_id)
            if child:
                child.show()
        
        config.is_open = True
        
        # Callback
        if self._on_window_open:
            self._on_window_open(window_id)
        
        return True

    def close_window(self, window_id, params=None):
        """Закрывает окно"""
        params = params or {}
        config = self._windows.get(window_id)
        
        if not config or not config.is_open:
            return False
        
        if not config.closable and not params.get('force', False):
            return False
        
        # Получаем элемент
        element = self._element_manager.get_element_by_id(window_id)
        if not element:
            return False
        
        # Анимация закрытия
        if config.animate_close and config.fade_mechanism_id:
            mech = self._mechanism_manager.get_mechanism_by_id(config.fade_mechanism_id)
            if mech and hasattr(mech, 'fade_out'):
                def on_fade_complete():
                    element.hide()
                    for child_id in config.content_elements:
                        child = self._element_manager.get_element_by_id(child_id)
                        if child:
                            child.hide()
                
                # TODO: callback после завершения анимации
                mech.fade_out(config.animation_duration)
                # Временно - просто прячем после задержки
                timer_id = element.canvas.after(config.animation_duration + 50, on_fade_complete)
                self._active_timers.append((element.canvas, timer_id))
            else:
                self._hide_window(config, element)
        else:
            self._hide_window(config, element)
        
        config.is_open = False
        
        # Убираем модальность
        if self._modal_window == window_id:
            self._modal_window = None
        
        # Callback
        if self._on_window_close:
            self._on_window_close(window_id)
        
        return True

    def _hide_window(self, config, element):
        """Скрывает окно и содержимое"""
        element.hide()
        for child_id in config.content_elements:
            child = self._element_manager.get_element_by_id(child_id)
            if child:
                child.hide()

    def toggle_window(self, window_id, params=None):
        """Переключает состояние окна"""
        config = self._windows.get(window_id)
        if not config:
            return False
        
        if config.is_open:
            return self.close_window(window_id, params)
        else:
            return self.open_window(window_id, params)

    def close_all(self, except_modal=True):
        """Закрывает все окна"""
        for window_id, config in self._windows.items():
            if except_modal and config.modal and config.is_open:
                continue
            self.close_window(window_id, {'force': True})

    def bring_to_front(self, window_id):
        """Поднимает окно на передний план"""
        config = self._windows.get(window_id)
        if not config or not config.is_open:
            return False
        
        config.z_index = self._z_index_counter
        self._z_index_counter += 1
        
        # Перерисовываем элемент поверх
        if self._element_manager:
            element = self._element_manager.get_element_by_id(window_id)
            if element:
                self._element_manager.bring_to_front(element)
        
        return True

    # === Добавление содержимого ===
    
    def add_content(self, window_id, element_id):
        """Добавляет элемент в содержимое окна"""
        config = self._windows.get(window_id)
        if not config:
            return False
        
        if element_id not in config.content_elements:
            config.content_elements.append(element_id)
        return True

    def remove_content(self, window_id, element_id):
        """Удаляет элемент из содержимого окна"""
        config = self._windows.get(window_id)
        if not config:
            return False
        
        if element_id in config.content_elements:
            config.content_elements.remove(element_id)
        return True

    def set_close_button(self, window_id, button_id):
        """Устанавливает кнопку закрытия"""
        config = self._windows.get(window_id)
        if config:
            config.close_button_id = button_id

    def set_fade_mechanism(self, window_id, mechanism_id):
        """Устанавливает механизм прозрачности"""
        config = self._windows.get(window_id)
        if config:
            config.fade_mechanism_id = mechanism_id

    # === Проверки ===
    
    def is_window_open(self, window_id):
        """Проверяет открыто ли окно"""
        config = self._windows.get(window_id)
        return config.is_open if config else False

    def is_modal_active(self):
        """Проверяет активно ли модальное окно"""
        return self._modal_window is not None

    def get_open_windows(self):
        """Возвращает список открытых окон"""
        return [
            config for config in self._windows.values()
            if config.is_open
        ]

    # === Сериализация ===
    
    def to_dict(self):
        return {
            window_id: config.to_dict()
            for window_id, config in self._windows.items()
        }

    def from_dict(self, data):
        self._windows.clear()
        for window_id, config_data in data.items():
            self._windows[window_id] = WindowConfig.from_dict(config_data)
            
    def cancel_all_timers(self):
        """Отменяет все активные таймеры"""
        for canvas, timer_id in self._active_timers:
            try:
                canvas.after_cancel(timer_id)
            except tk.TclError:
                pass  # Canvas уже уничтожен
        self._active_timers.clear()
    
    def destroy(self):
        """Очистка при уничтожении менеджера"""
        self.cancel_all_timers()
        self._windows.clear()


# Глобальный экземпляр
_window_manager = None


def get_window_manager():
    """Возвращает глобальный экземпляр WindowManager"""
    global _window_manager
    if _window_manager is None:
        _window_manager = WindowManager()
    return _window_manager

