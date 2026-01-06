#!/usr/bin/env python3
"""
Диалог настройки действий кнопки
Позволяет настроить что происходит при нажатии кнопки
"""
import tkinter as tk
from tkinter import ttk, messagebox


class ActionConfigDialog(tk.Toplevel):
    """Диалог настройки действий"""
    
    # Типы действий
    ACTION_TYPES = [
        ('show', 'Показать элемент'),
        ('hide', 'Скрыть элемент'),
        ('toggle', 'Переключить видимость'),
        ('start', 'Запустить механизм'),
        ('stop', 'Остановить механизм'),
        ('toggle_mech', 'Переключить механизм'),
        ('open_window', 'Открыть окно'),
        ('close_window', 'Закрыть окно'),
    ]
    
    def __init__(self, parent, button_element, element_manager, mechanism_manager, button_functions):
        super().__init__(parent)
        
        self.button_element = button_element
        self.element_manager = element_manager
        self.mechanism_manager = mechanism_manager
        self.button_functions = button_functions
        
        self.result = None
        
        self.title("Настройка действий кнопки")
        self.geometry("500x600")
        self.configure(bg="#2a2a2a")
        self.resizable(False, False)
        
        # Модальное окно
        self.transient(parent)
        self.grab_set()
        
        self._build_ui()
        self._load_current_actions()
        
        # Центрирование
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        """Строит интерфейс"""
        # === Заголовок ===
        header = tk.Frame(self, bg="#2a2a2a")
        header.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(
            header,
            text=f"Кнопка: {self.button_element.id[-8:]}",
            font=("Arial", 12, "bold"),
            bg="#2a2a2a",
            fg="#ffffff"
        ).pack(side=tk.LEFT)
        
        # Номер функции
        func_frame = tk.Frame(header, bg="#2a2a2a")
        func_frame.pack(side=tk.RIGHT)
        
        tk.Label(
            func_frame,
            text="Функция №:",
            font=("Arial", 10),
            bg="#2a2a2a",
            fg="#aaaaaa"
        ).pack(side=tk.LEFT, padx=5)
        
        self.func_id_var = tk.StringVar(value=str(self.button_element.get_function_id()))
        func_entry = tk.Entry(
            func_frame,
            textvariable=self.func_id_var,
            width=5,
            font=("Arial", 10),
            bg="#3a3a3a",
            fg="#ffffff",
            insertbackground="#ffffff"
        )
        func_entry.pack(side=tk.LEFT)
        
        # === Список действий ===
        actions_frame = tk.LabelFrame(
            self,
            text=" Действия ",
            font=("Arial", 10),
            bg="#2a2a2a",
            fg="#888888"
        )
        actions_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Список
        list_frame = tk.Frame(actions_frame, bg="#1e1e1e")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.actions_listbox = tk.Listbox(
            list_frame,
            font=("Arial", 10),
            bg="#1e1e1e",
            fg="#ffffff",
            selectbackground="#0066aa",
            selectforeground="#ffffff",
            height=10
        )
        
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.actions_listbox.yview)
        self.actions_listbox.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.actions_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Кнопки управления списком
        btn_frame = tk.Frame(actions_frame, bg="#2a2a2a")
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        for text, cmd in [
            ("Добавить", self._add_action),
            ("Удалить", self._remove_action),
            ("Вверх", self._move_action_up),
            ("Вниз", self._move_action_down),
        ]:
            tk.Button(
                btn_frame,
                text=text,
                font=("Arial", 9),
                bg="#3a3a3a",
                fg="#ffffff",
                activebackground="#4a4a4a",
                activeforeground="#ffffff",
                relief=tk.FLAT,
                command=cmd
            ).pack(side=tk.LEFT, padx=2)
        
        # === Редактор действия ===
        editor_frame = tk.LabelFrame(
            self,
            text=" Редактор действия ",
            font=("Arial", 10),
            bg="#2a2a2a",
            fg="#888888"
        )
        editor_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Тип действия
        type_row = tk.Frame(editor_frame, bg="#2a2a2a")
        type_row.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            type_row,
            text="Тип:",
            font=("Arial", 10),
            bg="#2a2a2a",
            fg="#aaaaaa",
            width=10,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.action_type_var = tk.StringVar(value='toggle')
        self.action_type_combo = ttk.Combobox(
            type_row,
            textvariable=self.action_type_var,
            values=[t[1] for t in self.ACTION_TYPES],
            state='readonly',
            width=25
        )
        self.action_type_combo.pack(side=tk.LEFT, padx=5)
        self.action_type_combo.current(2)  # toggle по умолчанию
        self.action_type_combo.bind('<<ComboboxSelected>>', self._on_type_change)
        
        # Цель
        target_row = tk.Frame(editor_frame, bg="#2a2a2a")
        target_row.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            target_row,
            text="Цель:",
            font=("Arial", 10),
            bg="#2a2a2a",
            fg="#aaaaaa",
            width=10,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.target_var = tk.StringVar()
        self.target_combo = ttk.Combobox(
            target_row,
            textvariable=self.target_var,
            state='readonly',
            width=25
        )
        self.target_combo.pack(side=tk.LEFT, padx=5)
        self._update_targets()
        
        # Задержка
        delay_row = tk.Frame(editor_frame, bg="#2a2a2a")
        delay_row.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            delay_row,
            text="Задержка (мс):",
            font=("Arial", 10),
            bg="#2a2a2a",
            fg="#aaaaaa",
            width=10,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.delay_var = tk.StringVar(value="0")
        tk.Entry(
            delay_row,
            textvariable=self.delay_var,
            width=10,
            font=("Arial", 10),
            bg="#3a3a3a",
            fg="#ffffff",
            insertbackground="#ffffff"
        ).pack(side=tk.LEFT, padx=5)
        
        # Длительность анимации
        duration_row = tk.Frame(editor_frame, bg="#2a2a2a")
        duration_row.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            duration_row,
            text="Анимация (мс):",
            font=("Arial", 10),
            bg="#2a2a2a",
            fg="#aaaaaa",
            width=10,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.duration_var = tk.StringVar(value="300")
        tk.Entry(
            duration_row,
            textvariable=self.duration_var,
            width=10,
            font=("Arial", 10),
            bg="#3a3a3a",
            fg="#ffffff",
            insertbackground="#ffffff"
        ).pack(side=tk.LEFT, padx=5)
        
        # === Кнопки OK/Cancel ===
        buttons_frame = tk.Frame(self, bg="#2a2a2a")
        buttons_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Button(
            buttons_frame,
            text="Отмена",
            font=("Arial", 10),
            bg="#3a3a3a",
            fg="#ffffff",
            activebackground="#4a4a4a",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            width=10,
            command=self.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(
            buttons_frame,
            text="Сохранить",
            font=("Arial", 10),
            bg="#0066aa",
            fg="#ffffff",
            activebackground="#0077bb",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            width=10,
            command=self._save
        ).pack(side=tk.RIGHT, padx=5)
        
        # Хранилище действий
        self.actions = []

    def _update_targets(self):
        """Обновляет список целей в зависимости от типа действия"""
        action_type = self._get_action_type_key()
        
        targets = []
        
        if action_type in ('show', 'hide', 'toggle', 'open_window', 'close_window'):
            # Элементы
            if self.element_manager:
                for elem in self.element_manager.get_all_elements():
                    if elem.id != self.button_element.id:
                        elem_type = elem.ELEMENT_TYPE if hasattr(elem, 'ELEMENT_TYPE') else 'unknown'
                        targets.append(f"{elem_type} | {elem.id[-8:]}")
        else:
            # Механизмы
            if self.mechanism_manager:
                for mech in self.mechanism_manager.get_all_mechanisms():
                    mech_type = mech.MECHANISM_TYPE if hasattr(mech, 'MECHANISM_TYPE') else 'unknown'
                    targets.append(f"{mech_type} | {mech.id[-8:]}")
        
        self.target_combo['values'] = targets
        if targets:
            self.target_combo.current(0)

    def _get_action_type_key(self):
        """Возвращает ключ типа действия"""
        selected = self.action_type_combo.current()
        if 0 <= selected < len(self.ACTION_TYPES):
            return self.ACTION_TYPES[selected][0]
        return 'toggle'

    def _on_type_change(self, event=None):
        """При смене типа действия"""
        self._update_targets()

    def _load_current_actions(self):
        """Загружает текущие действия кнопки"""
        func_id = self.button_element.get_function_id()
        actions = self.button_functions.get_actions(func_id)
        
        self.actions = []
        for action in actions:
            self.actions.append(action.to_dict())
        
        self._refresh_actions_list()

    def _refresh_actions_list(self):
        """Обновляет список действий"""
        self.actions_listbox.delete(0, tk.END)
        
        for i, action in enumerate(self.actions):
            action_type = action.get('action_type', 'unknown')
            target_id = action.get('target_id', '')
            delay = action.get('delay', 0)
            
            # Находим название типа
            type_name = action_type
            for key, name in self.ACTION_TYPES:
                if key == action_type:
                    type_name = name
                    break
            
            text = f"{i+1}. {type_name}"
            if target_id:
                text += f" → {target_id[-8:]}"
            if delay > 0:
                text += f" (+{delay}мс)"
            
            self.actions_listbox.insert(tk.END, text)

    def _add_action(self):
        """Добавляет новое действие"""
        action_type = self._get_action_type_key()
        target = self.target_var.get()
        
        if not target:
            messagebox.showwarning("Ошибка", "Выберите цель")
            return
        
        # Извлекаем ID из строки "type | id"
        target_id = target.split(' | ')[-1] if ' | ' in target else target
        
        # Находим полный ID
        full_target_id = None
        if action_type in ('show', 'hide', 'toggle', 'open_window', 'close_window'):
            if self.element_manager:
                for elem in self.element_manager.get_all_elements():
                    if elem.id.endswith(target_id):
                        full_target_id = elem.id
                        break
        else:
            if self.mechanism_manager:
                for mech in self.mechanism_manager.get_all_mechanisms():
                    if mech.id.endswith(target_id):
                        full_target_id = mech.id
                        break
        
        if not full_target_id:
            messagebox.showwarning("Ошибка", "Цель не найдена")
            return
        
        try:
            delay = int(self.delay_var.get())
        except ValueError:
            delay = 0
        
        try:
            duration = int(self.duration_var.get())
        except ValueError:
            duration = 300
        
        action = {
            'action_type': action_type,
            'target_id': full_target_id,
            'params': {'duration': duration},
            'delay': delay,
            'condition': None,
        }
        
        self.actions.append(action)
        self._refresh_actions_list()

    def _remove_action(self):
        """Удаляет выбранное действие"""
        selection = self.actions_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if 0 <= index < len(self.actions):
            del self.actions[index]
            self._refresh_actions_list()

    def _move_action_up(self):
        """Перемещает действие вверх"""
        selection = self.actions_listbox.curselection()
        if not selection or selection[0] == 0:
            return
        
        index = selection[0]
        self.actions[index], self.actions[index-1] = self.actions[index-1], self.actions[index]
        self._refresh_actions_list()
        self.actions_listbox.selection_set(index - 1)

    def _move_action_down(self):
        """Перемещает действие вниз"""
        selection = self.actions_listbox.curselection()
        if not selection or selection[0] >= len(self.actions) - 1:
            return
        
        index = selection[0]
        self.actions[index], self.actions[index+1] = self.actions[index+1], self.actions[index]
        self._refresh_actions_list()
        self.actions_listbox.selection_set(index + 1)

    def _save(self):
        """Сохраняет настройки"""
        try:
            func_id = int(self.func_id_var.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный номер функции")
            return
        
        # Устанавливаем номер функции кнопке
        self.button_element.set_function_id(func_id)
        
        # Очищаем старые действия
        self.button_functions.clear_actions(func_id)
        
        # Добавляем новые
        from ..button_functions import ButtonAction
        for action_data in self.actions:
            action = ButtonAction.from_dict(action_data)
            self.button_functions.add_action(func_id, action)
        
        self.result = True
        self.destroy()


def show_action_config(parent, button_element, element_manager, mechanism_manager, button_functions):
    """Показывает диалог настройки действий"""
    dialog = ActionConfigDialog(
        parent, button_element, element_manager, mechanism_manager, button_functions
    )
    parent.wait_window(dialog)
    return dialog.result

