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
        self.mousePressEvent = self.mouse_pressed

    def InitializeGUI(self):
        self.setWindowTitle("Calculator")
        self.setFixedSize(320, 500)
        self.setWindowIcon(QIcon("resources\\icon.png"))
        with open("styles.css", "r") as f:
            self.setStyleSheet(f.read())

    def CreateInteraction(self):
        self.last_button_equals = False
        self.operators = ["+", "-", "/", "*", "%"]
        self.history_operations = []
        self.history_results = []
        self.history = []
        self.history_visible = False
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        top_layout = QHBoxLayout()
        self.button_history = QPushButton()
        self.button_history.setIcon(QIcon("resources\\history.png"))
        self.button_history.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 0px;
                min-width: 24px;
                min-height: 24px;
            }
        """)
        self.button_history.clicked.connect(self.toogle_history)
        top_layout.addStretch()
        top_layout.addWidget(self.button_history)

        self.top_widget = QWidget(self)
        self.top_widget.setLayout(top_layout)
        self.top_widget.setMinimumHeight(100)
        layout.addWidget(self.top_widget)

        self.opacity_effect = QGraphicsOpacityEffect(self.top_widget)
        self.opacity_effect.setOpacity(1.0)
        self.top_widget.setGraphicsEffect(self.opacity_effect)

        # **Mid Layout: Display de la calculadora**
        self.mid_layout = QVBoxLayout()
        self.display = QLineEdit()
        self.displayResult = QLineEdit()    
        
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.displayResult.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setReadOnly(True)
        self.displayResult.setReadOnly(True)
        self.display.setFixedHeight(60)
        self.display.setStyleSheet("font-size: 50px")
        self.displayResult.setFixedHeight(35)
        self.displayResult.setStyleSheet("border: None; color: gray; font-size: 15px")
        self.mid_layout.addWidget(self.displayResult)
        self.mid_layout.addWidget(self.display)
        layout.addLayout(self.mid_layout)

        self.opacity_effectQLine = QGraphicsOpacityEffect(self.display)
        self.opacity_effectQLine.setOpacity(1.0)
        self.display.setGraphicsEffect(self.opacity_effectQLine)
        self.opacity_effectQLineResult = QGraphicsOpacityEffect(self.displayResult)
        self.opacity_effectQLineResult.setOpacity(1.0)
        self.displayResult.setGraphicsEffect(self.opacity_effectQLineResult)

        layout.addStretch()
        self.stack = QStackedWidget()
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
        self.history_layout.setContentsMargins(5, 0, 5, 0)
        self.history_widget.setStyleSheet("background: #323232; color: white; font-size: 20px")
        
        self.history_entries = QWidget()
        self.history_entries_layout = QVBoxLayout(self.history_entries)
        self.history_entries_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.history_layout.addWidget(self.history_entries)
        self.history_layout.addStretch()

        history_footer = QWidget()
        history_footer_layout = QHBoxLayout(history_footer)
        history_footer_layout.setContentsMargins(0, 0, 0, 0)

        self.delete_history = QPushButton()
        self.delete_history.setIcon(QIcon("resources\\delete_icon.png"))
        self.delete_history.clicked.connect(self.clear_history)
        self.delete_history.hide()

        history_footer_layout.addStretch()
        history_footer_layout.addWidget(self.delete_history)

        self.history_layout.addWidget(history_footer)

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
        if self.history_visible:
            return
        
        expression = self.display.text().strip()
        if text == "+/-":
            if expression and not expression.startswith("-"):
                self.display.setText("-" + expression)
            elif expression.startswith("-"):
                self.display.setText(expression[1:])
            return

        if text == "<-" or text == "":
            self.display.setText(self.display.text()[:-1])
            self.displayResult.clear()
            return
        elif text == "C":
            self.display.clear()
            self.displayResult.clear()
            self.reset_display = False
            return

        if text == "=":
            if not expression:
                return
            self.displayResult.setText(expression)
            result = calculate(expression)
            self.display.setText(str(result))

            self.history_operations.append(expression)
            self.history_results.append(str(result))
            
            formatted_text = (
                f"<div>"
                f"<span style='color:gray; font-;font-size:12pt;'>{expression} = </span><br>"
                f"<span style='color:white; font-size:16pt;'>{result}</span>"
                f"</div>"
            )
            self.last_button_equals = True
            self.history.append(formatted_text)
            return
        if self.last_button_equals:
            if text in self.operators:
                self.displayResult.clear()
                self.display.setText(self.display.text() + text)
            else:
                self.display.clear()
                self.displayResult.clear()
                self.display.setText(text)

            self.last_button_equals = False
        else:
            self.displayResult.clear()
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

            self.opacity_animationQLineResult = QPropertyAnimation(self.opacity_effectQLineResult, b"opacity")
            self.opacity_animationQLineResult.setStartValue(1.0)
            self.opacity_animationQLineResult.setEndValue(0.5)
            self.opacity_animationQLineResult.setEasingCurve(QEasingCurve.Type.InOutQuad)

            self.stack.setCurrentWidget(self.scroll_area)
            self.animation.start()
            self.opacity_animation.start()
            self.opacity_animationQLine.start()
            self.opacity_animationQLineResult.start()
             
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

            self.opacity_animationQLineResult = QPropertyAnimation(self.opacity_effectQLineResult, b"opacity")
            self.opacity_animationQLineResult.setStartValue(0.5)
            self.opacity_animationQLineResult.setEndValue(1.0)
            self.opacity_animationQLineResult.setEasingCurve(QEasingCurve.Type.InOutSine)

            self.opacity_animation.start()
            self.opacity_animationQLine.start()
            self.opacity_animationQLineResult.start()

            self.stack.setCurrentWidget(self.buttons_widget)

        self.history_visible = not self.history_visible

    def update_history(self):
        while self.history_entries_layout.count():
            item = self.history_entries_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if self.history:
            self.delete_history.show()
            for i, operation in enumerate(self.history):
                container = QWidget()
                container_layout = QVBoxLayout(container)
                container_layout.setContentsMargins(5, 5, 5, 5)

                label = QLabel(operation)
                label.setAlignment(Qt.AlignmentFlag.AlignRight)
                label.setCursor(Qt.CursorShape.PointingHandCursor)

                label.mousePressEvent = lambda event, index=i: self.copy_operation(index)

                container_layout.addWidget(label)
                self.history_entries_layout.addWidget(container)
        else:
            label = QLabel("No hay historial aún")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.history_entries_layout.addWidget(label)

    def copy_operation(self, index):
        if 0 <= index < len(self.history_operations):
            operation = self.history_operations[index]
            self.display.setText(operation)
            self.displayResult.clear()
            self.toogle_history()
            self.last_button_equals = False

    def mouse_pressed(self, event):
        if self.history_visible:
            global_pos = event.globalPosition().toPoint()            
            history_pos = self.scroll_area.mapFromGlobal(global_pos)            
            if not self.scroll_area.rect().contains(history_pos):
                self.toogle_history()
            
    def clear_history(self):
        self.delete_history.hide()
        self.history=[]
        self.update_history()

    def keyPressEvent(self, event):
        if self.history_visible:
            if event.key() == Qt.Key.Key_Escape or event.key() == Qt.Key.Key_H:
                self.toogle_history()
            return
        
        key = event.key()
        text = event.text()

        if text and text in "0123456789.+-*/":
            self.pressed_button(text)
        
        elif key == Qt.Key.Key_Enter or key == Qt.Key.Key_Equal or key == Qt.Key.Key_Return:
            self.pressed_button("=")
        elif key == Qt.Key.Key_Backspace:
            self.pressed_button("<-")
        elif key == Qt.Key.Key_Percent:
            self.pressed_button("%")
        elif key == Qt.Key.Key_H:
            self.toogle_history()
