#!/usr/bin/env python3
"""
Диалог настройки переключателя состояний
"""
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser


class StateSwitcherConfigDialog:
    """Диалог настройки переключателя состояний"""

    TRANSITION_TYPES = [
        ('instant', 'Мгновенно'),
        ('fade', 'Плавное затухание'),
        ('slide', 'Скольжение'),
    ]

    INDICATOR_POSITIONS = [
        ('top', 'Сверху'),
        ('bottom', 'Снизу'),
        ('left', 'Слева'),
        ('right', 'Справа'),
    ]

    def __init__(self, parent, element, element_manager=None, mechanism_manager=None):
        self.element = element
        self.element_manager = element_manager
        self.mechanism_manager = mechanism_manager
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("⟐ Настройка переключателя состояний")
        self.dialog.geometry("700x600")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрируем
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 700) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 600) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        self.dialog.configure(bg="#2a2a2a")
        
        self._build_ui()
        self._load_values()
        self.dialog.wait_window()

    def _build_ui(self):
        # Создаём Notebook для вкладок
        style = ttk.Style()
        style.configure('Dark.TNotebook', background='#2a2a2a')
        style.configure('Dark.TNotebook.Tab', background='#3a3a3a', foreground='#ffffff', padding=[10, 5])
        style.map('Dark.TNotebook.Tab', background=[('selected', '#4a4a4a')])
        
        notebook = ttk.Notebook(self.dialog, style='Dark.TNotebook')
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # === Вкладка "Основные" ===
        main_tab = tk.Frame(notebook, bg="#2a2a2a")
        notebook.add(main_tab, text="🔧 Основные")
        self._build_main_tab(main_tab)
        
        # === Вкладка "Состояния" ===
        states_tab = tk.Frame(notebook, bg="#2a2a2a")
        notebook.add(states_tab, text="📊 Состояния")
        self._build_states_tab(states_tab)
        
        # === Вкладка "Привязки" ===
        bindings_tab = tk.Frame(notebook, bg="#2a2a2a")
        notebook.add(bindings_tab, text="🔗 Привязки")
        self._build_bindings_tab(bindings_tab)
        
        # === Вкладка "Настройка состояния" ===
        state_config_tab = tk.Frame(notebook, bg="#2a2a2a")
        notebook.add(state_config_tab, text="⚙ Настройка")
        self._build_state_config_tab(state_config_tab)
        
        # Кнопки
        btn_frame = tk.Frame(self.dialog, bg="#2a2a2a")
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            btn_frame,
            text="Применить",
            font=("Arial", 10),
            bg="#0078d4",
            fg="#ffffff",
            activebackground="#0066b8",
            relief=tk.FLAT,
            padx=20,
            pady=6,
            command=self._on_apply
        ).pack(side=tk.LEFT)
        
        tk.Button(
            btn_frame,
            text="Отмена",
            font=("Arial", 10),
            bg="#4a4a4a",
            fg="#ffffff",
            activebackground="#5a5a5a",
            relief=tk.FLAT,
            padx=20,
            pady=6,
            command=self._on_cancel
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame,
            text="Захватить текущее",
            font=("Arial", 10),
            bg="#4a9f4a",
            fg="#ffffff",
            activebackground="#5ab55a",
            relief=tk.FLAT,
            padx=15,
            pady=6,
            command=self._capture_current
        ).pack(side=tk.RIGHT)

    def _build_main_tab(self, parent):
        """Строит вкладку основных настроек"""
        # Название
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=(15, 5))
        
        tk.Label(row, text="Название:", bg="#2a2a2a", fg="#cccccc", font=("Arial", 10)).pack(side=tk.LEFT)
        self.name_var = tk.StringVar()
        tk.Entry(row, textvariable=self.name_var, bg="#3a3a3a", fg="#ffffff", 
                insertbackground="#ffffff", font=("Arial", 10), relief=tk.FLAT).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0), ipady=4)
        
        # Тип перехода
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(row, text="Переход:", bg="#2a2a2a", fg="#cccccc", font=("Arial", 10)).pack(side=tk.LEFT)
        self.transition_var = tk.StringVar()
        transition_combo = ttk.Combobox(row, textvariable=self.transition_var, state="readonly", width=20)
        transition_combo['values'] = [t[1] for t in self.TRANSITION_TYPES]
        transition_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Длительность перехода
        tk.Label(row, text="Длит. (мс):", bg="#2a2a2a", fg="#cccccc", font=("Arial", 10)).pack(side=tk.LEFT, padx=(20, 0))
        self.duration_var = tk.StringVar()
        tk.Entry(row, textvariable=self.duration_var, bg="#3a3a3a", fg="#ffffff",
                insertbackground="#ffffff", font=("Arial", 10), relief=tk.FLAT, width=8).pack(side=tk.LEFT, padx=(5, 0), ipady=4)
        
        # Автопереключение
        auto_frame = tk.LabelFrame(parent, text=" Автопереключение ", bg="#2a2a2a", fg="#888888", font=("Arial", 9))
        auto_frame.pack(fill=tk.X, padx=15, pady=10)
        
        row = tk.Frame(auto_frame, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=10, pady=5)
        
        self.auto_switch_var = tk.BooleanVar()
        tk.Checkbutton(row, text="Включить автопереключение", variable=self.auto_switch_var,
                      bg="#2a2a2a", fg="#ffffff", selectcolor="#3a3a3a",
                      activebackground="#2a2a2a", font=("Arial", 10)).pack(side=tk.LEFT)
        
        tk.Label(row, text="Интервал (мс):", bg="#2a2a2a", fg="#cccccc", font=("Arial", 10)).pack(side=tk.LEFT, padx=(20, 0))
        self.interval_var = tk.StringVar()
        tk.Entry(row, textvariable=self.interval_var, bg="#3a3a3a", fg="#ffffff",
                insertbackground="#ffffff", font=("Arial", 10), relief=tk.FLAT, width=8).pack(side=tk.LEFT, padx=(5, 0), ipady=4)
        
        row = tk.Frame(auto_frame, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=10, pady=5)
        
        self.loop_var = tk.BooleanVar()
        tk.Checkbutton(row, text="Зациклить (вернуться к первому)", variable=self.loop_var,
                      bg="#2a2a2a", fg="#ffffff", selectcolor="#3a3a3a",
                      activebackground="#2a2a2a", font=("Arial", 10)).pack(side=tk.LEFT)
        
        # Триггер функции
        row = tk.Frame(parent, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(row, text="ID функции триггера:", bg="#2a2a2a", fg="#cccccc", font=("Arial", 10)).pack(side=tk.LEFT)
        self.trigger_var = tk.StringVar()
        tk.Entry(row, textvariable=self.trigger_var, bg="#3a3a3a", fg="#ffffff",
                insertbackground="#ffffff", font=("Arial", 10), relief=tk.FLAT, width=8).pack(side=tk.LEFT, padx=(10, 0), ipady=4)
        
        # Индикатор
        indicator_frame = tk.LabelFrame(parent, text=" Индикатор ", bg="#2a2a2a", fg="#888888", font=("Arial", 9))
        indicator_frame.pack(fill=tk.X, padx=15, pady=10)
        
        row = tk.Frame(indicator_frame, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=10, pady=5)
        
        self.show_indicator_var = tk.BooleanVar()
        tk.Checkbutton(row, text="Показывать индикатор", variable=self.show_indicator_var,
                      bg="#2a2a2a", fg="#ffffff", selectcolor="#3a3a3a",
                      activebackground="#2a2a2a", font=("Arial", 10)).pack(side=tk.LEFT)
        
        tk.Label(row, text="Позиция:", bg="#2a2a2a", fg="#cccccc", font=("Arial", 10)).pack(side=tk.LEFT, padx=(20, 0))
        self.indicator_pos_var = tk.StringVar()
        pos_combo = ttk.Combobox(row, textvariable=self.indicator_pos_var, state="readonly", width=12)
        pos_combo['values'] = [p[1] for p in self.INDICATOR_POSITIONS]
        pos_combo.pack(side=tk.LEFT, padx=(5, 0))

    def _build_states_tab(self, parent):
        """Строит вкладку управления состояниями"""
        # Список состояний
        list_frame = tk.Frame(parent, bg="#2a2a2a")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        tk.Label(list_frame, text="Состояния:", bg="#2a2a2a", fg="#cccccc", font=("Arial", 10, "bold")).pack(anchor="w")
        
        # Listbox со скроллом
        scroll_frame = tk.Frame(list_frame, bg="#2a2a2a")
        scroll_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = tk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.states_listbox = tk.Listbox(
            scroll_frame,
            bg="#3a3a3a",
            fg="#ffffff",
            selectbackground="#0078d4",
            selectforeground="#ffffff",
            font=("Arial", 11),
            height=10,
            yscrollcommand=scrollbar.set
        )
        self.states_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.states_listbox.yview)
        
        self.states_listbox.bind('<<ListboxSelect>>', self._on_state_select)
        
        # Кнопки управления
        btn_frame = tk.Frame(list_frame, bg="#2a2a2a")
        btn_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(btn_frame, text="➕ Добавить", font=("Arial", 9), bg="#4a9f4a", fg="#ffffff",
                 activebackground="#5ab55a", relief=tk.FLAT, padx=10, command=self._add_state).pack(side=tk.LEFT, padx=2)
        
        tk.Button(btn_frame, text="🗑 Удалить", font=("Arial", 9), bg="#9f4a4a", fg="#ffffff",
                 activebackground="#b05a5a", relief=tk.FLAT, padx=10, command=self._remove_state).pack(side=tk.LEFT, padx=2)
        
        tk.Button(btn_frame, text="⬆ Вверх", font=("Arial", 9), bg="#4a4a4a", fg="#ffffff",
                 activebackground="#5a5a5a", relief=tk.FLAT, padx=10, command=self._move_state_up).pack(side=tk.LEFT, padx=2)
        
        tk.Button(btn_frame, text="⬇ Вниз", font=("Arial", 9), bg="#4a4a4a", fg="#ffffff",
                 activebackground="#5a5a5a", relief=tk.FLAT, padx=10, command=self._move_state_down).pack(side=tk.LEFT, padx=2)
        
        # Редактирование состояния
        edit_frame = tk.LabelFrame(parent, text=" Редактирование состояния ", bg="#2a2a2a", fg="#888888", font=("Arial", 9))
        edit_frame.pack(fill=tk.X, padx=15, pady=5)
        
        row = tk.Frame(edit_frame, bg="#2a2a2a")
        row.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(row, text="Имя:", bg="#2a2a2a", fg="#cccccc", font=("Arial", 10)).pack(side=tk.LEFT)
        self.state_name_var = tk.StringVar()
        self.state_name_entry = tk.Entry(row, textvariable=self.state_name_var, bg="#3a3a3a", fg="#ffffff",
                                        insertbackground="#ffffff", font=("Arial", 10), relief=tk.FLAT, width=20)
        self.state_name_entry.pack(side=tk.LEFT, padx=(10, 0), ipady=4)
        
        tk.Label(row, text="Цвет:", bg="#2a2a2a", fg="#cccccc", font=("Arial", 10)).pack(side=tk.LEFT, padx=(20, 0))
        self.state_color_btn = tk.Button(row, text="  ", bg="#4a9fff", width=4,
                                        relief=tk.FLAT, command=self._pick_state_color)
        self.state_color_btn.pack(side=tk.LEFT, padx=(5, 0))
        self.state_color_var = "#4a9fff"
        
        tk.Button(row, text="✓ Сохранить", font=("Arial", 9), bg="#0078d4", fg="#ffffff",
                 activebackground="#0066b8", relief=tk.FLAT, padx=10, command=self._save_state_changes).pack(side=tk.LEFT, padx=(20, 0))

    def _build_bindings_tab(self, parent):
        """Строит вкладку привязок"""
        # Два столбца: элементы и механизмы
        columns = tk.Frame(parent, bg="#2a2a2a")
        columns.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Колонка элементов
        elem_frame = tk.LabelFrame(columns, text=" 🔷 Элементы ", bg="#2a2a2a", fg="#4a9fff", font=("Arial", 10))
        elem_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Доступные элементы
        tk.Label(elem_frame, text="Доступные:", bg="#2a2a2a", fg="#888888", font=("Arial", 9)).pack(anchor="w", padx=10, pady=(5, 0))
        
        self.available_elements_listbox = tk.Listbox(
            elem_frame, bg="#3a3a3a", fg="#ffffff", selectbackground="#0078d4",
            font=("Arial", 9), height=6
        )
        self.available_elements_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Button(elem_frame, text="▼ Привязать", font=("Arial", 9), bg="#4a9f4a", fg="#ffffff",
                 relief=tk.FLAT, command=self._bind_element).pack(pady=5)
        
        # Привязанные элементы
        tk.Label(elem_frame, text="Привязанные:", bg="#2a2a2a", fg="#4aff4a", font=("Arial", 9)).pack(anchor="w", padx=10)
        
        self.bound_elements_listbox = tk.Listbox(
            elem_frame, bg="#3a3a3a", fg="#4aff4a", selectbackground="#0078d4",
            font=("Arial", 9), height=6
        )
        self.bound_elements_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Button(elem_frame, text="▲ Отвязать", font=("Arial", 9), bg="#9f4a4a", fg="#ffffff",
                 relief=tk.FLAT, command=self._unbind_element).pack(pady=5)
        
        # Колонка механизмов
        mech_frame = tk.LabelFrame(columns, text=" ⚙ Механизмы ", bg="#2a2a2a", fg="#ff4aff", font=("Arial", 10))
        mech_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Доступные механизмы
        tk.Label(mech_frame, text="Доступные:", bg="#2a2a2a", fg="#888888", font=("Arial", 9)).pack(anchor="w", padx=10, pady=(5, 0))
        
        self.available_mechanisms_listbox = tk.Listbox(
            mech_frame, bg="#3a3a3a", fg="#ffffff", selectbackground="#0078d4",
            font=("Arial", 9), height=6
        )
        self.available_mechanisms_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Button(mech_frame, text="▼ Привязать", font=("Arial", 9), bg="#4a9f4a", fg="#ffffff",
                 relief=tk.FLAT, command=self._bind_mechanism).pack(pady=5)
        
        # Привязанные механизмы
        tk.Label(mech_frame, text="Привязанные:", bg="#2a2a2a", fg="#ff4aff", font=("Arial", 9)).pack(anchor="w", padx=10)
        
        self.bound_mechanisms_listbox = tk.Listbox(
            mech_frame, bg="#3a3a3a", fg="#ff4aff", selectbackground="#0078d4",
            font=("Arial", 9), height=6
        )
        self.bound_mechanisms_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Button(mech_frame, text="▲ Отвязать", font=("Arial", 9), bg="#9f4a4a", fg="#ffffff",
                 relief=tk.FLAT, command=self._unbind_mechanism).pack(pady=5)

    def _build_state_config_tab(self, parent):
        """Строит вкладку настройки конкретного состояния"""
        info = tk.Label(
            parent,
            text="Выберите состояние во вкладке 'Состояния',\nзатем настройте свойства элементов для этого состояния.",
            bg="#2a2a2a",
            fg="#888888",
            font=("Arial", 10),
            justify=tk.CENTER
        )
        info.pack(pady=20)
        
        # Фрейм настроек элементов
        self.state_config_frame = tk.Frame(parent, bg="#2a2a2a")
        self.state_config_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Элементы состояния
        tk.Label(self.state_config_frame, text="Свойства элементов в выбранном состоянии:", 
                bg="#2a2a2a", fg="#cccccc", font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.element_props_text = tk.Text(
            self.state_config_frame,
            bg="#3a3a3a",
            fg="#ffffff",
            font=("Consolas", 9),
            height=15,
            wrap=tk.WORD
        )
        self.element_props_text.pack(fill=tk.BOTH, expand=True, pady=10)

    def _load_values(self):
        """Загружает значения из элемента"""
        props = self.element.properties
        
        self.name_var.set(props.get('name', 'Переключатель'))
        
        # Тип перехода
        trans_type = props.get('transition_type', 'instant')
        for code, name in self.TRANSITION_TYPES:
            if code == trans_type:
                self.transition_var.set(name)
                break
        
        self.duration_var.set(str(props.get('transition_duration', 300)))
        self.auto_switch_var.set(props.get('auto_switch', False))
        self.interval_var.set(str(props.get('auto_switch_interval', 2000)))
        self.loop_var.set(props.get('loop', True))
        self.trigger_var.set(str(props.get('trigger_function_id', 0)))
        self.show_indicator_var.set(props.get('show_indicator', True))
        
        # Позиция индикатора
        ind_pos = props.get('indicator_position', 'bottom')
        for code, name in self.INDICATOR_POSITIONS:
            if code == ind_pos:
                self.indicator_pos_var.set(name)
                break
        
        # Загружаем состояния
        self._refresh_states_list()
        
        # Загружаем привязки
        self._refresh_bindings()

    def _refresh_states_list(self):
        """Обновляет список состояний"""
        self.states_listbox.delete(0, tk.END)
        
        for i, state in enumerate(self.element.states):
            prefix = "▶" if i == self.element.current_state_index else " "
            default = " ★" if state.is_default else ""
            self.states_listbox.insert(tk.END, f"{prefix} {state.icon} {state.name}{default}")

    def _refresh_bindings(self):
        """Обновляет списки привязок"""
        # Очищаем
        self.available_elements_listbox.delete(0, tk.END)
        self.bound_elements_listbox.delete(0, tk.END)
        self.available_mechanisms_listbox.delete(0, tk.END)
        self.bound_mechanisms_listbox.delete(0, tk.END)
        
        # Элементы
        if self.element_manager:
            for elem in self.element_manager.get_all_elements():
                if elem.id == self.element.id:
                    continue
                
                name = f"{elem.ELEMENT_TYPE}: {elem.id[:8]}"
                
                if elem.id in self.element.bound_elements:
                    self.bound_elements_listbox.insert(tk.END, name)
                else:
                    self.available_elements_listbox.insert(tk.END, name)
        
        # Механизмы
        if self.mechanism_manager:
            for mech in self.mechanism_manager.get_all_mechanisms():
                name = f"{mech.MECHANISM_TYPE}: {mech.id[:8]}"
                
                if mech.id in self.element.bound_mechanisms:
                    self.bound_mechanisms_listbox.insert(tk.END, name)
                else:
                    self.available_mechanisms_listbox.insert(tk.END, name)

    # === Обработчики событий ===
    
    def _on_state_select(self, event):
        """При выборе состояния"""
        sel = self.states_listbox.curselection()
        if not sel:
            return
        
        idx = sel[0]
        if 0 <= idx < len(self.element.states):
            state = self.element.states[idx]
            self.state_name_var.set(state.name)
            self.state_color_var = state.color
            self.state_color_btn.configure(bg=state.color)
            
            # Показываем свойства состояния
            self._show_state_properties(state)

    def _show_state_properties(self, state):
        """Показывает свойства состояния"""
        self.element_props_text.delete("1.0", tk.END)
        
        text = f"=== Состояние: {state.name} ===\n\n"
        
        text += "--- Элементы ---\n"
        for elem_id, props in state.element_states.items():
            text += f"\n{elem_id}:\n"
            for key, value in props.items():
                text += f"  {key}: {value}\n"
        
        text += "\n--- Механизмы ---\n"
        for mech_id, mech_state in state.mechanism_states.items():
            text += f"\n{mech_id}:\n"
            text += f"  active: {mech_state.get('is_active', False)}\n"
            for key, value in mech_state.get('properties', {}).items():
                text += f"  {key}: {value}\n"
        
        self.element_props_text.insert("1.0", text)

    def _add_state(self):
        """Добавляет новое состояние"""
        state = self.element.add_state(f"Состояние {len(self.element.states) + 1}")
        self._refresh_states_list()

    def _remove_state(self):
        """Удаляет состояние"""
        sel = self.states_listbox.curselection()
        if not sel:
            return
        
        idx = sel[0]
        if 0 <= idx < len(self.element.states):
            state = self.element.states[idx]
            if self.element.remove_state(state.id):
                self._refresh_states_list()
            else:
                messagebox.showwarning("Предупреждение", "Нельзя удалить. Минимум 2 состояния.")

    def _move_state_up(self):
        """Перемещает состояние вверх"""
        sel = self.states_listbox.curselection()
        if not sel or sel[0] == 0:
            return
        
        idx = sel[0]
        self.element.states[idx], self.element.states[idx - 1] = self.element.states[idx - 1], self.element.states[idx]
        self._refresh_states_list()
        self.states_listbox.selection_set(idx - 1)

    def _move_state_down(self):
        """Перемещает состояние вниз"""
        sel = self.states_listbox.curselection()
        if not sel or sel[0] >= len(self.element.states) - 1:
            return
        
        idx = sel[0]
        self.element.states[idx], self.element.states[idx + 1] = self.element.states[idx + 1], self.element.states[idx]
        self._refresh_states_list()
        self.states_listbox.selection_set(idx + 1)

    def _save_state_changes(self):
        """Сохраняет изменения состояния"""
        sel = self.states_listbox.curselection()
        if not sel:
            return
        
        idx = sel[0]
        if 0 <= idx < len(self.element.states):
            state = self.element.states[idx]
            state.name = self.state_name_var.get()
            state.color = self.state_color_var
            self._refresh_states_list()

    def _pick_state_color(self):
        """Выбор цвета состояния"""
        color = colorchooser.askcolor(color=self.state_color_var, title="Цвет состояния")
        if color[1]:
            self.state_color_var = color[1]
            self.state_color_btn.configure(bg=color[1])

    def _bind_element(self):
        """Привязывает элемент"""
        sel = self.available_elements_listbox.curselection()
        if not sel:
            return
        
        text = self.available_elements_listbox.get(sel[0])
        elem_id = text.split(": ")[1]
        
        # Находим полный ID
        if self.element_manager:
            for elem in self.element_manager.get_all_elements():
                if elem.id.startswith(elem_id):
                    self.element.bind_element(elem.id)
                    break
        
        self._refresh_bindings()

    def _unbind_element(self):
        """Отвязывает элемент"""
        sel = self.bound_elements_listbox.curselection()
        if not sel:
            return
        
        text = self.bound_elements_listbox.get(sel[0])
        elem_id = text.split(": ")[1]
        
        if self.element_manager:
            for elem in self.element_manager.get_all_elements():
                if elem.id.startswith(elem_id):
                    self.element.unbind_element(elem.id)
                    break
        
        self._refresh_bindings()

    def _bind_mechanism(self):
        """Привязывает механизм"""
        sel = self.available_mechanisms_listbox.curselection()
        if not sel:
            return
        
        text = self.available_mechanisms_listbox.get(sel[0])
        mech_id = text.split(": ")[1]
        
        if self.mechanism_manager:
            for mech in self.mechanism_manager.get_all_mechanisms():
                if mech.id.startswith(mech_id):
                    self.element.bind_mechanism(mech.id)
                    break
        
        self._refresh_bindings()

    def _unbind_mechanism(self):
        """Отвязывает механизм"""
        sel = self.bound_mechanisms_listbox.curselection()
        if not sel:
            return
        
        text = self.bound_mechanisms_listbox.get(sel[0])
        mech_id = text.split(": ")[1]
        
        if self.mechanism_manager:
            for mech in self.mechanism_manager.get_all_mechanisms():
                if mech.id.startswith(mech_id):
                    self.element.unbind_mechanism(mech.id)
                    break
        
        self._refresh_bindings()

    def _capture_current(self):
        """Захватывает текущее состояние"""
        self.element.capture_current_state(self.element_manager, self.mechanism_manager)
        
        sel = self.states_listbox.curselection()
        if sel and 0 <= sel[0] < len(self.element.states):
            self._show_state_properties(self.element.states[sel[0]])
        
        messagebox.showinfo("Захват", "Текущее состояние захвачено!")

    def _on_apply(self):
        """Применяет изменения"""
        props = self.element.properties
        
        props['name'] = self.name_var.get()
        
        # Тип перехода
        trans_name = self.transition_var.get()
        for code, name in self.TRANSITION_TYPES:
            if name == trans_name:
                props['transition_type'] = code
                break
        
        try:
            props['transition_duration'] = int(self.duration_var.get())
        except ValueError:
            pass
        
        props['auto_switch'] = self.auto_switch_var.get()
        
        try:
            props['auto_switch_interval'] = int(self.interval_var.get())
        except ValueError:
            pass
        
        props['loop'] = self.loop_var.get()
        
        try:
            props['trigger_function_id'] = int(self.trigger_var.get())
        except ValueError:
            pass
        
        props['show_indicator'] = self.show_indicator_var.get()
        
        # Позиция индикатора
        pos_name = self.indicator_pos_var.get()
        for code, name in self.INDICATOR_POSITIONS:
            if name == pos_name:
                props['indicator_position'] = code
                break
        
        self.element.update()
        
        # Уведомляем систему о изменении
        from ..utils.event_bus import event_bus
        event_bus.emit('element.updated', {'element': self.element})
        
        self.result = True
        self.dialog.destroy()

    def _on_cancel(self):
        """Отменяет изменения"""
        self.dialog.destroy()


def show_state_switcher_config(parent, element, element_manager=None, mechanism_manager=None):
    """Показывает диалог настройки переключателя состояний"""
    dialog = StateSwitcherConfigDialog(parent, element, element_manager, mechanism_manager)
    return dialog.result

