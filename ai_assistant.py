#!/usr/bin/env python3
"""
AI Assistant Module
Локальный ИИ-помощник для автоматизации создания интерфейсов
Использует GPT4All для работы без сервера
"""
import os
import json
import threading
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class AIModelType(Enum):
    """Типы доступных моделей"""
    TINY = "orca-mini-3b-gguf2-q4_0.gguf"  # ~2GB, быстрая
    SMALL = "Phi-3-mini-4k-instruct.Q4_0.gguf"  # ~2.3GB, умная
    MEDIUM = "mistral-7b-instruct-v0.1.Q4_0.gguf"  # ~4GB, качественная
    CODE = "replit-code-v1_5-3b-q4_0.gguf"  # ~2GB, для кода


@dataclass
class AIResponse:
    """Ответ от ИИ"""
    success: bool
    text: str
    tokens_used: int = 0
    generation_time: float = 0.0
    error: Optional[str] = None


class AIAssistant:
    """
    Локальный ИИ-помощник для автоматизации создания интерфейсов
    """
    
    # Системные промпты для разных задач
    SYSTEM_PROMPTS = {
        'general': """Ты помощник для создания пользовательских интерфейсов.
Отвечай кратко и по делу. Генерируй только запрошенный код без лишних объяснений.""",

        'code_generator': """Ты генератор кода для UI-элементов.
Генерируй только Python/tkinter код. Без объяснений, только код.
Используй классы из проекта: ElementBase, FrameElement, PanelElement, ButtonElement.
Следуй паттернам проекта.""",

        'css_generator': """Ты генератор CSS стилей.
Создавай современные, красивые CSS стили.
Используй CSS переменные, flexbox, grid.
Возвращай только CSS код.""",

        'html_generator': """Ты генератор HTML разметки.
Создавай семантически правильный HTML5.
Используй современные теги и атрибуты.
Возвращай только HTML код.""",

        'mechanism_creator': """Ты создатель механизмов анимации.
Генерируй параметры для механизмов: MoveTrackMechanism, RotatorMechanism, ScaleMechanism, etc.
Возвращай JSON с параметрами механизма.""",

        'layout_designer': """Ты дизайнер макетов интерфейсов.
Предлагай оптимальное расположение элементов.
Возвращай JSON со структурой: {elements: [{type, x, y, width, height, properties}]}""",

        'color_advisor': """Ты советник по цветовым схемам.
Предлагай гармоничные цветовые палитры.
Возвращай JSON: {primary, secondary, accent, background, text, success, warning, error}""",
        
        'automation': """Ты автоматизатор процессов создания UI.
Анализируй запрос и генерируй последовательность действий.
Возвращай JSON: {actions: [{type, params}]}"""
    }
    
    # Шаблоны для генерации
    TEMPLATES = {
        'button': '''
class CustomButton(ButtonElement):
    def __init__(self, canvas, x, y, width=100, height=40):
        super().__init__(canvas, x, y, width, height)
        self.properties.update({
            'text': '{text}',
            'fill_color': '{bg_color}',
            'text_color': '{text_color}',
            'corner_radius': {radius},
            'hover_effect': {hover}
        })
''',
        'panel': '''
class CustomPanel(PanelElement):
    def __init__(self, canvas, x, y, width=200, height=150):
        super().__init__(canvas, x, y, width, height)
        self.properties.update({
            'fill_color': '{bg_color}',
            'stroke_color': '{border_color}',
            'corner_radius': {radius},
            'shadow_enabled': {shadow}
        })
''',
        'animation': '''
mechanism = {mechanism_type}(
    canvas=canvas,
    speed={speed},
    duration={duration},
    easing='{easing}',
    loop={loop}
)
mechanism.attach(element)
mechanism.start()
'''
    }

    def __init__(self, model_type: AIModelType = AIModelType.TINY):
        self.model_type = model_type
        self.model = None
        self.model_path = os.path.expanduser("~/.local/share/nomic.ai/GPT4All/")
        self.is_loaded = False
        self.is_loading = False
        self.callbacks: Dict[str, List[Callable]] = {
            'on_load': [],
            'on_response': [],
            'on_error': []
        }
        
        # Кэш для быстрых ответов
        self.response_cache: Dict[str, str] = {}
        self.cache_enabled = True
        
        # Настройки генерации
        self.settings = {
            'max_tokens': 500,
            'temperature': 0.7,
            'top_p': 0.9,
            'repeat_penalty': 1.1
        }

    def on(self, event: str, callback: Callable):
        """Подписка на события"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def off(self, event: str, callback: Callable):
        """Отписка от события"""
        if event in self.callbacks and callback in self.callbacks[event]:
            self.callbacks[event].remove(callback)

    def _emit(self, event: str, *args, **kwargs):
        """Вызов колбэков события"""
        for callback in self.callbacks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"[AIAssistant] Callback error: {e}")

    def load_model(self, callback: Optional[Callable] = None):
        """Загружает модель в фоновом потоке"""
        if self.is_loaded or self.is_loading:
            if callback:
                callback(self.is_loaded)
            return
        
        self.is_loading = True
        
        def _load():
            try:
                from gpt4all import GPT4All
                
                # Создаём директорию для моделей если нет
                os.makedirs(self.model_path, exist_ok=True)
                
                # Загружаем модель (скачает автоматически если нет)
                self.model = GPT4All(
                    model_name=self.model_type.value,
                    model_path=self.model_path,
                    allow_download=True,
                    verbose=False
                )
                
                self.is_loaded = True
                self.is_loading = False
                
                self._emit('on_load', True)
                if callback:
                    callback(True)
                    
            except Exception as e:
                self.is_loading = False
                self._emit('on_error', str(e))
                if callback:
                    callback(False)
        
        thread = threading.Thread(target=_load, daemon=True)
        thread.start()

    def unload_model(self):
        """Выгружает модель из памяти"""
        if self.model:
            del self.model
            self.model = None
            self.is_loaded = False

    def generate(self, prompt: str, task_type: str = 'general', 
                 callback: Optional[Callable[[AIResponse], None]] = None) -> Optional[AIResponse]:
        """
        Генерирует ответ от ИИ
        
        Args:
            prompt: Запрос пользователя
            task_type: Тип задачи (general, code_generator, css_generator, etc.)
            callback: Колбэк для асинхронного ответа
        """
        # Проверяем кэш
        cache_key = f"{task_type}:{prompt}"
        if self.cache_enabled and cache_key in self.response_cache:
            response = AIResponse(
                success=True,
                text=self.response_cache[cache_key],
                tokens_used=0,
                generation_time=0.0
            )
            if callback:
                callback(response)
            return response
        
        if not self.is_loaded:
            error_response = AIResponse(
                success=False,
                text="",
                error="Модель не загружена. Вызовите load_model() сначала."
            )
            if callback:
                callback(error_response)
            return error_response
        
        def _generate():
            import time
            start_time = time.time()
            
            try:
                system_prompt = self.SYSTEM_PROMPTS.get(task_type, self.SYSTEM_PROMPTS['general'])
                
                with self.model.chat_session(system_prompt):
                    response_text = self.model.generate(
                        prompt,
                        max_tokens=self.settings['max_tokens'],
                        temp=self.settings['temperature'],
                        top_p=self.settings['top_p'],
                        repeat_penalty=self.settings['repeat_penalty']
                    )
                
                generation_time = time.time() - start_time
                
                # Кэшируем ответ
                if self.cache_enabled:
                    self.response_cache[cache_key] = response_text
                
                response = AIResponse(
                    success=True,
                    text=response_text,
                    tokens_used=len(response_text.split()),
                    generation_time=generation_time
                )
                
                self._emit('on_response', response)
                if callback:
                    callback(response)
                    
            except Exception as e:
                response = AIResponse(
                    success=False,
                    text="",
                    error=str(e)
                )
                self._emit('on_error', str(e))
                if callback:
                    callback(response)
        
        if callback:
            thread = threading.Thread(target=_generate, daemon=True)
            thread.start()
            return None
        else:
            # Синхронный режим
            _generate()

    # === Специализированные методы ===
    
    def generate_element(self, description: str, callback: Optional[Callable] = None) -> Optional[Dict]:
        """Генерирует код элемента по описанию"""
        prompt = f"Создай UI элемент: {description}. Верни JSON с параметрами."
        
        def process_response(response: AIResponse):
            if response.success:
                try:
                    # Пытаемся извлечь JSON из ответа
                    text = response.text
                    start = text.find('{')
                    end = text.rfind('}') + 1
                    if start >= 0 and end > start:
                        result = json.loads(text[start:end])
                        if callback:
                            callback(result)
                        return result
                except json.JSONDecodeError:
                    pass
            if callback:
                callback(None)
            return None
        
        self.generate(prompt, 'code_generator', process_response)

    def generate_layout(self, description: str, canvas_size: tuple, 
                       callback: Optional[Callable] = None) -> Optional[Dict]:
        """Генерирует макет интерфейса"""
        prompt = f"""Создай макет интерфейса: {description}
