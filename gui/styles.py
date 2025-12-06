"""
Stil Tanımlamaları
==================
Uygulama genelinde kullanılan renkler, fontlar ve stiller.
"""

class Colors:
    """Renk paleti"""
    PRIMARY = "#4F46E5"       # Indigo 600
    PRIMARY_HOVER = "#4338CA" # Indigo 700
    SECONDARY = "#10B981"     # Emerald 500
    SECONDARY_HOVER = "#059669" # Emerald 600
    ACCENT = "#F59E0B"        # Amber 500
    
    BG_DARK = "#0F172A"       # Slate 900
    BG_DARKER = "#020617"     # Slate 950
    BG_CARD = "#1E293B"       # Slate 800
    
    TEXT_MAIN = "#F8FAFC"     # Slate 50
    TEXT_MUTED = "#94A3B8"    # Slate 400
    
    BORDER = "#334155"        # Slate 700
    
    SUCCESS = "#10B981"
    WARNING = "#F59E0B"
    DANGER = "#EF4444"
    INFO = "#3B82F6"
    WHITE = "#FFFFFF"

class Styles:
    """Qt Style Sheets (QSS)"""
    
    MAIN_WINDOW = f"""
        QMainWindow {{
            background-color: {Colors.BG_DARK};
        }}
        QWidget {{
            background-color: {Colors.BG_DARK};
            color: {Colors.TEXT_MAIN};
            font-family: 'Segoe UI', sans-serif;
            font-size: 14px;
        }}
    """
    
    PAGE_CONTAINER = f"""
        QScrollArea {{
            border: none;
            background-color: {Colors.BG_DARK};
        }}
        QWidget {{
            background-color: {Colors.BG_DARK};
        }}
    """
    
    CARD = f"""
        QFrame {{
            background-color: {Colors.BG_CARD};
            border-radius: 12px;
            border: 1px solid {Colors.BORDER};
        }}
        QLabel {{
            background-color: transparent;
            border: none;
        }}
    """
    
    BUTTON_PRIMARY = f"""
        QPushButton {{
            background-color: {Colors.PRIMARY};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: {Colors.PRIMARY_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {Colors.PRIMARY};
        }}
        QPushButton:disabled {{
            background-color: {Colors.BORDER};
            color: {Colors.TEXT_MUTED};
        }}
    """
    
    BUTTON_OUTLINE = f"""
        QPushButton {{
            background-color: transparent;
            color: {Colors.PRIMARY};
            border: 2px solid {Colors.PRIMARY};
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: {Colors.PRIMARY}20;
        }}
    """
    
    BUTTON_SUCCESS = f"""
        QPushButton {{
            background-color: {Colors.SUCCESS};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: {Colors.SECONDARY_HOVER};
        }}
    """
    
    BUTTON_DANGER = f"""
        QPushButton {{
            background-color: {Colors.DANGER};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: #DC2626;
        }}
    """
    
    LABEL_TITLE = f"""
        QLabel {{
            font-size: 24px;
            font-weight: bold;
            color: {Colors.TEXT_MAIN};
            background-color: transparent;
            margin-bottom: 10px;
        }}
    """
    
    LABEL_SUBTITLE = f"""
        QLabel {{
            font-size: 16px;
            color: {Colors.TEXT_MUTED};
            background-color: transparent;
            margin-bottom: 20px;
        }}
    """
    
    HEADER_LABEL = LABEL_TITLE
    SUBHEADER_LABEL = LABEL_SUBTITLE
    
    TABLE = f"""
        QTableWidget {{
            background-color: {Colors.BG_CARD};
            border: 1px solid {Colors.BORDER};
            border-radius: 8px;
            gridline-color: {Colors.BORDER};
            color: {Colors.TEXT_MAIN};
        }}
        QHeaderView::section {{
            background-color: {Colors.BG_DARKER};
            color: {Colors.TEXT_MAIN};
            padding: 8px;
            border: none;
            font-weight: bold;
        }}
        QTableWidget::item {{
            padding: 5px;
        }}
        QTableWidget::item:selected {{
            background-color: {Colors.PRIMARY}40;
        }}
        QCornerButton::section {{
            background-color: {Colors.BG_DARKER};
        }}
    """
    
    INPUT_FIELD = f"""
        QLineEdit, QSpinBox, QTextEdit {{
            background-color: {Colors.BG_DARKER};
            border: 1px solid {Colors.BORDER};
            border-radius: 6px;
            padding: 8px;
            color: {Colors.TEXT_MAIN};
            font-size: 14px;
        }}
        QLineEdit:focus, QSpinBox:focus, QTextEdit:focus {{
            border: 1px solid {Colors.PRIMARY};
        }}
    """
    
    COMBOBOX = f"""
        QComboBox {{
            background-color: {Colors.BG_DARKER};
            border: 1px solid {Colors.BORDER};
            border-radius: 6px;
            padding: 8px;
            color: {Colors.TEXT_MAIN};
            font-size: 14px;
        }}
        QComboBox:hover {{
            border: 1px solid {Colors.TEXT_MUTED};
        }}
        QComboBox::drop-down {{
            border: none;
        }}
    """
    
    LOG_TEXT = f"""
        QTextEdit {{
            background-color: {Colors.BG_DARKER};
            color: {Colors.TEXT_MAIN};
            border: 1px solid {Colors.BORDER};
            border-radius: 8px;
            padding: 12px;
            font-family: 'Consolas', monospace;
            font-size: 13px;
        }}
    """
    
    PROGRESS_BAR = f"""
        QProgressBar {{
            border: 1px solid {Colors.BORDER};
            border-radius: 6px;
            text-align: center;
            background-color: {Colors.BG_DARKER};
            color: {Colors.TEXT_MAIN};
            height: 24px;
        }}
        QProgressBar::chunk {{
            background-color: {Colors.PRIMARY};
            border-radius: 5px;
        }}
    """
