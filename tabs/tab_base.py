#!/usr/bin/env python3
"""
Базовый класс для вкладок - GitHub Dark стиль
"""
import tkinter as tk
from tkinter import ttk


class TabBase:
    """Базовый класс для всех вкладок"""

    TAB_ID = "base"
    TAB_SYMBOL = "○"

    # GitHub Dark цвета
    COLOR_BG = '#0d1117'
    COLOR_BG_SECONDARY = '#161b22'
    COLOR_BG_OVERLAY = '#21262d'
    COLOR_BORDER = '#30363d'
    COLOR_BORDER_MUTED = '#21262d'
    COLOR_TEXT = '#e6edf3'
    COLOR_TEXT_MUTED = '#8d96a0'
    COLOR_TEXT_SUBTLE = '#6e7681'
    COLOR_ACCENT = '#2f81f7'
    COLOR_SUCCESS = '#238636'
    COLOR_WARNING = '#9e6a03'
    COLOR_DANGER = '#da3633'

    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.frame = None
        self.content = None

    def build(self):
        """Создаёт фрейм вкладки"""
        self.frame = tk.Frame(self.parent, bg=self.COLOR_BG_SECONDARY)
        self._build_content()

    def _build_content(self):
        """Переопределяется в подклассах"""
        pass

    def show(self):
        """Показывает вкладку"""
        if self.frame:
            self.frame.pack(fill=tk.BOTH, expand=True)

    def hide(self):
        """Скрывает вкладку"""
        if self.frame:
            self.frame.pack_forget()

    def on_activate(self):
        """Вызывается при активации вкладки"""
        pass

    def on_deactivate(self):
        """Вызывается при деактивации вкладки"""
        pass

    # === UI Helpers ===

    def _scroll_container(self, parent):
        """Создаёт прокручиваемый контейнер"""
        canvas = tk.Canvas(parent, bg=self.COLOR_BG_SECONDARY, highlightthickness=0)
        content = tk.Frame(canvas, bg=self.COLOR_BG_SECONDARY)
        
        def on_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        content.bind("<Configure>", on_configure)
        
        canvas.create_window((0, 0), window=content, anchor="nw", tags="content")
        canvas.bind('<Configure>', lambda e: canvas.itemconfig("content", width=e.width))
        
        # Скролл мышью
        def scroll(e):
            canvas.yview_scroll(-1 if e.num == 4 or e.delta > 0 else 1, "units")
        canvas.bind('<MouseWheel>', scroll)
        canvas.bind('<Button-4>', scroll)
        canvas.bind('<Button-5>', scroll)
        content.bind('<MouseWheel>', scroll)
        content.bind('<Button-4>', scroll)
        content.bind('<Button-5>', scroll)
        
        canvas.pack(fill=tk.BOTH, expand=True)
        return content

    def _section(self, parent, title):
        """Секция с заголовком"""
        frame = tk.Frame(parent, bg=self.COLOR_BG_OVERLAY)
        frame.pack(fill=tk.X, padx=4, pady=3)
        
        tk.Label(frame, text=title, font=("Arial", 9, "bold"),
                bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT_MUTED
                ).pack(anchor="w", padx=6, pady=(4, 2))
        
        content = tk.Frame(frame, bg=self.COLOR_BG_OVERLAY)
        content.pack(fill=tk.X, padx=6, pady=(0, 6))
        return content

    def _header(self, parent, title):
        """Заголовок секции"""
        tk.Label(parent, text=title, font=("Arial", 9, "bold"),
                bg=self.COLOR_BG_SECONDARY, fg=self.COLOR_TEXT_MUTED, anchor="w"
                ).pack(fill=tk.X, padx=6, pady=(6, 2))

    def _row(self, parent):
        """Строка элементов"""
        row = tk.Frame(parent, bg=self.COLOR_BG_OVERLAY)
        row.pack(fill=tk.X, pady=2)
        return row

    def _label(self, parent, text, width=10):
        """Метка"""
        return tk.Label(parent, text=text, font=("Arial", 9), width=width, anchor="w",
                       bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT_MUTED)

    def _entry(self, parent, var, width=8):
        """Поле ввода"""
        return tk.Entry(parent, textvariable=var, width=width, font=("Arial", 9),
                       bg=self.COLOR_BG, fg=self.COLOR_TEXT, relief=tk.FLAT,
                       insertbackground=self.COLOR_TEXT,
                       highlightthickness=1, highlightbackground=self.COLOR_BORDER)

    def _button(self, parent, text, command, style='default'):
        """Кнопка"""
        colors = {
            'default': (self.COLOR_BG_OVERLAY, self.COLOR_TEXT, self.COLOR_BORDER),
            'primary': (self.COLOR_ACCENT, '#fff', '#58a6ff'),
            'success': (self.COLOR_SUCCESS, '#fff', '#2ea043'),
            'danger': (self.COLOR_DANGER, '#fff', '#f85149'),
            'warning': (self.COLOR_WARNING, '#fff', '#bb8009'),
        }
        bg, fg, active = colors.get(style, colors['default'])
        
        return tk.Button(parent, text=text, font=("Arial", 9),
                        bg=bg, fg=fg, activebackground=active, activeforeground=fg,
                        relief=tk.FLAT, cursor="hand2", padx=8, pady=2, command=command)

    def _icon_button(self, parent, text, command, color=None):
        """Кнопка-иконка"""
        fg = color or self.COLOR_TEXT_MUTED
        return tk.Button(parent, text=text, font=("Arial", 10),
                        bg=self.COLOR_BG, fg=fg,
                        activebackground=self.COLOR_BORDER, activeforeground=self.COLOR_TEXT,
                        relief=tk.FLAT, width=3, cursor="hand2", command=command)

    def _checkbox(self, parent, text, var):
        """Чекбокс"""
        return tk.Checkbutton(parent, text=text, variable=var, font=("Arial", 9),
                             bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT,
                             selectcolor=self.COLOR_BG, activebackground=self.COLOR_BG_OVERLAY,
                             command=lambda: None)

    def _scale(self, parent, var, from_, to, length=100):
        """Слайдер"""
        return tk.Scale(parent, variable=var, from_=from_, to=to, orient=tk.HORIZONTAL,
                       length=length, showvalue=False, sliderlength=14, width=12,
                       bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT,
                       troughcolor=self.COLOR_BG, activebackground=self.COLOR_ACCENT,
                       highlightthickness=0)

    def _combo(self, parent, values, var=None, width=12):
        """Выпадающий список"""
        combo = ttk.Combobox(parent, values=values, state="readonly",
                            width=width, font=("Arial", 9))
        if var:
            combo.config(textvariable=var)
        if values:
            combo.current(0)
        return combo

    def _tree(self, parent, columns, height=8):
        """Treeview список"""
        tree = ttk.Treeview(parent, columns=columns, show='headings',
                           height=height, selectmode='browse')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=60, anchor='center')
        
        # Скролл
        tree.bind('<Button-4>', lambda e: tree.yview_scroll(-2, 'units'))
        tree.bind('<Button-5>', lambda e: tree.yview_scroll(2, 'units'))
        return tree

    def _separator(self, parent):
        """Разделитель"""
        tk.Frame(parent, bg=self.COLOR_BORDER, height=1).pack(fill=tk.X, padx=4, pady=4)

    def _tooltip(self, widget, text):
        """Подсказка при наведении"""
        tip = [None]
        
        def show(e):
            if tip[0] or not widget.winfo_exists():
                return
            try:
                tip[0] = tk.Toplevel(widget)
                tip[0].wm_overrideredirect(True)
                tip[0].wm_geometry(f"+{e.x_root+10}+{e.y_root-25}")
                tk.Label(tip[0], text=text, bg='#1f2428', fg='#e6edf3',
                        font=("Arial", 8), padx=6, pady=2).pack()
            except tk.TclError:
                pass  # Widget destroyed
        
        def hide(e):
            if tip[0]:
                try:
                    tip[0].destroy()
                except tk.TclError:
                    pass  # Already destroyed
                tip[0] = None
        
        widget.bind('<Enter>', show)
        widget.bind('<Leave>', hide)

    # Для совместимости
    def _create_tooltip(self, widget, text):
        self._tooltip(widget, text)
