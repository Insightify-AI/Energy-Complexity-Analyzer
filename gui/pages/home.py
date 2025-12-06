"""
Ana Sayfa (Dashboard)
=====================
Uygulamanın tanıtımı, istatistikler ve hızlı erişim kartları.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QScrollArea, QPushButton, QGridLayout,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from gui.styles import Styles, Colors


class StatCard(QFrame):
    """İstatistik kartı bileşeni"""
    def __init__(self, icon, title, value, color, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_CARD};
                border-radius: 12px;
                border: 1px solid {Colors.BORDER};
                border-left: 4px solid {color};
            }}
        """)
        self.setFixedHeight(90)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 28px; color: {color}; background: transparent; border: none;")
        layout.addWidget(icon_label)
        
        # Text
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 11px; color: {Colors.TEXT_MUTED}; font-weight: 600; background: transparent; border: none;")
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 22px; font-weight: 900; color: {Colors.TEXT_MAIN}; background: transparent; border: none;")
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(value_label)
        layout.addLayout(text_layout)
        layout.addStretch()


class FeatureCard(QFrame):
    """Özellik kartı bileşeni"""
    clicked = pyqtSignal(int)
    
    def __init__(self, icon, title, description, page_index, parent=None):
        super().__init__(parent)
        self.page_index = page_index
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_CARD};
                border-radius: 12px;
                border: 1px solid {Colors.BORDER};
            }}
            QFrame:hover {{
                border: 1px solid {Colors.ACCENT};
            }}
        """)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(140)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 32px; background: transparent; border: none;")
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {Colors.TEXT_MAIN}; background: transparent; border: none;")
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"font-size: 11px; color: {Colors.TEXT_MUTED}; background: transparent; border: none;")
        layout.addWidget(desc_label)
        
        layout.addStretch()
    
    def mousePressEvent(self, event):
        self.clicked.emit(self.page_index)
        super().mousePressEvent(event)


class HomePage(QWidget):
    navigate_to = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {Colors.BG_DARK};
            }}
        """)
        
        content = QWidget()
        content.setStyleSheet(f"background-color: {Colors.BG_DARK};")
        
        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Hero Section
        hero = QFrame()
        hero.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 {Colors.PRIMARY}, stop:1 #3A0CA3);
                border-radius: 16px;
                border: none;
            }}
        """)
        hero.setFixedHeight(160)
        
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(30, 25, 30, 25)
        hero_layout.setSpacing(10)
        
        welcome = QLabel("⚡ Algoritma Analizi Platformu")
        welcome.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 900;
            color: {Colors.WHITE};
            background: transparent;
            border: none;
        """)
        hero_layout.addWidget(welcome)
        
        hero_subtitle = QLabel("Algoritmaların performans ve enerji tüketimini ölçün, analiz edin ve karşılaştırın.")
        hero_subtitle.setStyleSheet(f"""
            font-size: 14px;
            color: rgba(255, 255, 255, 0.85);
            background: transparent;
            border: none;
        """)
        hero_layout.addWidget(hero_subtitle)
        
        hero_layout.addStretch()
        
        # Quick Start Button
        btn_layout = QHBoxLayout()
        start_btn = QPushButton("🚀  Hızlı Başla")
        start_btn.setCursor(Qt.PointingHandCursor)
        start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.WHITE};
                color: {Colors.PRIMARY};
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.9);
            }}
        """)
        start_btn.clicked.connect(lambda: self.navigate_to.emit(1))
        btn_layout.addWidget(start_btn)
        btn_layout.addStretch()
        hero_layout.addLayout(btn_layout)
        
        layout.addWidget(hero)
        
        # Stats Section
        stats_title = QLabel("📊 Genel Bakış")
        stats_title.setStyleSheet(f"font-size: 18px; font-weight: 800; color: {Colors.TEXT_MAIN}; background: transparent;")
        layout.addWidget(stats_title)
        
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        stats = [
            ("🧪", "Algoritma", "15+", Colors.PRIMARY),
            ("📈", "Kategori", "5", Colors.ACCENT),
            ("⚡", "Ölçüm", "Gerçek", Colors.SUCCESS),
            ("📊", "Mod", "Çoklu", Colors.SECONDARY),
        ]
        
        for icon, title, value, color in stats:
            card = StatCard(icon, title, value, color)
            stats_layout.addWidget(card)
        
        layout.addLayout(stats_layout)
        
        # Features Section
        features_title = QLabel("🎯 Özellikler")
        features_title.setStyleSheet(f"font-size: 18px; font-weight: 800; color: {Colors.TEXT_MAIN}; background: transparent;")
        layout.addWidget(features_title)
        
        features_grid = QGridLayout()
        features_grid.setSpacing(15)
        
        features = [
            ("🚀", "Test Çalıştırıcı", "Sorting, Searching ve daha fazla algoritma testi.", 1),
            ("📊", "Karşılaştırma", "Performans grafiklerini karşılaştırın.", 2),
            ("⚡", "Gerçek Enerji", "LibreHardwareMonitor ile ölçüm.", 3),
            ("📜", "Geçmiş", "Test sonuçlarını kaydedin.", 4),
        ]
        
        for i, (icon, title, desc, page_idx) in enumerate(features):
            card = FeatureCard(icon, title, desc, page_idx)
            card.clicked.connect(self.navigate_to.emit)
            features_grid.addWidget(card, i // 2, i % 2)
        
        layout.addLayout(features_grid)
        
        # Info Section
        info_frame = QFrame()
        info_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_CARD};
                border-radius: 12px;
                border: 1px solid {Colors.BORDER};
            }}
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(25, 20, 25, 20)
        info_layout.setSpacing(10)
        
        info_title = QLabel("ℹ️ Hakkında")
        info_title.setStyleSheet(f"font-size: 16px; font-weight: 800; color: {Colors.TEXT_MAIN}; background: transparent; border: none;")
        info_layout.addWidget(info_title)
        
        info_text = QLabel(
            "Bu platform, algoritmaların performans ve enerji tüketimini analiz etmek için "
            "geliştirilmiş kapsamlı bir araçtır. Akademik çalışmalar ve eğitim amaçlı kullanılabilir."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_MUTED}; background: transparent; border: none;")
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_frame)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
