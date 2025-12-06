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
from gui.pages.test_runner import TestRunnerPage
from gui.pages.comparison import ComparisonPage
from gui.pages.history import HistoryPage
from gui.pages.real_energy import RealEnergyPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Algoritma Analizi Platformu")
        self.setFixedSize(1000, 800)  # Fixed size - no resizing
        self.setStyleSheet(Styles.MAIN_WINDOW)
        
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
        self.add_nav_button(nav_layout, "🚀 Test", 1)
        self.add_nav_button(nav_layout, "📊 Karşılaştır", 2)
        self.add_nav_button(nav_layout, "⚡ Enerji", 3)
        self.add_nav_button(nav_layout, "📜 Geçmiş", 4)
        
        header_layout.addWidget(nav_container)
        header_layout.addStretch()
        
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
        self.test_page = TestRunnerPage()
        self.compare_page = ComparisonPage()
        self.real_energy_page = RealEnergyPage()
        self.history_page = HistoryPage()
        
        # Add pages to stack
        self.stack.addWidget(self.home_page)        # Index 0
        self.stack.addWidget(self.test_page)        # Index 1
        self.stack.addWidget(self.compare_page)     # Index 2
        self.stack.addWidget(self.real_energy_page) # Index 3
        self.stack.addWidget(self.history_page)     # Index 4
        
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
        elif index == 4: # History
            self.history_page.load_history()
