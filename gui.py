from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLineEdit, QLabel,
    QStackedWidget, QLayout, QScrollArea, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, QTimer
from PyQt6.QtGui import QIcon
from logic import calculate
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class CalculatorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.InitializeGUI()
        self.CreateInteraction()
        self.mousePressEvent = self.mouse_pressed

    def InitializeGUI(self):
        self.setWindowTitle("Calculator")
        self.setFixedSize(320, 500)
        icon_path = resource_path("resources\\icon.png")
        self.setWindowIcon(QIcon(icon_path))
        
        css_path = resource_path("styles.css")
    
        try:
            with open(css_path, "r", encoding='utf-8') as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo de estilos en {css_path}")
        except Exception as e:
            print(f"Error al cargar estilos: {e}")

    def CreateInteraction(self):
        self.last_button_equals = False
        self.pressedEqualHistoryOperation = False
        self.operators = ["+", "-", "/", "*", "%"]
        self.history_operations = []
        self.history_results = []
        self.history = []
        self.history_visible = False
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        top_layout = QHBoxLayout()
        self.button_history = QPushButton()
        
        history_icon_path = resource_path("resources\\history.png")
        self.button_history.setIcon(QIcon(history_icon_path))
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
        self.display.setFixedHeight(65)
        self.display.setStyleSheet("font-size: 58px")
        self.displayResult.setFixedHeight(35)
        self.displayResult.setStyleSheet("border: None; color: gray; font-size: 16px")
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
        delete_icon_path = resource_path("resources\\delete_icon.png")
        self.delete_history.setIcon(QIcon(delete_icon_path))
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
            "%", "C", "backspace", "/",
            "7", "8", "9", "*",
            "4", "5", "6", "-",
            "1", "2", "3", "+",
            "+/-", "0", ".", "="
        ]

        row, col = 0, 0
        for text_button in buttons:
            button = QPushButton(text_button)        
            if text_button == "backspace":
                button.setText("")
                button.setProperty("action", "backspace")
                backspace_icon_path = resource_path("resources\\backspace.png")
                button.setIcon(QIcon(backspace_icon_path))
                button.clicked.connect(self.handle_backspace)
            else:
                button.clicked.connect(lambda checked, text=text_button: self.pressed_button(text))

            if text_button == "=":
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #dcbca6; 
                        color: black;
                    }
                    QPushButton:hover {
                        background-color: #c5a58e; /* Un tono más oscuro */
                    }
                    QPushButton:pressed {
                        background-color: #b48f76; /* Aún más oscuro */
                    }
                """)
                

            
            self.buttons_layout.addWidget(button, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

    def pressed_button(self, text):
        if len(self.display.text()) >= 16 and text not in ["+/-", "C", "="] and text not in self.operators and not self.last_button_equals:
            return

        expression = self.display.text().strip()

        if expression and expression[0] == "0":
            self.display.setText(expression[:-1])

        expressionResult= self.displayResult.text().strip()

        if text == "+/-":
            if not expression or not expression.startswith("-"):
                self.display.setText("-" + expression)
            elif expression.startswith("-"):
                self.display.setText(expression[1:])
            return

        if text == "C":
            self.display.clear()
            self.displayResult.clear()
            self.last_button_equals = False
            self.adjust_font_size()
            return
        if text == "=":
            if not expression or expression == "0":
                return
            
            if expression == "Syntax error":
                self.display.clear()
                self.displayResult.clear()
                return

            if self.history_results and expression == self.history_results[-1] or self.pressedEqualHistoryOperation:
                
                if len(self.history_operations) >= 1:
                    if self.pressedEqualHistoryOperation:
                        last_operation = self.copiedOperation
                    else:
                        last_operation = self.history_operations[-1]
                    
                    operator = None
                    second_operand = None
                    found = False
                    i = 0
                    while i < len(self.operators) and not found:
                        op = self.operators[i]
                        
                        if op in last_operation:
                            last_op_index = last_operation.rfind(op)
                            operator = op
                            second_operand = last_operation[last_op_index+1:]
                            found = True
                        i += 1
                    
                    if operator and second_operand:
                        self.displayResult.clear()
                        expressionResult = expression + operator
                        expression = second_operand
                    else:
                        return

                    self.pressedEqualHistoryOperation = False
                        
                          
            self.displayResult.setText(expressionResult + expression)
            result = calculate(expressionResult + expression)
            
            result_str = str(result)
            if len(result_str) > 16:
                result_str = f"{float(result):.10e}"

            self.display.setText(result_str)

            self.adjust_font_size()
            if not result == "Syntax error":
                self.history_operations.append(expressionResult + expression)
                self.history_results.append(result_str)
                
                formatted_text = (
                    f"<div>"
                    f"<span style='color:gray; font-;font-size:12pt;'>{expressionResult + expression} = </span><br>"
                    f"<span style='color:white; font-size:16pt;'>{result_str}</span>"
                    f"</div>"
                )
                self.history.append(formatted_text)
            self.last_button_equals = True
            return
        
        if text in self.operators:
            
            if expression:
                if expression[-1] in self.operators:
                    self.display.setText(expression[:-1] + text)
                    self.adjust_font_size()
                    return
            else:
                return
            
            if self.last_button_equals:
                if text in self.operators:
                    self.displayResult.setText(self.display.text() + text)
                    self.display.clear()

                self.last_button_equals = False
                return
            
            else:
                self.displayResult.setText(expression + text)
                self.display.clear()
                return
            
        if self.last_button_equals:
            self.display.clear()
            self.displayResult.clear()
            self.display.setText(text)
            self.last_button_equals = False
        else:
            self.display.setText(self.display.text() + text)
            self.adjust_font_size()

    def handle_backspace(self):
        if not self.history_visible and not self.display.text() == "":
            if self.display.text() == "Syntax error":
                self.display.clear()    
            else:
                self.display.setText(self.display.text()[:-1])
                self.displayResult.clear()
            self.adjust_font_size()

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
            result = self.history_results[index]
            self.displayResult.setText(operation)
            self.display.setText(result)
            self.toogle_history()
            self.pressedEqualHistoryOperation = True
            self.copiedOperation = operation
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

    def adjust_font_size(self):
        text_length = len(self.display.text())
        
        if text_length <= 10:
            font_size = 58
        else:
            reduction_per_char = 5
            font_size = 58 - (text_length - 10) * reduction_per_char
            font_size = max(font_size, 28)
        
        self.display.setStyleSheet(f"font-size: {font_size}px")

    def keyPressEvent(self, event):
        if self.history_visible:
            if event.key() == Qt.Key.Key_Escape or event.key() == Qt.Key.Key_H:
                self.toogle_history()
            return
        
        key = event.key()
        text = event.text()

        if text and text in "0123456789.+-*/":
            for button in self.findChildren(QPushButton):
                if button.text() == text:
                    button.setDown(True)
                    QTimer.singleShot(100, lambda b=button: b.setDown(False))
                    self.pressed_button(text)
        
        elif key == Qt.Key.Key_Enter or key == Qt.Key.Key_Equal or key == Qt.Key.Key_Return:
            for button in self.findChildren(QPushButton):
                if button.text() == "=":
                    button.setDown(True)
                    QTimer.singleShot(100, lambda b=button: b.setDown(False))
                    self.pressed_button("=")
        elif key == Qt.Key.Key_Backspace:
            backspace_button = None
            buttons = self.findChildren(QPushButton)
            i = 0
            found = False
            
            while i < len(buttons) and not found:
                if buttons[i].property("action") == "backspace":
                    backspace_button = buttons[i]
                    found = True
                i += 1
                    
            if backspace_button:
                backspace_button.setDown(True)
                QTimer.singleShot(100, lambda b=backspace_button: b.setDown(False))
                self.handle_backspace()
        elif key == Qt.Key.Key_Percent:
            for button in self.findChildren(QPushButton):
                if button.text() == "%":
                    button.setDown(True)
                    QTimer.singleShot(100, lambda b=button: b.setDown(False))
                    self.pressed_button("%")
        elif key == Qt.Key.Key_H:
            self.toogle_history()
