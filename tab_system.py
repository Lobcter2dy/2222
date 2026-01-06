#!/usr/bin/env python3
"""
Система вкладок с горизонтальной прокруткой
"""
import tkinter as tk
from modules.config import Config


class TabSystem:
    """Система управления вкладками"""

    # GitHub Dark цвета
    COLOR_BG = '#0d1117'
    COLOR_BG_SECONDARY = '#161b22'
    COLOR_BORDER = '#30363d'
    COLOR_TEXT = '#e6edf3'
    COLOR_TEXT_MUTED = '#8d96a0'
    COLOR_ACCENT = '#2f81f7'

    def __init__(self, parent, config: Config):
        self.parent = parent
        self.config = config
        self.tabs = {}
        self.tab_buttons = {}
        self.active_tab = None

    def build(self):
        """Создаёт систему вкладок"""
        # Контейнер кнопок с прокруткой
        header = tk.Frame(self.parent, bg=self.COLOR_BG_SECONDARY)
        header.pack(fill=tk.X, padx=2, pady=2)

        # Кнопка влево
        self.btn_left = tk.Button(
            header, text="‹", font=("Arial", 10),
            bg=self.COLOR_BG_SECONDARY, fg=self.COLOR_TEXT_MUTED,
            activebackground=self.COLOR_BORDER, activeforeground=self.COLOR_TEXT,
            relief=tk.FLAT, width=2, cursor="hand2",
            command=lambda: self._scroll(-80)
        )
        self.btn_left.pack(side=tk.LEFT, padx=1)

        # Canvas для прокрутки
        self.canvas = tk.Canvas(
            header, bg=self.COLOR_BG_SECONDARY,
            highlightthickness=0, height=30
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.buttons_frame = tk.Frame(self.canvas, bg=self.COLOR_BG_SECONDARY)
        self.canvas_win = self.canvas.create_window((0, 0), window=self.buttons_frame, anchor="nw")

        self.buttons_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<MouseWheel>", self._on_wheel)
        self.canvas.bind("<Button-4>", self._on_wheel)
        self.canvas.bind("<Button-5>", self._on_wheel)

        # Кнопка вправо
        self.btn_right = tk.Button(
            header, text="›", font=("Arial", 10),
            bg=self.COLOR_BG_SECONDARY, fg=self.COLOR_TEXT_MUTED,
            activebackground=self.COLOR_BORDER, activeforeground=self.COLOR_TEXT,
            relief=tk.FLAT, width=2, cursor="hand2",
            command=lambda: self._scroll(80)
        )
        self.btn_right.pack(side=tk.RIGHT, padx=1)

        # Контейнер содержимого
        self.content_frame = tk.Frame(self.parent, bg=self.COLOR_BG_SECONDARY)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        self._create_tabs()
        self._create_buttons()

        if self.tabs:
            self.switch_to(list(self.tabs.keys())[0])

    def _on_frame_configure(self, e):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._update_scroll_btns()

    def _on_canvas_configure(self, e):
        self._update_scroll_btns()

    def _on_wheel(self, e):
        delta = -1 if (e.num == 4 or e.delta > 0) else 1
        self.canvas.xview_scroll(delta * 2, "units")
        self._update_scroll_btns()

    def _scroll(self, delta):
        """Плавная прокрутка"""
        steps = 8
        step_size = delta / steps
        
        for i in range(steps):
            x = self.canvas.xview()[0]
            self.canvas.xview_moveto(x + step_size / self.canvas.winfo_width())
            self.parent.update_idletasks()
            self.parent.after(10)
        
        self._update_scroll_btns()

    def _update_scroll_btns(self):
        """Обновить видимость кнопок прокрутки"""
        try:
            bbox = self.canvas.bbox("all")
            if not bbox:
                return
            
            view = self.canvas.xview()
            can_scroll_left = view[0] > 0.001
            can_scroll_right = view[1] < 0.999 and bbox[2] > self.canvas.winfo_width()
            
            self.btn_left.config(
                fg=self.COLOR_TEXT if can_scroll_left else self.COLOR_BORDER
            )
            self.btn_right.config(
                fg=self.COLOR_TEXT if can_scroll_right else self.COLOR_BORDER
            )
        except tk.TclError:
            pass  # Widget not ready yet

    def _create_tabs(self):
        """Создаёт экземпляры вкладок"""
        from modules.tabs.tab_elements import TabElements
        from modules.tabs.tab_mechanisms import TabMechanisms
        from modules.tabs.tab_layers import TabLayers
        from modules.tabs.tab_color import TabColor
        from modules.tabs.tab_text import TabText
        from modules.tabs.tab_filters import TabFilters
        from modules.tabs.tab_sounds import TabSounds
        from modules.tabs.tab_menu import TabMenu
        from modules.tabs.tab_code import TabCode
        from modules.tabs.tab_settings import TabSettings
        from modules.tabs.tab_ai import TabAI

        tab_classes = [
            TabElements, TabMechanisms, TabLayers, TabColor, TabText,
            TabFilters, TabSounds, TabMenu, TabCode, TabSettings, TabAI
        ]

        for TabClass in tab_classes:
            tab = TabClass(self.content_frame, self.config)
            tab.build()
            self.tabs[TabClass.TAB_ID] = tab

    def _create_buttons(self):
        """Создаёт кнопки вкладок"""
        for tab_id, tab in self.tabs.items():
            symbol = getattr(tab, 'TAB_SYMBOL', '○')
            
            btn = tk.Button(
                self.buttons_frame,
                text=symbol,
                font=("Arial", 11),
                bg=self.COLOR_BG_SECONDARY,
                fg=self.COLOR_TEXT_MUTED,
                activebackground=self.COLOR_BORDER,
                activeforeground=self.COLOR_TEXT,
                relief=tk.FLAT,
                width=3,
                cursor="hand2",
                command=lambda tid=tab_id: self.switch_to(tid)
            )
            btn.pack(side=tk.LEFT, padx=1, pady=2)
            self.tab_buttons[tab_id] = btn

    def switch_to(self, tab_id):
        """Переключает на вкладку"""
        if tab_id not in self.tabs:
            return

        # Деактивировать предыдущую
        if self.active_tab and self.active_tab in self.tabs:
            self.tabs[self.active_tab].hide()
            self.tabs[self.active_tab].on_deactivate()
            if self.active_tab in self.tab_buttons:
                self.tab_buttons[self.active_tab].config(
                    bg=self.COLOR_BG_SECONDARY,
                    fg=self.COLOR_TEXT_MUTED
                )

        # Активировать новую
        self.active_tab = tab_id
        self.tabs[tab_id].show()
        self.tabs[tab_id].on_activate()
        
        if tab_id in self.tab_buttons:
            self.tab_buttons[tab_id].config(
                bg=self.COLOR_ACCENT,
                fg='#ffffff'
            )

        # Прокрутить к кнопке
        self._scroll_to_button(tab_id)

    def _scroll_to_button(self, tab_id):
        """Прокрутить к кнопке вкладки"""
        if tab_id not in self.tab_buttons:
            return
        
        try:
            btn = self.tab_buttons[tab_id]
            btn_x = btn.winfo_x()
            btn_w = btn.winfo_width()
            canvas_w = self.canvas.winfo_width()
            
            if btn_x + btn_w > canvas_w:
                self.canvas.xview_moveto(btn_x / self.canvas.bbox("all")[2])
            elif btn_x < 0:
                self.canvas.xview_moveto(0)
            
            self._update_scroll_btns()
        except (tk.TclError, TypeError, ZeroDivisionError):
            pass  # Widget geometry not ready

    def get_tab(self, tab_id):
        """Возвращает вкладку по ID"""
        return self.tabs.get(tab_id)

    def get_active_tab(self):
        """Возвращает активную вкладку"""
        if self.active_tab:
            return self.tabs.get(self.active_tab)
        return None
