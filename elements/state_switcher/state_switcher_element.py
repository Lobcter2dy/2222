#!/usr/bin/env python3
"""
Элемент переключателя состояний (State Switcher)
Позволяет переключаться между различными состояниями элементов и механизмов
"""
import uuid
import json


class ElementState:
    """Класс для хранения состояния элемента"""
    
    def __init__(self, name="Состояние"):
        self.id = f"state_{uuid.uuid4().hex[:6]}"
        self.name = name
        self.is_default = False
        
        # Привязанные элементы и их свойства в этом состоянии
        self.element_states = {}  # element_id -> {properties}
        
        # Привязанные механизмы и их состояния
        self.mechanism_states = {}  # mechanism_id -> {is_active, properties}
        
        # Визуальные настройки состояния
        self.color = "#4a9fff"
        self.icon = "●"

    def set_element_properties(self, element_id: str, properties: dict):
        """Сохраняет свойства элемента для этого состояния"""
        self.element_states[element_id] = properties.copy()

    def set_mechanism_state(self, mechanism_id: str, is_active: bool, properties: dict = None):
        """Сохраняет состояние механизма"""
        self.mechanism_states[mechanism_id] = {
            'is_active': is_active,
            'properties': properties or {}
        }

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'is_default': self.is_default,
            'element_states': self.element_states,
            'mechanism_states': self.mechanism_states,
            'color': self.color,
            'icon': self.icon,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ElementState':
        state = cls(data.get('name', 'Состояние'))
        state.id = data.get('id', state.id)
        state.is_default = data.get('is_default', False)
        state.element_states = data.get('element_states', {})
        state.mechanism_states = data.get('mechanism_states', {})
        state.color = data.get('color', '#4a9fff')
        state.icon = data.get('icon', '●')
        return state


