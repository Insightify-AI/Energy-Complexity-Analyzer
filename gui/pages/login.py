"""
Giriş Sayfası
=============
Modern ve şık giriş ekranı.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame, QMessageBox, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from gui.styles import Styles, Colors

class LoginPage(QWidget):
    login_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        # Main Layout - Centered with Gradient Background
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Background styling for the whole page
        self.setStyleSheet(f"""
            LoginPage {{
                background-color: {Colors.BG_DARK};
            }}
        """)
        
        # Login Card
        card = QFrame()
        card.setFixedSize(420, 550)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_CARD};
                border-radius: 24px;
                border: 1px solid {Colors.BORDER};
            }}
        """)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 120))
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(50, 50, 50, 50)
        card_layout.setSpacing(25)
        
        # Logo / Icon
        logo = QLabel("⚡")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet(f"""
            font-size: 72px;
            margin-bottom: 10px;
            color: {Colors.PRIMARY};
        """)
        card_layout.addWidget(logo)
        
        # Title
        title = QLabel("Hoş Geldiniz")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            font-size: 32px;
            font-weight: 900;
            color: {Colors.TEXT_MAIN};
            margin-bottom: 5px;
        """)
        card_layout.addWidget(title)
        
        subtitle = QLabel("Algoritma Analizi Platformu")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"""
            font-size: 15px;
            color: {Colors.TEXT_HIGHLIGHT};
            font-weight: 600;
            margin-bottom: 20px;
        """)
        card_layout.addWidget(subtitle)
        
        # Username Input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Kullanıcı Adı")
        self.username_input.setStyleSheet(Styles.INPUT_FIELD)
        self.username_input.setMinimumHeight(50)
        card_layout.addWidget(self.username_input)
        
        # Password Input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Şifre")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(Styles.INPUT_FIELD)
        self.password_input.setMinimumHeight(50)
        self.password_input.returnPressed.connect(self.handle_login)
        card_layout.addWidget(self.password_input)
        
        # Login Button
        login_btn = QPushButton("GİRİŞ YAP")
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        login_btn.setMinimumHeight(50)
        login_btn.clicked.connect(self.handle_login)
        card_layout.addWidget(login_btn)
        
        card_layout.addStretch()
        
        # Footer
        footer = QLabel("v2.1.0 Pro Edition")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 12px; font-weight: 500;")
        card_layout.addWidget(footer)
        
        main_layout.addWidget(card)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        # Simple hardcoded check for demonstration
        if username == "admin" and password == "admin":
            self.login_successful.emit()
        elif username == "" or password == "":
             QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun.")
        else:
            QMessageBox.warning(self, "Hata", "Kullanıcı adı veya şifre hatalı.")
