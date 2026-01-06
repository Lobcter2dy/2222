# -*- coding: utf-8 -*-
"""Менеджер артефактов (заготовок)"""

import os
import json
import uuid
from datetime import datetime


class Artifact:
    """Артефакт - заготовка интерфейса"""
    
    def __init__(self, artifact_id=None):
        self.id = artifact_id or str(uuid.uuid4())[:8]
        self.name = "Новый артефакт"
        self.description = ""
        self.icon = "◆"
        self.category = "general"
        self.created = datetime.now().isoformat()
        self.modified = datetime.now().isoformat()
        
        # Данные артефакта
        self.html = ""
        self.css = ""
        self.js = ""
        
        # Элементы артефакта
        self.elements = []  # Список дочерних элементов
        self.main_element = None  # Основной элемент
        
        # Стиль
        self.style = {
            'bg_color': '#1a1a1a',
            'text_color': '#e0e0e0',
            'accent_color': '#32b8c6',
            'border_color': '#2a2a2a'
        }
        
        # Размеры по умолчанию
        self.default_width = 400
        self.default_height = 300
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'category': self.category,
            'created': self.created,
            'modified': self.modified,
            'html': self.html,
            'css': self.css,
            'js': self.js,
            'elements': self.elements,
            'main_element': self.main_element,
            'style': self.style,
            'default_width': self.default_width,
            'default_height': self.default_height
        }
    
    @classmethod
    def from_dict(cls, data):
        artifact = cls(data.get('id'))
        artifact.name = data.get('name', 'Артефакт')
        artifact.description = data.get('description', '')
        artifact.icon = data.get('icon', '◆')
        artifact.category = data.get('category', 'general')
        artifact.created = data.get('created', datetime.now().isoformat())
        artifact.modified = data.get('modified', datetime.now().isoformat())
        artifact.html = data.get('html', '')
        artifact.css = data.get('css', '')
        artifact.js = data.get('js', '')
        artifact.elements = data.get('elements', [])
        artifact.main_element = data.get('main_element')
        artifact.style = data.get('style', {})
        artifact.default_width = data.get('default_width', 400)
        artifact.default_height = data.get('default_height', 300)
        return artifact


