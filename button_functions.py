#!/usr/bin/env python3
"""
Система функций для кнопок
Здесь описываются функции и действия, которые вызываются кнопками
"""


class ButtonAction:
    """Описание действия кнопки"""
    
    # Типы действий
    ACTION_SHOW = 'show'           # Показать элемент
    ACTION_HIDE = 'hide'           # Скрыть элемент
    ACTION_TOGGLE = 'toggle'       # Переключить видимость
    ACTION_START_MECH = 'start'    # Запустить механизм
    ACTION_STOP_MECH = 'stop'      # Остановить механизм
    ACTION_TOGGLE_MECH = 'toggle_mech'  # Переключить механизм
    ACTION_OPEN_WINDOW = 'open_window'  # Открыть окно (панель)
    ACTION_CLOSE_WINDOW = 'close_window'  # Закрыть окно
    ACTION_CUSTOM = 'custom'       # Пользовательская функция
    
    def __init__(self, action_type, target_id=None, params=None):
        self.action_type = action_type
        self.target_id = target_id       # ID элемента/механизма
        self.params = params or {}       # Дополнительные параметры
        self.delay = 0                   # Задержка выполнения (мс)
        self.condition = None            # Условие выполнения
    
    def to_dict(self):
        return {
            'action_type': self.action_type,
            'target_id': self.target_id,
            'params': self.params,
            'delay': self.delay,
            'condition': self.condition,
        }
    
    @classmethod
    def from_dict(cls, data):
        action = cls(
            data.get('action_type', 'custom'),
            data.get('target_id'),
            data.get('params', {})
        )
        action.delay = data.get('delay', 0)
        action.condition = data.get('condition')
        return action


