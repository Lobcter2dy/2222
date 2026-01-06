#!/usr/bin/env python3
"""
Механизм: Рельсы/Трек перемещения (MoveTrack)
Позволяет перемещать прикреплённые элементы по заданной траектории
"""
from .mechanism_base import MechanismBase
import math


class MoveTrackMechanism(MechanismBase):
    """Рельсы - механизм линейного перемещения"""

    MECHANISM_TYPE = "move_track"
    MECHANISM_SYMBOL = "⟷"
    MECHANISM_NAME = "Рельсы"

    def __init__(self, canvas, config):
        super().__init__(canvas, config)
        
        # Размеры по умолчанию
        self.width = 200
        self.height = 10
        
        # Дополнительные свойства для трека
        self.properties.update({
            'direction': 'horizontal',   # horizontal, vertical, custom
            'start_x': 0,                # Начальная точка X (относительно)
            'start_y': 0,                # Начальная точка Y
            'end_x': 200,                # Конечная точка X
            'end_y': 0,                  # Конечная точка Y
            'speed': 100,                # Пикселей в секунду
            'loop': False,               # Зацикливание
            'reverse_on_end': True,      # Движение туда-обратно
            'easing': 'linear',          # linear, ease_in, ease_out, ease_in_out
        })
        
        # Ссылка на element_manager для обновления элементов
        self.element_manager = None
        
        # Начальные позиции прикреплённых элементов
        self._initial_positions = {}  # element_id -> (x, y)

    def set_element_manager(self, manager):
        """Устанавливает менеджер элементов"""
        self.element_manager = manager

    def draw(self):
        """Рисует трек на холсте"""
        if not self.is_visible:
            return

        x1, y1, x2, y2 = self.get_screen_bounds()
        
        # Получаем точки трека
        start_x = self.x + self.properties['start_x']
        start_y = self.y + self.properties['start_y']
        end_x = self.x + self.properties['end_x']
        end_y = self.y + self.properties['end_y']
        
        # Преобразуем в экранные координаты
        if self.zoom_system:
            sx1, sy1 = self.zoom_system.real_to_screen(start_x, start_y)
            sx2, sy2 = self.zoom_system.real_to_screen(end_x, end_y)
        else:
            sx1, sy1 = start_x, start_y
            sx2, sy2 = end_x, end_y
        
        # Цвет в зависимости от состояния
        if self.is_active and not self.is_paused:
            track_color = "#00ff00"  # Зелёный - активен
        elif self.is_paused:
            track_color = "#ffaa00"  # Оранжевый - пауза
        else:
            track_color = "#666666"  # Серый - неактивен
        
        # 1. Линия трека (пунктир)
        track_line = self.canvas.create_line(
            sx1, sy1, sx2, sy2,
            fill=track_color,
            width=3,
            dash=(8, 4),
            tags=("mechanism", self.id, "track_line")
        )
        self.canvas_items.append(track_line)
        
        # 2. Начальная точка (круг)
        r = 8
        start_point = self.canvas.create_oval(
            sx1 - r, sy1 - r, sx1 + r, sy1 + r,
            fill="#00aa00",
            outline="#ffffff",
            width=2,
            tags=("mechanism", self.id, "start_point")
        )
        self.canvas_items.append(start_point)
        
        # 3. Конечная точка (квадрат)
        end_point = self.canvas.create_rectangle(
            sx2 - r, sy2 - r, sx2 + r, sy2 + r,
            fill="#aa0000",
            outline="#ffffff",
            width=2,
            tags=("mechanism", self.id, "end_point")
        )
        self.canvas_items.append(end_point)
        
        # 4. Точка закрепа (anchor) - в начальной позиции
        anchor_x = sx1 + (sx2 - sx1) * self._animation_progress
        anchor_y = sy1 + (sy2 - sy1) * self._animation_progress
        
        anchor_size = 6
        anchor_point = self.canvas.create_oval(
            anchor_x - anchor_size, anchor_y - anchor_size,
            anchor_x + anchor_size, anchor_y + anchor_size,
            fill="#ffff00",
            outline="#000000",
            width=1,
            tags=("mechanism", self.id, "anchor")
        )
        self.canvas_items.append(anchor_point)
        
        # 5. Индикаторы прикреплённых элементов
        if self.attached_elements:
            attach_label = self.canvas.create_text(
                (sx1 + sx2) / 2, min(sy1, sy2) - 15,
                text=f"📎 {len(self.attached_elements)}",
                fill="#aaaaaa",
                font=("Arial", 9),
                anchor="center",
                tags=("mechanism", self.id, "attach_count")
            )
            self.canvas_items.append(attach_label)
        
        # 6. Метка типа механизма
        label = self.canvas.create_text(
            (sx1 + sx2) / 2, max(sy1, sy2) + 15,
            text=f"{self.MECHANISM_SYMBOL} {self.MECHANISM_NAME}",
            fill="#888888",
            font=("Arial", 8),
            anchor="center",
            tags=("mechanism", self.id, "label")
        )
        self.canvas_items.append(label)

    def attach_element(self, element_id):
        """Прикрепляет элемент и сохраняет его начальную позицию"""
        if element_id not in self.attached_elements:
            self.attached_elements.append(element_id)
            
            # Сохраняем начальную позицию элемента
            if self.element_manager:
                element = self.element_manager.get_element_by_id(element_id)
                if element:
                    self._initial_positions[element_id] = (element.x, element.y)
            
            self.update()

    def detach_element(self, element_id):
        """Открепляет элемент и возвращает его в начальную позицию"""
        if element_id in self.attached_elements:
            self.attached_elements.remove(element_id)
            
            # Возвращаем элемент в начальную позицию
            if element_id in self._initial_positions:
                if self.element_manager:
                    element = self.element_manager.get_element_by_id(element_id)
                    if element:
                        init_x, init_y = self._initial_positions[element_id]
                        element.move_to(init_x, init_y)
                del self._initial_positions[element_id]
            
            self.update()

    def _run_animation(self):
        """Основной цикл анимации"""
        if not self.is_active or self.is_paused:
            return
        
        # Вычисляем шаг анимации
        speed = self.properties.get('speed', 100)
        
        # Длина трека
        dx = self.properties['end_x'] - self.properties['start_x']
        dy = self.properties['end_y'] - self.properties['start_y']
        track_length = math.sqrt(dx * dx + dy * dy)
        
        if track_length == 0:
            return
        
        # Шаг прогресса за кадр (60 FPS)
        frame_time = 1 / 60
        step = (speed * frame_time) / track_length
        
        # Обновляем прогресс
        self._animation_progress += step * self._animation_direction
        
        # Проверяем границы
        if self._animation_progress >= 1.0:
            self._animation_progress = 1.0
            if self.properties.get('reverse_on_end'):
                self._animation_direction = -1
            elif self.properties.get('loop'):
                self._animation_progress = 0.0
            else:
                self.is_active = False
                return
        elif self._animation_progress <= 0.0:
            self._animation_progress = 0.0
            if self.properties.get('loop') or self.properties.get('reverse_on_end'):
                self._animation_direction = 1
            else:
                self.is_active = False
                return
        
        # Применяем easing
        eased_progress = self._apply_easing(self._animation_progress)
        
        # Обновляем позиции прикреплённых элементов
        self._update_attached_positions(eased_progress)
        
        # Перерисовываем механизм
        self.update()
        
        # Следующий кадр
        self._animation_id = self.canvas.after(16, self._run_animation)  # ~60 FPS

    def _apply_easing(self, t):
        """Применяет функцию плавности"""
        easing = self.properties.get('easing', 'linear')
        
        if easing == 'linear':
            return t
        elif easing == 'ease_in':
            return t * t
        elif easing == 'ease_out':
            return 1 - (1 - t) * (1 - t)
        elif easing == 'ease_in_out':
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - 2 * (1 - t) * (1 - t)
        elif easing == 'ease_in_cubic':
            return t * t * t
        elif easing == 'ease_out_cubic':
            return 1 - (1 - t) ** 3
        elif easing == 'ease_in_out_cubic':
            if t < 0.5:
                return 4 * t * t * t
            else:
                return 1 - (-2 * t + 2) ** 3 / 2
        elif easing == 'bounce':
            if t < 1/2.75:
                return 7.5625 * t * t
            elif t < 2/2.75:
                t -= 1.5/2.75
                return 7.5625 * t * t + 0.75
            elif t < 2.5/2.75:
                t -= 2.25/2.75
                return 7.5625 * t * t + 0.9375
            else:
                t -= 2.625/2.75
                return 7.5625 * t * t + 0.984375
        elif easing == 'elastic':
            if t == 0 or t == 1:
                return t
            return math.pow(2, -10 * t) * math.sin((t - 0.1) * 5 * math.pi) + 1
        elif easing == 'back':
            c1 = 1.70158
            c3 = c1 + 1
            return c3 * t * t * t - c1 * t * t
        
        return t

    def _update_attached_positions(self, progress=None):
        """Обновляет позиции прикреплённых элементов"""
        if not self.element_manager:
            return
        
        if progress is None:
            progress = self._animation_progress
        
        # Вычисляем смещение от начальной точки
        dx = self.properties['end_x'] - self.properties['start_x']
        dy = self.properties['end_y'] - self.properties['start_y']
        
        offset_x = dx * progress
        offset_y = dy * progress
        
        # Обновляем каждый прикреплённый элемент
        for element_id in self.attached_elements:
            if element_id in self._initial_positions:
                init_x, init_y = self._initial_positions[element_id]
                
                element = self.element_manager.get_element_by_id(element_id)
                if element:
                    new_x = init_x + offset_x
                    new_y = init_y + offset_y
                    element.move_to(new_x, new_y)

    def get_anchor_point(self):
        """Возвращает текущую позицию точки закрепа"""
        start_x = self.x + self.properties['start_x']
        start_y = self.y + self.properties['start_y']
        end_x = self.x + self.properties['end_x']
        end_y = self.y + self.properties['end_y']
        
        current_x = start_x + (end_x - start_x) * self._animation_progress
        current_y = start_y + (end_y - start_y) * self._animation_progress
        
        return (current_x, current_y)

    def set_track_points(self, start_x, start_y, end_x, end_y):
        """Устанавливает точки трека"""
        self.properties['start_x'] = start_x
        self.properties['start_y'] = start_y
        self.properties['end_x'] = end_x
        self.properties['end_y'] = end_y
        self.update()

    def set_direction(self, direction):
        """Устанавливает направление (horizontal, vertical)"""
        self.properties['direction'] = direction
        
        if direction == 'horizontal':
            self.properties['start_y'] = 0
            self.properties['end_y'] = 0
        elif direction == 'vertical':
            self.properties['start_x'] = 0
            self.properties['end_x'] = 0
        
        self.update()

