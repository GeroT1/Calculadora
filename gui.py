from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLineEdit, QLabel,
    QStackedWidget, QLayout, QScrollArea, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve
from PyQt6.QtGui import QIcon
from logic import calculate
import re

class CalculatorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.InitializeGUI()
        self.CreateInteraction()
        self.reset_display = False

    def InitializeGUI(self):
        self.setWindowTitle("Calculator")
        self.setFixedSize(320, 500)
        self.setWindowIcon(QIcon("resources\\icon.png"))
        with open("styles.css", "r") as f:
            self.setStyleSheet(f.read())

    def CreateInteraction(self):
        self.history = []
        self.history_visible = False
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        top_layout = QHBoxLayout()
        self.button_history = QPushButton()
        self.button_history.setIcon(QIcon("resources\\history.png"))
        self.button_history.clicked.connect(self.toogle_history)
        top_layout.addStretch()
        top_layout.addWidget(self.button_history)

        self.top_widget = QWidget(self)
        self.top_widget.setLayout(top_layout)
        self.top_widget.setMinimumHeight(100)
        layout.addWidget(self.top_widget)
        #Le agregue self. al widget y las dos lineas de abajo
        self.opacity_effect = QGraphicsOpacityEffect(self.top_widget)
        self.top_widget.setGraphicsEffect(self.opacity_effect)

        # **Mid Layout: Display de la calculadora**
        self.mid_layout = QVBoxLayout()
        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setReadOnly(True)
        self.display.setFixedHeight(60) 
        self.mid_layout.addWidget(self.display)
        layout.addLayout(self.mid_layout)
        self.opacity_effectQLine = QGraphicsOpacityEffect(self.display)
        self.display.setGraphicsEffect(self.opacity_effectQLine)

        layout.addStretch()
        self.stack = QStackedWidget()
        #Agregue esta parte para la animacion, revisar!!!!
        self.stack.setGeometry(0, self.height(), self.width(), 300)

        # **Botones**
        self.buttons_widget = QWidget()
        self.buttons_layout = QGridLayout(self.buttons_widget)
        self.buttons_layout.setContentsMargins(5, 0, 5, 10)
        self.buttons_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.buttons_layout.setVerticalSpacing(3) 
        self.buttons_layout.setHorizontalSpacing(3)
        self.create_buttons()
        self.stack.addWidget(self.buttons_widget)

        # **Historial**
        self.history_widget = QWidget()
        self.history_layout = QVBoxLayout(self.history_widget)
        self.history_widget.setStyleSheet("background: #323232; color: white; font-size: 20px")

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.history_widget)

        self.stack.addWidget(self.scroll_area)
        layout.addWidget(self.stack)

        self.setLayout(layout)

    def create_buttons(self):
        buttons = [
            "%", "C", "<-", "/",
            "7", "8", "9", "*",
            "4", "5", "6", "-",
            "1", "2", "3", "+",
            "+/-", "0", ".", "="
        ]

        row, col = 0, 0
        for text_button in buttons:
            button = QPushButton(text_button)        
            if text_button == "<-":
                button.setText("")
                button.setIcon(QIcon("resources\\backspace.png"))

            button.clicked.connect(lambda checked, text=text_button: self.pressed_button(text))
            self.buttons_layout.addWidget(button, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

    def pressed_button(self, text):
        if text == "+/-":
            expression = self.display.text().strip()
            if expression and not expression.startswith("-"):
                self.display.setText("-" + expression)
            elif expression.startswith("-"):
                self.display.setText(expression[1:])
            return

        if text == "=":
            expression = self.display.text()
            self.reset_display = True
            result = calculate(expression)
            self.display.setText(str(result))
            formatted_text = (
                f"<div>"
                f"<span style='color:gray; font-;font-size:12pt;'>{expression} = </span><br>"
                f"<span style='color:white; font-size:16pt;'>{result}</span>"
                f"</div>"
            )
            self.history.append(formatted_text)
        elif self.reset_display:
            self.display.clear()
            self.reset_display = False
            self.display.setText(text)
        elif text == "<-":
            self.display.setText(self.display.text()[:-1])
        elif text == "C":
            self.display.clear()
        elif text == "CE":
            expression = self.display.text()
            match = re.search(r"[+\*-/](?!.*[+\*-/])", expression)
            if match:
                pos = match.start() + 1
                self.display.setText(expression[:pos])
        else:
            self.display.setText(self.display.text() + text)

    def toogle_history(self):
        if not self.history_visible:
            self.update_history()
            self.animation = QPropertyAnimation(self.history_widget, b"geometry")
            self.animation.setStartValue(QRect(0, self.height(), self.width(), 300))
            self.animation.setEndValue(QRect(0, self.height()-600, self.width()-5, 500))
            self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)  

            
            self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.opacity_animation.setStartValue(1.0)
            self.opacity_animation.setEndValue(0.5)
            self.opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

            self.opacity_animationQLine = QPropertyAnimation(self.opacity_effectQLine, b"opacity")
            self.opacity_animationQLine.setStartValue(1.0)
            self.opacity_animationQLine.setEndValue(0.5)
            self.opacity_animationQLine.setEasingCurve(QEasingCurve.Type.InOutQuad)

            self.stack.setCurrentWidget(self.scroll_area)
            self.animation.start()
            self.opacity_animation.start()
            self.opacity_animationQLine.start()
             
        else:
            self.animation.stop()
            self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.opacity_animation.setStartValue(0.5)
            self.opacity_animation.setEndValue(1.0)
            self.opacity_animation.setEasingCurve(QEasingCurve.Type.InOutSine)

            self.opacity_animationQLine = QPropertyAnimation(self.opacity_effectQLine, b"opacity")
            self.opacity_animationQLine.setStartValue(0.5)
            self.opacity_animationQLine.setEndValue(1.0)
            self.opacity_animationQLine.setEasingCurve(QEasingCurve.Type.InOutSine)

            self.opacity_animation.start()
            self.opacity_animationQLine.start()

            self.stack.setCurrentWidget(self.buttons_widget)

        self.history_visible = not self.history_visible

    def update_history(self):
        for i in reversed(range(self.history_layout.count())):
            self.history_layout.itemAt(i).widget().deleteLater()

        if self.history:
            for operation in self.history[-10:]:
                label = QLabel(operation)
                label.setAlignment(Qt.AlignmentFlag.AlignRight)
                self.history_layout.addWidget(label)
        else:
            label = QLabel("No hay historial aún")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.history_layout.addWidget(label)

    def mouse_pressed(self, event):
        if self.history_visible and not self.history_widget.geometry().contains(event.pos()):
            self.stack.setCurrentWidget(self.buttons_widget)
            