class ButtonFunctions:
    """Менеджер функций и действий кнопок"""

    def __init__(self):
        # Словарь функций: номер -> callable
        self._functions = {}
        
        # Словарь действий: номер -> список ButtonAction
        self._actions = {}
        
        # Ссылка на приложение (для доступа к другим системам)
        self._app = None
        self._element_manager = None
        self._mechanism_manager = None
        self._window_manager = None

    def set_app(self, app):
        """Устанавливает ссылку на приложение"""
        self._app = app

    def set_element_manager(self, manager):
        """Устанавливает менеджер элементов"""
        self._element_manager = manager

    def set_mechanism_manager(self, manager):
        """Устанавливает менеджер механизмов"""
        self._mechanism_manager = manager

    def set_window_manager(self, manager):
        """Устанавливает менеджер окон"""
        self._window_manager = manager

    # === Регистрация функций ===
    
    def register(self, func_id, func, name=""):
        """
        Регистрирует функцию под указанным номером
        
        Args:
            func_id: номер функции (int)
            func: callable
            name: описание функции (опционально)
        """
        self._functions[func_id] = {
            'func': func,
            'name': name or f"Функция {func_id}"
        }

    def unregister(self, func_id):
        """Удаляет функцию по номеру"""
        if func_id in self._functions:
            del self._functions[func_id]

    # === Регистрация действий ===
    
    def add_action(self, func_id, action: ButtonAction):
        """Добавляет действие к функции"""
        if func_id not in self._actions:
            self._actions[func_id] = []
        self._actions[func_id].append(action)

    def remove_action(self, func_id, index):
        """Удаляет действие по индексу"""
        if func_id in self._actions and 0 <= index < len(self._actions[func_id]):
            del self._actions[func_id][index]

    def clear_actions(self, func_id):
        """Очищает все действия функции"""
        if func_id in self._actions:
            self._actions[func_id] = []

    def get_actions(self, func_id):
        """Возвращает список действий функции"""
        return self._actions.get(func_id, [])

    # === Вызов функций ===

    def call(self, func_id, *args, **kwargs):
        """
        Вызывает функцию и все её действия по номеру
        
        Args:
            func_id: номер функции
            *args, **kwargs: аргументы для функции
            
        Returns:
            Результат вызова функции или None
        """
        results = []
        
        # Выполняем базовую функцию
        if func_id in self._functions:
            try:
                func_info = self._functions[func_id]
                print(f"[ButtonFunctions] Вызов: {func_info['name']} (#{func_id})")
                result = func_info['func'](*args, **kwargs)
                results.append(result)
            except Exception as e:
                print(f"[ButtonFunctions] Ошибка функции #{func_id}: {e}")
        
        # Выполняем действия
        if func_id in self._actions:
            for action in self._actions[func_id]:
                try:
                    self._execute_action(action)
                except Exception as e:
                    print(f"[ButtonFunctions] Ошибка действия: {e}")
        
        return results[0] if results else None

    def _execute_action(self, action: ButtonAction):
        """Выполняет действие"""
        if action.delay > 0 and self._app:
            # Отложенное выполнение
            self._app.root.after(action.delay, lambda: self._do_action(action))
        else:
            self._do_action(action)

    def _do_action(self, action: ButtonAction):
        """Непосредственное выполнение действия"""
        action_type = action.action_type
        target_id = action.target_id
        params = action.params
        
        # === Действия с элементами ===
        if action_type == ButtonAction.ACTION_SHOW:
            if self._element_manager and target_id:
                element = self._element_manager.get_element_by_id(target_id)
                if element:
                    element.show()
                    # Запускаем механизмы появления
                    for mech in element.get_attached_mechanisms():
                        if hasattr(mech, 'fade_in'):
                            mech.fade_in(params.get('duration', 300))
        
        elif action_type == ButtonAction.ACTION_HIDE:
            if self._element_manager and target_id:
                element = self._element_manager.get_element_by_id(target_id)
                if element:
                    # Запускаем механизмы исчезновения
                    has_fade = False
                    for mech in element.get_attached_mechanisms():
                        if hasattr(mech, 'fade_out'):
                            mech.fade_out(params.get('duration', 300))
                            has_fade = True
                    
                    if not has_fade:
                        element.hide()
        
        elif action_type == ButtonAction.ACTION_TOGGLE:
            if self._element_manager and target_id:
                element = self._element_manager.get_element_by_id(target_id)
                if element:
                    if element.is_visible:
                        self._do_action(ButtonAction(ButtonAction.ACTION_HIDE, target_id, params))
                    else:
                        self._do_action(ButtonAction(ButtonAction.ACTION_SHOW, target_id, params))
        
        # === Действия с механизмами ===
        elif action_type == ButtonAction.ACTION_START_MECH:
            if self._mechanism_manager and target_id:
                mech = self._mechanism_manager.get_mechanism_by_id(target_id)
                if mech:
                    mech.start()
        
        elif action_type == ButtonAction.ACTION_STOP_MECH:
            if self._mechanism_manager and target_id:
                mech = self._mechanism_manager.get_mechanism_by_id(target_id)
                if mech:
                    mech.stop()
        
        elif action_type == ButtonAction.ACTION_TOGGLE_MECH:
            if self._mechanism_manager and target_id:
                mech = self._mechanism_manager.get_mechanism_by_id(target_id)
                if mech:
                    mech.toggle()
        
        # === Действия с окнами ===
        elif action_type == ButtonAction.ACTION_OPEN_WINDOW:
            if self._window_manager and target_id:
                self._window_manager.open_window(target_id, params)
        
        elif action_type == ButtonAction.ACTION_CLOSE_WINDOW:
            if self._window_manager and target_id:
                self._window_manager.close_window(target_id, params)

    # === Удобные методы ===
    
    def create_show_action(self, func_id, element_id, duration=300, delay=0):
        """Создаёт действие показа элемента"""
        action = ButtonAction(
            ButtonAction.ACTION_SHOW,
            element_id,
            {'duration': duration}
        )
        action.delay = delay
        self.add_action(func_id, action)
        return action

    def create_hide_action(self, func_id, element_id, duration=300, delay=0):
        """Создаёт действие скрытия элемента"""
        action = ButtonAction(
            ButtonAction.ACTION_HIDE,
            element_id,
            {'duration': duration}
        )
        action.delay = delay
        self.add_action(func_id, action)
        return action

    def create_toggle_action(self, func_id, element_id, duration=300, delay=0):
        """Создаёт действие переключения элемента"""
        action = ButtonAction(
            ButtonAction.ACTION_TOGGLE,
            element_id,
            {'duration': duration}
        )
        action.delay = delay
        self.add_action(func_id, action)
        return action

    def create_mechanism_action(self, func_id, mech_id, action_type='toggle', delay=0):
        """Создаёт действие с механизмом"""
        action = ButtonAction(action_type, mech_id)
        action.delay = delay
        self.add_action(func_id, action)
        return action

    # === Информация ===

    def get_all(self):
        """Возвращает словарь всех зарегистрированных функций"""
        return {
            fid: info['name'] 
            for fid, info in self._functions.items()
        }

    def exists(self, func_id):
        """Проверяет существование функции"""
        return func_id in self._functions or func_id in self._actions

    def get_info(self, func_id):
        """Возвращает информацию о функции"""
        return {
            'name': self._functions.get(func_id, {}).get('name', f'Функция #{func_id}'),
            'has_function': func_id in self._functions,
            'actions_count': len(self._actions.get(func_id, [])),
            'actions': [a.to_dict() for a in self._actions.get(func_id, [])]
        }

    # === Сериализация ===
    
    def to_dict(self):
        """Сериализует действия"""
        return {
            func_id: [action.to_dict() for action in actions]
            for func_id, actions in self._actions.items()
        }

    def from_dict(self, data):
        """Загружает действия"""
        self._actions.clear()
        for func_id, actions_data in data.items():
            func_id = int(func_id) if isinstance(func_id, str) else func_id
            self._actions[func_id] = [
                ButtonAction.from_dict(a) for a in actions_data
            ]


# Глобальный экземпляр менеджера функций
button_functions = ButtonFunctions()


# === РЕГИСТРАЦИЯ СТАНДАРТНЫХ ФУНКЦИЙ ===

def _func_empty():
    """Пустая функция"""
    pass

# Регистрируем базовые функции
button_functions.register(0, _func_empty, "Нет действия")
button_functions.register(1, _func_empty, "Действие 1")
button_functions.register(2, _func_empty, "Действие 2")
button_functions.register(3, _func_empty, "Действие 3")
button_functions.register(4, _func_empty, "Действие 4")
button_functions.register(5, _func_empty, "Действие 5")


# === API ДЛЯ ИСПОЛЬЗОВАНИЯ ===

def call_button_function(func_id, *args, **kwargs):
    """Вызывает функцию по номеру"""
    return button_functions.call(func_id, *args, **kwargs)


def register_button_function(func_id, func, name=""):
    """Регистрирует новую функцию"""
    button_functions.register(func_id, func, name)


def get_available_functions():
    """Возвращает список доступных функций"""
    return button_functions.get_all()


def get_button_functions():
    """Возвращает глобальный экземпляр ButtonFunctions"""
    return button_functions
