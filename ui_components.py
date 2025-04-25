# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QLineEdit, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QPalette, QColor, QLinearGradient, QPainter
from PyQt5.QtCore import Qt, pyqtSignal

# 通用样式常量
COMMON_STYLES = {
    'font_family': 'Microsoft YaHei',
    'border_radius': '10px',
    'backdrop_filter': 'blur(10px)',
    'background_opacity': 0.7,
    'border_color': 'rgba(255, 255, 255, 0.2)'
}

class UIComponents:
    """UI组件管理类"""
    @staticmethod
    def create_styled_entry(parent, width=20, bind_submit=None):
        entry = QLineEdit(parent)
        entry.setFixedWidth(width * 12)
        entry.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px 15px;
                border: 2px solid rgba(221, 221, 221, 0.8);
                border-radius: 8px;
                font-family: {COMMON_STYLES['font_family']};
                font-size: 15px;
                background-color: rgba(255, 255, 255, 0.85);
                backdrop-filter: {COMMON_STYLES['backdrop_filter']};
            }}
            QLineEdit:focus {{
                border-color: rgba(74, 144, 226, 0.8);
                background-color: rgba(255, 255, 255, 0.95);
                outline: none;
            }}
        """)
        entry.setAttribute(Qt.WA_TranslucentBackground)
        entry.setAlignment(Qt.AlignCenter)
        
        if bind_submit:
            entry.returnPressed.connect(bind_submit)
        return entry
    
    @staticmethod
    def create_label(parent, text, font_size, bg_color, **kwargs):
        label = QLabel(text, parent)
        label.setStyleSheet(f"""
            QLabel {{
                font-family: {COMMON_STYLES['font_family']};
                font-size: {font_size}px;
                background-color: rgba(255, 255, 255, {COMMON_STYLES['background_opacity']});
                padding: 15px 20px;
                border-radius: {COMMON_STYLES['border_radius']};
                color: #333;
                font-weight: 500;
                backdrop-filter: {COMMON_STYLES['backdrop_filter']};
                border: 1px solid {COMMON_STYLES['border_color']};
            }}
        """)
        
        label.setAlignment(Qt.AlignCenter if 'anchor' not in kwargs or kwargs['anchor'] != 'nw'
                          else Qt.AlignLeft | Qt.AlignTop)
        return label

class ThemeManager:
    """主题管理类"""
    THEMES = {
        '蓝色主题': {
            'start': {'r': 230, 'g': 243, 'b': 255},  # E6F3FF
            'end': {'r': 184, 'g': 226, 'b': 255},    # B8E2FF
            'button': '#4a90e2',
            'button_hover': '#357abd',
            'button_pressed': '#2a5f9e'
        },
        '绿色主题': {
            'start': {'r': 230, 'g': 255, 'b': 230},  # E6FFE6
            'end': {'r': 184, 'g': 255, 'b': 184},    # B8FFB8
            'button': '#4CAF50',
            'button_hover': '#388E3C',
            'button_pressed': '#2E7D32'
        },
        '紫色主题': {
            'start': {'r': 243, 'g': 230, 'b': 255},  # F3E6FF
            'end': {'r': 226, 'g': 184, 'b': 255},    # E2B8FF
            'button': '#9C27B0',
            'button_hover': '#7B1FA2',
            'button_pressed': '#6A1B9A'
        },
        '暗色主题': {
            'start': {'r': 48, 'g': 48, 'b': 48},     # 303030
            'end': {'r': 33, 'g': 33, 'b': 33},       # 212121
            'button': '#424242',
            'button_hover': '#616161',
            'button_pressed': '#757575'
        },
        '日落主题': {
            'start': {'r': 255, 'g': 231, 'b': 217},  # FFE7D9
            'end': {'r': 255, 'g': 183, 'b': 153},    # FFB799
            'button': '#FF5722',
            'button_hover': '#F4511E',
            'button_pressed': '#E64A19'
        }
    }
    
    @staticmethod
    def get_theme_color(theme_name):
        theme = ThemeManager.THEMES[theme_name]
        return "#{:02x}{:02x}{:02x}".format(
            theme['start']['r'],
            theme['start']['g'],
            theme['start']['b']
        )
    
    @staticmethod
    def create_gradient_background(parent, theme_name):
        theme = ThemeManager.THEMES[theme_name]
        start, end = theme['start'], theme['end']
        
        gradient = QLinearGradient(0, 0, 0, parent.height())
        gradient.setColorAt(0.0, QColor(start['r'], start['g'], start['b']))
        gradient.setColorAt(1.0, QColor(end['r'], end['g'], end['b']))
        
        palette = parent.palette()
        palette.setBrush(QPalette.Window, gradient)
        parent.setPalette(palette)
        parent.setAutoFillBackground(True)