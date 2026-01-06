#!/usr/bin/env python3
"""
Вкладка настроек текста
"""
import tkinter as tk
from tkinter import ttk, colorchooser, font as tkfont
from .tab_base import TabBase


class TabText(TabBase):
    """Вкладка текста"""

    TAB_ID = "text"
    TAB_SYMBOL = "T"

    FONTS = ['Arial', 'Helvetica', 'Times New Roman', 'Courier New', 'Verdana',
             'Georgia', 'Tahoma', 'Trebuchet MS', 'Impact', 'Comic Sans MS']

    def __init__(self, parent, config):
        super().__init__(parent, config)
        self.on_change_callback = None
        self._updating = False
        self.vars = {}

    def set_change_callback(self, callback):
        self.on_change_callback = callback

    def _notify(self):
        if self._updating or not self.on_change_callback:
            return
        self.on_change_callback(self.get_values())

    def _build_content(self):
        self.content = self._scroll_container(self.frame)
        
        # Метка
        self.elem_lbl = tk.Label(self.content, text="Текстовый элемент не выбран",
                                font=("Arial", 10, "bold"),
                                bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT_MUTED, pady=6)
        self.elem_lbl.pack(fill=tk.X, padx=4, pady=4)
        
        # === Текст ===
        sec = self._section(self.content, "Содержимое")
        
        self.vars['text'] = tk.StringVar(value="Текст")
        text_frame = tk.Frame(sec, bg=self.COLOR_BG)
        text_frame.pack(fill=tk.X)
        
        self.text_widget = tk.Text(text_frame, height=3, font=("Arial", 10),
                                   bg=self.COLOR_BG, fg=self.COLOR_TEXT,
                                   insertbackground=self.COLOR_TEXT, relief=tk.FLAT,
                                   wrap=tk.WORD)
        self.text_widget.pack(fill=tk.X, padx=2, pady=2)
        self.text_widget.insert('1.0', 'Текст')
        self.text_widget.bind('<KeyRelease>', lambda e: self._notify())
        
        # === Шрифт ===
        sec = self._section(self.content, "Шрифт")
        
        row = self._row(sec)
        self._label(row, "Семейство:").pack(side=tk.LEFT)
        self.vars['font_family'] = tk.StringVar(value='Arial')
        self.font_combo = self._combo(row, self.FONTS, self.vars['font_family'], 14)
        self.font_combo.pack(side=tk.LEFT)
        self.font_combo.bind('<<ComboboxSelected>>', lambda e: self._notify())
        
        row = self._row(sec)
        self._label(row, "Размер:").pack(side=tk.LEFT)
        self.vars['font_size'] = tk.IntVar(value=14)
        s = self._scale(row, self.vars['font_size'], 8, 72, 100)
        s.config(command=lambda v: self._notify())
        s.pack(side=tk.LEFT)
        tk.Label(row, textvariable=self.vars['font_size'], font=("Arial", 9), width=3,
                bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT).pack(side=tk.LEFT)
        
        # === Стиль ===
        sec = self._section(self.content, "Стиль")
        
        row = self._row(sec)
        self.vars['bold'] = tk.BooleanVar(value=False)
        self.vars['italic'] = tk.BooleanVar(value=False)
        self.vars['underline'] = tk.BooleanVar(value=False)
        self.vars['strikethrough'] = tk.BooleanVar(value=False)
        
        for var, txt in [(self.vars['bold'], 'B'), (self.vars['italic'], 'I'),
                         (self.vars['underline'], 'U'), (self.vars['strikethrough'], 'S')]:
            btn = tk.Checkbutton(row, text=txt, variable=var, font=("Arial", 10, "bold"),
                                bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT,
                                selectcolor=self.COLOR_ACCENT, activebackground=self.COLOR_BG_OVERLAY,
                                indicatoron=False, width=3, command=self._notify)
            btn.pack(side=tk.LEFT, padx=2)
        
        # === Выравнивание ===
        sec = self._section(self.content, "Выравнивание")
        
        row = self._row(sec)
        self._label(row, "Горизонт.:").pack(side=tk.LEFT)
        self.vars['align_h'] = tk.StringVar(value='left')
        for val, txt in [('left', '◧'), ('center', '◫'), ('right', '◨')]:
            tk.Radiobutton(row, text=txt, variable=self.vars['align_h'], value=val,
                          font=("Arial", 12), bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT,
                          selectcolor=self.COLOR_BG, activebackground=self.COLOR_BG_OVERLAY,
                          indicatoron=False, width=3, command=self._notify).pack(side=tk.LEFT, padx=2)
        
        row = self._row(sec)
        self._label(row, "Вертикал.:").pack(side=tk.LEFT)
        self.vars['align_v'] = tk.StringVar(value='top')
        for val, txt in [('top', '⊤'), ('middle', '⊡'), ('bottom', '⊥')]:
            tk.Radiobutton(row, text=txt, variable=self.vars['align_v'], value=val,
                          font=("Arial", 12), bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT,
                          selectcolor=self.COLOR_BG, activebackground=self.COLOR_BG_OVERLAY,
                          indicatoron=False, width=3, command=self._notify).pack(side=tk.LEFT, padx=2)
        
        # === Цвет ===
        sec = self._section(self.content, "Цвет текста")
        
        row = self._row(sec)
        self._label(row, "Цвет:").pack(side=tk.LEFT)
        self.vars['text_color'] = tk.StringVar(value='#e6edf3')
        self.text_color_btn = self._color_btn(row, self.vars['text_color'])
        self.text_color_btn.pack(side=tk.LEFT, padx=4)
        
        # Быстрые цвета
        quick = tk.Frame(row, bg=self.COLOR_BG_OVERLAY)
        quick.pack(side=tk.LEFT, padx=8)
        for color in ['#ffffff', '#000000', '#e6edf3', '#8d96a0', '#2f81f7', '#238636']:
            b = tk.Button(quick, text="", width=2, height=1, bg=color, relief=tk.FLAT,
                         command=lambda c=color: self._set_text_color(c))
            b.pack(side=tk.LEFT, padx=1)
        
        # === Интервалы ===
        sec = self._section(self.content, "Интервалы")
        
        row = self._row(sec)
        self._label(row, "Межстрочный:").pack(side=tk.LEFT)
        self.vars['line_spacing'] = tk.DoubleVar(value=1.2)
        s = self._scale(row, self.vars['line_spacing'], 0.5, 3.0, 80)
        s.config(resolution=0.1, command=lambda v: self._notify())
        s.pack(side=tk.LEFT)
        
        row = self._row(sec)
        self._label(row, "Межбуквенный:").pack(side=tk.LEFT)
        self.vars['letter_spacing'] = tk.IntVar(value=0)
        s = self._scale(row, self.vars['letter_spacing'], -5, 20, 80)
        s.config(command=lambda v: self._notify())
        s.pack(side=tk.LEFT)
        
        # === Обводка ===
        sec = self._section(self.content, "Обводка текста")
        
        row = self._row(sec)
        self.vars['text_stroke_enabled'] = tk.BooleanVar(value=False)
        cb = self._checkbox(row, "Включить", self.vars['text_stroke_enabled'])
        cb.config(command=self._notify)
        cb.pack(side=tk.LEFT)
        
        self.vars['text_stroke_color'] = tk.StringVar(value='#000000')
        self.stroke_btn = self._color_btn(row, self.vars['text_stroke_color'])
        self.stroke_btn.pack(side=tk.RIGHT)
        
        row = self._row(sec)
        self._label(row, "Толщина:").pack(side=tk.LEFT)
        self.vars['text_stroke_width'] = tk.IntVar(value=1)
        self._scale(row, self.vars['text_stroke_width'], 1, 5, 80).pack(side=tk.LEFT)
        
        # === Тень текста ===
        sec = self._section(self.content, "Тень текста")
        
        row = self._row(sec)
        self.vars['text_shadow_enabled'] = tk.BooleanVar(value=False)
        cb = self._checkbox(row, "Включить", self.vars['text_shadow_enabled'])
        cb.config(command=self._notify)
        cb.pack(side=tk.LEFT)
        
        self.vars['text_shadow_color'] = tk.StringVar(value='#000000')
        self.shadow_btn = self._color_btn(row, self.vars['text_shadow_color'])
        self.shadow_btn.pack(side=tk.RIGHT)
        
        row = self._row(sec)
        self._label(row, "X:", 3).pack(side=tk.LEFT)
        self.vars['text_shadow_x'] = tk.IntVar(value=2)
        self._scale(row, self.vars['text_shadow_x'], -10, 10, 50).pack(side=tk.LEFT)
        
        self._label(row, "Y:", 3).pack(side=tk.LEFT, padx=(4, 0))
        self.vars['text_shadow_y'] = tk.IntVar(value=2)
        self._scale(row, self.vars['text_shadow_y'], -10, 10, 50).pack(side=tk.LEFT)

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
            self._notify()

    def _set_text_color(self, color):
        self.vars['text_color'].set(color)
        self.text_color_btn.config(bg=color, activebackground=color)
        self._notify()

    def get_values(self):
        values = {k: v.get() for k, v in self.vars.items()}
        values['text'] = self.text_widget.get('1.0', 'end-1c')
        return values

    def set_values(self, values):
        self._updating = True
        try:
            for k, v in values.items():
                if k in self.vars:
                    self.vars[k].set(v)
            if 'text' in values:
                self.text_widget.delete('1.0', tk.END)
                self.text_widget.insert('1.0', values['text'])
            # Обновить кнопки цвета
            self.text_color_btn.config(bg=self.vars['text_color'].get())
            self.stroke_btn.config(bg=self.vars['text_stroke_color'].get())
            self.shadow_btn.config(bg=self.vars['text_shadow_color'].get())
        finally:
            self._updating = False

    def update_for_element(self, element):
        """Обновляет панель текста для элемента"""
        if element and hasattr(element, 'ELEMENT_TYPE') and element.ELEMENT_TYPE == 'text':
            self._updating = True
            try:
                props = element.properties
                
                # Загружаем все текстовые свойства
                self.vars['text_size'].set(props.get('font_size', 12))
                self.vars['text_color'].set(props.get('text_color', '#ffffff'))
                
                # Семейство шрифта
                font_family = props.get('font_family', 'Arial')
                self.font_var.set(font_family)
                
                # Стили шрифта
                self.vars['text_bold'].set(props.get('font_weight', 'normal') == 'bold')
                self.vars['text_italic'].set(props.get('font_style', 'normal') == 'italic')
                
                # Выравнивание
                self.vars['text_align'].set(props.get('text_align', 'left'))
                
                # Текст элемента
                text_content = props.get('text', '')
                self.text_widget.delete('1.0', tk.END)
                self.text_widget.insert('1.0', text_content)
                
                # Обновляем кнопки цвета
                self.text_color_btn.config(bg=self.vars['text_color'].get())
                
                print(f"[TabText] Загружены настройки текста")
                
            finally:
                self._updating = False
        else:
            self.clear_element()
    
    def clear_element(self):
        """Очищает панель текста"""
        self._updating = True
        try:
            # Сбрасываем на дефолтные значения
            self.vars['text_size'].set(12)
            self.vars['text_color'].set('#ffffff')
            self.font_var.set('Arial')
            self.vars['text_bold'].set(False)
            self.vars['text_italic'].set(False)
            self.vars['text_align'].set('left')
            
            self.text_widget.delete('1.0', tk.END)
            self.text_widget.insert('1.0', 'Текст элемента')
            
            # Обновляем кнопки
            self.text_color_btn.config(bg='#ffffff')
            
        finally:
            self._updating = False
        
    def update_for_element_OLD(self, element):
        if element and getattr(element, 'ELEMENT_TYPE', '') == 'text':
            self.elem_lbl.config(text=f"T {element.id[:12]}", fg=self.COLOR_ACCENT)
            if hasattr(element, 'text_properties'):
                self.set_values(element.text_properties)
        else:
            self.elem_lbl.config(text="Текстовый элемент не выбран", fg=self.COLOR_TEXT_MUTED)

    def set_element(self, element):
        """Устанавливает текстовый элемент для редактирования"""
        self.update_for_element(element)

    def clear_element(self):
        """Очищает элемент"""
        self.elem_lbl.config(text="Текстовый элемент не выбран", fg=self.COLOR_TEXT_MUTED)
