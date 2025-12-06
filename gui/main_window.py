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
from PyQt5.QtGui import QIcon

from gui.styles import Styles, Colors
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
        self.resize(1200, 800)
        self.setStyleSheet(Styles.MAIN_WINDOW)
        
        # Main Container
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = QFrame()
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_DARKER};
                border-right: 1px solid {Colors.BORDER};
            }}
        """)
        sidebar.setFixedWidth(250)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 40, 20, 20)
        sidebar_layout.setSpacing(10)
        
        # Logo / Title
        title = QLabel("ALGORİTMA\nANALİZİ")
        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {Colors.PRIMARY};
            margin-bottom: 40px;
        """)
        title.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(title)
        
        # Navigation Buttons
        self.nav_buttons = []
        
        self.add_nav_button(sidebar_layout, "🚀 Test Çalıştır", 0)
        self.add_nav_button(sidebar_layout, "📊 Karşılaştırma", 1)
        self.add_nav_button(sidebar_layout, "🔋 Gerçek Enerji", 2)
        self.add_nav_button(sidebar_layout, "📜 Geçmiş", 3)
        
        sidebar_layout.addStretch()
        
        # Version
        version = QLabel("v2.0.0")
        version.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 12px;")
        version.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(version)
        
        main_layout.addWidget(sidebar)
        
        # Content Area
        self.stack = QStackedWidget()
        
        # Pages
        self.test_page = TestRunnerPage()
        self.compare_page = ComparisonPage()
        self.real_energy_page = RealEnergyPage()
        self.history_page = HistoryPage()
        
        self.stack.addWidget(self.test_page)
        self.stack.addWidget(self.compare_page)
        self.stack.addWidget(self.real_energy_page)
        self.stack.addWidget(self.history_page)
        
        main_layout.addWidget(self.stack)
        
        # Set default page
        self.switch_page(0)

    def add_nav_button(self, layout, text, index):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: 12px 16px;
                border-radius: 8px;
                color: {Colors.TEXT_MUTED};
                background-color: transparent;
                font-weight: 600;
                font-size: 14px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {Colors.BG_CARD};
                color: {Colors.TEXT_MAIN};
            }}
            QPushButton:checked {{
                background-color: {Colors.PRIMARY};
                color: white;
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
        if index == 1: # Comparison
            self.compare_page.load_results()
        elif index == 3: # History
            self.history_page.load_history()
