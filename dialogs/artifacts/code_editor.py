"""
Артефакт: Редактор кода с подсветкой синтаксиса
На основе Code Editor Pro
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re
from typing import Dict, Any, List, Optional
from .base import FunctionalArtifact, ArtifactRegistry


class CodeEditorArtifact(FunctionalArtifact):
    """
    Функциональный артефакт - редактор кода.
    Поддержка подсветки синтаксиса, вкладок, консоли.
    """
    
    ARTIFACT_ID = "code_editor"
    ARTIFACT_NAME = "Редактор кода"
    ARTIFACT_ICON = "💻"
    ARTIFACT_DESCRIPTION = "Редактор с подсветкой синтаксиса"
    
    # Цвета подсветки синтаксиса
    SYNTAX_COLORS = {
        'keyword': '#569cd6',
        'string': '#ce9178',
        'number': '#b5cea8',
        'comment': '#6a9955',
        'function': '#dcdcaa',
        'class': '#4ec9b0',
        'operator': '#d4d4d4',
        'bracket': '#ffd700',
    }
    
    # Ключевые слова по языкам
    KEYWORDS = {
        'python': ['def', 'class', 'if', 'elif', 'else', 'for', 'while', 'try', 
                   'except', 'finally', 'with', 'as', 'import', 'from', 'return',
                   'yield', 'lambda', 'pass', 'break', 'continue', 'and', 'or',
                   'not', 'in', 'is', 'True', 'False', 'None', 'self', 'async', 'await'],
        'javascript': ['function', 'const', 'let', 'var', 'if', 'else', 'for', 
                       'while', 'return', 'class', 'new', 'this', 'true', 'false',
                       'null', 'undefined', 'async', 'await', 'import', 'export',
                       'default', 'try', 'catch', 'finally', 'throw'],
        'json': ['true', 'false', 'null'],
    }
    
    def __init__(self, parent_canvas, x, y, width=450, height=400, config=None):
        default_config = {
            'font_family': 'Consolas',
            'font_size': 11,
            'tab_size': 4,
            'show_line_numbers': True,
            'word_wrap': False,
            'auto_indent': True,
            'language': 'python',
        }
        if config:
            default_config.update(config)
            
        super().__init__(parent_canvas, x, y, width, height, default_config)
        
        # Файлы
        self.files: Dict[str, Dict] = {
            'untitled.py': {'content': '# Welcome to Code Editor\nprint("Hello, World!")', 'language': 'python'}
        }
        self.current_file = 'untitled.py'
        
        # История для undo/redo
        self.history: List[str] = []
        self.history_index = -1
        
    def _build_content(self):
        """Строит контент редактора"""
        # Панель вкладок файлов
        self._create_file_tabs()
        
        # Панель инструментов
        self._create_toolbar()
        
        # Основная область редактирования
        self._create_editor_area()
        
        # Консоль/вывод
        self._create_console()
        
        # Статус бар
        self._create_status_bar()
        
        # Загружаем файл
        self._load_file(self.current_file)
        
    def _create_file_tabs(self):
        """Создаёт вкладки файлов"""
        tabs_frame = tk.Frame(self.content_frame, bg=self.COLOR_BG_DARK, height=28)
        tabs_frame.pack(fill=tk.X)
        tabs_frame.pack_propagate(False)
        
        self.tabs_container = tk.Frame(tabs_frame, bg=self.COLOR_BG_DARK)
        self.tabs_container.pack(side=tk.LEFT, fill=tk.Y)
        
        # Кнопка добавить файл
        add_btn = tk.Label(tabs_frame, text="＋", font=('Segoe UI', 12),
                          fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_BG_DARK,
                          cursor='hand2', padx=8)
        add_btn.pack(side=tk.RIGHT, pady=4)
        add_btn.bind('<Button-1>', lambda e: self._new_file())
        add_btn.bind('<Enter>', lambda e: add_btn.config(fg=self.COLOR_ACCENT))
        add_btn.bind('<Leave>', lambda e: add_btn.config(fg=self.COLOR_TEXT_MUTED))
        
        self._refresh_tabs()
        
    def _refresh_tabs(self):
        """Обновляет вкладки файлов"""
        for w in self.tabs_container.winfo_children():
            w.destroy()
            
        for filename in self.files:
            is_active = filename == self.current_file
            
            tab = tk.Frame(self.tabs_container, bg=self.COLOR_ACCENT if is_active else self.COLOR_BG,
                          padx=2, pady=2)
            tab.pack(side=tk.LEFT, padx=1)
            
            # Иконка языка
            lang = self.files[filename].get('language', 'text')
            icon = {'python': '🐍', 'javascript': '📜', 'json': '{}', 'html': '🌐'}.get(lang, '📄')
            
            lbl = tk.Label(tab, text=f"{icon} {filename}", font=('Segoe UI', 9),
                          fg='white' if is_active else self.COLOR_TEXT,
                          bg=self.COLOR_ACCENT if is_active else self.COLOR_BG,
                          cursor='hand2')
            lbl.pack(side=tk.LEFT, padx=4)
            lbl.bind('<Button-1>', lambda e, f=filename: self._switch_file(f))
            
            # Кнопка закрыть
            close = tk.Label(tab, text="×", font=('Segoe UI', 10),
                            fg='white' if is_active else self.COLOR_TEXT_MUTED,
                            bg=self.COLOR_ACCENT if is_active else self.COLOR_BG,
                            cursor='hand2')
            close.pack(side=tk.LEFT)
            close.bind('<Button-1>', lambda e, f=filename: self._close_file(f))
            
    def _create_toolbar(self):
        """Создаёт панель инструментов"""
        toolbar = tk.Frame(self.content_frame, bg=self.COLOR_BG_DARK, height=30)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)
        
        # Кнопки
        buttons = [
            ('💾', 'Сохранить', self._save_file),
            ('📂', 'Открыть', self._open_file),
            ('↶', 'Отменить', self._undo),
            ('↷', 'Повторить', self._redo),
            ('|', None, None),
            ('🎨', 'Форматировать', self._format_code),
            ('▶', 'Выполнить', self._run_code),
            ('🔍', 'Найти', self._show_find),
        ]
        
        for icon, tooltip, cmd in buttons:
            if icon == '|':
                sep = tk.Frame(toolbar, bg=self.COLOR_BORDER, width=1)
                sep.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=6)
            else:
                btn = tk.Label(toolbar, text=icon, font=('Segoe UI', 11),
                              fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_BG_DARK,
                              cursor='hand2', padx=6)
                btn.pack(side=tk.LEFT, pady=4)
                if cmd:
                    btn.bind('<Button-1>', lambda e, c=cmd: c())
                btn.bind('<Enter>', lambda e, b=btn: b.config(fg=self.COLOR_TEXT))
                btn.bind('<Leave>', lambda e, b=btn: b.config(fg=self.COLOR_TEXT_MUTED))
                
    def _create_editor_area(self):
        """Создаёт область редактирования"""
        editor_frame = tk.Frame(self.content_frame, bg=self.COLOR_BG)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Номера строк
        self.line_numbers = tk.Text(editor_frame, width=4, padx=4, pady=4,
                                    font=(self.config['font_family'], self.config['font_size']),
                                    bg=self.COLOR_BG_DARK, fg=self.COLOR_TEXT_MUTED,
                                    relief='flat', state='disabled',
                                    highlightthickness=0, bd=0)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Редактор кода
        self.editor = tk.Text(editor_frame, padx=8, pady=4,
                             font=(self.config['font_family'], self.config['font_size']),
                             bg=self.COLOR_BG, fg=self.COLOR_TEXT,
                             insertbackground=self.COLOR_ACCENT,
                             selectbackground=self.COLOR_ACCENT,
                             relief='flat', highlightthickness=0,
                             undo=True, wrap='none' if not self.config['word_wrap'] else 'word')
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(editor_frame, orient='vertical', command=self._on_scroll)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor.config(yscrollcommand=scrollbar.set)
        
        # Привязка событий
        self.editor.bind('<KeyRelease>', self._on_key_release)
        self.editor.bind('<Return>', self._on_enter)
        self.editor.bind('<Tab>', self._on_tab)
        self.editor.bind('<<Modified>>', self._on_modified)
        
        # Теги для подсветки
        self._setup_syntax_tags()
        
    def _setup_syntax_tags(self):
        """Настраивает теги для подсветки синтаксиса"""
        for tag, color in self.SYNTAX_COLORS.items():
            self.editor.tag_configure(tag, foreground=color)
            
    def _create_console(self):
        """Создаёт панель консоли"""
        self.console_frame = tk.Frame(self.content_frame, bg=self.COLOR_BG_DARK, height=80)
        self.console_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.console_frame.pack_propagate(False)
        
        # Заголовок
        header = tk.Frame(self.console_frame, bg=self.COLOR_BG_DARK)
        header.pack(fill=tk.X)
        
        tk.Label(header, text="📊 Консоль", font=('Segoe UI', 9),
                fg=self.COLOR_ACCENT, bg=self.COLOR_BG_DARK).pack(side=tk.LEFT, padx=8, pady=4)
        
        # Кнопка очистки
        clear_btn = tk.Label(header, text="🗑", font=('Segoe UI', 9),
                            fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_BG_DARK,
                            cursor='hand2')
        clear_btn.pack(side=tk.RIGHT, padx=8)
        clear_btn.bind('<Button-1>', lambda e: self._clear_console())
        
        # Текст консоли
        self.console = tk.Text(self.console_frame, height=4,
                              font=(self.config['font_family'], 9),
                              bg=self.COLOR_BG, fg=self.COLOR_TEXT,
                              relief='flat', highlightthickness=0,
                              state='disabled')
        self.console.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))
        
        # Теги для консоли
        self.console.tag_configure('error', foreground='#f85149')
        self.console.tag_configure('success', foreground='#3fb950')
        self.console.tag_configure('info', foreground='#58a6ff')
        
    def _create_status_bar(self):
        """Создаёт статус бар"""
        status = tk.Frame(self.content_frame, bg=self.COLOR_BG_DARK, height=22)
        status.pack(fill=tk.X, side=tk.BOTTOM)
        status.pack_propagate(False)
        
        self.status_line = tk.StringVar(value="Строка 1, Столбец 1")
        tk.Label(status, textvariable=self.status_line, font=('Segoe UI', 8),
                fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_BG_DARK).pack(side=tk.LEFT, padx=8)
        
        self.status_lang = tk.StringVar(value="Python")
        tk.Label(status, textvariable=self.status_lang, font=('Segoe UI', 8),
                fg=self.COLOR_ACCENT, bg=self.COLOR_BG_DARK).pack(side=tk.RIGHT, padx=8)
        
    def _on_scroll(self, *args):
        """Синхронизация скролла"""
        self.editor.yview(*args)
        self.line_numbers.yview(*args)
        
    def _on_key_release(self, event=None):
        """Обработка ввода"""
        self._update_line_numbers()
        self._highlight_syntax()
        self._update_cursor_position()
        
    def _on_enter(self, event):
        """Автоотступ при Enter"""
        if self.config['auto_indent']:
            line = self.editor.get('insert linestart', 'insert')
            indent = len(line) - len(line.lstrip())
            
            # Увеличиваем отступ после : 
            if line.rstrip().endswith(':'):
                indent += self.config['tab_size']
                
            self.editor.insert('insert', '\n' + ' ' * indent)
            return 'break'
            
    def _on_tab(self, event):
        """Tab вставляет пробелы"""
        self.editor.insert('insert', ' ' * self.config['tab_size'])
        return 'break'
        
    def _on_modified(self, event=None):
        """Отслеживание изменений"""
        self.editor.edit_modified(False)
        
    def _update_line_numbers(self):
        """Обновляет номера строк"""
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        
        lines = self.editor.get('1.0', 'end').count('\n')
        line_nums = '\n'.join(str(i) for i in range(1, lines + 1))
        self.line_numbers.insert('1.0', line_nums)
        self.line_numbers.config(state='disabled')
        
    def _update_cursor_position(self):
        """Обновляет позицию курсора в статус баре"""
        pos = self.editor.index('insert')
        line, col = pos.split('.')
        self.status_line.set(f"Строка {line}, Столбец {int(col) + 1}")
        
    def _highlight_syntax(self):
        """Подсветка синтаксиса"""
        # Удаляем все теги
        for tag in self.SYNTAX_COLORS:
            self.editor.tag_remove(tag, '1.0', 'end')
            
        content = self.editor.get('1.0', 'end')
        lang = self.files[self.current_file].get('language', 'text')
        
        # Ключевые слова
        keywords = self.KEYWORDS.get(lang, [])
        for keyword in keywords:
            start = '1.0'
            while True:
                pos = self.editor.search(r'\m' + keyword + r'\M', start, 
                                         stopindex='end', regexp=True)
                if not pos:
                    break
                end = f"{pos}+{len(keyword)}c"
                self.editor.tag_add('keyword', pos, end)
                start = end
                
        # Строки
        for pattern, tag in [(r'"[^"]*"', 'string'), (r"'[^']*'", 'string')]:
            start = '1.0'
            while True:
                pos = self.editor.search(pattern, start, stopindex='end', regexp=True)
                if not pos:
                    break
                # Находим конец строки
                match_text = self.editor.get(pos, 'end').split('\n')[0]
                match = re.match(pattern, match_text)
                if match:
                    end = f"{pos}+{len(match.group())}c"
                    self.editor.tag_add(tag, pos, end)
                    start = end
                else:
                    start = f"{pos}+1c"
                    
        # Комментарии
        comment_char = '#' if lang == 'python' else '//'
        start = '1.0'
        while True:
            pos = self.editor.search(comment_char, start, stopindex='end')
            if not pos:
                break
            end = f"{pos} lineend"
            self.editor.tag_add('comment', pos, end)
            start = f"{pos}+1l"
            
        # Числа
        start = '1.0'
        while True:
            pos = self.editor.search(r'\d+', start, stopindex='end', regexp=True)
            if not pos:
                break
            # Находим длину числа
            text = self.editor.get(pos, 'end')
            match = re.match(r'\d+', text)
            if match:
                end = f"{pos}+{len(match.group())}c"
                self.editor.tag_add('number', pos, end)
                start = end
            else:
                start = f"{pos}+1c"
                
    def _load_file(self, filename: str):
        """Загружает файл в редактор"""
        if filename not in self.files:
            return
            
        self.current_file = filename
        self.editor.delete('1.0', 'end')
        self.editor.insert('1.0', self.files[filename]['content'])
        
        # Определяем язык
        lang = self.files[filename].get('language', 'text')
        lang_names = {'python': 'Python', 'javascript': 'JavaScript', 'json': 'JSON'}
        self.status_lang.set(lang_names.get(lang, 'Text'))
        
        self._update_line_numbers()
        self._highlight_syntax()
        self._refresh_tabs()
        
    def _switch_file(self, filename: str):
        """Переключает на файл"""
        # Сохраняем текущий
        self.files[self.current_file]['content'] = self.editor.get('1.0', 'end-1c')
        self._load_file(filename)
        
    def _new_file(self):
        """Создаёт новый файл"""
        num = 1
        while f'untitled{num}.py' in self.files:
            num += 1
        filename = f'untitled{num}.py'
        self.files[filename] = {'content': '', 'language': 'python'}
        self._load_file(filename)
        
    def _close_file(self, filename: str):
        """Закрывает файл"""
        if len(self.files) <= 1:
            return
        del self.files[filename]
        if self.current_file == filename:
            self.current_file = list(self.files.keys())[0]
        self._load_file(self.current_file)
        
    def _save_file(self):
        """Сохраняет файл"""
        self.files[self.current_file]['content'] = self.editor.get('1.0', 'end-1c')
        self._log(f"✓ Сохранено: {self.current_file}", 'success')
        
    def _open_file(self):
        """Открывает файл с диска"""
        path = filedialog.askopenfilename(
            filetypes=[('Python', '*.py'), ('JavaScript', '*.js'), 
                      ('JSON', '*.json'), ('All', '*.*')]
        )
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                filename = os.path.basename(path)
                ext = os.path.splitext(filename)[1]
                lang = {'.py': 'python', '.js': 'javascript', '.json': 'json'}.get(ext, 'text')
                self.files[filename] = {'content': content, 'language': lang}
                self._load_file(filename)
                self._log(f"✓ Открыт: {filename}", 'success')
            except Exception as e:
                self._log(f"✗ Ошибка: {e}", 'error')
                
    def _undo(self):
        """Отмена"""
        try:
            self.editor.edit_undo()
            self._on_key_release()
        except tk.TclError:
            pass  # Нет действий для отмены
            
    def _redo(self):
        """Повтор"""
        try:
            self.editor.edit_redo()
            self._on_key_release()
        except tk.TclError:
            pass  # Нет действий для повтора
            
    def _format_code(self):
        """Форматирует код"""
        content = self.editor.get('1.0', 'end-1c')
        lang = self.files[self.current_file].get('language', 'text')
        
        try:
            if lang == 'json':
                import json
                formatted = json.dumps(json.loads(content), indent=2, ensure_ascii=False)
                self.editor.delete('1.0', 'end')
                self.editor.insert('1.0', formatted)
                self._log("✓ JSON отформатирован", 'success')
            else:
                self._log("ℹ Форматирование для этого языка недоступно", 'info')
        except Exception as e:
            self._log(f"✗ Ошибка форматирования: {e}", 'error')
            
        self._on_key_release()
        
    def _run_code(self):
        """Выполняет код безопасно в sandbox"""
        content = self.editor.get('1.0', 'end-1c')
        lang = self.files[self.current_file].get('language', 'text')
        
        self._log("▶ Выполнение в sandbox...", 'info')
        
        if lang == 'python':
            try:
                from ..utils.safe_exec import safe_exec, SafeExecutionError
                
                # Выполняем в безопасном окружении
                success, output, result = safe_exec(content)
                
                if success:
                    if output:
                        self._log(output.strip(), 'info')
                    self._log("✓ Выполнено успешно", 'success')
                else:
                    self._log(f"✗ {output}", 'error')
                    
            except ImportError:
                # Fallback если модуль недоступен
                self._log("⚠ Sandbox недоступен, выполнение отключено", 'error')
            except Exception as e:
                self._log(f"✗ Ошибка: {e}", 'error')
        else:
            self._log("ℹ Выполнение доступно только для Python", 'info')
            
    def _show_find(self):
        """Показывает диалог поиска"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Поиск")
        dialog.geometry("300x100")
        dialog.configure(bg=self.COLOR_BG)
        dialog.transient(self.frame)
        
        tk.Label(dialog, text="Найти:", bg=self.COLOR_BG, fg=self.COLOR_TEXT).pack(pady=(10, 5))
        
        find_var = tk.StringVar()
        entry = tk.Entry(dialog, textvariable=find_var, width=30,
                        bg=self.COLOR_BG_DARK, fg=self.COLOR_TEXT,
                        insertbackground=self.COLOR_TEXT)
        entry.pack(pady=5)
        entry.focus()
        
        def do_find():
            text = find_var.get()
            self.editor.tag_remove('found', '1.0', 'end')
            if text:
                start = '1.0'
                count = 0
                while True:
                    pos = self.editor.search(text, start, stopindex='end')
                    if not pos:
                        break
                    end = f"{pos}+{len(text)}c"
                    self.editor.tag_add('found', pos, end)
                    self.editor.tag_configure('found', background=self.COLOR_ACCENT)
                    start = end
                    count += 1
                self._log(f"Найдено: {count} совпадений", 'info')
                
        entry.bind('<Return>', lambda e: do_find())
        tk.Button(dialog, text="Найти", command=do_find,
                 bg=self.COLOR_ACCENT, fg='white').pack(pady=10)
                 
    def _clear_console(self):
        """Очищает консоль"""
        self.console.config(state='normal')
        self.console.delete('1.0', 'end')
        self.console.config(state='disabled')
        
    def _log(self, message: str, msg_type: str = 'info'):
        """Выводит в консоль"""
        self.console.config(state='normal')
        self.console.insert('end', message + '\n', msg_type)
        self.console.see('end')
        self.console.config(state='disabled')
        
    def get_settings_fields(self) -> List[Dict[str, Any]]:
        """Возвращает поля настроек"""
        return [
            {'id': 'font_size', 'type': 'number', 'label': 'Размер шрифта', 
             'value': self.config.get('font_size', 11)},
            {'id': 'tab_size', 'type': 'number', 'label': 'Размер Tab', 
             'value': self.config.get('tab_size', 4)},
            {'id': 'show_line_numbers', 'type': 'checkbox', 'label': 'Номера строк', 
             'value': self.config.get('show_line_numbers', True)},
            {'id': 'word_wrap', 'type': 'checkbox', 'label': 'Перенос слов', 
             'value': self.config.get('word_wrap', False)},
            {'id': 'auto_indent', 'type': 'checkbox', 'label': 'Автоотступ', 
             'value': self.config.get('auto_indent', True)},
        ]
        
    def apply_settings(self, settings: Dict[str, Any]):
        """Применяет настройки"""
        self.config.update(settings)
        
        # Применяем размер шрифта
        font_size = settings.get('font_size', 11)
        self.editor.config(font=(self.config['font_family'], font_size))
        self.line_numbers.config(font=(self.config['font_family'], font_size))
        
        # Номера строк
        if settings.get('show_line_numbers', True):
            self.line_numbers.pack(side=tk.LEFT, fill=tk.Y, before=self.editor)
        else:
            self.line_numbers.pack_forget()
            
        # Перенос слов
        wrap = 'word' if settings.get('word_wrap', False) else 'none'
        self.editor.config(wrap=wrap)
        
    # Публичные методы
    
    def set_content(self, content: str, language: str = 'python'):
        """Устанавливает содержимое редактора"""
        self.files[self.current_file] = {'content': content, 'language': language}
        self._load_file(self.current_file)
        
    def get_content(self) -> str:
        """Возвращает содержимое редактора"""
        return self.editor.get('1.0', 'end-1c')
        
    def add_file(self, filename: str, content: str = '', language: str = 'python'):
        """Добавляет файл"""
        self.files[filename] = {'content': content, 'language': language}
        self._refresh_tabs()


# Регистрируем артефакт
ArtifactRegistry.register(CodeEditorArtifact)

