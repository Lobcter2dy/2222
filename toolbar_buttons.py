#!/usr/bin/env python3
"""
Кнопки панели инструментов - стиль GitHub Dark
"""
import tkinter as tk
from tkinter import filedialog, messagebox


# GitHub Dark цвета
COLOR_BG = '#0d1117'
COLOR_BG_SECONDARY = '#161b22'
COLOR_BG_OVERLAY = '#21262d'
COLOR_BORDER = '#30363d'
COLOR_TEXT = '#e6edf3'
COLOR_TEXT_MUTED = '#8d96a0'
COLOR_ACCENT = '#2f81f7'
COLOR_SUCCESS = '#238636'
COLOR_SUCCESS_EMPHASIS = '#1f6b2e'
COLOR_WARNING = '#9e6a03'
COLOR_WARNING_EMPHASIS = '#7d5200'
COLOR_DANGER = '#da3633'


class ToolbarButton:
    """Кнопка панели инструментов"""
    
    def __init__(self, parent, config, button_id, symbol, tooltip, command):
        self.parent = parent
        self.config = config
        self.button_id = button_id
        self.symbol = symbol
        self.tooltip = tooltip
        self.command = command
        self.settings = {}
        self.button = None
        self._create_button()
    
    def _create_button(self):
        self.button = tk.Button(
            self.parent,
            text=self.symbol,
            font=("Arial", 12),  # Увеличен шрифт
            bg=COLOR_BG_OVERLAY,
            fg=COLOR_TEXT_MUTED,
            activebackground=COLOR_BORDER,
            activeforeground=COLOR_TEXT,
            relief=tk.FLAT,
            borderwidth=0,
            width=4,  # Увеличена ширина
            pady=6,   # Увеличен отступ
            cursor="hand2",
            command=self._on_click
        )
        self.button.pack(fill=tk.X, padx=1, pady=1)
        self.button.bind("<Button-3>", self._on_right_click)
        self._create_tooltip()
    
    def _on_click(self):
        if self.command:
            self.command()
    
    def _on_right_click(self, event):
        ToolbarButtonSettings(self.parent.winfo_toplevel(), self)
    
    def _create_tooltip(self):
        tooltip_window = None
        
        def show(event):
            nonlocal tooltip_window
            if tooltip_window:
                return
            x, y = event.x_root + 10, event.y_root - 30
            tooltip_window = tk.Toplevel(self.button)
            tooltip_window.wm_overrideredirect(True)
            tooltip_window.wm_geometry(f"+{x}+{y}")
            tooltip_window.configure(bg=COLOR_BG)
            tk.Label(
                tooltip_window, text=self.tooltip,
                bg=COLOR_BG, fg=COLOR_TEXT,
                font=("Arial", 9), padx=6, pady=3
            ).pack()
        
        def hide(event):
            nonlocal tooltip_window
            if tooltip_window:
                tooltip_window.destroy()
                tooltip_window = None
        
        self.button.bind("<Enter>", show)
        self.button.bind("<Leave>", hide)


