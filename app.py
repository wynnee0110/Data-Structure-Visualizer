import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6 import uic
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("MainWindow.ui", self)  # load your .ui file

        self.stack = []

        # Use the existing page of stackedWidget_2
        self.stack_page = self.stackedWidget_2.currentWidget()
        self.stack_layout = QVBoxLayout(self.stack_page)
        self.stack_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Connect buttons
        self.pushButton.clicked.connect(self.push_item)
        self.pushButton_2.clicked.connect(self.pop_item)
        self.pushButton_3.clicked.connect(self.peek_item)
        self.pushButton_4.clicked.connect(self.clear_stack)
        self.pushButton_5.clicked.connect(self.check_empty)

    def update_display(self):
        # Clear previous boxes
        for i in reversed(range(self.stack_layout.count())):
            widget = self.stack_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Add new boxes for stack items
        for value in reversed(self.stack):  # show top at top
            box = QLabel(str(value))
            box.setFixedSize(80, 40)
            box.setStyleSheet("border: 1px solid black; background-color: black; text-black; color: white;")
            box.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.stack_layout.addWidget(box)

    def push_item(self):
        value = self.lineEdit.text()
        if value:
            self.stack.append(value)
            self.lineEdit.clear()
            self.update_display()

    def pop_item(self):
        if self.stack:
            self.stack.pop()
            self.update_display()

    def peek_item(self):
        if self.stack:
            print("Peek:", self.stack[-1])  # or update a label

    def clear_stack(self):
        self.stack.clear()
        self.update_display()

    def check_empty(self):
        if not self.stack:
            print("Stack is empty")
        else:
            print("Stack is not empty")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
