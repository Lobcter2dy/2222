"""
Функциональные артефакты - панели с встроенным функционалом
"""

from .base import FunctionalArtifact, ArtifactRegistry
from .file_browser import FileBrowserArtifact
from .code_editor import CodeEditorArtifact

__all__ = [
    'FunctionalArtifact',
    'ArtifactRegistry', 
    'FileBrowserArtifact',
    'CodeEditorArtifact'
]