class ToolbarButtonSettings(tk.Toplevel):
    """Диалог настроек кнопки - GitHub стиль"""
    
    def __init__(self, parent, toolbar_button):
        super().__init__(parent)
        self.toolbar_button = toolbar_button
        
        self.title(f"Настройка: {toolbar_button.tooltip}")
        self.geometry("400x300")  # Увеличен размер
        self.resizable(True, True)  # Разрешено изменение размера
        self.minsize(350, 250)     # Минимальный размер
        self.transient(parent)
        self.grab_set()
        self.configure(bg=COLOR_BG_SECONDARY)
        
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 400) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 300) // 2
        self.geometry(f"+{x}+{y}")
        
        self._build_ui()
    
    def _build_ui(self):
        # Создаём основной контейнер с прокруткой
        main_frame = tk.Frame(self, bg=COLOR_BG_SECONDARY)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        header_frame = tk.Frame(main_frame, bg=COLOR_BG_SECONDARY)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            header_frame, text=f"{self.toolbar_button.symbol} {self.toolbar_button.tooltip}",
            font=("Arial", 14, "bold"), bg=COLOR_BG_SECONDARY, fg=COLOR_TEXT
        ).pack(side=tk.LEFT)
        
        tk.Label(
            header_frame, text=f"ID: {self.toolbar_button.button_id}",
            font=("Arial", 9), bg=COLOR_BG_SECONDARY, fg=COLOR_TEXT_MUTED
        ).pack(side=tk.RIGHT)
        
        # === Секция: Внешний вид ===
        appearance_frame = tk.LabelFrame(
            main_frame, text=" Внешний вид ", font=("Arial", 10, "bold"),
            bg=COLOR_BG_SECONDARY, fg=COLOR_TEXT, relief=tk.GROOVE, borderwidth=1
        )
        appearance_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Символ кнопки
        symbol_frame = tk.Frame(appearance_frame, bg=COLOR_BG_SECONDARY)
        symbol_frame.pack(fill=tk.X, padx=10, pady=8)
        
        tk.Label(symbol_frame, text="Символ:", font=("Arial", 10),
                bg=COLOR_BG_SECONDARY, fg=COLOR_TEXT).pack(side=tk.LEFT)
        
        self.symbol_var = tk.StringVar(value=self.toolbar_button.symbol)
        symbol_entry = tk.Entry(
            symbol_frame, textvariable=self.symbol_var, font=("Arial", 12),
            bg=COLOR_BG_OVERLAY, fg=COLOR_TEXT, insertbackground=COLOR_TEXT,
            relief=tk.FLAT, width=8, justify=tk.CENTER
        )
        symbol_entry.pack(side=tk.RIGHT)
        symbol_entry.bind('<KeyRelease>', self._update_symbol)
        
        # Подсказка
        tooltip_frame = tk.Frame(appearance_frame, bg=COLOR_BG_SECONDARY)
        tooltip_frame.pack(fill=tk.X, padx=10, pady=8)
        
        tk.Label(tooltip_frame, text="Подсказка:", font=("Arial", 10),
                bg=COLOR_BG_SECONDARY, fg=COLOR_TEXT).pack(side=tk.LEFT)
        
        self.tooltip_var = tk.StringVar(value=self.toolbar_button.tooltip)
        tooltip_entry = tk.Entry(
            tooltip_frame, textvariable=self.tooltip_var, font=("Arial", 10),
            bg=COLOR_BG_OVERLAY, fg=COLOR_TEXT, insertbackground=COLOR_TEXT,
            relief=tk.FLAT, width=20
        )
        tooltip_entry.pack(side=tk.RIGHT)
        tooltip_entry.bind('<KeyRelease>', self._update_tooltip)
        
        # === Секция: Действие ===
        action_frame = tk.LabelFrame(
            main_frame, text=" Действие ", font=("Arial", 10, "bold"),
            bg=COLOR_BG_SECONDARY, fg=COLOR_TEXT, relief=tk.GROOVE, borderwidth=1
        )
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        action_info = tk.Label(
            action_frame, text=f"Функция: {self.toolbar_button.command.__name__ if self.toolbar_button.command else 'Не назначена'}",
            font=("Arial", 9), bg=COLOR_BG_SECONDARY, fg=COLOR_TEXT_MUTED, wraplength=300
        )
        action_info.pack(padx=10, pady=8)
        
        # === Секция: Состояние ===
        state_frame = tk.LabelFrame(
            main_frame, text=" Состояние ", font=("Arial", 10, "bold"),
            bg=COLOR_BG_SECONDARY, fg=COLOR_TEXT, relief=tk.GROOVE, borderwidth=1
        )
        state_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Включена/выключена
        enabled_frame = tk.Frame(state_frame, bg=COLOR_BG_SECONDARY)
        enabled_frame.pack(fill=tk.X, padx=10, pady=8)
        
        self.enabled_var = tk.BooleanVar(value=self.toolbar_button.button['state'] != tk.DISABLED)
        enabled_cb = tk.Checkbutton(
            enabled_frame, text="Кнопка активна", variable=self.enabled_var,
            font=("Arial", 10), bg=COLOR_BG_SECONDARY, fg=COLOR_TEXT,
            selectcolor=COLOR_BG_OVERLAY, activebackground=COLOR_BG_SECONDARY,
            command=self._update_enabled
        )
        enabled_cb.pack(side=tk.LEFT)
        
        # Кнопки управления
        button_frame = tk.Frame(main_frame, bg=COLOR_BG_SECONDARY)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Применить
        apply_btn = tk.Button(
            button_frame, text="Применить", font=("Arial", 10),
            bg=COLOR_SUCCESS, fg=COLOR_TEXT,
            activebackground=COLOR_SUCCESS_EMPHASIS, relief=tk.FLAT,
            padx=20, pady=6, command=self._apply_changes
        )
        apply_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Сброс
        reset_btn = tk.Button(
            button_frame, text="Сброс", font=("Arial", 10),
            bg=COLOR_WARNING, fg=COLOR_TEXT,
            activebackground=COLOR_WARNING_EMPHASIS, relief=tk.FLAT,
            padx=20, pady=6, command=self._reset_settings
        )
        reset_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Закрыть
        close_btn = tk.Button(
            button_frame, text="Закрыть", font=("Arial", 10),
            bg=COLOR_BG_OVERLAY, fg=COLOR_TEXT,
            activebackground=COLOR_BORDER, relief=tk.FLAT,
            padx=20, pady=6, command=self.destroy
        )
        close_btn.pack(side=tk.RIGHT)
        
    def _update_symbol(self, event=None):
        """Обновляет символ кнопки в реальном времени"""
        new_symbol = self.symbol_var.get()
        if len(new_symbol) > 0:
            self.toolbar_button.button.config(text=new_symbol)
    
    def _update_tooltip(self, event=None):
        """Обновляет подсказку кнопки"""
        self.toolbar_button.tooltip = self.tooltip_var.get()
    
    def _update_enabled(self):
        """Переключает состояние кнопки"""
        if self.enabled_var.get():
            self.toolbar_button.button.config(state=tk.NORMAL)
        else:
            self.toolbar_button.button.config(state=tk.DISABLED)
    
    def _apply_changes(self):
        """Применяет все изменения"""
        # Сохраняем символ
        self.toolbar_button.symbol = self.symbol_var.get()
        self.toolbar_button.button.config(text=self.symbol_var.get())
        
        # Сохраняем подсказку  
        self.toolbar_button.tooltip = self.tooltip_var.get()
        
        # Состояние уже обновлено через _update_enabled
        
        # Показываем подтверждение
        self.title("✓ Настройки применены")
        self.after(1500, lambda: self.title(f"Настройка: {self.toolbar_button.tooltip}"))
    
    def _reset_settings(self):
        """Сбрасывает настройки к значениям по умолчанию"""
        self.symbol_var.set(self.toolbar_button.symbol)
        self.tooltip_var.set(self.toolbar_button.tooltip)
        self.enabled_var.set(True)
        self.toolbar_button.button.config(state=tk.NORMAL)