class ArtifactManager:
    """Менеджер артефактов"""
    
    CATEGORIES = {
        'general': {'name': 'Общие', 'icon': '◆'},
        'navigation': {'name': 'Навигация', 'icon': '☰'},
        'forms': {'name': 'Формы', 'icon': '☐'},
        'cards': {'name': 'Карточки', 'icon': '▢'},
        'panels': {'name': 'Панели', 'icon': '▣'},
        'widgets': {'name': 'Виджеты', 'icon': '⬡'},
        'custom': {'name': 'Пользовательские', 'icon': '★'}
    }
    
    def __init__(self, artifacts_dir=None):
        self.artifacts_dir = artifacts_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'artifacts'
        )
        self.artifacts = []
        self.selected_artifact = None
        self._selection_callbacks = []
        
        self._ensure_dir()
        self._load_artifacts()
        self._create_default_artifacts()
    
    def _ensure_dir(self):
        """Создаёт папку артефактов"""
        if not os.path.exists(self.artifacts_dir):
            os.makedirs(self.artifacts_dir)
    
    def _load_artifacts(self):
        """Загружает артефакты из папки"""
        self.artifacts = []
        for filename in os.listdir(self.artifacts_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.artifacts_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.artifacts.append(Artifact.from_dict(data))
                except Exception as e:
                    print(f"Ошибка загрузки артефакта {filename}: {e}")
    
    def _create_default_artifacts(self):
        """Создаёт артефакты по умолчанию"""
        # Проверяем есть ли уже артефакты
        if self.get_artifact_by_name('Directory Browser'):
            return
        
        # Артефакт Directory Browser
        browser = Artifact()
        browser.name = "Directory Browser"
        browser.description = "Браузер директорий с древовидной структурой"
        browser.icon = "📁"
        browser.category = "navigation"
        browser.default_width = 600
        browser.default_height = 400
        browser.style = {
            'bg_color': '#0f0f0f',
            'text_color': '#e0e0e0',
            'accent_color': '#32b8c6',
            'border_color': '#2a2a2a'
        }
        browser.elements = [
            {'type': 'header', 'name': 'Заголовок', 'icon': '▬'},
            {'type': 'breadcrumb', 'name': 'Путь', 'icon': '→'},
            {'type': 'tree', 'name': 'Дерево', 'icon': '☰'},
            {'type': 'sidebar', 'name': 'Боковая панель', 'icon': '▮'},
            {'type': 'context_menu', 'name': 'Контекстное меню', 'icon': '▤'}
        ]
        
        self.add_artifact(browser)
        
        # Артефакт Simple Card
        card = Artifact()
        card.name = "Simple Card"
        card.description = "Простая карточка с заголовком и контентом"
        card.icon = "▢"
        card.category = "cards"
        card.default_width = 300
        card.default_height = 200
        card.style = {
            'bg_color': '#1a1a1a',
            'text_color': '#ffffff',
            'accent_color': '#4a90d9',
            'border_color': '#333333'
        }
        card.elements = [
            {'type': 'title', 'name': 'Заголовок', 'icon': 'T'},
            {'type': 'content', 'name': 'Контент', 'icon': '¶'},
            {'type': 'footer', 'name': 'Подвал', 'icon': '▬'}
        ]
        
        self.add_artifact(card)
        
        # Артефакт Button Group
        buttons = Artifact()
        buttons.name = "Button Group"
        buttons.description = "Группа кнопок с действиями"
        buttons.icon = "▣"
        buttons.category = "forms"
        buttons.default_width = 250
        buttons.default_height = 50
        buttons.elements = [
            {'type': 'btn_primary', 'name': 'Основная', 'icon': '●'},
            {'type': 'btn_secondary', 'name': 'Вторичная', 'icon': '○'},
            {'type': 'btn_danger', 'name': 'Опасная', 'icon': '◉'}
        ]
        
        self.add_artifact(buttons)
    
    def add_artifact(self, artifact):
        """Добавляет артефакт"""
        self.artifacts.append(artifact)
        self._save_artifact(artifact)
    
    def remove_artifact(self, artifact):
        """Удаляет артефакт"""
        if artifact in self.artifacts:
            self.artifacts.remove(artifact)
            filepath = os.path.join(self.artifacts_dir, f"{artifact.id}.json")
            if os.path.exists(filepath):
                os.remove(filepath)
    
    def _save_artifact(self, artifact):
        """Сохраняет артефакт в файл"""
        artifact.modified = datetime.now().isoformat()
        filepath = os.path.join(self.artifacts_dir, f"{artifact.id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(artifact.to_dict(), f, ensure_ascii=False, indent=2)
    
    def save_all(self):
        """Сохраняет все артефакты"""
        for artifact in self.artifacts:
            self._save_artifact(artifact)
    
    def get_all_artifacts(self):
        """Возвращает все артефакты"""
        return self.artifacts
    
    def get_artifacts_by_category(self, category):
        """Возвращает артефакты по категории"""
        return [a for a in self.artifacts if a.category == category]
    
    def get_artifact_by_name(self, name):
        """Возвращает артефакт по имени"""
        for a in self.artifacts:
            if a.name == name:
                return a
        return None
    
    def get_artifact_by_id(self, artifact_id):
        """Возвращает артефакт по ID"""
        for a in self.artifacts:
            if a.id == artifact_id:
                return a
        return None
    
    def select_artifact(self, artifact):
        """Выбирает артефакт"""
        self.selected_artifact = artifact
        self._notify_selection()
    
    def deselect(self):
        """Снимает выбор"""
        self.selected_artifact = None
        self._notify_selection()
    
    def set_selection_callback(self, callback):
        """Добавляет колбэк выбора"""
        if callback not in self._selection_callbacks:
            self._selection_callbacks.append(callback)
    
    def _notify_selection(self):
        """Уведомляет о смене выбора"""
        for callback in self._selection_callbacks:
            try:
                callback(self.selected_artifact)
            except Exception as e:
                print(f"Artifact selection callback error: {e}")
    
    def create_artifact_from_elements(self, elements, name="Новый артефакт"):
        """Создаёт артефакт из элементов"""
        artifact = Artifact()
        artifact.name = name
        artifact.elements = [
            {
                'type': getattr(e, 'ELEMENT_TYPE', 'unknown'),
                'name': e.id,
                'properties': e.properties.copy() if hasattr(e, 'properties') else {}
            }
            for e in elements
        ]
        self.add_artifact(artifact)
        return artifact

