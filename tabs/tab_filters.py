#!/usr/bin/env python3
"""
Вкладка фильтров и эффектов
"""
import tkinter as tk
from tkinter import ttk, colorchooser
from .tab_base import TabBase


class TabFilters(TabBase):
    """Вкладка фильтров"""

    TAB_ID = "filters"
    TAB_SYMBOL = "◈"

    PRESETS = [
        ('Нет', {}),
        ('Яркий', {'brightness': 120, 'contrast': 110, 'saturation': 120}),
        ('Мягкий', {'brightness': 105, 'contrast': 95, 'saturation': 90}),
        ('Тёплый', {'temperature': 30, 'brightness': 105}),
        ('Холодный', {'temperature': -30, 'brightness': 105}),
        ('Винтаж', {'sepia': 40, 'contrast': 110, 'saturation': 80}),
        ('Ч/Б', {'saturation': 0}),
        ('Высокий контраст', {'contrast': 150, 'brightness': 95}),
    ]

    EFFECTS = [
        ('glass', 'Стекло', 'Эффект матового стекла'),
        ('neon', 'Неон', 'Неоновое свечение'),
        ('shadow', 'Тень', 'Объёмная тень'),
        ('glow', 'Свечение', 'Мягкое свечение'),
        ('emboss', 'Тиснение', 'Эффект тиснения'),
        ('blur', 'Размытие', 'Гауссово размытие'),
    ]

    def __init__(self, parent, config):
        super().__init__(parent, config)
        self.element_manager = None
        self.main_canvas = None
        self.app = None
        self.vars = {}

    def set_element_manager(self, manager):
        self.element_manager = manager

    def set_main_canvas(self, canvas):
        self.main_canvas = canvas

    def set_app(self, app):
        self.app = app

    def _build_content(self):
        self.content = self._scroll_container(self.frame)
        
        # === Пресеты ===
        sec = self._section(self.content, "Пресеты фильтров")
        
        grid = tk.Frame(sec, bg=self.COLOR_BG_OVERLAY)
        grid.pack(fill=tk.X)
        
        for i, (name, values) in enumerate(self.PRESETS):
            btn = tk.Button(grid, text=name, font=("Arial", 9),
                           bg=self.COLOR_BG, fg=self.COLOR_TEXT,
                           activebackground=self.COLOR_ACCENT, activeforeground='#fff',
                           relief=tk.FLAT, padx=6, cursor="hand2",
                           command=lambda v=values: self._apply_preset(v))
            btn.grid(row=i//4, column=i%4, padx=2, pady=2, sticky="ew")
        
        for c in range(4):
            grid.columnconfigure(c, weight=1)
        
        # === Ручные настройки ===
        sec = self._section(self.content, "Настройки фильтров")
        
        # Яркость
        row = self._row(sec)
        self._label(row, "Яркость:").pack(side=tk.LEFT)
        self.vars['brightness'] = tk.IntVar(value=100)
        s = self._scale(row, self.vars['brightness'], 50, 150, 100)
        s.pack(side=tk.LEFT)
        tk.Label(row, textvariable=self.vars['brightness'], font=("Arial", 9), width=4,
                bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT).pack(side=tk.LEFT)
        
        # Контраст
        row = self._row(sec)
        self._label(row, "Контраст:").pack(side=tk.LEFT)
        self.vars['contrast'] = tk.IntVar(value=100)
        self._scale(row, self.vars['contrast'], 50, 150, 100).pack(side=tk.LEFT)
        tk.Label(row, textvariable=self.vars['contrast'], font=("Arial", 9), width=4,
                bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT).pack(side=tk.LEFT)
        
        # Насыщенность
        row = self._row(sec)
        self._label(row, "Насыщенность:").pack(side=tk.LEFT)
        self.vars['saturation'] = tk.IntVar(value=100)
        self._scale(row, self.vars['saturation'], 0, 200, 100).pack(side=tk.LEFT)
        tk.Label(row, textvariable=self.vars['saturation'], font=("Arial", 9), width=4,
                bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT).pack(side=tk.LEFT)
        
        # Температура
        row = self._row(sec)
        self._label(row, "Температура:").pack(side=tk.LEFT)
        self.vars['temperature'] = tk.IntVar(value=0)
        self._scale(row, self.vars['temperature'], -50, 50, 100).pack(side=tk.LEFT)
        tk.Label(row, textvariable=self.vars['temperature'], font=("Arial", 9), width=4,
                bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT).pack(side=tk.LEFT)
        
        # Сепия
        row = self._row(sec)
        self._label(row, "Сепия:").pack(side=tk.LEFT)
        self.vars['sepia'] = tk.IntVar(value=0)
        self._scale(row, self.vars['sepia'], 0, 100, 100).pack(side=tk.LEFT)
        tk.Label(row, textvariable=self.vars['sepia'], font=("Arial", 9), width=4,
                bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT).pack(side=tk.LEFT)
        
        # Кнопки
        row = self._row(sec)
        self._button(row, "Применить", self._apply_filters, 'primary').pack(side=tk.LEFT, padx=2)
        self._button(row, "Сбросить", self._reset_filters).pack(side=tk.LEFT, padx=2)
        
        # === Эффекты ===
        sec = self._section(self.content, "Эффекты")
        
        for eid, name, desc in self.EFFECTS:
            row = self._row(sec)
            
            self.vars[f'effect_{eid}'] = tk.BooleanVar(value=False)
            cb = self._checkbox(row, name, self.vars[f'effect_{eid}'])
            cb.pack(side=tk.LEFT)
            
            tk.Label(row, text=f"— {desc}", font=("Arial", 8),
                    bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT_SUBTLE).pack(side=tk.LEFT, padx=8)
        
        row = self._row(sec)
        self._button(row, "Применить эффекты", self._apply_effects, 'primary').pack(side=tk.LEFT)
        
        # === Цветовая схема ===
        sec = self._section(self.content, "Цветовая схема")
        
        row = self._row(sec)
        self._label(row, "Основной:").pack(side=tk.LEFT)
        self.vars['primary_color'] = tk.StringVar(value='#2f81f7')
        self.primary_btn = self._color_btn(row, self.vars['primary_color'])
        self.primary_btn.pack(side=tk.LEFT, padx=4)
        
        row = self._row(sec)
        self._label(row, "Фон:").pack(side=tk.LEFT)
        self.vars['bg_color'] = tk.StringVar(value='#0d1117')
        self.bg_btn = self._color_btn(row, self.vars['bg_color'])
        self.bg_btn.pack(side=tk.LEFT, padx=4)
        
        row = self._row(sec)
        self._label(row, "Текст:").pack(side=tk.LEFT)
        self.vars['text_color'] = tk.StringVar(value='#e6edf3')
        self.text_btn = self._color_btn(row, self.vars['text_color'])
        self.text_btn.pack(side=tk.LEFT, padx=4)
        
        row = self._row(sec)
        self._button(row, "Применить схему", self._apply_scheme, 'primary').pack(side=tk.LEFT)

    def _color_btn(self, parent, var):
        btn = tk.Button(parent, text="", width=4, bg=var.get(), relief=tk.FLAT,
                       activebackground=var.get(), cursor="hand2")
        btn.config(command=lambda: self._pick_color(var, btn))
        return btn

    def _pick_color(self, var, btn):
        color = colorchooser.askcolor(color=var.get(), title="Цвет")[1]
        if color:
            var.set(color)
            btn.config(bg=color, activebackground=color)

    def _apply_preset(self, values):
        # Сбросить
        self.vars['brightness'].set(100)
        self.vars['contrast'].set(100)
        self.vars['saturation'].set(100)
        self.vars['temperature'].set(0)
        self.vars['sepia'].set(0)
        
        # Применить пресет
        for k, v in values.items():
            if k in self.vars:
                self.vars[k].set(v)
        
        self._apply_filters()

    def _apply_filters(self):
        """Применить фильтры к выбранному элементу"""
        if not self.element_manager:
            return
        
        elem = self.element_manager.selected_element
        if elem:
            filters = {
                'brightness': self.vars['brightness'].get(),
                'contrast': self.vars['contrast'].get(),
                'saturation': self.vars['saturation'].get(),
                'temperature': self.vars['temperature'].get(),
                'sepia': self.vars['sepia'].get(),
            }
            if hasattr(elem, 'set_filters'):
                elem.set_filters(filters)
            elif hasattr(elem, 'properties'):
                elem.properties.update(filters)
                elem.update()

    def _reset_filters(self):
        self.vars['brightness'].set(100)
        self.vars['contrast'].set(100)
        self.vars['saturation'].set(100)
        self.vars['temperature'].set(0)
        self.vars['sepia'].set(0)
        self._apply_filters()
    
    def update_for_element(self, element):
        """Обновляет панель фильтров для элемента"""
        if not element or not hasattr(element, 'properties'):
            return
        
        self._updating = True
        try:
            props = element.properties
            
            # Загружаем фильтры
            self.vars['brightness'].set(props.get('brightness', 100))
            self.vars['contrast'].set(props.get('contrast', 100))
            self.vars['saturation'].set(props.get('saturation', 100))
            self.vars['temperature'].set(props.get('temperature', 0))
            self.vars['sepia'].set(props.get('sepia', 0))
            
            # Загружаем цвета
            self.vars['bg_color'].set(props.get('filter_bg_color', '#000000'))
            
            print(f"[TabFilters] Загружены настройки для {element.ELEMENT_TYPE}")
            
        finally:
            self._updating = False
    
    def clear_element(self):
        """Очищает привязку к элементу"""
        self._updating = True
        try:
            # Сбрасываем на дефолтные значения
            self.vars['brightness'].set(100)
            self.vars['contrast'].set(100)
            self.vars['saturation'].set(100)
            self.vars['temperature'].set(0)
            self.vars['sepia'].set(0)
            self.vars['bg_color'].set('#000000')
        finally:
            self._updating = False

    def _apply_effects(self):
        """Применить эффекты"""
        if not self.element_manager:
            return
        
        elem = self.element_manager.selected_element
        if elem:
            effects = []
            for eid, _, _ in self.EFFECTS:
                if self.vars.get(f'effect_{eid}', tk.BooleanVar()).get():
                    effects.append(eid)
            
            if hasattr(elem, 'set_effects'):
                elem.set_effects(effects)
            elif hasattr(elem, 'properties'):
                elem.properties['effects'] = effects
                elem.update()

    def _apply_scheme(self):
        """Применить цветовую схему"""
        if self.main_canvas:
            color = self.vars['bg_color'].get()
            if hasattr(self.main_canvas, 'properties'):
                self.main_canvas.properties['fill_color'] = color
                self.main_canvas.update()
