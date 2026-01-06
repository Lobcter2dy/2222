#!/usr/bin/env python3
"""
Вкладка AI ассистента
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
from .tab_base import TabBase


class TabAI(TabBase):
    """Вкладка AI"""

    TAB_ID = "ai"
    TAB_SYMBOL = "◈"

    PROVIDERS = [
        ('openai', 'OpenAI', ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo']),
        ('anthropic', 'Anthropic', ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku']),
        ('google', 'Google AI', ['gemini-pro', 'gemini-pro-vision']),
        ('perplexity', 'Perplexity', ['pplx-7b-online', 'pplx-70b-online']),
        ('github', 'GitHub Copilot', ['copilot']),
        ('mistral', 'Mistral AI', ['mistral-large', 'mistral-medium', 'mistral-small']),
        ('ollama', 'Ollama', ['llama2', 'codellama', 'mistral']),
        ('gpt4all', 'GPT4All', ['ggml-gpt4all-j', 'ggml-vicuna-13b']),
    ]

    def __init__(self, parent, config):
        super().__init__(parent, config)
        self.element_manager = None
        self.main_canvas = None
        self.settings_tab = None
        self.app = None
        self.chat_history = []

    def set_element_manager(self, manager):
        self.element_manager = manager

    def set_main_canvas(self, canvas):
        self.main_canvas = canvas

    def set_settings_tab(self, tab):
        self.settings_tab = tab

    def set_app(self, app):
        self.app = app

    def _build_content(self):
        self.content = self._scroll_container(self.frame)
        
        # === Провайдер ===
        sec = self._section(self.content, "AI Провайдер")
        
        row = self._row(sec)
        self._label(row, "Сервис:", 8).pack(side=tk.LEFT)
        self.provider_var = tk.StringVar(value='openai')
        provider_combo = self._combo(row, [p[1] for p in self.PROVIDERS], self.provider_var, 14)
        provider_combo.pack(side=tk.LEFT)
        provider_combo.bind('<<ComboboxSelected>>', self._on_provider_change)
        
        row = self._row(sec)
        self._label(row, "Модель:", 8).pack(side=tk.LEFT)
        self.model_var = tk.StringVar(value='gpt-4')
        self.model_combo = self._combo(row, ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'], self.model_var, 14)
        self.model_combo.pack(side=tk.LEFT)
        
        # Статус
        self.status_lbl = tk.Label(sec, text="○ Не подключено", font=("Arial", 9),
                                  bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_WARNING)
        self.status_lbl.pack(anchor="w", pady=(4, 0))
        
        # === Чат ===
        sec = self._section(self.content, "Чат")
        
        # История чата
        chat_frame = tk.Frame(sec, bg=self.COLOR_BG)
        chat_frame.pack(fill=tk.BOTH, expand=True)
        
        self.chat_text = tk.Text(chat_frame, height=12, font=("Arial", 9),
                                bg=self.COLOR_BG, fg=self.COLOR_TEXT,
                                insertbackground=self.COLOR_TEXT, relief=tk.FLAT,
                                wrap=tk.WORD, state='disabled')
        self.chat_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.chat_text.tag_configure('user', foreground=self.COLOR_ACCENT)
        self.chat_text.tag_configure('ai', foreground='#7ee787')
        self.chat_text.tag_configure('system', foreground=self.COLOR_TEXT_MUTED)
        
        # Скролл
        self.chat_text.bind('<Button-4>', lambda e: self.chat_text.yview_scroll(-2, 'units'))
        self.chat_text.bind('<Button-5>', lambda e: self.chat_text.yview_scroll(2, 'units'))
        
        # Ввод
        input_frame = tk.Frame(sec, bg=self.COLOR_BG_OVERLAY)
        input_frame.pack(fill=tk.X, pady=(4, 0))
        
        self.input_var = tk.StringVar()
        input_entry = tk.Entry(input_frame, textvariable=self.input_var, font=("Arial", 10),
                              bg=self.COLOR_BG, fg=self.COLOR_TEXT, relief=tk.FLAT,
                              insertbackground=self.COLOR_TEXT,
                              highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        input_entry.bind('<Return>', lambda e: self._send_message())
        
        self._button(input_frame, "→", self._send_message, 'primary').pack(side=tk.RIGHT)
        
        # Быстрые действия
        row = self._row(sec)
        for txt, cmd in [('Создать', self._ai_create), ('Улучшить', self._ai_improve),
                         ('Объяснить', self._ai_explain), ('Исправить', self._ai_fix)]:
            self._button(row, txt, cmd).pack(side=tk.LEFT, padx=2)
        
        # === Генератор ===
        sec = self._section(self.content, "Генератор")
        
        row = self._row(sec)
        self._label(row, "Тип:", 6).pack(side=tk.LEFT)
        self.gen_type = tk.StringVar(value='element')
        for val, txt in [('element', 'Элемент'), ('layout', 'Макет'), ('style', 'Стиль')]:
            tk.Radiobutton(row, text=txt, variable=self.gen_type, value=val,
                          font=("Arial", 9), bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT,
                          selectcolor=self.COLOR_BG, activebackground=self.COLOR_BG_OVERLAY
                          ).pack(side=tk.LEFT, padx=4)
        
        row = self._row(sec)
        self._label(row, "Описание:", 10).pack(side=tk.LEFT)
        self.gen_desc = tk.StringVar()
        self._entry(row, self.gen_desc, 25).pack(side=tk.LEFT)
        
        row = self._row(sec)
        self._button(row, "Сгенерировать", self._generate, 'success').pack(side=tk.LEFT, padx=2)
        self._button(row, "Применить", self._apply_generated).pack(side=tk.LEFT, padx=2)
        
        # === Контекст ===
        sec = self._section(self.content, "Контекст")
        
        row = self._row(sec)
        self.ctx_elements = tk.BooleanVar(value=True)
        self._checkbox(row, "Элементы", self.ctx_elements).pack(side=tk.LEFT)
        
        self.ctx_styles = tk.BooleanVar(value=True)
        self._checkbox(row, "Стили", self.ctx_styles).pack(side=tk.LEFT, padx=(8, 0))
        
        self.ctx_canvas = tk.BooleanVar(value=True)
        self._checkbox(row, "Холст", self.ctx_canvas).pack(side=tk.LEFT, padx=(8, 0))
        
        # === Параметры ===
        sec = self._section(self.content, "Параметры")
        
        row = self._row(sec)
        self._label(row, "Температура:", 12).pack(side=tk.LEFT)
        self.temp_var = tk.DoubleVar(value=0.7)
        s = self._scale(row, self.temp_var, 0, 2, 80)
        s.config(resolution=0.1)
        s.pack(side=tk.LEFT)
        tk.Label(row, textvariable=self.temp_var, font=("Arial", 9), width=4,
                bg=self.COLOR_BG_OVERLAY, fg=self.COLOR_TEXT).pack(side=tk.LEFT)
        
        row = self._row(sec)
        self._label(row, "Макс. токенов:", 12).pack(side=tk.LEFT)
        self.tokens_var = tk.StringVar(value='2048')
        self._entry(row, self.tokens_var, 8).pack(side=tk.LEFT)
        
        row = self._row(sec)
        self._button(row, "Тест подключения", self._test_connection).pack(side=tk.LEFT, padx=2)
        self._button(row, "Очистить чат", self._clear_chat).pack(side=tk.LEFT, padx=2)

    def _on_provider_change(self, e=None):
        """При смене провайдера"""
        provider_name = self.provider_var.get()
        for pid, pname, models in self.PROVIDERS:
            if pname == provider_name:
                self.model_combo['values'] = models
                if models:
                    self.model_combo.current(0)
                break

    def _send_message(self):
        """Отправить сообщение"""
        msg = self.input_var.get().strip()
        if not msg:
            return
        
        self.input_var.set('')
        self._add_message('user', msg)
        
        # Получить контекст
        context = self._get_context()
        
        # Отправить запрос (заглушка)
        response = self._call_ai(msg, context)
        self._add_message('ai', response)

    def _add_message(self, role, text):
        """Добавить сообщение в чат"""
        self.chat_text.config(state='normal')
        
        prefix = 'Вы: ' if role == 'user' else 'AI: ' if role == 'ai' else '# '
        self.chat_text.insert(tk.END, f"\n{prefix}", role)
        self.chat_text.insert(tk.END, f"{text}\n", role)
        
        self.chat_text.config(state='disabled')
        self.chat_text.see(tk.END)
        
        self.chat_history.append({'role': role, 'content': text})

    def _get_context(self):
        """Получить контекст интерфейса"""
        context = {}
        
        if self.ctx_elements.get() and self.element_manager:
            elements = []
            for elem in self.element_manager.get_all_elements():
                elements.append({
                    'type': getattr(elem, 'ELEMENT_TYPE', 'unknown'),
                    'x': int(elem.x), 'y': int(elem.y),
                    'width': int(elem.width), 'height': int(elem.height),
                })
            context['elements'] = elements
        
        if self.ctx_canvas.get() and self.main_canvas:
            context['canvas'] = {
                'width': int(self.main_canvas.width),
                'height': int(self.main_canvas.height),
                'color': self.main_canvas.properties.get('fill_color', '#000'),
            }
        
        return context

    def _call_ai(self, message, context):
        """Вызов AI API (заглушка)"""
        # Проверить API ключ
        provider = self.provider_var.get().lower()
        api_key = None
        if self.settings_tab:
            for pid, pname, _ in self.PROVIDERS:
                if pname == self.provider_var.get():
                    api_key = self.settings_tab.get_api_key(pid)
                    break
        
        if not api_key and provider not in ['ollama', 'gpt4all']:
            return "⚠ API ключ не настроен. Перейдите в настройки."
        
        # Заглушка ответа
        return f"Получено сообщение: '{message}'. Контекст: {len(context)} элементов. (AI интеграция в разработке)"

    def _test_connection(self):
        """Тест подключения"""
        self._add_message('system', 'Тестирование подключения...')
        
        provider = self.provider_var.get()
        api_key = None
        if self.settings_tab:
            for pid, pname, _ in self.PROVIDERS:
                if pname == provider:
                    api_key = self.settings_tab.get_api_key(pid)
                    break
        
        if api_key:
            self.status_lbl.config(text="● Подключено", fg=self.COLOR_SUCCESS)
            self._add_message('system', f'Подключение к {provider} установлено')
        else:
            self.status_lbl.config(text="○ Нет ключа", fg=self.COLOR_WARNING)
            self._add_message('system', f'API ключ для {provider} не найден')

    def _clear_chat(self):
        """Очистить чат"""
        self.chat_text.config(state='normal')
        self.chat_text.delete('1.0', tk.END)
        self.chat_text.config(state='disabled')
        self.chat_history.clear()

    def _ai_create(self):
        self.input_var.set("Создай элемент: ")

    def _ai_improve(self):
        self.input_var.set("Улучши выбранный элемент: ")

    def _ai_explain(self):
        self.input_var.set("Объясни структуру интерфейса")
        self._send_message()

    def _ai_fix(self):
        self.input_var.set("Найди и исправь проблемы")
        self._send_message()

    def _generate(self):
        """Генерация по описанию"""
        desc = self.gen_desc.get()
        if not desc:
            return
        
        gen_type = self.gen_type.get()
        self._add_message('user', f"Сгенерируй {gen_type}: {desc}")
        
        response = f"Генерация {gen_type} по описанию '{desc}' (в разработке)"
        self._add_message('ai', response)

    def _apply_generated(self):
        """Применить сгенерированное"""
        self._add_message('system', 'Применение результата генерации...')