Размер холста: {canvas_size[0]}x{canvas_size[1]} пикселей.
Верни JSON: {{elements: [{{type, x, y, width, height, properties}}]}}"""
        
        def process_response(response: AIResponse):
            if response.success:
                try:
                    text = response.text
                    start = text.find('{')
                    end = text.rfind('}') + 1
                    if start >= 0 and end > start:
                        result = json.loads(text[start:end])
                        if callback:
                            callback(result)
                        return result
                except json.JSONDecodeError:
                    pass
            if callback:
                callback(None)
            return None
        
        self.generate(prompt, 'layout_designer', process_response)

    def generate_color_palette(self, style: str, callback: Optional[Callable] = None) -> Optional[Dict]:
        """Генерирует цветовую палитру"""
        prompt = f"""Создай цветовую палитру в стиле: {style}
Верни JSON: {{primary, secondary, accent, background, text, success, warning, error}}
Все цвета в формате HEX (#RRGGBB)."""
        
        def process_response(response: AIResponse):
            if response.success:
                try:
                    text = response.text
                    start = text.find('{')
                    end = text.rfind('}') + 1
                    if start >= 0 and end > start:
                        result = json.loads(text[start:end])
                        if callback:
                            callback(result)
                        return result
                except json.JSONDecodeError:
                    pass
            if callback:
                callback(None)
            return None
        
        self.generate(prompt, 'color_advisor', process_response)

    def generate_animation(self, element_type: str, effect: str, 
                          callback: Optional[Callable] = None) -> Optional[Dict]:
        """Генерирует параметры анимации"""
        prompt = f"""Создай анимацию для элемента {element_type}: {effect}
Верни JSON: {{mechanism_type, speed, duration, easing, loop, params}}"""
        
        def process_response(response: AIResponse):
            if response.success:
                try:
                    text = response.text
                    start = text.find('{')
                    end = text.rfind('}') + 1
                    if start >= 0 and end > start:
                        result = json.loads(text[start:end])
                        if callback:
                            callback(result)
                        return result
                except json.JSONDecodeError:
                    pass
            if callback:
                callback(None)
            return None
        
        self.generate(prompt, 'mechanism_creator', process_response)

    def generate_css(self, description: str, callback: Optional[Callable] = None) -> Optional[str]:
        """Генерирует CSS код"""
        prompt = f"Создай CSS стили: {description}. Только CSS код, без объяснений."
        
        def process_response(response: AIResponse):
            if response.success:
                # Извлекаем CSS из ответа
                text = response.text
                # Убираем markdown обертку если есть
                if '```css' in text:
                    start = text.find('```css') + 6
                    end = text.find('```', start)
                    text = text[start:end].strip()
                elif '```' in text:
                    start = text.find('```') + 3
                    end = text.find('```', start)
                    text = text[start:end].strip()
                
                if callback:
                    callback(text)
                return text
            if callback:
                callback(None)
            return None
        
        self.generate(prompt, 'css_generator', process_response)

    def generate_html(self, description: str, callback: Optional[Callable] = None) -> Optional[str]:
        """Генерирует HTML код"""
        prompt = f"Создай HTML разметку: {description}. Только HTML код, без объяснений."
        
        def process_response(response: AIResponse):
            if response.success:
                text = response.text
                if '```html' in text:
                    start = text.find('```html') + 7
                    end = text.find('```', start)
                    text = text[start:end].strip()
                elif '```' in text:
                    start = text.find('```') + 3
                    end = text.find('```', start)
                    text = text[start:end].strip()
                
                if callback:
                    callback(text)
                return text
            if callback:
                callback(None)
            return None
        
        self.generate(prompt, 'html_generator', process_response)

    def automate_task(self, task_description: str, 
                      callback: Optional[Callable] = None) -> Optional[List[Dict]]:
        """Создаёт последовательность действий для автоматизации"""
        prompt = f"""Автоматизируй задачу: {task_description}
Доступные действия: create_element, set_property, add_animation, apply_style, group_elements
Верни JSON: {{actions: [{{type, params}}]}}"""
        
        def process_response(response: AIResponse):
            if response.success:
                try:
                    text = response.text
                    start = text.find('{')
                    end = text.rfind('}') + 1
                    if start >= 0 and end > start:
                        result = json.loads(text[start:end])
                        actions = result.get('actions', [])
                        if callback:
                            callback(actions)
                        return actions
                except json.JSONDecodeError:
                    pass
            if callback:
                callback(None)
            return None
        
        self.generate(prompt, 'automation', process_response)

    def clear_cache(self):
        """Очищает кэш ответов"""
        self.response_cache.clear()

    def get_model_info(self) -> Dict[str, Any]:
        """Возвращает информацию о модели"""
        return {
            'model_type': self.model_type.value,
            'is_loaded': self.is_loaded,
            'is_loading': self.is_loading,
            'cache_size': len(self.response_cache),
            'settings': self.settings.copy()
        }


# Глобальный экземпляр (singleton)
_ai_assistant: Optional[AIAssistant] = None


def get_ai_assistant(model_type: AIModelType = AIModelType.TINY) -> AIAssistant:
    """Возвращает глобальный экземпляр AI-помощника"""
    global _ai_assistant
    if _ai_assistant is None:
        _ai_assistant = AIAssistant(model_type)
    return _ai_assistant

