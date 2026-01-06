# -*- coding: utf-8 -*-
"""
Элемент-артефакт - готовый функциональный виджет
Например: браузер папок, карточка, меню и т.д.
"""
import tkinter as tk
import os
from ..element_base import ElementBase


class ArtifactElement(ElementBase):
    """Элемент-артефакт с встроенным функционалом"""
    
    ELEMENT_TYPE = "artifact"
    ELEMENT_SYMBOL = "◆"
    
    def __init__(self, canvas, config):
        super().__init__(canvas, config)
        self.artifact_type = None  # Тип артефакта
        self.artifact_data = {}    # Данные артефакта
        self.internal_items = []   # Внутренние элементы (для дерева и т.д.)
        self.selected_item = None
        self.expanded = set()
        
        # Свойства по умолчанию
        self.properties.update({
            'fill_color': '#0f0f0f',
            'stroke_color': '#2a2a2a',
            'stroke_width': 1,
            'text_color': '#e0e0e0',
            'accent_color': '#32b8c6',
            'corner_radius': 6
        })
        
        # Данные для Directory Browser
        self.tree_data = None
        self.scroll_offset = 0
    
    def set_artifact_type(self, artifact_type, data=None):
        """Устанавливает тип артефакта"""
        self.artifact_type = artifact_type
        self.artifact_data = data or {}
        
        if artifact_type == 'directory_browser':
            self._init_directory_browser()
        elif artifact_type == 'card':
            self._init_card()
        elif artifact_type == 'menu':
            self._init_menu()
        
        self.update()
    
    def _init_directory_browser(self):
        """Инициализирует браузер директорий"""
        # Демо-данные структуры папок
        self.tree_data = {
            'name': 'root',
            'type': 'folder',
            'expanded': True,
            'children': [
                {
                    'name': 'src',
                    'type': 'folder',
                    'expanded': False,
                    'children': [
                        {'name': 'index.js', 'type': 'file'},
                        {'name': 'utils.js', 'type': 'file'},
                        {
                            'name': 'components',
                            'type': 'folder',
                            'expanded': False,
                            'children': [
                                {'name': 'Button.jsx', 'type': 'file'},
                                {'name': 'Modal.jsx', 'type': 'file'}
                            ]
                        }
                    ]
                },
                {
                    'name': 'public',
                    'type': 'folder',
                    'expanded': False,
                    'children': [
                        {'name': 'index.html', 'type': 'file'},
                        {'name': 'favicon.ico', 'type': 'file'}
                    ]
                },
                {'name': 'package.json', 'type': 'file'},
                {'name': 'README.md', 'type': 'file'}
            ]
        }
        self.expanded.add('root')
    
    def _init_card(self):
        """Инициализирует карточку"""
        self.artifact_data = {
            'title': 'Заголовок',
            'content': 'Содержимое карточки',
            'footer': 'Подвал'
        }
    
    def _init_menu(self):
        """Инициализирует меню"""
        self.artifact_data = {
            'items': [
                {'label': 'Пункт 1', 'icon': '●'},
                {'label': 'Пункт 2', 'icon': '●'},
                {'label': 'Пункт 3', 'icon': '●'},
            ]
        }
    
    def draw(self):
        """Отрисовка артефакта"""
        self.clear()
        
        if not self.is_visible:
            return
        
        x, y, w, h = self._get_screen_coords()
        
        # Фон
        fill = self.properties.get('fill_color', '#0f0f0f')
        stroke = self.properties.get('stroke_color', '#2a2a2a')
        radius = self.properties.get('corner_radius', 6)
        
        # Рамка с закруглёнными углами
        self._draw_rounded_rect(x, y, w, h, radius, fill, stroke)
        
        # Рисуем содержимое в зависимости от типа
        if self.artifact_type == 'directory_browser':
            self._draw_directory_browser(x, y, w, h)
        elif self.artifact_type == 'card':
            self._draw_card(x, y, w, h)
        elif self.artifact_type == 'menu':
            self._draw_menu(x, y, w, h)
        else:
            # Пустой артефакт
            self._draw_placeholder(x, y, w, h)
    
    def _draw_rounded_rect(self, x, y, w, h, r, fill, stroke):
        """Рисует прямоугольник с закруглёнными углами"""
        points = [
            x + r, y,
            x + w - r, y,
            x + w, y,
            x + w, y + r,
            x + w, y + h - r,
            x + w, y + h,
            x + w - r, y + h,
            x + r, y + h,
            x, y + h,
            x, y + h - r,
            x, y + r,
            x, y,
            x + r, y
        ]
        
        item = self.canvas.create_polygon(points, smooth=True, fill=fill, 
                                          outline=stroke, width=1, tags=self.tags)
        self.canvas_items.append(item)
    
    def _draw_directory_browser(self, x, y, w, h):
        """Рисует браузер директорий"""
        text_color = self.properties.get('text_color', '#e0e0e0')
        accent = self.properties.get('accent_color', '#32b8c6')
        
        # Заголовок
        header_h = 30
        item = self.canvas.create_rectangle(x, y, x + w, y + header_h, 
                                           fill='#1a1a1a', outline='#2a2a2a', tags=self.tags)
        self.canvas_items.append(item)
        
        item = self.canvas.create_text(x + 10, y + 15, text="📁 Directory Browser",
                                       fill=accent, font=("Arial", 10, "bold"),
                                       anchor='w', tags=self.tags)
        self.canvas_items.append(item)
        
        # Дерево файлов
        if self.tree_data:
            self._draw_tree_node(self.tree_data, x + 8, y + header_h + 5, w - 16, 0)
    
    def _draw_tree_node(self, node, x, y, w, depth):
        """Рисует узел дерева"""
        if y > self.y + self.height - 20:
            return y  # Выход за границы
        
        text_color = self.properties.get('text_color', '#e0e0e0')
        accent = self.properties.get('accent_color', '#32b8c6')
        
        indent = depth * 16
        
        # Иконка
        if node['type'] == 'folder':
            icon = '📁' if node.get('expanded') else '📂'
            color = accent
        else:
            icon = '📄'
            color = '#8fa0c0'
        
        # Стрелка для папок
        if node['type'] == 'folder' and node.get('children'):
            arrow = '▼' if node.get('expanded') else '▶'
            item = self.canvas.create_text(x + indent, y, text=arrow,
                                          fill='#666', font=("Arial", 8),
                                          anchor='w', tags=self.tags)
            self.canvas_items.append(item)
        
        # Иконка и имя
        item = self.canvas.create_text(x + indent + 14, y, text=f"{icon} {node['name']}",
                                      fill=color, font=("Arial", 9),
                                      anchor='w', tags=self.tags)
        self.canvas_items.append(item)
        
        y += 18
        
        # Дети
        if node['type'] == 'folder' and node.get('expanded') and node.get('children'):
            for child in node['children']:
                y = self._draw_tree_node(child, x, y, w, depth + 1)
        
        return y
    
    def _draw_card(self, x, y, w, h):
        """Рисует карточку"""
        text_color = self.properties.get('text_color', '#e0e0e0')
        accent = self.properties.get('accent_color', '#32b8c6')
        
        # Заголовок
        title = self.artifact_data.get('title', 'Заголовок')
        item = self.canvas.create_text(x + w/2, y + 25, text=title,
                                       fill=accent, font=("Arial", 12, "bold"),
                                       tags=self.tags)
        self.canvas_items.append(item)
        
        # Разделитель
        item = self.canvas.create_line(x + 10, y + 45, x + w - 10, y + 45,
                                       fill='#2a2a2a', tags=self.tags)
        self.canvas_items.append(item)
        
        # Контент
        content = self.artifact_data.get('content', 'Содержимое')
        item = self.canvas.create_text(x + w/2, y + h/2, text=content,
                                       fill=text_color, font=("Arial", 10),
                                       tags=self.tags)
        self.canvas_items.append(item)
        
        # Подвал
        footer = self.artifact_data.get('footer', '')
        if footer:
            item = self.canvas.create_text(x + w/2, y + h - 20, text=footer,
                                          fill='#666', font=("Arial", 9),
                                          tags=self.tags)
            self.canvas_items.append(item)
    
    def _draw_menu(self, x, y, w, h):
        """Рисует меню"""
        text_color = self.properties.get('text_color', '#e0e0e0')
        accent = self.properties.get('accent_color', '#32b8c6')
        
        items = self.artifact_data.get('items', [])
        item_h = 32
        
        for i, menu_item in enumerate(items):
            iy = y + i * item_h + 5
            if iy + item_h > y + h:
                break
            
            # Фон пункта
            bg = '#1a1a1a' if i % 2 == 0 else '#151515'
            rect = self.canvas.create_rectangle(x + 2, iy, x + w - 2, iy + item_h - 2,
                                               fill=bg, outline='', tags=self.tags)
            self.canvas_items.append(rect)
            
            # Текст
            label = menu_item.get('label', 'Пункт')
            icon = menu_item.get('icon', '●')
            txt = self.canvas.create_text(x + 15, iy + item_h/2, 
                                         text=f"{icon}  {label}",
                                         fill=text_color, font=("Arial", 10),
                                         anchor='w', tags=self.tags)
            self.canvas_items.append(txt)
    
    def _draw_placeholder(self, x, y, w, h):
        """Рисует заглушку"""
        text_color = self.properties.get('text_color', '#666')
        item = self.canvas.create_text(x + w/2, y + h/2, 
                                       text="◆ Артефакт",
                                       fill=text_color, font=("Arial", 11),
                                       tags=self.tags)
        self.canvas_items.append(item)
    
    def on_click(self, x, y):
        """Обработка клика внутри артефакта"""
        if self.artifact_type == 'directory_browser':
            # Определяем на какой элемент кликнули
            local_y = y - self.y - 35  # Учитываем header
            if local_y > 0:
                item_index = int(local_y / 18)
                self._toggle_tree_item(item_index)
    
    def _toggle_tree_item(self, index):
        """Переключает раскрытие папки"""
        if not self.tree_data:
            return
        
        # Простой поиск по индексу
        counter = [0]
        self._find_and_toggle(self.tree_data, index, counter)
        self.update()
    
    def _find_and_toggle(self, node, target_index, counter):
        """Находит и переключает узел"""
        if counter[0] == target_index:
            if node['type'] == 'folder':
                node['expanded'] = not node.get('expanded', False)
            return True
        
        counter[0] += 1
        
        if node['type'] == 'folder' and node.get('expanded') and node.get('children'):
            for child in node['children']:
                if self._find_and_toggle(child, target_index, counter):
                    return True
        
        return False
    
    def to_dict(self):
        """Сериализация"""
        data = super().to_dict()
        data['artifact_type'] = self.artifact_type
        data['artifact_data'] = self.artifact_data
        data['tree_data'] = self.tree_data
        return data
    
    @classmethod
    def from_dict(cls, canvas, config, data):
        """Десериализация"""
        element = super().from_dict(canvas, config, data)
        element.artifact_type = data.get('artifact_type')
        element.artifact_data = data.get('artifact_data', {})
        element.tree_data = data.get('tree_data')
        return element

