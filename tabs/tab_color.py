#!/usr/bin/env python3
"""
Вкладка настроек цвета и визуальных эффектов
"""
import tkinter as tk
from tkinter import colorchooser
from .tab_base import TabBase


class TabColor(TabBase):
    """Вкладка цвета"""

    TAB_ID = "color"
    TAB_SYMBOL = "◉"

    PALETTE = [
        '#ffffff', '#000000', '#e6edf3', '#8d96a0', '#2f81f7', '#238636',
        '#da3633', '#9e6a03', '#161b22', '#0d1117', '#21262d', '#30363d',
        '#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff',
        '#ff8800', '#88ff00', '#0088ff', '#ff0088', '#8800ff', '#00ff88',
    ]

    def __init__(self, parent, config):
        super().__init__(parent, config)
        self.on_change_callback = None
        self._updating = False
        self.vars = {}
        self.is_main_canvas_mode = False  # Режим настройки главной панели
        self.current_element = None       # Текущий выбранный элемент

    def set_change_callback(self, callback):
        self.on_change_callback = callback

    def _notify(self):
        if self._updating or not self.on_change_callback:
            return
        self.on_change_callback(self.get_values())

    def _build_content(self):
        self.content = self._scroll_container(self.frame)
        
        # Метка элемента
        self.elem_lbl = tk.Label(self.content, text="Элемент не выбран",
                                font=("Arial", 10, "bold"),
                                bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT_MUTED, pady=6)
        self.elem_lbl.pack(fill=tk.X, padx=4, pady=4)
        
        # === Заливка ===
        sec = self._section(self.content, "Заливка")
        
        row = self._row(sec)
        self._label(row, "Цвет:").pack(side=tk.LEFT)
        self.vars['fill_color'] = tk.StringVar(value='#161b22')
        self.fill_btn = self._color_btn(row, self.vars['fill_color'])
        self.fill_btn.pack(side=tk.LEFT, padx=4)
        
        self.vars['fill_enabled'] = tk.BooleanVar(value=True)
        cb = self._checkbox(row, "Вкл", self.vars['fill_enabled'])
        cb.config(command=self._notify)
        cb.pack(side=tk.LEFT, padx=8)
        
        # === Обводка ===
        sec = self._section(self.content, "Обводка")
        
        row = self._row(sec)
        self._label(row, "Цвет:").pack(side=tk.LEFT)
        self.vars['stroke_color'] = tk.StringVar(value='#30363d')
        self.stroke_btn = self._color_btn(row, self.vars['stroke_color'])
        self.stroke_btn.pack(side=tk.LEFT, padx=4)
        
        self.vars['stroke_enabled'] = tk.BooleanVar(value=True)
        cb = self._checkbox(row, "Вкл", self.vars['stroke_enabled'])
        cb.config(command=self._notify)
        cb.pack(side=tk.LEFT, padx=8)
        
        row = self._row(sec)
        self._label(row, "Толщина:").pack(side=tk.LEFT)
        self.vars['stroke_width'] = tk.IntVar(value=1)
        s = self._scale(row, self.vars['stroke_width'], 0, 20, 100)
        s.config(command=lambda v: self._notify())
        s.pack(side=tk.LEFT)
        tk.Label(row, textvariable=self.vars['stroke_width'], font=("Arial", 9), width=3,
                bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT).pack(side=tk.LEFT)
        
        # Стиль линии
        row = self._row(sec)
        self._label(row, "Стиль:").pack(side=tk.LEFT)
        self.vars['stroke_style'] = tk.StringVar(value='solid')
        for val, txt in [('solid', '—'), ('dashed', '- -'), ('dotted', '···')]:
            rb = tk.Radiobutton(row, text=txt, variable=self.vars['stroke_style'], value=val,
                               font=("Arial", 9), bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT,
                               selectcolor=self.COLOR_BG, activebackground=self.COLOR_BG_OVERLAY,
                               command=self._notify)
            rb.pack(side=tk.LEFT, padx=3)
        
        # === Углы ===
        sec = self._section(self.content, "Скругление")
        
        row = self._row(sec)
        self._label(row, "Радиус:").pack(side=tk.LEFT)
        self.vars['corner_radius'] = tk.IntVar(value=0)
        s = self._scale(row, self.vars['corner_radius'], 0, 50, 100)
        s.config(command=lambda v: self._notify())
        s.pack(side=tk.LEFT)
        tk.Label(row, textvariable=self.vars['corner_radius'], font=("Arial", 9), width=3,
                bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT).pack(side=tk.LEFT)
        
        # === Тень ===
        sec = self._section(self.content, "Тень")
        
        row = self._row(sec)
        self.vars['shadow_enabled'] = tk.BooleanVar(value=False)
        cb = self._checkbox(row, "Включить", self.vars['shadow_enabled'])
        cb.config(command=self._notify)
        cb.pack(side=tk.LEFT)
        
        self.vars['shadow_color'] = tk.StringVar(value='#000000')
        self.shadow_btn = self._color_btn(row, self.vars['shadow_color'])
        self.shadow_btn.pack(side=tk.RIGHT)
        
        row = self._row(sec)
        self._label(row, "X:", 3).pack(side=tk.LEFT)
        self.vars['shadow_x'] = tk.IntVar(value=4)
        self._scale(row, self.vars['shadow_x'], -20, 20, 60).pack(side=tk.LEFT)
        
        self._label(row, "Y:", 3).pack(side=tk.LEFT, padx=(8, 0))
        self.vars['shadow_y'] = tk.IntVar(value=4)
        self._scale(row, self.vars['shadow_y'], -20, 20, 60).pack(side=tk.LEFT)
        
        row = self._row(sec)
        self._label(row, "Blur:", 5).pack(side=tk.LEFT)
        self.vars['shadow_blur'] = tk.IntVar(value=8)
        self._scale(row, self.vars['shadow_blur'], 0, 30, 60).pack(side=tk.LEFT)
        
        self._label(row, "Alpha:", 5).pack(side=tk.LEFT, padx=(8, 0))
        self.vars['shadow_opacity'] = tk.IntVar(value=50)
        self._scale(row, self.vars['shadow_opacity'], 0, 100, 60).pack(side=tk.LEFT)
        
        # === Свечение ===
        sec = self._section(self.content, "Свечение")
        
        row = self._row(sec)
        self.vars['glow_enabled'] = tk.BooleanVar(value=False)
        cb = self._checkbox(row, "Включить", self.vars['glow_enabled'])
        cb.config(command=self._notify)
        cb.pack(side=tk.LEFT)
        
        self.vars['glow_color'] = tk.StringVar(value='#2f81f7')
        self.glow_btn = self._color_btn(row, self.vars['glow_color'])
        self.glow_btn.pack(side=tk.RIGHT)
        
        row = self._row(sec)
        self._label(row, "Размер:", 7).pack(side=tk.LEFT)
        self.vars['glow_size'] = tk.IntVar(value=10)
        self._scale(row, self.vars['glow_size'], 0, 30, 80).pack(side=tk.LEFT)
        
        self._label(row, "Сила:", 5).pack(side=tk.LEFT, padx=(8, 0))
        self.vars['glow_intensity'] = tk.IntVar(value=50)
        self._scale(row, self.vars['glow_intensity'], 0, 100, 60).pack(side=tk.LEFT)
        
        # === Прозрачность ===
        sec = self._section(self.content, "Прозрачность")
        
        row = self._row(sec)
        self._label(row, "Общая:").pack(side=tk.LEFT)
        self.vars['opacity'] = tk.IntVar(value=100)
        s = self._scale(row, self.vars['opacity'], 0, 100, 120)
        s.config(command=lambda v: self._notify())
        s.pack(side=tk.LEFT)
        tk.Label(row, textvariable=self.vars['opacity'], font=("Arial", 9), width=4,
                bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT).pack(side=tk.LEFT)
        tk.Label(row, text="%", font=("Arial", 9),
                bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT_MUTED).pack(side=tk.LEFT)
        
        # === Палитра ===
        sec = self._section(self.content, "Быстрые цвета")
        
        grid = tk.Frame(sec, bg=self.COLOR_BG_OVERLAY)
        grid.pack(fill=tk.X, pady=4)
        
        for i, color in enumerate(self.PALETTE):
            btn = tk.Button(grid, text="", width=2, height=1, bg=color, relief=tk.FLAT,
                           activebackground=color, cursor="hand2",
                           command=lambda c=color: self._apply_color(c))
            btn.grid(row=i//6, column=i%6, padx=1, pady=1)
        
        row = self._row(sec)
        self.vars['palette_target'] = tk.StringVar(value='fill')
        tk.Label(row, text="Применить:", font=("Arial", 9),
                bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT_MUTED).pack(side=tk.LEFT)
        for val, txt in [('fill', 'Заливка'), ('stroke', 'Обводка')]:
            tk.Radiobutton(row, text=txt, variable=self.vars['palette_target'], value=val,
                          font=("Arial", 9), bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT,
                          selectcolor=self.COLOR_BG, activebackground=self.COLOR_BG_OVERLAY
                          ).pack(side=tk.LEFT, padx=4)

    def _color_btn(self, parent, var):
        """Кнопка выбора цвета"""
        btn = tk.Button(parent, text="", width=4, bg=var.get(), relief=tk.FLAT,
                       activebackground=var.get(), cursor="hand2")
        btn.config(command=lambda: self._pick_color(var, btn))
        return btn

    def _pick_color(self, var, btn):
        """Выбор цвета"""
        color = colorchooser.askcolor(color=var.get(), title="Выберите цвет")[1]
        if color:
            var.set(color)
            btn.config(bg=color, activebackground=color)
            self._notify()

    def _apply_color(self, color):
        """Применить цвет из палитры"""
        target = self.vars.get('palette_target')
        if target:
            key = f"{target.get()}_color"
            if key in self.vars:
                self.vars[key].set(color)
                if key == 'fill_color':
                    self.fill_btn.config(bg=color, activebackground=color)
                elif key == 'stroke_color':
                    self.stroke_btn.config(bg=color, activebackground=color)
                self._notify()

    def get_values(self):
        """Получить все значения"""
        return {k: v.get() for k, v in self.vars.items()}

    def set_values(self, values):
        """Установить значения"""
        self._updating = True
        try:
            for k, v in values.items():
                if k in self.vars:
                    self.vars[k].set(v)
            # Обновить кнопки цвета
            self.fill_btn.config(bg=self.vars['fill_color'].get(),
                               activebackground=self.vars['fill_color'].get())
            self.stroke_btn.config(bg=self.vars['stroke_color'].get(),
                                 activebackground=self.vars['stroke_color'].get())
            self.shadow_btn.config(bg=self.vars['shadow_color'].get(),
                                 activebackground=self.vars['shadow_color'].get())
            self.glow_btn.config(bg=self.vars['glow_color'].get(),
                               activebackground=self.vars['glow_color'].get())
        finally:
            self._updating = False

    def update_for_element(self, element):
        """Обновить для элемента"""
        self.current_element = element
        self.is_main_canvas_mode = False
        
        if element:
            sym = getattr(element, 'ELEMENT_SYMBOL', '●')
            etype = getattr(element, 'ELEMENT_TYPE', 'element')
            self.elem_lbl.config(text=f"{sym} {etype}", fg=self.COLOR_ACCENT)
            if hasattr(element, 'properties'):
                self.set_values(element.properties)
        else:
            self.elem_lbl.config(text="Элемент не выбран", fg=self.COLOR_TEXT_MUTED)

    def update_for_main_canvas(self, main_canvas):
        """Обновить для главной панели"""
        self.current_element = None
        self.is_main_canvas_mode = True
        
        self.elem_lbl.config(text="● Главная панель", fg=self.COLOR_ACCENT)
        if hasattr(main_canvas, 'properties'):
            self.set_values(main_canvas.properties)

    def set_element_type(self, element_type, is_main_canvas=False):
        """Устанавливает тип элемента"""
        self.is_main_canvas_mode = is_main_canvas
        
        if is_main_canvas:
            self.elem_lbl.config(text="● Главная панель", fg=self.COLOR_ACCENT)
        elif element_type:
            self.elem_lbl.config(text=f"● {element_type}", fg=self.COLOR_ACCENT) 
        else:
            self.elem_lbl.config(text="Элемент не выбран", fg=self.COLOR_TEXT_MUTED)
    
    def clear_element(self):
        """Очищает выбранный элемент"""
        self.current_element = None
        self.is_main_canvas_mode = False
        self.elem_lbl.config(text="Элемент не выбран", fg=self.COLOR_TEXT_MUTED)

    def set_element(self, element):
        """Устанавливает элемент для редактирования"""
        self.update_for_element(element)
