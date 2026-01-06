#!/usr/bin/env python3
"""
Механизм: Пульсация (Pulse)
Комбинированная анимация масштаба и прозрачности
"""
import math
from .mechanism_base import MechanismBase


class PulseMechanism(MechanismBase):
    """Механизм пульсации элементов"""

    MECHANISM_TYPE = "pulse"
    MECHANISM_SYMBOL = "◉"
    MECHANISM_NAME = "Пульсация"

    def __init__(self, canvas, config):
        super().__init__(canvas, config)
        
        self.width = 70
        self.height = 70
        
        self.properties.update({
            # Масштаб пульсации
            'scale_min': 0.9,            # Минимальный масштаб
            'scale_max': 1.1,            # Максимальный масштаб
            'scale_enabled': True,       # Включить масштабирование
            
            # Прозрачность пульсации
            'opacity_min': 70,           # Минимальная прозрачность
            'opacity_max': 100,          # Максимальная прозрачность
            'opacity_enabled': True,     # Включить изменение прозрачности
            
            # Цвет (для элементов с цветом)
            'color_enabled': False,
            'color_start': '#ffffff',
            'color_end': '#ff0000',
            
            # Скорость и частота
            'frequency': 1.0,            # Пульсаций в секунду
            'phase': 0,                  # Начальная фаза (0-360)
            
            # Форма волны
            'wave_type': 'sine',         # sine, square, triangle, sawtooth
            
            # Поведение
            'loop': True,
            'pulse_count': 0,            # 0 = бесконечно
            'sync_mode': 'together',     # together, alternating, cascade
            
            # Эффекты
            'glow_enabled': False,       # Свечение
            'glow_intensity': 0.5,
            'shadow_pulse': False,       # Пульсация тени
        })
        
        self.element_manager = None
        self._initial_sizes = {}
        self._initial_positions = {}
        self._initial_opacity = {}
        self._current_value = 0.0  # -1 to 1
        self._pulse_counter = 0
        self._time = 0

    def set_element_manager(self, manager):
        self.element_manager = manager

    def draw(self):
        if not self.is_visible:
            return

        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        
        if self.zoom_system:
            sx, sy = self.zoom_system.real_to_screen(cx, cy)
            r = self.zoom_system.scale_value(self.width / 2)
        else:
            sx, sy = cx, cy
            r = self.width / 2
        
        # Цвет состояния
        if self.is_active and not self.is_paused:
            color = "#ff00ff"
        elif self.is_paused:
            color = "#ffaa00"
        else:
            color = "#666666"
        
        # Анимированный размер
        pulse_scale = 1 + self._current_value * 0.2 if self.is_active else 1
        animated_r = r * pulse_scale
        
        # 1. Внешний круг (пунктир)
        outer = self.canvas.create_oval(
            sx - r, sy - r, sx + r, sy + r,
            outline=color, width=1, dash=(4, 4),
            tags=("mechanism", self.id, "outer")
        )
        self.canvas_items.append(outer)
        
        # 2. Внутренний круг (пульсирующий)
        # Прозрачность через цвет
        alpha = int(128 + 127 * self._current_value) if self.is_active else 128
        inner_color = f"#{alpha:02x}{alpha:02x}{alpha:02x}"
        
        inner = self.canvas.create_oval(
            sx - animated_r * 0.6, sy - animated_r * 0.6,
            sx + animated_r * 0.6, sy + animated_r * 0.6,
            fill=inner_color, outline=color, width=2,
            tags=("mechanism", self.id, "inner")
        )
        self.canvas_items.append(inner)
        
        # 3. Кольца пульсации
        for i, ring_r in enumerate([0.3, 0.5, 0.7]):
            ring_scale = ring_r + self._current_value * 0.1 * (i + 1) if self.is_active else ring_r
            ring = self.canvas.create_oval(
                sx - r * ring_scale, sy - r * ring_scale,
                sx + r * ring_scale, sy + r * ring_scale,
                outline=color, width=1,
                tags=("mechanism", self.id, f"ring_{i}")
            )
            self.canvas_items.append(ring)
        
        # 4. Центральная точка
        center = self.canvas.create_oval(
            sx - 5, sy - 5, sx + 5, sy + 5,
            fill=color, outline="#ffffff", width=1,
            tags=("mechanism", self.id, "center")
        )
        self.canvas_items.append(center)
        
        # 5. Волновой индикатор
        wave_type = self.properties.get('wave_type', 'sine')
        wave_symbols = {'sine': '∿', 'square': '⊓', 'triangle': '△', 'sawtooth': '⋀'}
        wave_sym = wave_symbols.get(wave_type, '∿')
        
        wave = self.canvas.create_text(
            sx, sy + r + 15,
            text=wave_sym,
            fill="#888888",
            font=("Arial", 12),
            tags=("mechanism", self.id, "wave")
        )
        self.canvas_items.append(wave)
        
        # 6. Название
        name = self.canvas.create_text(
            sx, sy + r + 30,
            text=f"{self.MECHANISM_SYMBOL} {self.MECHANISM_NAME}",
            fill="#666666",
            font=("Arial", 8),
            tags=("mechanism", self.id, "name")
        )
        self.canvas_items.append(name)
        
        # 7. Частота
        freq = self.canvas.create_text(
            sx, sy + r + 42,
            text=f"{self.properties.get('frequency', 1.0):.1f} Hz",
            fill="#888888",
            font=("Arial", 8),
            tags=("mechanism", self.id, "freq")
        )
        self.canvas_items.append(freq)
        
        # 8. Индикатор элементов
        if self.attached_elements:
            attach = self.canvas.create_text(
                sx, sy - r - 12,
                text=f"📎 {len(self.attached_elements)}",
                fill="#aaaaaa",
                font=("Arial", 9),
                tags=("mechanism", self.id, "attach")
            )
            self.canvas_items.append(attach)

    def attach_element(self, element_id):
        if element_id not in self.attached_elements:
            self.attached_elements.append(element_id)
            
            if self.element_manager:
                element = self.element_manager.get_element_by_id(element_id)
                if element:
                    self._initial_sizes[element_id] = (element.width, element.height)
                    self._initial_positions[element_id] = (element.x, element.y)
                    if hasattr(element, 'properties'):
                        self._initial_opacity[element_id] = element.properties.get('opacity', 100)
            
            self.update()

    def detach_element(self, element_id):
        if element_id in self.attached_elements:
            self.attached_elements.remove(element_id)
            
            if self.element_manager:
                element = self.element_manager.get_element_by_id(element_id)
                if element:
                    # Восстанавливаем размер
                    if element_id in self._initial_sizes:
                        w, h = self._initial_sizes[element_id]
                        element.width = w
                        element.height = h
                    
                    # Восстанавливаем позицию
                    if element_id in self._initial_positions:
                        x, y = self._initial_positions[element_id]
                        element.move_to(x, y)
                    
                    # Восстанавливаем прозрачность
                    if element_id in self._initial_opacity and hasattr(element, 'properties'):
                        element.properties['opacity'] = self._initial_opacity[element_id]
                    
                    element.update()
            
            for d in [self._initial_sizes, self._initial_positions, self._initial_opacity]:
                if element_id in d:
                    del d[element_id]
            
            self.update()

    def _get_wave_value(self, t):
        """Возвращает значение волны (-1 to 1)"""
        wave_type = self.properties.get('wave_type', 'sine')
        phase = math.radians(self.properties.get('phase', 0))
        
        # Нормализованное время (0-1 для одного цикла)
        normalized = (t + phase / (2 * math.pi)) % 1
        
        if wave_type == 'sine':
            return math.sin(normalized * 2 * math.pi)
        
        elif wave_type == 'square':
            return 1 if normalized < 0.5 else -1
        
        elif wave_type == 'triangle':
            if normalized < 0.25:
                return normalized * 4
            elif normalized < 0.75:
                return 1 - (normalized - 0.25) * 4
            else:
                return -1 + (normalized - 0.75) * 4
        
        elif wave_type == 'sawtooth':
            return 2 * normalized - 1
        
        return math.sin(normalized * 2 * math.pi)

    def _run_animation(self):
        if not self.is_active or self.is_paused:
            return
        
        frequency = self.properties.get('frequency', 1.0)
        frame_time = 1 / 60
        
        self._time += frame_time
        
        # Вычисляем значение волны
        self._current_value = self._get_wave_value(self._time * frequency)
        
        # Считаем пульсации
        pulse_count = self.properties.get('pulse_count', 0)
        if pulse_count > 0:
            completed_pulses = int(self._time * frequency)
            if completed_pulses >= pulse_count:
                self.is_active = False
                self._current_value = 0
                self._update_attached_positions()
                self.update()
                return
        
        # Обновляем элементы
        self._update_attached_positions()
        
        self.update()
        self._animation_id = self.canvas.after(16, self._run_animation)

    def _update_attached_positions(self):
        if not self.element_manager:
            return
        
        scale_enabled = self.properties.get('scale_enabled', True)
        opacity_enabled = self.properties.get('opacity_enabled', True)
        
        scale_min = self.properties.get('scale_min', 0.9)
        scale_max = self.properties.get('scale_max', 1.1)
        opacity_min = self.properties.get('opacity_min', 70)
        opacity_max = self.properties.get('opacity_max', 100)
        
        # Преобразуем -1..1 в 0..1
        t = (self._current_value + 1) / 2
        
        for i, element_id in enumerate(self.attached_elements):
            element = self.element_manager.get_element_by_id(element_id)
            if not element:
                continue
            
            # Сдвиг фазы для каскадного режима
            sync_mode = self.properties.get('sync_mode', 'together')
            if sync_mode == 'alternating':
                t_elem = 1 - t if i % 2 else t
            elif sync_mode == 'cascade':
                phase_offset = i * 0.2
                t_elem = (t + phase_offset) % 1
            else:
                t_elem = t
            
            # Масштаб
            if scale_enabled and element_id in self._initial_sizes:
                current_scale = scale_min + (scale_max - scale_min) * t_elem
                init_w, init_h = self._initial_sizes[element_id]
                
                new_w = init_w * current_scale
                new_h = init_h * current_scale
                
                # Центрирование
                if element_id in self._initial_positions:
                    init_x, init_y = self._initial_positions[element_id]
                    new_x = init_x - (new_w - init_w) / 2
                    new_y = init_y - (new_h - init_h) / 2
                    element.move_to(new_x, new_y)
                
                element.width = new_w
                element.height = new_h
            
            # Прозрачность
            if opacity_enabled and hasattr(element, 'properties'):
                current_opacity = opacity_min + (opacity_max - opacity_min) * t_elem
                element.properties['opacity'] = int(current_opacity)
            
            element.update()

    def start(self):
        self._time = 0
        self._current_value = 0
        self._pulse_counter = 0
        super().start()

    def stop(self):
        self._current_value = 0
        self._time = 0
        super().stop()

