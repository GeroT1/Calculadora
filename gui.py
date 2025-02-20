from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
from PyQt6.QtGui import QIcon
from logic import Calculate

class CalculatorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.InitializeGUI()
        self.CreateInteraction()

    def InitializeGUI(self):
        self.setWindowTitle("Calculator")
        self.setGeometry(100, 100, 10, 500)
        self.setWindowIcon(QIcon("resources\\icon.png"))
        
    def CreateInteraction(self):
        layout = QVBoxLayout()

        self.display = QLineEdit()
        self.display.setReadOnly(True)
        layout.addWidget(self.display)

        buttons = [
            "(", ")","C", "/",
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
        self.setLayout(layout)

    def pressed_button(self, text):
        if text == "=":
            expression = self.display.text()
            result = Calculate(expression)
            self.display.setText(str(result))
        elif text == "<-":
            print("Borrar el ultimo caracter")
        elif text == "C":
            self.display.clear()
        elif text == "CE":
            print("Borrar ultimos numeros despues de una operacion por ejemplo en 4 x 9 se borraria el",
                   "9 no el 4 ni la x")
        else:
            self.display.setText(self.display.text() + text)
