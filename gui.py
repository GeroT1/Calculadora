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
        self.opacity_effect = QGraphicsOpacityEffect(self.top_widget)
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
        self.displayResult.setFixedHeight(35)
        self.mid_layout.addWidget(self.display)
        self.mid_layout.addWidget(self.displayResult)
        layout.addLayout(self.mid_layout)
        self.opacity_effectQLine = QGraphicsOpacityEffect(self.display)
        self.display.setGraphicsEffect(self.opacity_effectQLine)

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
            return
        elif text == "C":
            self.display.clear()
            self.displayResult.clear()
            self.reset_display = False
            return

        if text == "=":
            if not expression:
                return
            self.displayResult.clear()
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
            self.reset_display = True
        elif self.reset_display:
            self.display.clear()
            self.reset_display = False
            self.display.setText(text)
            self.update_result()
        else:
            self.display.setText(self.display.text() + text)
            self.update_result()

    def toogle_history(self):
        if not self.history_visible:
            self.saved_expression = self.display.text()

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
            self.display.setText(self.saved_expression)
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
        while self.history_entries_layout.count():
            item = self.history_entries_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if self.history:
            self.delete_history.show()
            for operation in self.history:
                label = QLabel(operation)
                label.setAlignment(Qt.AlignmentFlag.AlignRight)
                self.history_entries_layout.addWidget(label)
        else:
            label = QLabel("No hay historial aún")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.history_entries_layout.addWidget(label)

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
        
    def update_result(self):
        expression = self.display.text()

        if not expression or expression == "<-":
            self.displayResult.clear()
            return
        
        if expression[-1] in "+-/*%":
            try:
                base_expression = expression[:-1]
                if base_expression:
                    result = calculate(base_expression)
                    self.displayResult.setText(str(result))
                else:
                    self.displayResult.clear()
            except:
                self.displayResult.clear()
        else:
            try:
                result = calculate(expression)
                self.displayResult.setText(str(result))
            except:
                pass