class ToolbarManager:
    """Менеджер кнопок панели инструментов"""
    
    def __init__(self, parent, config, app_ref=None):
        self.parent = parent
        self.config = config
        self.app = app_ref
        self.buttons = []

    def create_all_buttons(self, frame):
        """Создаёт все кнопки панели - компактный стиль GitHub"""
        
        # Группа: Файл
        self._create_group(frame, "Файл", [
            ("new", "+", "Новый", self._on_new),
            ("open", "↑", "Открыть", self._on_open),
            ("save", "↓", "Сохранить", self._on_save),
        ])
        
        # Группа: Экспорт
        self._create_group(frame, "I/O", [
            ("import", "⇧", "Импорт", self._on_import),
            ("export", "⇩", "Экспорт", self._on_export),
            ("img", "▣", "Изображение", self._on_export_image),
        ])
        
        # Группа: Правка
        self._create_group(frame, "Правка", [
            ("undo", "↶", "Отменить", self._on_undo),
            ("redo", "↷", "Повторить", self._on_redo),
            ("copy", "⊡", "Копировать", self._on_copy),
            ("paste", "⊞", "Вставить", self._on_paste),
            ("del", "×", "Удалить", self._on_delete),
        ])
        
        # Группа: Слои
        self._create_group(frame, "Слои", [
            ("front", "⊼", "Наверх", self._on_to_front),
            ("back", "⊻", "Вниз", self._on_to_back),
        ])
        
        # Группа: Вид
        self._create_group(frame, "Вид", [
            ("zin", "+", "Увеличить", self._on_zoom_in),
            ("zout", "−", "Уменьшить", self._on_zoom_out),
            ("fit", "⊡", "По размеру", self._on_fit),
            ("100", "1:1", "100%", self._on_zoom_100),
        ])
        
        # Группа: Сетка
        self._create_group(frame, "Сетка", [
            ("grid", "#", "Переключить сетку", self._on_grid_toggle),
            ("grid+", "⊞", "Увеличить сетку", self._on_grid_increase),
            ("grid-", "⊟", "Уменьшить сетку", self._on_grid_decrease),
        ])
        
        # Группа: Экран
        self._create_group(frame, "Экран", [
            ("fullscreen", "⛶", "Полный экран (F11)", self._on_fullscreen),
        ])
        
        # Группа: Просмотр + Экран (справа)
        self._create_group(frame, "", [
            ("preview", "▶", "Просмотр (F5)", self._on_preview),
            ("fullscreen", "⛶", "Полный экран (F11)", self._on_fullscreen),
        ], side=tk.RIGHT)
        

    def _create_group(self, frame, label, buttons_data, side=tk.LEFT):
        """Создаёт группу кнопок"""
        group = tk.Frame(frame, bg=COLOR_BG_SECONDARY)
        group.pack(side=side, padx=2)
        
        if label:
            tk.Label(
                group, text=label, font=("Arial", 8),  # Увеличен шрифт подписи
                bg=COLOR_BG_SECONDARY, fg=COLOR_BORDER
            ).pack(side=tk.TOP, pady=(0, 2))
        
        btn_row = tk.Frame(group, bg=COLOR_BG_SECONDARY)
        btn_row.pack(side=tk.TOP)
        
        for btn_id, symbol, tooltip, command in buttons_data:
            self.buttons.append(ToolbarButton(btn_row, self.config, btn_id, symbol, tooltip, command))
    
    def _create_fullscreen_button(self, frame):
        """Создаёт компактную кнопку полноэкранного режима панели"""
        # Компактная кнопка справа
        btn = tk.Button(
            frame,
            text="⛶",
            font=("Arial", 10),  # Меньший шрифт
            bg=COLOR_BG_OVERLAY,
            fg=COLOR_TEXT_MUTED,
            activebackground=COLOR_BORDER,
            activeforeground=COLOR_TEXT,
            relief=tk.FLAT,
            borderwidth=0,
            width=2,  # Компактная ширина
            pady=4,
            cursor="hand2",
            command=self._on_panel_fullscreen
        )
        btn.pack(side=tk.RIGHT, padx=(2, 4), pady=2)
        
        # Tooltip
        self._add_tooltip(btn, "Панель на весь экран")

    # Обработчики
    def _on_new(self):
        if self.app and hasattr(self.app, 'new_project'):
            self.app.new_project()

    def _on_open(self):
        if self.app and hasattr(self.app, 'open_project'):
            self.app.open_project()

    def _on_save(self):
        if self.app and hasattr(self.app, 'save_project'):
            self.app.save_project()

    def _on_import(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json"), ("Все", "*.*")])
        if path and self.app:
            print(f"Импорт: {path}")

    def _on_export(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path and self.app:
            print(f"Экспорт: {path}")

    def _on_export_image(self):
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
        if path and self.app:
            print(f"Экспорт изображения: {path}")

    def _on_undo(self):
        if self.app and hasattr(self.app, 'undo'):
            self.app.undo()

    def _on_redo(self):
        if self.app and hasattr(self.app, 'redo'):
            self.app.redo()

    def _on_copy(self):
        if self.app and hasattr(self.app, 'copy_selected'):
            self.app.copy_selected()

    def _on_paste(self):
        if self.app and hasattr(self.app, 'paste'):
            self.app.paste()

    def _on_delete(self):
        if self.app and hasattr(self.app, 'delete_selected'):
            self.app.delete_selected()

    def _on_to_front(self):
        if self.app and hasattr(self.app, 'bring_to_front'):
            self.app.bring_to_front()

    def _on_to_back(self):
        if self.app and hasattr(self.app, 'send_to_back'):
            self.app.send_to_back()

    def _on_zoom_in(self):
        if self.app and hasattr(self.app, 'zoom_in'):
            self.app.zoom_in()

    def _on_zoom_out(self):
        if self.app and hasattr(self.app, 'zoom_out'):
            self.app.zoom_out()

    def _on_fit(self):
        if self.app and hasattr(self.app, 'zoom_fit'):
            self.app.zoom_fit()

    def _on_zoom_100(self):
        if self.app and hasattr(self.app, 'zoom_reset'):
            self.app.zoom_reset()

    def _on_preview(self):
        if self.app and hasattr(self.app, 'toggle_preview_mode'):
            self.app.toggle_preview_mode()

    def _on_fullscreen(self):
        if self.app and hasattr(self.app, 'toggle_fullscreen'):
            self.app.toggle_fullscreen()
    
    def _on_grid_toggle(self):
        if self.app and hasattr(self.app, 'toggle_grid'):
            self.app.toggle_grid()
    
    def _on_grid_increase(self):
        if self.app and hasattr(self.app, 'grid_increase'):
            self.app.grid_increase()
    
    def _on_grid_decrease(self):
        if self.app and hasattr(self.app, 'grid_decrease'):
            self.app.grid_decrease()
    
    def _on_panel_fullscreen(self):
        """Полноэкранный режим только для панели (Preview Mode)"""
        if self.app and hasattr(self.app, 'toggle_preview_mode'):
            self.app.toggle_preview_mode()
    
    def _add_tooltip(self, widget, text):
        """Добавляет tooltip к виджету"""
        tooltip_window = None
        
        def show(event):
            nonlocal tooltip_window
            if tooltip_window:
                return
            x, y = event.x_root + 10, event.y_root - 30
            tooltip_window = tk.Toplevel(widget)
            tooltip_window.wm_overrideredirect(True)
            tooltip_window.wm_geometry(f"+{x}+{y}")
            tooltip_window.configure(bg=COLOR_BG)
            tk.Label(
                tooltip_window, text=text,
                bg=COLOR_BG, fg=COLOR_TEXT,
                font=("Arial", 9), padx=6, pady=3
            ).pack()
        
        def hide(event):
            nonlocal tooltip_window
            if tooltip_window:
                tooltip_window.destroy()
                tooltip_window = None
        
        widget.bind("<Enter>", show)
        widget.bind("<Leave>", hide)
