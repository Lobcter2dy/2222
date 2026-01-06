#!/usr/bin/env python3
"""
Генератор кода
Преобразует элементы холста в HTML/CSS/JavaScript
"""


class CodeGenerator:
    """Генератор кода из элементов"""

    def __init__(self):
        self.elements = []
        self.main_canvas = None
        
        # Настройки генерации
        self.settings = {
            'use_css_variables': True,
            'use_flexbox': True,
            'minify': False,
            'include_comments': True,
        }

    def set_elements(self, elements, main_canvas=None):
        """Устанавливает элементы для генерации"""
        self.elements = elements
        self.main_canvas = main_canvas

    def generate_all(self):
        """Генерирует полный HTML документ"""
        html = self.generate_html()
        css = self.generate_css()
        js = self.generate_js()
        
        return f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Interface</title>
    <style>
{self._indent(css, 2)}
    </style>
</head>
<body>
{self._indent(html, 1)}
    <script>
{self._indent(js, 2)}
    </script>
</body>
</html>'''

    def generate_html(self):
        """Генерирует HTML разметку"""
        lines = []
        
        if self.settings['include_comments']:
            lines.append('<!-- Generated Interface -->')
        
        # Контейнер (главная панель)
        if self.main_canvas:
            lines.append(f'<div class="main-container" id="main-container">')
        
        # Элементы
        for element in self.elements:
            html = self._element_to_html(element)
            if html:
                lines.append(f'    {html}')
        
        if self.main_canvas:
            lines.append('</div>')
        
        return '\n'.join(lines)

    def generate_css(self):
        """Генерирует CSS стили"""
        lines = []
        
        if self.settings['include_comments']:
            lines.append('/* Generated Styles */')
            lines.append('')
        
        # CSS переменные
        if self.settings['use_css_variables']:
            lines.append(':root {')
            lines.append('    --primary-color: #ffffff;')
            lines.append('    --background-color: #000000;')
            lines.append('    --border-color: #333333;')
            lines.append('}')
            lines.append('')
        
        # Базовые стили
        lines.append('* {')
        lines.append('    box-sizing: border-box;')
        lines.append('    margin: 0;')
        lines.append('    padding: 0;')
        lines.append('}')
        lines.append('')
        
        # Стили главного контейнера
        if self.main_canvas:
            lines.append('.main-container {')
            lines.append('    position: relative;')
            lines.append(f'    width: {self.main_canvas.width}px;')
            lines.append(f'    height: {self.main_canvas.height}px;')
            lines.append(f'    background-color: {self.main_canvas.properties.get("fill_color", "#000000")};')
            stroke = self.main_canvas.properties.get("stroke_color", "#333333")
            stroke_w = self.main_canvas.properties.get("stroke_width", 1)
            if stroke and stroke_w:
                lines.append(f'    border: {stroke_w}px solid {stroke};')
            lines.append('    margin: 0 auto;')
            lines.append('}')
            lines.append('')
        
        # Стили элементов
        for element in self.elements:
            css = self._element_to_css(element)
            if css:
                lines.append(css)
                lines.append('')
        
        return '\n'.join(lines)

    def generate_js(self):
        """Генерирует JavaScript код"""
        lines = []
        
        if self.settings['include_comments']:
            lines.append('// Generated JavaScript')
            lines.append('')
        
        lines.append('document.addEventListener("DOMContentLoaded", function() {')
        lines.append('    // Initialization')
        lines.append('    console.log("Interface loaded");')
        lines.append('')
        
        # Обработчики для элементов
        for element in self.elements:
            js = self._element_to_js(element)
            if js:
                lines.append(self._indent(js, 1))
        
        lines.append('});')
        
        return '\n'.join(lines)

    def _element_to_html(self, element):
        """Преобразует элемент в HTML"""
        el_type = element.ELEMENT_TYPE
        el_id = element.id.replace('_', '-')
        
        if el_type == 'frame':
            return f'<div class="frame {el_id}" id="{el_id}"></div>'
        elif el_type == 'panel':
            return f'<div class="panel {el_id}" id="{el_id}"></div>'
        
        return f'<div class="element {el_id}" id="{el_id}"></div>'

    def _element_to_css(self, element):
        """Преобразует свойства элемента в CSS"""
        el_id = element.id.replace('_', '-')
        props = element.properties
        
        lines = [f'.{el_id} {{']
        lines.append('    position: absolute;')
        
        # Позиция (относительно главного контейнера)
        x = element.x
        y = element.y
        if self.main_canvas:
            x -= self.main_canvas.x
            y -= self.main_canvas.y
        
        lines.append(f'    left: {int(x)}px;')
        lines.append(f'    top: {int(y)}px;')
        lines.append(f'    width: {int(element.width)}px;')
        lines.append(f'    height: {int(element.height)}px;')
        
        # Цвета
        fill = props.get('fill_color', '')
        stroke = props.get('stroke_color', '#ffffff')
        stroke_width = props.get('stroke_width', 2)
        display_mode = props.get('display_mode', 'stroke')
        
        # Заливка
        if display_mode in ('fill', 'both') and fill:
            lines.append(f'    background-color: {fill};')
        else:
            lines.append('    background-color: transparent;')
        
        # Обводка
        if display_mode in ('stroke', 'both') and stroke:
            line_style = props.get('line_style', 'solid')
            css_style = self._line_style_to_css(line_style)
            lines.append(f'    border: {stroke_width}px {css_style} {stroke};')
        
        # Скругление углов
        shape = props.get('shape', 'rectangle')
        corner_radius = props.get('corner_radius', 0)
        
        if shape == 'pill':
            lines.append('    border-radius: 9999px;')
        elif shape == 'rounded' and corner_radius > 0:
            # Проверяем индивидуальные углы
            tl = props.get('corner_tl')
            tr = props.get('corner_tr')
            bl = props.get('corner_bl')
            br = props.get('corner_br')
            
            if any(c is not None for c in [tl, tr, bl, br]):
                tl = tl if tl is not None else corner_radius
                tr = tr if tr is not None else corner_radius
                br = br if br is not None else corner_radius
                bl = bl if bl is not None else corner_radius
                lines.append(f'    border-radius: {tl}px {tr}px {br}px {bl}px;')
            else:
                lines.append(f'    border-radius: {corner_radius}px;')
        elif shape == 'chamfer':
            # CSS clip-path для скошенных углов
            chamfer = props.get('chamfer_size', 10)
            lines.append(f'    clip-path: polygon({chamfer}px 0, calc(100% - {chamfer}px) 0, 100% {chamfer}px, 100% calc(100% - {chamfer}px), calc(100% - {chamfer}px) 100%, {chamfer}px 100%, 0 calc(100% - {chamfer}px), 0 {chamfer}px);')
        
        # Тень
        if props.get('shadow_enabled'):
            sx = props.get('shadow_x', 2)
            sy = props.get('shadow_y', 2)
            color = props.get('shadow_color', '#000000')
            lines.append(f'    box-shadow: {sx}px {sy}px 8px {color};')
        
        # Внутренняя тень
        if props.get('inset_shadow'):
            size = props.get('inset_shadow_size', 5)
            color = props.get('inset_shadow_color', '#000000')
            lines.append(f'    box-shadow: inset 0 0 {size}px {color};')
        
        # Свечение
        if props.get('glow_enabled'):
            radius = props.get('glow_radius', 5)
            color = props.get('glow_color', '#ffffff')
            # Добавляем к существующей тени или создаём новую
            if props.get('shadow_enabled') or props.get('inset_shadow'):
                # Уже есть box-shadow, нужно добавить
                pass
            else:
                lines.append(f'    box-shadow: 0 0 {radius}px {color};')
        
        # Двойная рамка
        if props.get('double_border'):
            gap = props.get('double_border_gap', 3)
            color = props.get('double_border_color') or stroke
            lines.append(f'    outline: {stroke_width}px solid {color};')
            lines.append(f'    outline-offset: {gap}px;')
        
        lines.append('}')
        return '\n'.join(lines)

    def _element_to_js(self, element):
        """Генерирует JavaScript для элемента"""
        el_id = element.id.replace('_', '-')
        
        lines = []
        lines.append(f'// Element: {el_id}')
        lines.append(f'const {el_id.replace("-", "_")} = document.getElementById("{el_id}");')
        lines.append(f'{el_id.replace("-", "_")}.addEventListener("click", function(e) {{')
        lines.append(f'    console.log("Clicked: {el_id}");')
        lines.append('});')
        
        return '\n'.join(lines)

    def _line_style_to_css(self, style):
        """Преобразует стиль линии в CSS"""
        styles = {
            'solid': 'solid',
            'dashed': 'dashed',
            'dotted': 'dotted',
            'dash_dot': 'dashed',
            'long_dash': 'dashed',
        }
        return styles.get(style, 'solid')

    def _indent(self, text, level):
        """Добавляет отступы"""
        indent = '    ' * level
        return '\n'.join(indent + line if line else '' for line in text.split('\n'))

    # === Экспорт отдельных частей ===
    
    def export_html_only(self):
        """Экспортирует только HTML"""
        return self.generate_html()

    def export_css_only(self):
        """Экспортирует только CSS"""
        return self.generate_css()

    def export_js_only(self):
        """Экспортирует только JavaScript"""
        return self.generate_js()

    def export_react_component(self):
        """Экспортирует как React компонент"""
        lines = []
        lines.append('import React from "react";')
        lines.append('import "./styles.css";')
        lines.append('')
        lines.append('export default function GeneratedInterface() {')
        lines.append('    return (')
        lines.append('        <div className="main-container">')
        
        for element in self.elements:
            el_id = element.id.replace('_', '-')
            el_type = element.ELEMENT_TYPE
            lines.append(f'            <div className="{el_type} {el_id}" />')
        
        lines.append('        </div>')
        lines.append('    );')
        lines.append('}')
        
        return '\n'.join(lines)

    def export_vue_component(self):
        """Экспортирует как Vue компонент"""
        html = self.generate_html()
        css = self.generate_css()
        
        return f'''<template>
{self._indent(html, 1)}
</template>

<script>
export default {{
    name: "GeneratedInterface",
    mounted() {{
        console.log("Interface loaded");
    }}
}}
</script>

<style scoped>
{css}
</style>'''

