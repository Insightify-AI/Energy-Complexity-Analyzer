"""
Stil Tanımlamaları
==================
Uygulama genelinde kullanılan renkler, fontlar ve stiller.
"""

class Colors:
    """Canlı ve Modern Renk Paleti"""
    # Ana Renkler (Vibrant Blue & Pink)
    PRIMARY = "#4361EE"       # Vibrant Blue
    PRIMARY_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4361EE, stop:1 #3A0CA3)"
    SECONDARY = "#F72585"     # Vibrant Pink/Rose
    ACCENT = "#4CC9F0"        # Cyan/Light Blue
    
    # Arkaplanlar (Deep Dark)
    BG_DARK = "#0B0E14"       # Almost Black
    BG_DARKER = "#05070A"     # Pure Dark
    BG_CARD = "#151922"       # Dark Blue-Grey
    BG_SIDEBAR = "#0F1219"    # Slightly lighter than darker
    
    # Metin Renkleri
    TEXT_MAIN = "#FFFFFF"     # Pure White
    TEXT_MUTED = "#94A3B8"    # Muted Blue-Grey
    TEXT_SECONDARY = "#94A3B8"  # Alias for TEXT_MUTED
    TEXT_HIGHLIGHT = "#4CC9F0" # Cyan for highlights
    
    # Ek Arka Planlar
    BG_TERTIARY = "#1A1F2E"    # Slightly lighter than BG_CARD
    
    # Kenarlıklar
    BORDER = "#2A303C"        # Subtle Border
    BORDER_HIGHLIGHT = "#4361EE"
    
    # Durum Renkleri
    SUCCESS = "#10B981"       # Emerald
    WARNING = "#F59E0B"       # Amber
    DANGER = "#EF4444"        # Red
    INFO = "#3B82F6"          # Blue
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
        QScrollBar:vertical {{
            border: none;
            background: {Colors.BG_DARKER};
            width: 10px;
            margin: 0px 0px 0px 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {Colors.BORDER};
            min-height: 20px;
            border-radius: 5px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
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
            border-radius: 16px;
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
            background: {Colors.PRIMARY_GRADIENT};
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px 24px;
            font-weight: bold;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        QPushButton:hover {{
            background-color: {Colors.PRIMARY}E6;
            border: 1px solid {Colors.ACCENT};
        }}
        QPushButton:pressed {{
            padding-top: 14px;
            padding-left: 26px;
        }}
        QPushButton:disabled {{
            background: {Colors.BORDER};
            color: {Colors.TEXT_MUTED};
            border: none;
        }}
    """
    
    BUTTON_OUTLINE = f"""
        QPushButton {{
            background-color: transparent;
            color: {Colors.ACCENT};
            border: 2px solid {Colors.ACCENT};
            border-radius: 10px;
            padding: 10px 22px;
            font-weight: bold;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: {Colors.ACCENT}1A;
            color: {Colors.WHITE};
        }}
    """
    
    BUTTON_SUCCESS = f"""
        QPushButton {{
            background-color: {Colors.SUCCESS};
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px 24px;
            font-weight: bold;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: #059669;
        }}
    """
    
    BUTTON_DANGER = f"""
        QPushButton {{
            background-color: {Colors.DANGER};
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px 24px;
            font-weight: bold;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: #DC2626;
        }}
    """
    
    LABEL_TITLE = f"""
        QLabel {{
            font-size: 32px;
            font-weight: 800;
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
            margin-bottom: 30px;
        }}
    """
    
    HEADER_LABEL = LABEL_TITLE
    SUBHEADER_LABEL = LABEL_SUBTITLE
    
    TABLE = f"""
        QTableWidget {{
            background-color: {Colors.BG_CARD};
            border: 1px solid {Colors.BORDER};
            border-radius: 12px;
            gridline-color: {Colors.BORDER};
            color: {Colors.TEXT_MAIN};
            selection-background-color: {Colors.PRIMARY}40;
            selection-color: {Colors.TEXT_MAIN};
            font-size: 13px;
        }}
        QHeaderView::section {{
            background-color: {Colors.BG_DARKER};
            color: {Colors.ACCENT};
            padding: 12px;
            border: none;
            font-weight: bold;
            font-size: 13px;
            text-transform: uppercase;
            border-bottom: 2px solid {Colors.BORDER};
        }}
        QTableWidget::item {{
            padding: 10px;
            border-bottom: 1px solid {Colors.BG_DARK};
        }}
        QTableWidget::item:selected {{
            background-color: {Colors.PRIMARY}40;
            border-left: 2px solid {Colors.ACCENT};
        }}
        QCornerButton::section {{
            background-color: {Colors.BG_DARKER};
        }}
    """
    
    INPUT_FIELD = f"""
        QLineEdit, QSpinBox, QTextEdit {{
            background-color: {Colors.BG_DARKER};
            border: 2px solid {Colors.BORDER};
            border-radius: 8px;
            padding: 12px;
            color: {Colors.TEXT_MAIN};
            font-size: 14px;
            selection-background-color: {Colors.PRIMARY};
        }}
        QLineEdit:focus, QSpinBox:focus, QTextEdit:focus {{
            border: 2px solid {Colors.PRIMARY};
            background-color: {Colors.BG_DARK};
        }}
        QLineEdit:hover, QSpinBox:hover, QTextEdit:hover {{
            border: 2px solid {Colors.TEXT_MUTED};
        }}
    """
    
    COMBOBOX = f"""
        QComboBox {{
            background-color: {Colors.BG_DARKER};
            border: 2px solid {Colors.BORDER};
            border-radius: 8px;
            padding: 10px;
            color: {Colors.TEXT_MAIN};
            font-size: 14px;
        }}
        QComboBox:hover {{
            border: 2px solid {Colors.ACCENT};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 2px solid {Colors.TEXT_MUTED};
            border-bottom: 2px solid {Colors.TEXT_MUTED};
            width: 8px;
            height: 8px;
            margin-right: 10px;
            transform: rotate(-45deg);
        }}
    """
    
    LOG_TEXT = f"""
        QTextEdit {{
            background-color: {Colors.BG_DARKER};
            color: {Colors.ACCENT};
            border: 1px solid {Colors.BORDER};
            border-radius: 12px;
            padding: 15px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.5;
        }}
    """
    
    PROGRESS_BAR = f"""
        QProgressBar {{
            border: none;
            border-radius: 4px;
            text-align: center;
            background-color: {Colors.BG_DARKER};
            color: {Colors.TEXT_MAIN};
            height: 8px;
        }}
        QProgressBar::chunk {{
            background-color: {Colors.PRIMARY};
            background: {Colors.PRIMARY_GRADIENT};
            border-radius: 4px;
        }}
    """
