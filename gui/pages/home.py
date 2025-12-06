"""
Ana Sayfa (Dashboard)
=====================
Uygulamanın tanıtımı, istatistikler ve hızlı erişim kartları.
Algoritma Analizi Platformu - 9 farklı algoritma, 3 kategori
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


class AlgorithmBadge(QFrame):
    """Algoritma rozeti bileşeni"""
    def __init__(self, name, complexity, category_color, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_DARKER};
                border-radius: 8px;
                border: 1px solid {Colors.BORDER};
                border-left: 3px solid {category_color};
            }}
        """)
        self.setFixedHeight(50)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        
        name_label = QLabel(name)
        name_label.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {Colors.TEXT_MAIN}; background: transparent; border: none;")
        layout.addWidget(name_label)
        
        layout.addStretch()
        
        complexity_label = QLabel(complexity)
        complexity_label.setStyleSheet(f"""
            font-size: 10px; 
            color: {Colors.TEXT_MUTED}; 
            background-color: {Colors.BG_CARD}; 
            padding: 4px 8px; 
            border-radius: 4px;
            border: none;
        """)
        layout.addWidget(complexity_label)


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
        
        # ============ HERO SECTION ============
        hero = QFrame()
        hero.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 {Colors.PRIMARY}, stop:0.5 #7209B7, stop:1 #3A0CA3);
                border-radius: 16px;
                border: none;
            }}
        """)
        hero.setFixedHeight(180)
        
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(30, 25, 30, 25)
        hero_layout.setSpacing(8)
        
        welcome = QLabel("⚡ Algoritma Analizi Platformu")
        welcome.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 900;
            color: {Colors.WHITE};
            background: transparent;
            border: none;
        """)
        hero_layout.addWidget(welcome)
        
        hero_subtitle = QLabel(
            "Python tabanlı kapsamlı algoritma performans ve enerji tüketimi analiz platformu. "
            "9 farklı algoritma, 3 kategori, gerçek zamanlı enerji ölçümü."
        )
        hero_subtitle.setWordWrap(True)
        hero_subtitle.setStyleSheet(f"""
            font-size: 13px;
            color: rgba(255, 255, 255, 0.9);
            background: transparent;
            border: none;
        """)
        hero_layout.addWidget(hero_subtitle)
        
        hero_layout.addStretch()
        
        # Quick Start Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        start_btn = QPushButton("🚀  Enerji Analizi Başlat")
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
        
        compare_btn = QPushButton("📊  Karşılaştır")
        compare_btn.setCursor(Qt.PointingHandCursor)
        compare_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.2);
                color: {Colors.WHITE};
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.3);
            }}
        """)
        compare_btn.clicked.connect(lambda: self.navigate_to.emit(2))
        btn_layout.addWidget(compare_btn)
        
        btn_layout.addStretch()
        hero_layout.addLayout(btn_layout)
        
        layout.addWidget(hero)
        
        # ============ STATS SECTION ============
        stats_title = QLabel("📊 Platform İstatistikleri")
        stats_title.setStyleSheet(f"font-size: 18px; font-weight: 800; color: {Colors.TEXT_MAIN}; background: transparent;")
        layout.addWidget(stats_title)
        
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        stats = [
            ("🧪", "Algoritma Sayısı", "9", Colors.PRIMARY),
            ("📁", "Kategori", "3", Colors.ACCENT),
            ("⚡", "Enerji Ölçümü", "Gerçek", Colors.SUCCESS),
            ("🔄", "Çalıştırma", "Çoklu", Colors.SECONDARY),
        ]
        
        for icon, title, value, color in stats:
            card = StatCard(icon, title, value, color)
            stats_layout.addWidget(card)
        
        layout.addLayout(stats_layout)
        
        # ============ ALGORITHMS SECTION ============
        algo_title = QLabel("🧬 Desteklenen Algoritmalar")
        algo_title.setStyleSheet(f"font-size: 18px; font-weight: 800; color: {Colors.TEXT_MAIN}; background: transparent;")
        layout.addWidget(algo_title)
        
        # Algorithm Categories
        categories_layout = QHBoxLayout()
        categories_layout.setSpacing(20)
        
        # Divide & Conquer
        dc_frame = QFrame()
        dc_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_CARD};
                border-radius: 12px;
                border: 1px solid {Colors.BORDER};
            }}
        """)
        dc_layout = QVBoxLayout(dc_frame)
        dc_layout.setContentsMargins(16, 16, 16, 16)
        dc_layout.setSpacing(10)
        
        dc_title = QLabel("🔀 Böl ve Yönet")
        dc_title.setStyleSheet(f"font-size: 14px; font-weight: 800; color: {Colors.PRIMARY}; background: transparent; border: none;")
        dc_layout.addWidget(dc_title)
        
        dc_algorithms = [
            ("Merge Sort", "O(n log n)"),
            ("Quick Sort", "O(n log n)"),
            ("Strassen Matrix", "O(n^2.81)"),
        ]
        for name, complexity in dc_algorithms:
            badge = AlgorithmBadge(name, complexity, Colors.PRIMARY)
            dc_layout.addWidget(badge)
        
        categories_layout.addWidget(dc_frame)
        
        # Dynamic Programming
        dp_frame = QFrame()
        dp_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_CARD};
                border-radius: 12px;
                border: 1px solid {Colors.BORDER};
            }}
        """)
        dp_layout = QVBoxLayout(dp_frame)
        dp_layout.setContentsMargins(16, 16, 16, 16)
        dp_layout.setSpacing(10)
        
        dp_title = QLabel("📐 Dinamik Programlama")
        dp_title.setStyleSheet(f"font-size: 14px; font-weight: 800; color: {Colors.ACCENT}; background: transparent; border: none;")
        dp_layout.addWidget(dp_title)
        
        dp_algorithms = [
            ("0/1 Knapsack", "O(n×W)"),
            ("Floyd-Warshall", "O(n³)"),
            ("Bellman-Ford", "O(V×E)"),
        ]
        for name, complexity in dp_algorithms:
            badge = AlgorithmBadge(name, complexity, Colors.ACCENT)
            dp_layout.addWidget(badge)
        
        categories_layout.addWidget(dp_frame)
        
        # Greedy
        greedy_frame = QFrame()
        greedy_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_CARD};
                border-radius: 12px;
                border: 1px solid {Colors.BORDER};
            }}
        """)
        greedy_layout = QVBoxLayout(greedy_frame)
        greedy_layout.setContentsMargins(16, 16, 16, 16)
        greedy_layout.setSpacing(10)
        
        greedy_title = QLabel("🎯 Açgözlü Algoritmalar")
        greedy_title.setStyleSheet(f"font-size: 14px; font-weight: 800; color: {Colors.SUCCESS}; background: transparent; border: none;")
        greedy_layout.addWidget(greedy_title)
        
        greedy_algorithms = [
            ("Dijkstra", "O(V²)"),
            ("Prim's MST", "O(V²)"),
            ("Huffman Coding", "O(n log n)"),
        ]
        for name, complexity in greedy_algorithms:
            badge = AlgorithmBadge(name, complexity, Colors.SUCCESS)
            greedy_layout.addWidget(badge)
        
        categories_layout.addWidget(greedy_frame)
        
        layout.addLayout(categories_layout)
        
        # ============ FEATURES SECTION ============
        features_title = QLabel("🎯 Platform Özellikleri")
        features_title.setStyleSheet(f"font-size: 18px; font-weight: 800; color: {Colors.TEXT_MAIN}; background: transparent;")
        layout.addWidget(features_title)
        
        features_grid = QGridLayout()
        features_grid.setSpacing(15)
        
        features = [
            ("⚡", "Gerçek Enerji Ölçümü", "LibreHardwareMonitor ile CPU güç tüketimi ölçümü.", 1),
            ("📊", "Algoritma Karşılaştırma", "Performans grafiklerini yan yana karşılaştırın.", 2),
            ("📜", "Test Geçmişi", "Tüm test sonuçlarını kaydedin ve analiz edin.", 3),
            ("🔄", "Çoklu Çalıştırma", "Güvenilir sonuçlar için birden fazla test çalıştırın.", 1),
        ]
        
        for i, (icon, title, desc, page_idx) in enumerate(features):
            card = FeatureCard(icon, title, desc, page_idx)
            card.clicked.connect(self.navigate_to.emit)
            features_grid.addWidget(card, i // 2, i % 2)
        
        layout.addLayout(features_grid)
        
        # ============ INFO SECTION ============
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
        info_layout.setSpacing(12)
        
        info_title = QLabel("Sistem Hakkında")
        info_title.setStyleSheet(f"font-size: 16px; font-weight: 800; color: {Colors.TEXT_MAIN}; background: transparent; border: none;")
        info_layout.addWidget(info_title)
        
        info_text = QLabel(
            "Bu platform, algoritmaların performans ve enerji tüketimini analiz etmek için "
            "geliştirilmiş kapsamlı bir araçtır. Böl ve Yönet, Dinamik Programlama ve Açgözlü "
            "algoritma kategorilerinde toplam 9 farklı algoritma içerir.\n\n"
            "🔬 Akademik çalışmalar ve araştırmalar için idealdir.\n"
            "📚 Algoritma eğitimi ve öğretimi için kullanılabilir.\n"
            "⚡ Gerçek zamanlı enerji ölçümü ile yeşil yazılım geliştirme destekler."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_MUTED}; background: transparent; border: none; line-height: 1.5;")
        info_layout.addWidget(info_text)
        
        # Tech Stack
        tech_layout = QHBoxLayout()
        tech_layout.setSpacing(8)
        
        tech_items = ["Python 3.x", "PyQt5", "LibreHardwareMonitor", "Matplotlib"]
        for tech in tech_items:
            tech_label = QLabel(tech)
            tech_label.setStyleSheet(f"""
                font-size: 10px; 
                color: {Colors.PRIMARY}; 
                background-color: {Colors.BG_DARKER}; 
                padding: 5px 10px; 
                border-radius: 4px;
                border: 1px solid {Colors.BORDER};
            """)
            tech_layout.addWidget(tech_label)
        
        tech_layout.addStretch()
        info_layout.addLayout(tech_layout)
        
        layout.addWidget(info_frame)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
