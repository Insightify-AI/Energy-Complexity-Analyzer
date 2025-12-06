"""
Ana Pencere
===========
Uygulamanın ana penceresi ve navigasyon yapısı.
"""

import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QStackedWidget, QLabel, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from gui.styles import Styles, Colors
from gui.pages.home import HomePage
from gui.pages.comparison import ComparisonPage
from gui.pages.history import HistoryPage
from gui.pages.real_energy import RealEnergyPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Algoritma Analizi Platformu")
        self.resize(1100, 800)  # Resizable window
        self.setMinimumSize(900, 600)
        self.setStyleSheet(Styles.MAIN_WINDOW)
        
        # Track fullscreen state
        self.is_fullscreen = False
        
        # Main Container
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ============ TOP HEADER ============
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_DARKER};
                border-bottom: 1px solid {Colors.BORDER};
            }}
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(25, 0, 25, 0)
        header_layout.setSpacing(0)
        
        # Logo / Title
        logo = QLabel("⚡ Algoritma Analizi")
        logo.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 900;
            color: {Colors.TEXT_MAIN};
            letter-spacing: 0.5px;
            padding-right: 40px;
        """)
        header_layout.addWidget(logo)
        
        # Navigation Buttons Container
        nav_container = QWidget()
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(5)
        
        self.nav_buttons = []
        
        # Menu Items
        self.add_nav_button(nav_layout, "🏠 Ana Sayfa", 0)
        self.add_nav_button(nav_layout, "⚡ Enerji Analizi", 1)
        self.add_nav_button(nav_layout, "📊 Karşılaştır", 2)
        self.add_nav_button(nav_layout, "📜 Geçmiş", 3)
        
        header_layout.addWidget(nav_container)
        header_layout.addStretch()
        
        # Fullscreen Toggle Button
        self.fullscreen_btn = QPushButton("⛶")
        self.fullscreen_btn.setToolTip("Tam Ekran (F11)")
        self.fullscreen_btn.setCursor(Qt.PointingHandCursor)
        self.fullscreen_btn.setFixedSize(36, 36)
        self.fullscreen_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.BG_CARD};
                color: {Colors.TEXT_MUTED};
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {Colors.PRIMARY};
                color: white;
                border-color: {Colors.PRIMARY};
            }}
        """)
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        header_layout.addWidget(self.fullscreen_btn)
        
        header_layout.addSpacing(10)
        
        # Version Badge
        version = QLabel("v2.1.0")
        version.setStyleSheet(f"""
            color: {Colors.TEXT_MUTED};
            font-size: 11px;
            padding: 5px 12px;
            background-color: {Colors.BG_CARD};
            border-radius: 12px;
            border: 1px solid {Colors.BORDER};
        """)
        header_layout.addWidget(version)
        
        main_layout.addWidget(header)
        
        # ============ CONTENT AREA ============
        content_container = QFrame()
        content_container.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_DARK};
            }}
        """)
        
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {Colors.BG_DARK};
            }}
        """)
        
        # Pages
        self.home_page = HomePage()
        self.energy_page = RealEnergyPage()
        self.compare_page = ComparisonPage()
        self.history_page = HistoryPage()
        
        # Add pages to stack
        self.stack.addWidget(self.home_page)        # Index 0
        self.stack.addWidget(self.energy_page)      # Index 1
        self.stack.addWidget(self.compare_page)     # Index 2
        self.stack.addWidget(self.history_page)     # Index 3
        
        content_layout.addWidget(self.stack)
        main_layout.addWidget(content_container)
        
        # Connect home page navigation
        self.home_page.navigate_to.connect(self.switch_page)
        
        # Start at Home Page
        self.switch_page(0)

    def add_nav_button(self, layout, text, index):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(40)
        btn.setStyleSheet(f"""
            QPushButton {{
                padding: 8px 16px;
                border-radius: 8px;
                color: {Colors.TEXT_MUTED};
                background-color: transparent;
                font-weight: 600;
                font-size: 13px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {Colors.BG_CARD};
                color: {Colors.TEXT_MAIN};
            }}
            QPushButton:checked {{
                background-color: {Colors.PRIMARY};
                color: {Colors.WHITE};
            }}
        """)
        btn.clicked.connect(lambda: self.switch_page(index))
        layout.addWidget(btn)
        self.nav_buttons.append(btn)

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        
        # Update buttons
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
            
        # Refresh page if needed
        if index == 2: # Comparison
            self.compare_page.load_results()
        elif index == 3: # History
            self.history_page.load_history()
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.is_fullscreen:
            self.showNormal()
            self.fullscreen_btn.setText("⛶")
            self.fullscreen_btn.setToolTip("Tam Ekran (F11)")
            self.is_fullscreen = False
        else:
            self.showFullScreen()
            self.fullscreen_btn.setText("⛶")
            self.fullscreen_btn.setToolTip("Normal Boyut (F11)")
            self.is_fullscreen = True
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key_Escape and self.is_fullscreen:
            self.toggle_fullscreen()
        else:
            super().keyPressEvent(event)
