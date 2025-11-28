import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
    QVBoxLayout, QLineEdit
)
from PyQt6.QtGui import QPen, QBrush, QFont
from PyQt6.QtCore import Qt, QPointF
from PyQt6 import uic

# ------------------------
# BST Node and BST Class
# ------------------------
class BSTNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None

    def insert(self, val):
        if not self.root:
            self.root = BSTNode(val)
        else:
            self._insert_node(self.root, val)

    def _insert_node(self, node, val):
        if val < node.val:
            if node.left:
                self._insert_node(node.left, val)
            else:
                node.left = BSTNode(val)
        else:
            if node.right:
                self._insert_node(node.right, val)
            else:
                node.right = BSTNode(val)

# ------------------------
# BST Graphics
# ------------------------
class BSTGraphics:
    def __init__(self, graphics_view: QGraphicsView):
        self.view = graphics_view
        self.scene = QGraphicsScene(-2000, -2000, 4000, 4000)
        self.view.setScene(self.scene)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.node_radius = 25
        self.y_spacing = 80

    def draw_bst(self, root):
        self.scene.clear()
        if root:
            width = self.view.viewport().width()
            start_x = 0
            start_y = 50
            self._draw_node(root, start_x, start_y, width / 2)
            self.view.centerOn(0, start_y)  # Center by default

    def _draw_node(self, node, x, y, x_offset):
        circle = self.scene.addEllipse(
            x - self.node_radius, y, self.node_radius * 2, self.node_radius * 2,
            pen=QPen(Qt.GlobalColor.black, 2),
            brush=QBrush(Qt.GlobalColor.white)
        )
        label = self.scene.addText(str(node.val), QFont("Arial", 14))
        label.setPos(x - 8, y + 7)

        if node.left:
            child_x = x - x_offset / 2
            child_y = y + self.node_radius * 2 + self.y_spacing
            self.scene.addLine(
                x, y + self.node_radius * 2,
                child_x, child_y,
                pen=QPen(Qt.GlobalColor.blue, 2)
            )
            self._draw_node(node.left, child_x, child_y, x_offset / 2)

        if node.right:
            child_x = x + x_offset / 2
            child_y = y + self.node_radius * 2 + self.y_spacing
            self.scene.addLine(
                x, y + self.node_radius * 2,
                child_x, child_y,
                pen=QPen(Qt.GlobalColor.blue, 2)
            )
            self._draw_node(node.right, child_x, child_y, x_offset / 2)

# ------------------------
# Stack Graphics
# ------------------------
class StackGraphics:
    def __init__(self, graphics_view: QGraphicsView):
        self.view = graphics_view
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def draw_stack(self, stack):
        self.scene.clear()
        y = 0
        top_label = self.scene.addText("TOP →", QFont("Arial", 16))
        top_label.setPos(-70, y)
        y += 30
        for text in reversed(stack):
            rect = self.scene.addRect(0, y, 80, 50, QPen(Qt.GlobalColor.black, 2), QBrush(Qt.GlobalColor.white))
            label = self.scene.addText(str(text), QFont("Arial", 14))
            label.setPos(25, y + 10)
            y += 50 + 20
        # Center stack scene
        self.view.centerOn(40, y/2)

# ------------------------
# Main Window
# ------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("MainWindow.ui", self)

        # Stack
        self.stack = []
        self.stack_graphics = StackGraphics(QGraphicsView())
        if not self.canvasContainer.layout():
            self.canvasContainer.setLayout(QVBoxLayout())
        self.canvasContainer.layout().addWidget(self.stack_graphics.view)

        # BST
        self.bst = BST()
        self.bst_graphics = BSTGraphics(self.graphicsView)

        # Add input for BST
        self.lineEditBST = QLineEdit(self)
        self.lineEditBST.setPlaceholderText("Enter number for BST")
        self.frame.layout().addWidget(self.lineEditBST)
        self.lineEditBST.returnPressed.connect(self.insert_bst)

        # Connect stack buttons
        self.pushButton.clicked.connect(self.push_stack)
        self.pushButton_2.clicked.connect(self.pop_stack)
        self.pushButton_7.clicked.connect(self.clear_stack)

    # ------------------------
    # Stack Operations
    # ------------------------
    def push_stack(self):
        value = self.lineEdit.text()
        if value:
            self.stack.append(value)
            self.stack_graphics.draw_stack(self.stack)
            self.lineEdit.clear()

            # Add to BST automatically
            try:
                val = int(value)
                self.bst.insert(val)
                self.bst_graphics.draw_bst(self.bst.root)
            except ValueError:
                pass

    def pop_stack(self):
        if self.stack:
            self.stack.pop()
            self.stack_graphics.draw_stack(self.stack)

    def clear_stack(self):
        self.stack = []
        self.stack_graphics.draw_stack(self.stack)

    # ------------------------
    # BST Operation
    # ------------------------
    def insert_bst(self):
        value = self.lineEditBST.text()
        if value:
            try:
                val = int(value)
                self.bst.insert(val)

                self.bst_graphics.draw_bst(self.bst.root)
                self.lineEditBST.clear()
            except ValueError:
                pass

# ------------------------
# Run Application
# ------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
