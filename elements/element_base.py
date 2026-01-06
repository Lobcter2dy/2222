#!/usr/bin/env python3
"""
Базовый класс элемента (расширенный)
Все визуальные элементы наследуются от него
Содержит единую систему свойств, механизмов, текста и группировки
"""
from abc import ABC, abstractmethod
import uuid


class ElementBase(ABC):
    """Базовый класс для всех элементов интерфейса"""

    # Переопределить в наследниках
    ELEMENT_TYPE = "base"
    ELEMENT_SYMBOL = "?"
    
    # ID счётчик
    _id_counter = 0
    
    # Единая система свойств (все возможные свойства)
    DEFAULT_PROPERTIES = {
        # === Основные цвета ===
        'fill_color': '',           # Цвет заливки (пустой = прозрачный)
        'stroke_color': '#ffffff',  # Цвет обводки
        'stroke_width': 2,          # Толщина обводки
        'opacity': 100,             # Прозрачность (0-100)
        
        # === Геометрия ===
        'shape': 'rectangle',       # rectangle, rounded, pill, chamfer
        'display_mode': 'stroke',   # stroke, fill, both
        'line_style': 'solid',      # solid, dashed, dotted, dash_dot, long_dash
        
        # === Углы ===
        'corner_radius': 0,
        'corner_tl': None,
        'corner_tr': None,
        'corner_bl': None,
        'corner_br': None,
        'chamfer_size': 10,
        
        # === Двойная рамка ===
        'double_border': False,
        'double_border_gap': 3,
        'double_border_color': '',
        
        # === Тень ===
        'shadow_enabled': False,
        'shadow_x': 2,
        'shadow_y': 2,
        'shadow_color': '#000000',
        
        # === Внутренняя тень ===
        'inset_shadow': False,
        'inset_shadow_size': 5,
        'inset_shadow_color': '#000000',
        
        # === Свечение ===
        'glow_enabled': False,
        'glow_radius': 5,
        'glow_color': '#ffffff',
        
        # === Встроенный текст ===
        'label_enabled': False,
        'label_text': '',
        'label_font': 'Arial',
        'label_size': 12,
        'label_color': '#ffffff',
        'label_bold': False,
        'label_italic': False,
        'label_position': 'center',  # center, top, bottom, left, right, top-left, top-right, bottom-left, bottom-right
        'label_offset_x': 0,
        'label_offset_y': 0,
        
        # === Трансформации ===
        'rotation': 0,              # Угол поворота (градусы)
        'scale_x': 1.0,             # Масштаб по X
        'scale_y': 1.0,             # Масштаб по Y
        'flip_h': False,            # Отразить горизонтально
        'flip_v': False,            # Отразить вертикально
        
        # === Анимация (базовая) ===
        'animation_enabled': False,
        'animation_type': 'none',   # none, pulse, bounce, shake, glow
        'animation_speed': 1.0,
        'animation_loop': True,
    }
    
    # Стили линий
    LINE_STYLES = {
        'solid': None,
        'dashed': (8, 4),
        'dotted': (2, 4),
        'dash_dot': (8, 4, 2, 4),
        'long_dash': (16, 8),
    }
    
    # Позиции текста
    LABEL_ANCHORS = {
        'center': ('center', 0.5, 0.5),
        'top': ('s', 0.5, 0),
        'bottom': ('n', 0.5, 1),
        'left': ('e', 0, 0.5),
        'right': ('w', 1, 0.5),
        'top-left': ('se', 0, 0),
        'top-right': ('sw', 1, 0),
        'bottom-left': ('ne', 0, 1),
        'bottom-right': ('nw', 1, 1),
    }

    def __init__(self, canvas, config):
        self.canvas = canvas
        self.config = config
        
        # Уникальный ID
        ElementBase._id_counter += 1
        self.id = f"{self.ELEMENT_TYPE}_{ElementBase._id_counter}"
        
        # Позиция и размеры
        self.x = 0
        self.y = 0
        self.width = 100
        self.height = 100
        
        # Система масштабирования
        self.zoom_system = None
        
        # Свойства элемента
        self.properties = self.DEFAULT_PROPERTIES.copy()
        
        # Canvas объекты
        self.canvas_items = []
        
        # Состояние
        self.is_visible = True
        self.is_protected = False
        self.size_locked = False
        self.position_locked = False
        
        # === Система механизмов ===
        self.attached_mechanisms = []  # ID привязанных механизмов
        self._mechanism_manager = None
        
        # === Система группировки ===
        self.parent_group = None       # ID родительской группы
        self.children = []             # ID дочерних элементов
        self.is_group = False          # Является ли группой
        self._element_manager = None
        
        # === Система событий ===
        self.event_handlers = {
            'click': [],
            'hover_enter': [],
            'hover_leave': [],
            'drag_start': [],
            'drag': [],
            'drag_end': [],
            'state_change': [],
        }
        
        # === Привязка к переключателю состояний ===
        self.state_switcher_id = None
        
        # === Анимация ===
        self._animation_timer = None
        self._animation_state = {}

    # === Установка менеджеров ===
    
    def set_zoom_system(self, zoom_system):
        self.zoom_system = zoom_system

    def set_mechanism_manager(self, manager):
        self._mechanism_manager = manager

    def set_element_manager(self, manager):
        self._element_manager = manager

    # === Механизмы ===
    
    def attach_mechanism(self, mechanism_id: str):
        """Привязывает механизм к элементу"""
        if mechanism_id not in self.attached_mechanisms:
            self.attached_mechanisms.append(mechanism_id)
            
            # Уведомляем механизм
            if self._mechanism_manager:
                mech = self._mechanism_manager.get_mechanism_by_id(mechanism_id)
                if mech and hasattr(mech, 'attach_to_element'):
                    mech.attach_to_element(self.id)

    def detach_mechanism(self, mechanism_id: str):
        """Отвязывает механизм от элемента"""
        if mechanism_id in self.attached_mechanisms:
            self.attached_mechanisms.remove(mechanism_id)
            
            if self._mechanism_manager:
                mech = self._mechanism_manager.get_mechanism_by_id(mechanism_id)
                if mech and hasattr(mech, 'detach_from_element'):
                    mech.detach_from_element(self.id)

    def get_attached_mechanisms(self) -> list:
        """Возвращает привязанные механизмы"""
        if not self._mechanism_manager:
            return []
        
        mechanisms = []
        for mech_id in self.attached_mechanisms:
            mech = self._mechanism_manager.get_mechanism_by_id(mech_id)
            if mech:
                mechanisms.append(mech)
        return mechanisms

    def start_all_mechanisms(self):
        """Запускает все привязанные механизмы"""
        for mech in self.get_attached_mechanisms():
            if hasattr(mech, 'start'):
                mech.start()

    def stop_all_mechanisms(self):
        """Останавливает все привязанные механизмы"""
        for mech in self.get_attached_mechanisms():
            if hasattr(mech, 'stop'):
                mech.stop()

    # === Группировка ===
    
    def add_child(self, child_id: str):
        """Добавляет дочерний элемент"""
        if child_id not in self.children:
            self.children.append(child_id)
            self.is_group = len(self.children) > 0
            
            if self._element_manager:
                child = self._element_manager.get_element_by_id(child_id)
                if child:
                    child.parent_group = self.id

    def remove_child(self, child_id: str):
        """Удаляет дочерний элемент"""
        if child_id in self.children:
            self.children.remove(child_id)
            self.is_group = len(self.children) > 0
            
            if self._element_manager:
                child = self._element_manager.get_element_by_id(child_id)
                if child:
                    child.parent_group = None

    def get_children(self) -> list:
        """Возвращает дочерние элементы"""
        if not self._element_manager:
            return []
        
        children = []
        for child_id in self.children:
            child = self._element_manager.get_element_by_id(child_id)
            if child:
                children.append(child)
        return children

    def get_parent(self):
        """Возвращает родительский элемент"""
        if not self.parent_group or not self._element_manager:
            return None
        return self._element_manager.get_element_by_id(self.parent_group)

    def move_children_by(self, dx, dy):
        """Перемещает дочерние элементы"""
        for child in self.get_children():
            child.x += dx
            child.y += dy
            child.move_children_by(dx, dy)  # Рекурсивно
            child.update()

    def get_group_bounds(self) -> tuple:
        """Возвращает границы группы (включая детей)"""
        if not self.children:
            return self.get_bounds()
        
        min_x, min_y = self.x, self.y
        max_x, max_y = self.x + self.width, self.y + self.height
        
        for child in self.get_children():
            cx1, cy1, cx2, cy2 = child.get_group_bounds()
            min_x = min(min_x, cx1)
            min_y = min(min_y, cy1)
            max_x = max(max_x, cx2)
            max_y = max(max_y, cy2)
        
        return (min_x, min_y, max_x, max_y)

    # === Текстовая подпись ===
    
    def set_label(self, text: str, **kwargs):
        """Устанавливает текстовую подпись"""
        self.properties['label_enabled'] = True
        self.properties['label_text'] = text
        
        for key, value in kwargs.items():
            if f'label_{key}' in self.properties:
                self.properties[f'label_{key}'] = value
        
        self.update()

    def remove_label(self):
        """Удаляет текстовую подпись"""
        self.properties['label_enabled'] = False
        self.properties['label_text'] = ''
        self.update()

    def _draw_label(self):
        """Рисует текстовую подпись"""
        if not self.properties.get('label_enabled') or not self.properties.get('label_text'):
            return
        
        x1, y1, x2, y2 = self.get_screen_bounds()
        w, h = x2 - x1, y2 - y1
        
        # Позиция
        pos = self.properties.get('label_position', 'center')
        anchor_info = self.LABEL_ANCHORS.get(pos, ('center', 0.5, 0.5))
        anchor, rx, ry = anchor_info
        
        x = x1 + w * rx + self.properties.get('label_offset_x', 0)
        y = y1 + h * ry + self.properties.get('label_offset_y', 0)
        
        # Шрифт
        font_name = self.properties.get('label_font', 'Arial')
        font_size = self._scale(self.properties.get('label_size', 12))
        font_style = ''
        if self.properties.get('label_bold'):
            font_style += 'bold '
        if self.properties.get('label_italic'):
            font_style += 'italic'
        
        font = (font_name, int(font_size), font_style.strip() or 'normal')
        
        # Рисуем текст
        item = self.canvas.create_text(
            x, y,
            text=self.properties['label_text'],
            fill=self.properties.get('label_color', '#ffffff'),
            font=font,
            anchor=anchor,
            tags=(self.id, "element", "label")
        )
        self.canvas_items.append(item)

    # === События ===
    
    def on(self, event: str, handler):
        """Подписывается на событие"""
        if event in self.event_handlers:
            self.event_handlers[event].append(handler)

    def off(self, event: str, handler=None):
        """Отписывается от события"""
        if event in self.event_handlers:
            if handler:
                if handler in self.event_handlers[event]:
                    self.event_handlers[event].remove(handler)
            else:
                self.event_handlers[event] = []

    def trigger(self, event: str, data=None):
        """Вызывает событие"""
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    handler(self, data)
                except Exception as e:
                    print(f"[ElementBase] Event handler error: {e}")

    # === Анимация (базовая) ===
    
    def start_animation(self, animation_type: str = None):
        """Запускает встроенную анимацию"""
        if animation_type:
            self.properties['animation_type'] = animation_type
        self.properties['animation_enabled'] = True
        self._run_animation()

    def stop_animation(self):
        """Останавливает анимацию"""
        self.properties['animation_enabled'] = False
        if self._animation_timer:
            self.canvas.after_cancel(self._animation_timer)
            self._animation_timer = None
        self._animation_state = {}
        self.update()

    def _run_animation(self):
        """Выполняет кадр анимации"""
        if not self.properties.get('animation_enabled'):
            return
        
        anim_type = self.properties.get('animation_type', 'none')
        
        if anim_type == 'pulse':
            self._animate_pulse()
        elif anim_type == 'bounce':
            self._animate_bounce()
        elif anim_type == 'shake':
            self._animate_shake()
        elif anim_type == 'glow':
            self._animate_glow()
        
        # Следующий кадр
        interval = int(50 / self.properties.get('animation_speed', 1.0))
        self._animation_timer = self.canvas.after(interval, self._run_animation)

    def _animate_pulse(self):
        """Анимация пульсации"""
        import math
        
        if 'pulse_phase' not in self._animation_state:
            self._animation_state['pulse_phase'] = 0
        
        phase = self._animation_state['pulse_phase']
        scale = 1.0 + 0.1 * math.sin(phase)
        
        self.properties['scale_x'] = scale
        self.properties['scale_y'] = scale
        
        self._animation_state['pulse_phase'] += 0.1
        self.update()

    def _animate_bounce(self):
        """Анимация подпрыгивания"""
        import math
        
        if 'bounce_phase' not in self._animation_state:
            self._animation_state['bounce_phase'] = 0
            self._animation_state['bounce_base_y'] = self.y
        
        phase = self._animation_state['bounce_phase']
        offset = abs(math.sin(phase)) * 20
        
        self.y = self._animation_state['bounce_base_y'] - offset
        self._animation_state['bounce_phase'] += 0.15
        self.update()

    def _animate_shake(self):
        """Анимация тряски"""
        import random
        
        if 'shake_base_x' not in self._animation_state:
            self._animation_state['shake_base_x'] = self.x
            self._animation_state['shake_base_y'] = self.y
        
        self.x = self._animation_state['shake_base_x'] + random.randint(-3, 3)
        self.y = self._animation_state['shake_base_y'] + random.randint(-3, 3)
        self.update()

    def _animate_glow(self):
        """Анимация свечения"""
        import math
        
        if 'glow_phase' not in self._animation_state:
            self._animation_state['glow_phase'] = 0
        
        phase = self._animation_state['glow_phase']
        radius = 5 + 10 * (0.5 + 0.5 * math.sin(phase))
        
        self.properties['glow_enabled'] = True
        self.properties['glow_radius'] = radius
        
        self._animation_state['glow_phase'] += 0.1
        self.update()

    # === Координаты ===
    
    def get_screen_bounds(self):
        """Возвращает экранные координаты"""
        if self.zoom_system:
            sx, sy = self.zoom_system.real_to_screen(self.x, self.y)
            sw = self.zoom_system.scale_value(self.width)
            sh = self.zoom_system.scale_value(self.height)
            return (sx, sy, sx + sw, sy + sh)
        return self.get_bounds()

    def get_bounds(self):
        """Возвращает реальные координаты"""
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def get_center(self):
        """Возвращает центр элемента"""
        return (self.x + self.width / 2, self.y + self.height / 2)

    # === Абстрактные методы ===
    
    @abstractmethod
    def draw(self):
        """Рисует элемент"""
        pass

    def contains_point(self, x, y):
        """Проверяет попадание точки"""
        x1, y1, x2, y2 = self.get_screen_bounds()
        return x1 <= x <= x2 and y1 <= y <= y2

    # === Управление ===
    
    def update(self):
        """Перерисовывает элемент"""
        self.clear()
        if self.is_visible:
            self.draw()
            self._draw_label()

    def clear(self):
        """Очищает графику"""
        for item in self.canvas_items:
            try:
                self.canvas.delete(item)
            except tk.TclError:
                pass  # Canvas item already deleted
        self.canvas_items = []

    def show(self):
        self.is_visible = True
        self.update()

    def hide(self):
        self.is_visible = False
        self.clear()

    def delete(self):
        """Удаляет элемент полностью"""
        self.stop_animation()
        self.stop_all_mechanisms()
        
        # Отвязываем детей
        for child in self.get_children():
            child.parent_group = None
        
        self.clear()

    # === Перемещение и размер ===
    
    def move_to(self, x, y):
        """Перемещает элемент"""
        if self.position_locked:
            return
        
        dx, dy = x - self.x, y - self.y
        self.x = x
        self.y = y
        
        # Перемещаем детей
        self.move_children_by(dx, dy)
        
        self.update()
        self.trigger('drag', {'x': x, 'y': y})

    def move_by(self, dx, dy):
        """Смещает элемент"""
        self.move_to(self.x + dx, self.y + dy)

    def resize(self, width, height):
        """Изменяет размер"""
        if self.size_locked:
            return
        self.width = max(10, width)
        self.height = max(10, height)
        self.update()

    # === Свойства ===
    
    def set_property(self, key, value):
        if key in self.properties:
            self.properties[key] = value
            self.update()
            self.trigger('state_change', {'property': key, 'value': value})

    def get_property(self, key):
        return self.properties.get(key)

    def set_properties(self, props):
        changed = False
        for key, value in props.items():
            if key in self.properties:
                self.properties[key] = value
                changed = True
        if changed:
            self.update()
            self.trigger('state_change', {'properties': props})

    def get_properties(self):
        return self.properties.copy()

    # === Вспомогательные методы ===
    
    def _scale(self, value):
        if self.zoom_system and value:
            return self.zoom_system.scale_value(value)
        return value

    def _get_dash_pattern(self):
        style = self.properties.get('line_style', 'solid')
        return self.LINE_STYLES.get(style)

    def _get_corner_radii(self):
        base = self.properties.get('corner_radius', 0)
        return (
            self.properties['corner_tl'] if self.properties.get('corner_tl') is not None else base,
            self.properties['corner_tr'] if self.properties.get('corner_tr') is not None else base,
            self.properties['corner_br'] if self.properties.get('corner_br') is not None else base,
            self.properties['corner_bl'] if self.properties.get('corner_bl') is not None else base,
        )

    # === Рисование форм ===
    
    def _draw_rect(self, x1, y1, x2, y2, **kwargs):
        tags = kwargs.pop('tags', ("element", self.id))
        dash = kwargs.pop('dash', None)
        
        item = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            dash=dash if dash else '',
            tags=tags,
            **kwargs
        )
        self.canvas_items.append(item)
        return item

    def _draw_rounded_rect(self, x1, y1, x2, y2, r_tl, r_tr, r_br, r_bl, **kwargs):
        w, h = x2 - x1, y2 - y1
        max_r = min(w, h) / 2
        r_tl = min(r_tl, max_r)
        r_tr = min(r_tr, max_r)
        r_br = min(r_br, max_r)
        r_bl = min(r_bl, max_r)
        
        points = [
            x1 + r_tl, y1,
            x2 - r_tr, y1,
            x2, y1 if r_tr == 0 else y1,
            x2, y1 + r_tr if r_tr > 0 else y1,
            x2, y2 - r_br,
            x2, y2 if r_br == 0 else y2,
            x2 - r_br if r_br > 0 else x2, y2,
            x1 + r_bl, y2,
            x1, y2 if r_bl == 0 else y2,
            x1, y2 - r_bl if r_bl > 0 else y2,
            x1, y1 + r_tl,
            x1, y1 if r_tl == 0 else y1,
            x1 + r_tl if r_tl > 0 else x1, y1,
        ]

        tags = kwargs.pop('tags', ("element", self.id))
        
        item = self.canvas.create_polygon(
            points, smooth=True, tags=tags, **kwargs
        )
        self.canvas_items.append(item)
        return item

    def _draw_chamfered_rect(self, x1, y1, x2, y2, chamfer, **kwargs):
        w, h = x2 - x1, y2 - y1
        chamfer = min(chamfer, w / 2, h / 2)
        
        points = [
            x1 + chamfer, y1,
            x2 - chamfer, y1,
            x2, y1 + chamfer,
            x2, y2 - chamfer,
            x2 - chamfer, y2,
            x1 + chamfer, y2,
            x1, y2 - chamfer,
            x1, y1 + chamfer,
        ]
        
        tags = kwargs.pop('tags', ("element", self.id))
        
        item = self.canvas.create_polygon(
            points, smooth=False, tags=tags, **kwargs
        )
        self.canvas_items.append(item)
        return item

    def _draw_shape(self, x1, y1, x2, y2, shape, radii, chamfer, **kwargs):
        if shape == 'chamfer':
            return self._draw_chamfered_rect(x1, y1, x2, y2, chamfer, **kwargs)
        elif shape in ('rounded', 'pill') or any(r > 0 for r in radii):
            return self._draw_rounded_rect(x1, y1, x2, y2, *radii, **kwargs)
        else:
            return self._draw_rect(x1, y1, x2, y2, **kwargs)

    # === Сериализация ===
    
    def to_dict(self):
        return {
            'type': self.ELEMENT_TYPE,
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'properties': self.properties.copy(),
            'is_visible': self.is_visible,
            'is_protected': self.is_protected,
            'size_locked': self.size_locked,
            'position_locked': self.position_locked,
            'attached_mechanisms': self.attached_mechanisms.copy(),
            'parent_group': self.parent_group,
            'children': self.children.copy(),
            'is_group': self.is_group,
            'state_switcher_id': self.state_switcher_id,
        }

    def from_dict(self, data):
        self.x = data.get('x', 0)
        self.y = data.get('y', 0)
        self.width = data.get('width', 100)
        self.height = data.get('height', 100)
        self.properties.update(data.get('properties', {}))
        self.is_visible = data.get('is_visible', True)
        self.is_protected = data.get('is_protected', False)
        self.size_locked = data.get('size_locked', False)
        self.position_locked = data.get('position_locked', False)
        self.attached_mechanisms = data.get('attached_mechanisms', [])
        self.parent_group = data.get('parent_group')
        self.children = data.get('children', [])
        self.is_group = data.get('is_group', False)
        self.state_switcher_id = data.get('state_switcher_id')
        self.update()

    # === Копирование ===
    
    def clone(self):
        """Создаёт копию элемента"""
        data = self.to_dict()
        data['id'] = f"{self.ELEMENT_TYPE}_{uuid.uuid4().hex[:8]}"
        data['x'] += 20
        data['y'] += 20
        data['parent_group'] = None
        data['children'] = []
        data['attached_mechanisms'] = []
        return data
