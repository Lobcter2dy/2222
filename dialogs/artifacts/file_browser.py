"""
Артефакт: Файловый браузер (просмотр папок)
"""

import tkinter as tk
from tkinter import ttk, filedialog
import os
from typing import Dict, Any, List, Optional
from .base import FunctionalArtifact, ArtifactRegistry


class FileBrowserArtifact(FunctionalArtifact):
    """
    Функциональный артефакт для просмотра файловой системы.
    Отображает дерево папок и файлов внутри панели.
    """
    
    ARTIFACT_ID = "file_browser"
    ARTIFACT_NAME = "Файловый браузер"
    ARTIFACT_ICON = "📁"
    ARTIFACT_DESCRIPTION = "Просмотр папок и файлов"
    
    # Иконки для файлов
    ICONS = {
        'folder': '📁',
        'folder_open': '📂',
        'file': '📄',
        'image': '🖼️',
        'code': '📝',
        'audio': '🎵',
        'video': '🎬',
        'archive': '📦',
        'unknown': '📄'
    }
    
    # Расширения файлов
    EXTENSIONS = {
        'image': {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp', '.ico'},
        'code': {'.py', '.js', '.ts', '.html', '.css', '.json', '.xml', '.yaml', '.yml', '.md'},
        'audio': {'.mp3', '.wav', '.ogg', '.flac', '.aac'},
        'video': {'.mp4', '.avi', '.mkv', '.mov', '.webm'},
        'archive': {'.zip', '.rar', '.7z', '.tar', '.gz'}
    }
    
    def __init__(self, parent_canvas, x, y, width=320, height=450, config=None):
        # Дефолтная конфигурация
        default_config = {
            'root_path': os.path.expanduser('~'),
            'show_hidden': False,
            'show_files': True,
            'filter_extensions': [],  # Пустой = все файлы
            'sort_folders_first': True,
            'double_click_action': 'open',  # open, select, custom
        }
        if config:
            default_config.update(config)
            
        super().__init__(parent_canvas, x, y, width, height, default_config)
        
        # Текущий путь
        self.current_path = self.config.get('root_path', os.path.expanduser('~'))
        
        # Выбранные элементы
        self.selected_items: List[str] = []
        
        # Колбэки
        self._on_file_select: Optional[callable] = None
        self._on_file_open: Optional[callable] = None
        
    def _build_content(self):
        """Строит контент браузера"""
        # Панель навигации
        self._create_nav_bar()
        
        # Дерево файлов
        self._create_file_tree()
        
        # Панель статуса
        self._create_status_bar()
        
        # Загружаем содержимое
        self._load_directory(self.current_path)
        
    def _create_nav_bar(self):
        """Создаёт панель навигации"""
        nav = tk.Frame(self.content_frame, bg=self.COLOR_BG_DARK, height=32)
        nav.pack(fill=tk.X, pady=(0, 1))
        nav.pack_propagate(False)
        
        # Кнопка "Вверх"
        up_btn = tk.Label(nav, text="⬆", font=('Segoe UI', 11),
                         fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_BG_DARK,
                         cursor='hand2', padx=8)
        up_btn.pack(side=tk.LEFT, pady=4)
        up_btn.bind('<Button-1>', lambda e: self._go_up())
        up_btn.bind('<Enter>', lambda e: up_btn.config(fg=self.COLOR_TEXT))
        up_btn.bind('<Leave>', lambda e: up_btn.config(fg=self.COLOR_TEXT_MUTED))
        
        # Кнопка "Домой"
        home_btn = tk.Label(nav, text="🏠", font=('Segoe UI', 11),
                           fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_BG_DARK,
                           cursor='hand2', padx=4)
        home_btn.pack(side=tk.LEFT, pady=4)
        home_btn.bind('<Button-1>', lambda e: self._go_home())
        home_btn.bind('<Enter>', lambda e: home_btn.config(fg=self.COLOR_TEXT))
        home_btn.bind('<Leave>', lambda e: home_btn.config(fg=self.COLOR_TEXT_MUTED))
        
        # Кнопка "Обзор"
        browse_btn = tk.Label(nav, text="📂", font=('Segoe UI', 11),
                             fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_BG_DARK,
                             cursor='hand2', padx=4)
        browse_btn.pack(side=tk.LEFT, pady=4)
        browse_btn.bind('<Button-1>', lambda e: self._browse_folder())
        browse_btn.bind('<Enter>', lambda e: browse_btn.config(fg=self.COLOR_TEXT))
        browse_btn.bind('<Leave>', lambda e: browse_btn.config(fg=self.COLOR_TEXT_MUTED))
        
        # Поле пути
        self.path_var = tk.StringVar(value=self.current_path)
        path_entry = tk.Entry(nav, textvariable=self.path_var,
                             font=('Consolas', 9), bg=self.COLOR_BG,
                             fg=self.COLOR_TEXT, insertbackground=self.COLOR_TEXT,
                             relief='flat', highlightthickness=1,
                             highlightbackground=self.COLOR_BORDER)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, pady=6)
        path_entry.bind('<Return>', lambda e: self._load_directory(self.path_var.get()))
        
        # Кнопка обновить
        refresh_btn = tk.Label(nav, text="↻", font=('Segoe UI', 12),
                              fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_BG_DARK,
                              cursor='hand2', padx=8)
        refresh_btn.pack(side=tk.RIGHT, pady=4)
        refresh_btn.bind('<Button-1>', lambda e: self._refresh())
        refresh_btn.bind('<Enter>', lambda e: refresh_btn.config(fg=self.COLOR_TEXT))
        refresh_btn.bind('<Leave>', lambda e: refresh_btn.config(fg=self.COLOR_TEXT_MUTED))
        
    def _create_file_tree(self):
        """Создаёт дерево файлов"""
        # Контейнер с прокруткой
        tree_frame = tk.Frame(self.content_frame, bg=self.COLOR_BG)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Стиль для Treeview
        style = ttk.Style()
        style_name = f'FileBrowser{id(self)}.Treeview'
        style.configure(style_name,
                       background=self.COLOR_BG,
                       fieldbackground=self.COLOR_BG,
                       foreground=self.COLOR_TEXT,
                       rowheight=24,
                       borderwidth=0)
        style.map(style_name,
                 background=[('selected', self.COLOR_ACCENT)],
                 foreground=[('selected', '#ffffff')])
        
        # Treeview
        self.tree = ttk.Treeview(tree_frame, style=style_name,
                                 selectmode='extended', show='tree')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', 
                                  command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=scrollbar.set)
        
        # События
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<<TreeviewSelect>>', self._on_tree_select)
        self.tree.bind('<Button-3>', self._on_tree_right_click)
        
    def _create_status_bar(self):
        """Создаёт панель статуса"""
        status = tk.Frame(self.content_frame, bg=self.COLOR_BG_DARK, height=24)
        status.pack(fill=tk.X, side=tk.BOTTOM)
        status.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="")
        status_label = tk.Label(status, textvariable=self.status_var,
                               font=('Segoe UI', 8), fg=self.COLOR_TEXT_MUTED,
                               bg=self.COLOR_BG_DARK, anchor='w')
        status_label.pack(side=tk.LEFT, padx=8, fill=tk.X, expand=True)
        
    def _load_directory(self, path: str):
        """Загружает содержимое директории"""
        if not os.path.isdir(path):
            self.status_var.set(f"❌ Путь не найден")
            return
            
        self.current_path = path
        self.path_var.set(path)
        
        # Очищаем дерево
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            items = os.listdir(path)
        except PermissionError:
            self.status_var.set("⛔ Доступ запрещён")
            return
        except Exception as e:
            self.status_var.set(f"❌ Ошибка: {str(e)[:30]}")
            return
            
        # Фильтруем скрытые файлы
        if not self.config.get('show_hidden', False):
            items = [i for i in items if not i.startswith('.')]
            
        # Разделяем на папки и файлы
        folders = []
        files = []
        
        for item in items:
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                folders.append(item)
            elif self.config.get('show_files', True):
                files.append(item)
                
        # Сортируем
        folders.sort(key=str.lower)
        files.sort(key=str.lower)
        
        # Если папки первые
        if self.config.get('sort_folders_first', True):
            sorted_items = folders + files
        else:
            sorted_items = sorted(folders + files, key=str.lower)
            
        # Добавляем в дерево
        folder_count = 0
        file_count = 0
        
        for item in sorted_items:
            full_path = os.path.join(path, item)
            is_folder = os.path.isdir(full_path)
            
            if is_folder:
                icon = self.ICONS['folder']
                folder_count += 1
            else:
                icon = self._get_file_icon(item)
                file_count += 1
                
            # Фильтр расширений
            filter_ext = self.config.get('filter_extensions', [])
            if filter_ext and not is_folder:
                ext = os.path.splitext(item)[1].lower()
                if ext not in filter_ext:
                    continue
                    
            display_name = f"{icon} {item}"
            self.tree.insert('', 'end', iid=full_path, text=display_name,
                           values=(full_path,))
                           
        # Статус
        status_parts = []
        if folder_count > 0:
            status_parts.append(f"📁 {folder_count}")
        if file_count > 0:
            status_parts.append(f"📄 {file_count}")
        self.status_var.set("  ".join(status_parts) if status_parts else "Пусто")
        
    def _get_file_icon(self, filename: str) -> str:
        """Возвращает иконку для файла"""
        ext = os.path.splitext(filename)[1].lower()
        
        for file_type, extensions in self.EXTENSIONS.items():
            if ext in extensions:
                return self.ICONS.get(file_type, self.ICONS['file'])
                
        return self.ICONS['file']
        
    def _on_double_click(self, event):
        """Двойной клик по элементу"""
        selection = self.tree.selection()
        if not selection:
            return
            
        item_path = selection[0]
        
        if os.path.isdir(item_path):
            # Открываем папку
            self._load_directory(item_path)
        else:
            # Действие для файла
            action = self.config.get('double_click_action', 'open')
            if action == 'open' and self._on_file_open:
                self._on_file_open(item_path)
            elif action == 'select' and self._on_file_select:
                self._on_file_select(item_path)
                
    def _on_tree_select(self, event):
        """Выбор элемента в дереве"""
        self.selected_items = list(self.tree.selection())
        if self._on_file_select and self.selected_items:
            self._on_file_select(self.selected_items[0])
            
    def _on_tree_right_click(self, event):
        """Правый клик по дереву"""
        # Выбираем элемент под курсором
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            
        menu = tk.Menu(self.tree, tearoff=0, bg=self.COLOR_BG,
                      fg=self.COLOR_TEXT, activebackground=self.COLOR_ACCENT)
        
        if item:
            is_folder = os.path.isdir(item)
            menu.add_command(label="📂 Открыть" if is_folder else "📄 Выбрать",
                           command=lambda: self._on_double_click(None))
            menu.add_separator()
            
        menu.add_command(label="📁 Новая папка", command=self._create_folder)
        menu.add_command(label="↻ Обновить", command=self._refresh)
        
        menu.tk_popup(event.x_root, event.y_root)
        
    def _go_up(self):
        """Переход на уровень вверх"""
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self._load_directory(parent)
            
    def _go_home(self):
        """Переход в домашнюю директорию"""
        self._load_directory(os.path.expanduser('~'))
        
    def _browse_folder(self):
        """Выбор папки через диалог"""
        folder = filedialog.askdirectory(initialdir=self.current_path)
        if folder:
            self._load_directory(folder)
            
    def _refresh(self):
        """Обновляет текущую директорию"""
        self._load_directory(self.current_path)
        
    def _create_folder(self):
        """Создаёт новую папку"""
        # TODO: Диалог создания папки
        pass
        
    def _show_settings(self):
        """Показывает настройки артефакта"""
        dialog = tk.Toplevel(self.frame)
        dialog.title(f"Настройки: {self.ARTIFACT_NAME}")
        dialog.geometry("400x350")
        dialog.configure(bg=self.COLOR_BG)
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Центрируем
        dialog.update_idletasks()
        x = self.frame.winfo_rootx() + 50
        y = self.frame.winfo_rooty() + 50
        dialog.geometry(f"+{x}+{y}")
        
        # Контент
        content = tk.Frame(dialog, bg=self.COLOR_BG)
        content.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        # Корневой путь
        tk.Label(content, text="Корневой путь:", font=('Segoe UI', 10),
                fg=self.COLOR_TEXT, bg=self.COLOR_BG).pack(anchor='w')
        
        path_frame = tk.Frame(content, bg=self.COLOR_BG)
        path_frame.pack(fill=tk.X, pady=(4, 12))
        
        path_var = tk.StringVar(value=self.config.get('root_path', ''))
        path_entry = tk.Entry(path_frame, textvariable=path_var,
                             font=('Consolas', 10), bg=self.COLOR_BG_DARK,
                             fg=self.COLOR_TEXT, insertbackground=self.COLOR_TEXT)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = tk.Button(path_frame, text="...", font=('Segoe UI', 10),
                              bg=self.COLOR_BG_DARK, fg=self.COLOR_TEXT,
                              command=lambda: path_var.set(
                                  filedialog.askdirectory() or path_var.get()))
        browse_btn.pack(side=tk.RIGHT, padx=(4, 0))
        
        # Чекбоксы
        show_hidden_var = tk.BooleanVar(value=self.config.get('show_hidden', False))
        tk.Checkbutton(content, text="Показывать скрытые файлы",
                      variable=show_hidden_var, font=('Segoe UI', 10),
                      fg=self.COLOR_TEXT, bg=self.COLOR_BG,
                      selectcolor=self.COLOR_BG_DARK,
                      activebackground=self.COLOR_BG).pack(anchor='w', pady=4)
        
        show_files_var = tk.BooleanVar(value=self.config.get('show_files', True))
        tk.Checkbutton(content, text="Показывать файлы",
                      variable=show_files_var, font=('Segoe UI', 10),
                      fg=self.COLOR_TEXT, bg=self.COLOR_BG,
                      selectcolor=self.COLOR_BG_DARK,
                      activebackground=self.COLOR_BG).pack(anchor='w', pady=4)
        
        folders_first_var = tk.BooleanVar(value=self.config.get('sort_folders_first', True))
        tk.Checkbutton(content, text="Папки в начале списка",
                      variable=folders_first_var, font=('Segoe UI', 10),
                      fg=self.COLOR_TEXT, bg=self.COLOR_BG,
                      selectcolor=self.COLOR_BG_DARK,
                      activebackground=self.COLOR_BG).pack(anchor='w', pady=4)
        
        # Кнопки
        btn_frame = tk.Frame(content, bg=self.COLOR_BG)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(16, 0))
        
        def apply():
            self.config['root_path'] = path_var.get()
            self.config['show_hidden'] = show_hidden_var.get()
            self.config['show_files'] = show_files_var.get()
            self.config['sort_folders_first'] = folders_first_var.get()
            self._refresh()
            dialog.destroy()
            
        tk.Button(btn_frame, text="Применить", font=('Segoe UI', 10),
                 bg=self.COLOR_ACCENT, fg='white', relief='flat',
                 padx=16, command=apply).pack(side=tk.RIGHT)
        
        tk.Button(btn_frame, text="Отмена", font=('Segoe UI', 10),
                 bg=self.COLOR_BG_DARK, fg=self.COLOR_TEXT, relief='flat',
                 padx=16, command=dialog.destroy).pack(side=tk.RIGHT, padx=(0, 8))
                 
    def get_settings_fields(self) -> List[Dict[str, Any]]:
        """Возвращает поля настроек для левой панели"""
        return [
            {
                'id': 'root_path',
                'type': 'path',
                'label': 'Корневой путь',
                'value': self.config.get('root_path', ''),
            },
            {
                'id': 'show_hidden',
                'type': 'checkbox',
                'label': 'Скрытые файлы',
                'value': self.config.get('show_hidden', False),
            },
            {
                'id': 'show_files',
                'type': 'checkbox',
                'label': 'Показывать файлы',
                'value': self.config.get('show_files', True),
            },
            {
                'id': 'sort_folders_first',
                'type': 'checkbox',
                'label': 'Папки сначала',
                'value': self.config.get('sort_folders_first', True),
            },
        ]
        
    # Публичные методы для внешнего использования
    
    def set_root_path(self, path: str):
        """Устанавливает корневой путь"""
        if os.path.isdir(path):
            self.config['root_path'] = path
            self._load_directory(path)
            
    def get_selected_path(self) -> Optional[str]:
        """Возвращает путь выбранного элемента"""
        return self.selected_items[0] if self.selected_items else None
        
    def set_file_select_callback(self, callback: callable):
        """Устанавливает колбэк выбора файла"""
        self._on_file_select = callback
        
    def set_file_open_callback(self, callback: callable):
        """Устанавливает колбэк открытия файла"""
        self._on_file_open = callback


# Регистрируем артефакт
ArtifactRegistry.register(FileBrowserArtifact)

