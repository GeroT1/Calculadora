from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
from PyQt6.QtGui import QIcon
from logic import Calculate
import re

class CalculatorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.InitializeGUI()
        self.CreateInteraction()

    def InitializeGUI(self):
        self.setWindowTitle("Calculator")
        self.setFixedSize(320,500)
        self.setWindowIcon(QIcon("resources\\icon.png"))
        with open("styles.css", "r") as f:
            self.setStyleSheet(f.read())
        
    def CreateInteraction(self):
        layout = QVBoxLayout()

        self.display = QLineEdit()
        self.display.setReadOnly(True)
        layout.addWidget(self.display)

        buttons = [
            "CE", "C","<-", "/",
            "7", "8", "9", "*",
            "4", "5", "6", "-",
            "1", "2", "3", "+",
            "%", "0", ",", "="
        ]

        grid_layout = QGridLayout()

        row, col = 0, 0

        for text_button in buttons:
            button = QPushButton(text_button)
            button.clicked.connect(lambda checked, text=text_button: self.pressed_button(text))
            grid_layout.addWidget(button, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1
        
        layout.addLayout(grid_layout)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(3)
        self.setLayout(layout)

    def pressed_button(self, text):
        if text == "=":
            expression = self.display.text()
            result = Calculate(expression)
            self.display.setText(str(result))
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