class StateSwitcherElement:
    """Элемент переключателя состояний"""
    
    ELEMENT_TYPE = "state_switcher"
    ELEMENT_SYMBOL = "⟐"

    def __init__(self, canvas, x, y, width=150, height=80):
        self.id = f"state_sw_{uuid.uuid4().hex[:8]}"
        self.canvas = canvas
        
        # Позиция и размеры
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Состояния
        self.states = []  # List[ElementState]
        self.current_state_index = 0
        
        # Привязанные элементы и механизмы
        self.bound_elements = []  # List of element_id
        self.bound_mechanisms = []  # List of mechanism_id
        
        # Настройки переключения
        self.properties = {
            'name': 'Переключатель',
            'transition_duration': 300,  # ms
            'transition_type': 'instant',  # instant, fade, slide
            'auto_switch': False,
            'auto_switch_interval': 2000,  # ms
            'loop': True,
            'trigger_function_id': 0,  # ID функции для запуска
            'show_indicator': True,
            'indicator_position': 'bottom',  # top, bottom, left, right
        }
        
        # Визуальные настройки
        self.fill_color = "#2a2a3a"
        self.border_color = "#4a9fff"
        self.text_color = "#ffffff"
        self.active_color = "#4aff4a"
        
        # Состояние
        self.is_visible = True
        self.is_locked = False
        self.is_protected = False
        self.size_locked = False
        
        # Canvas items
        self.canvas_items = []
        
        # Таймер для автопереключения
        self._auto_timer = None
        
        # Создаём начальные состояния
        self._create_default_states()

    def _create_default_states(self):
        """Создаёт начальные состояния"""
        state1 = ElementState("Состояние 1")
        state1.is_default = True
        state1.color = "#4a9fff"
        state1.icon = "①"
        
        state2 = ElementState("Состояние 2")
        state2.color = "#ff4a4a"
        state2.icon = "②"
        
        self.states = [state1, state2]

    # === Управление состояниями ===
    
    def add_state(self, name="Новое состояние") -> ElementState:
        """Добавляет новое состояние"""
        state = ElementState(name)
        state.icon = self._get_next_icon()
        
        # Копируем текущие состояния привязанных элементов
        for elem_id in self.bound_elements:
            state.element_states[elem_id] = {}
        
        for mech_id in self.bound_mechanisms:
            state.mechanism_states[mech_id] = {'is_active': False, 'properties': {}}
        
        self.states.append(state)
        self.update()
        return state

    def remove_state(self, state_id: str) -> bool:
        """Удаляет состояние"""
        if len(self.states) <= 2:
            return False  # Минимум 2 состояния
        
        for i, state in enumerate(self.states):
            if state.id == state_id:
                self.states.pop(i)
                if self.current_state_index >= len(self.states):
                    self.current_state_index = len(self.states) - 1
                self.update()
                return True
        return False

    def get_state(self, state_id: str) -> ElementState:
        """Возвращает состояние по ID"""
        for state in self.states:
            if state.id == state_id:
                return state
        return None

    def get_current_state(self) -> ElementState:
        """Возвращает текущее состояние"""
        if 0 <= self.current_state_index < len(self.states):
            return self.states[self.current_state_index]
        return None

    def _get_next_icon(self) -> str:
        """Возвращает следующую иконку для состояния"""
        icons = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩']
        idx = len(self.states)
        return icons[idx] if idx < len(icons) else f"⊕{idx+1}"

    # === Переключение состояний ===
    
    def switch_to_state(self, state_index: int, element_manager=None, mechanism_manager=None):
        """Переключает на указанное состояние"""
        if not 0 <= state_index < len(self.states):
            return False
        
        self.current_state_index = state_index
        state = self.states[state_index]
        
        # Применяем состояния к элементам
        if element_manager:
            for elem_id, props in state.element_states.items():
                elem = element_manager.get_element_by_id(elem_id)
                if elem:
                    self._apply_properties_to_element(elem, props)
        
        # Применяем состояния к механизмам
        if mechanism_manager:
            for mech_id, mech_state in state.mechanism_states.items():
                mech = mechanism_manager.get_mechanism_by_id(mech_id)
                if mech:
                    self._apply_state_to_mechanism(mech, mech_state)
        
        self.update()
        return True

    def switch_next(self, element_manager=None, mechanism_manager=None):
        """Переключает на следующее состояние"""
        next_index = self.current_state_index + 1
        if next_index >= len(self.states):
            if self.properties['loop']:
                next_index = 0
            else:
                return False
        
        return self.switch_to_state(next_index, element_manager, mechanism_manager)

    def switch_previous(self, element_manager=None, mechanism_manager=None):
        """Переключает на предыдущее состояние"""
        prev_index = self.current_state_index - 1
        if prev_index < 0:
            if self.properties['loop']:
                prev_index = len(self.states) - 1
            else:
                return False
        
        return self.switch_to_state(prev_index, element_manager, mechanism_manager)

    def _apply_properties_to_element(self, element, properties: dict):
        """Применяет свойства к элементу"""
        for key, value in properties.items():
            if key == 'x':
                element.x = value
            elif key == 'y':
                element.y = value
            elif key == 'width':
                element.width = value
            elif key == 'height':
                element.height = value
            elif key == 'is_visible':
                if value:
                    element.show()
                else:
                    element.hide()
            elif key == 'fill_color':
                element.fill_color = value
            elif key == 'border_color':
                element.border_color = value
            elif key == 'opacity':
                if hasattr(element, 'properties'):
                    element.properties['opacity'] = value
            elif hasattr(element, 'properties') and key in element.properties:
                element.properties[key] = value
        
        element.update()

    def _apply_state_to_mechanism(self, mechanism, mech_state: dict):
        """Применяет состояние к механизму"""
        is_active = mech_state.get('is_active', False)
        properties = mech_state.get('properties', {})
        
        if is_active:
            mechanism.start()
        else:
            mechanism.stop()
        
        for key, value in properties.items():
            if hasattr(mechanism, key):
                setattr(mechanism, key, value)
            elif hasattr(mechanism, 'properties') and key in mechanism.properties:
                mechanism.properties[key] = value
        
        mechanism.update()

    # === Привязка элементов и механизмов ===
    
    def bind_element(self, element_id: str):
        """Привязывает элемент к переключателю"""
        if element_id not in self.bound_elements:
            self.bound_elements.append(element_id)
            
            # Добавляем в каждое состояние
            for state in self.states:
                if element_id not in state.element_states:
                    state.element_states[element_id] = {}

    def unbind_element(self, element_id: str):
        """Отвязывает элемент"""
        if element_id in self.bound_elements:
            self.bound_elements.remove(element_id)
            
            for state in self.states:
                if element_id in state.element_states:
                    del state.element_states[element_id]

    def bind_mechanism(self, mechanism_id: str):
        """Привязывает механизм к переключателю"""
        if mechanism_id not in self.bound_mechanisms:
            self.bound_mechanisms.append(mechanism_id)
            
            for state in self.states:
                if mechanism_id not in state.mechanism_states:
                    state.mechanism_states[mechanism_id] = {'is_active': False, 'properties': {}}

    def unbind_mechanism(self, mechanism_id: str):
        """Отвязывает механизм"""
        if mechanism_id in self.bound_mechanisms:
            self.bound_mechanisms.remove(mechanism_id)
            
            for state in self.states:
                if mechanism_id in state.mechanism_states:
                    del state.mechanism_states[mechanism_id]

    # === Захват состояния ===
    
    def capture_current_state(self, element_manager=None, mechanism_manager=None):
        """Захватывает текущее состояние привязанных объектов"""
        state = self.get_current_state()
        if not state:
            return
        
        # Захватываем элементы
        if element_manager:
            for elem_id in self.bound_elements:
                elem = element_manager.get_element_by_id(elem_id)
                if elem:
                    state.element_states[elem_id] = self._capture_element_state(elem)
        
        # Захватываем механизмы
        if mechanism_manager:
            for mech_id in self.bound_mechanisms:
                mech = mechanism_manager.get_mechanism_by_id(mech_id)
                if mech:
                    state.mechanism_states[mech_id] = self._capture_mechanism_state(mech)

    def _capture_element_state(self, element) -> dict:
        """Захватывает состояние элемента"""
        state = {
            'x': element.x,
            'y': element.y,
            'width': element.width,
            'height': element.height,
            'is_visible': element.is_visible,
        }
        
        if hasattr(element, 'fill_color'):
            state['fill_color'] = element.fill_color
        if hasattr(element, 'border_color'):
            state['border_color'] = element.border_color
        if hasattr(element, 'properties'):
            state['opacity'] = element.properties.get('opacity', 100)
        
        return state

    def _capture_mechanism_state(self, mechanism) -> dict:
        """Захватывает состояние механизма"""
        return {
            'is_active': mechanism.is_active if hasattr(mechanism, 'is_active') else False,
            'properties': {}
        }

    # === Автопереключение ===
    
    def start_auto_switch(self, element_manager=None, mechanism_manager=None):
        """Запускает автоматическое переключение"""
        if not self.properties['auto_switch']:
            return
        
        self._stop_auto_timer()
        
        interval = self.properties['auto_switch_interval']
        
        def auto_tick():
            self.switch_next(element_manager, mechanism_manager)
            if self.properties['auto_switch']:
                self._auto_timer = self.canvas.after(interval, auto_tick)
        
        self._auto_timer = self.canvas.after(interval, auto_tick)

    def stop_auto_switch(self):
        """Останавливает автопереключение"""
        self._stop_auto_timer()

    def _stop_auto_timer(self):
        """Останавливает таймер"""
        if self._auto_timer:
            self.canvas.after_cancel(self._auto_timer)
            self._auto_timer = None

    # === Рендеринг ===
    
    def draw(self):
        """Рисует элемент"""
        self.clear()
        
        if not self.is_visible:
            return
        
        x1, y1 = self.x, self.y
        x2, y2 = x1 + self.width, y1 + self.height
        
        # 1. Основной фон
        bg = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=self.fill_color,
            outline=self.border_color,
            width=2,
            tags=(self.id, "state_switcher", "element")
        )
        self.canvas_items.append(bg)
        
        # 2. Заголовок
        header_y = y1 + 20
        header = self.canvas.create_text(
            x1 + self.width / 2, header_y,
            text=f"⟐ {self.properties['name']}",
            fill=self.text_color,
            font=("Arial", 9, "bold"),
            tags=(self.id, "state_switcher")
        )
        self.canvas_items.append(header)
        
        # 3. Индикаторы состояний
        if self.properties['show_indicator']:
            self._draw_state_indicators(x1, y1, x2, y2)
        
        # 4. Текущее состояние
        current = self.get_current_state()
        if current:
            state_y = y1 + self.height - 25
            state_text = self.canvas.create_text(
                x1 + self.width / 2, state_y,
                text=f"{current.icon} {current.name}",
                fill=current.color,
                font=("Arial", 10, "bold"),
                tags=(self.id, "state_switcher")
            )
            self.canvas_items.append(state_text)
        
        # 5. Кнопки навигации
        self._draw_nav_buttons(x1, y1, x2, y2)

    def _draw_state_indicators(self, x1, y1, x2, y2):
        """Рисует индикаторы состояний"""
        indicator_y = y1 + 40
        
        total_width = len(self.states) * 20
        start_x = x1 + (self.width - total_width) / 2
        
        for i, state in enumerate(self.states):
            ix = start_x + i * 20 + 10
            is_current = i == self.current_state_index
            
            # Кружок
            color = state.color if is_current else "#555555"
            size = 8 if is_current else 6
            
            indicator = self.canvas.create_oval(
                ix - size, indicator_y - size,
                ix + size, indicator_y + size,
                fill=color,
                outline="#ffffff" if is_current else "",
                width=2 if is_current else 0,
                tags=(self.id, "state_switcher", f"indicator_{state.id}")
            )
            self.canvas_items.append(indicator)
            
            # Привязка клика
            self.canvas.tag_bind(indicator, "<Button-1>", 
                lambda e, idx=i: self.switch_to_state(idx))

    def _draw_nav_buttons(self, x1, y1, x2, y2):
        """Рисует кнопки навигации"""
        nav_y = y1 + self.height / 2
        
        # Кнопка "Назад"
        prev_btn = self.canvas.create_text(
            x1 + 15, nav_y,
            text="◀",
            fill="#888888",
            font=("Arial", 14),
            tags=(self.id, "state_switcher", "nav_prev")
        )
        self.canvas_items.append(prev_btn)
        self.canvas.tag_bind(prev_btn, "<Button-1>", lambda e: self.switch_previous())
        self.canvas.tag_bind(prev_btn, "<Enter>", lambda e: self.canvas.itemconfig(prev_btn, fill="#ffffff"))
        self.canvas.tag_bind(prev_btn, "<Leave>", lambda e: self.canvas.itemconfig(prev_btn, fill="#888888"))
        
        # Кнопка "Вперёд"
        next_btn = self.canvas.create_text(
            x2 - 15, nav_y,
            text="▶",
            fill="#888888",
            font=("Arial", 14),
            tags=(self.id, "state_switcher", "nav_next")
        )
        self.canvas_items.append(next_btn)
        self.canvas.tag_bind(next_btn, "<Button-1>", lambda e: self.switch_next())
        self.canvas.tag_bind(next_btn, "<Enter>", lambda e: self.canvas.itemconfig(next_btn, fill="#ffffff"))
        self.canvas.tag_bind(next_btn, "<Leave>", lambda e: self.canvas.itemconfig(next_btn, fill="#888888"))

    def clear(self):
        """Очищает элемент"""
        for item in self.canvas_items:
            try:
                self.canvas.delete(item)
            except tk.TclError:
                pass  # Canvas item already deleted
        self.canvas_items = []

    def update(self):
        """Обновляет элемент"""
        self.draw()

    def show(self):
        """Показывает элемент"""
        self.is_visible = True
        self.update()

    def hide(self):
        """Скрывает элемент"""
        self.is_visible = False
        self.clear()

    def delete(self):
        """Удаляет элемент"""
        self._stop_auto_timer()
        self.clear()

    # === Сериализация ===
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'type': self.ELEMENT_TYPE,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'states': [s.to_dict() for s in self.states],
            'current_state_index': self.current_state_index,
            'bound_elements': self.bound_elements,
            'bound_mechanisms': self.bound_mechanisms,
            'properties': self.properties,
            'fill_color': self.fill_color,
            'border_color': self.border_color,
            'text_color': self.text_color,
            'active_color': self.active_color,
            'is_visible': self.is_visible,
            'is_locked': self.is_locked,
            'size_locked': self.size_locked,
        }

    def from_dict(self, data: dict):
        self.id = data.get('id', self.id)
        self.x = data.get('x', self.x)
        self.y = data.get('y', self.y)
        self.width = data.get('width', self.width)
        self.height = data.get('height', self.height)
        
        self.states = []
        for state_data in data.get('states', []):
            self.states.append(ElementState.from_dict(state_data))
        
        if not self.states:
            self._create_default_states()
        
        self.current_state_index = data.get('current_state_index', 0)
        self.bound_elements = data.get('bound_elements', [])
        self.bound_mechanisms = data.get('bound_mechanisms', [])
        self.properties = {**self.properties, **data.get('properties', {})}
        self.fill_color = data.get('fill_color', self.fill_color)
        self.border_color = data.get('border_color', self.border_color)
        self.text_color = data.get('text_color', self.text_color)
        self.active_color = data.get('active_color', self.active_color)
        self.is_visible = data.get('is_visible', True)
        self.is_locked = data.get('is_locked', False)
        self.size_locked = data.get('size_locked', False)

    @classmethod
    def create_from_dict(cls, canvas, data: dict) -> 'StateSwitcherElement':
        elem = cls(canvas, data.get('x', 0), data.get('y', 0))
        elem.from_dict(data)
        return elem

    # === Проверка попадания ===
    
    def contains_point(self, x, y) -> bool:
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

    def get_bounds(self) -> tuple:
        return (self.x, self.y, self.x + self.width, self.y + self.height)

