import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsScene, QGraphicsView,
    QGraphicsRectItem, QGraphicsTextItem, QVBoxLayout
)
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QPainter, QTextCursor
from PyQt6 import uic

Ui_MainWindow, _ = uic.loadUiType("MainWindow.ui")


class ZoomableGraphicsView(QGraphicsView):
    """Pan + Zoom graphics view."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self._zoom = 0
        self._panning = False
        self._last_pos = QPointF()
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._panning = True
            self._last_pos = e.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            e.accept()
        else:
            super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if self._panning:
            delta = e.pos() - self._last_pos
            self._last_pos = e.pos()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - int(delta.x())
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - int(delta.y())
            )
            e.accept()
        else:
            super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._panning = False
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            e.accept()
        else:
            super().mouseReleaseEvent(e)

    def wheelEvent(self, e):
        scene_before = self.mapToScene(e.position().toPoint())
        delta_y = e.angleDelta().y()
        factor = 1.15 if delta_y > 0 else 1 / 1.15
        self._zoom += 1 if factor > 1 else -1
        if -12 < self._zoom < 12:
            self.scale(factor, factor)
            scene_after = self.mapToScene(e.position().toPoint())
            shift = scene_after - scene_before
            self.translate(shift.x(), shift.y())
        else:
            self._zoom = max(-12, min(self._zoom, 12))


# --- BST implementation ---
class BSTNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


class BST:
    def __init__(self):
        self.root = None

    def insert(self, value):
        new_node = BSTNode(value)
        if not self.root:
            self.root = new_node
            return new_node
        cur = self.root
        while True:
            if value < cur.value:
                if not cur.left:
                    cur.left = new_node
                    return new_node
                cur = cur.left
            elif value > cur.value:
                if not cur.right:
                    cur.right = new_node
                    return new_node
                cur = cur.right
            else:
                return None  # ignore duplicates


# --- Main Window ---
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.stack = []  # list of tuples: (value, BSTNode)
        self.bst = BST()
        self.bst_positions = {}  # store positions of nodes

        # STACK VIEW
        self.stack_scene = QGraphicsScene()
        old = self.StackView
        parent = old.parent()
        layout = parent.layout()
        self.stack_view = ZoomableGraphicsView()
        self.stack_view.setScene(self.stack_scene)
        self.stack_scene.setSceneRect(-2000, -2000, 5000, 5000)
        if layout:
            layout.replaceWidget(old, self.stack_view)
        old.deleteLater()

        # BST VIEW
        self.bst_scene = QGraphicsScene()
        self.bst_view = ZoomableGraphicsView()
        bst_layout = QVBoxLayout(self.BstView)
        bst_layout.setContentsMargins(0, 0, 0, 0)
        bst_layout.addWidget(self.bst_view)
        self.bst_view.setScene(self.bst_scene)
        self.bst_scene.setSceneRect(-2000, -2000, 5000, 5000)

        # Buttons
        self.pushButton.clicked.connect(self.push_action)
        self.popButton.clicked.connect(self.pop_action)
        self.peekButton.clicked.connect(self.peek_action)
        self.clearButton.clicked.connect(self.clear_action)

        self.draw_stack()
        self.draw_bst()

    # --- Actions ---
    def push_action(self):
        text = self.lineEdit.text().strip()
        if not text:
            self.statusbar.showMessage("Enter a number", 2000)
            return
        try:
            num = int(text)
        except:
            self.statusbar.showMessage("Invalid integer", 2000)
            return

        bst_node = self.bst.insert(num)
        self.stack.append((num, bst_node))
        self.lineEdit.clear()
        self.draw_stack()
        self.draw_bst()
        self.show_code(f"PUSH {num}")
        self.statusbar.showMessage(f"Pushed {num}", 2000)

    def pop_action(self):
        if not self.stack:
            self.statusbar.showMessage("Stack empty", 2000)
            return
        val, node = self.stack.pop()
        self.draw_stack()
        self.draw_bst()
        self.show_code(f"POP {val}")
        self.statusbar.showMessage(f"Popped {val}", 2000)

    def peek_action(self):
        if not self.stack:
            self.statusbar.showMessage("Stack empty", 2000)
            return
        top_val, top_node = self.stack[-1]
        self.show_code(f"PEEK -> {top_val}")
        self.statusbar.showMessage(f"Top value: {top_val}", 2000)

    def clear_action(self):
        self.stack.clear()
        self.bst = BST()
        self.bst_positions.clear()
        self.draw_stack()
        self.draw_bst()
        self.show_code("CLEAR")
        self.statusbar.showMessage("Cleared all data", 2000)

    # --- Code display ---
    def show_code(self, text):
        old = self.TextCode.toPlainText()
        self.TextCode.setPlainText(old + text + "\n")
        self.TextCode.moveCursor(QTextCursor.MoveOperation.End)
        self.Page.setCurrentWidget(self.CodeView)

    # --- Draw stack ---
    def draw_stack(self):
        self.stack_scene.clear()
        if not self.stack:
            self.stack_scene.addText("Stack is empty").setPos(150, 150)
            return

        w, h = 120, 50
        x0, y0 = 50, 40
        spacing = 12

        for i, (val, node) in enumerate(reversed(self.stack)):
            y = y0 + i * (h + spacing)
            rect = QGraphicsRectItem(x0, y, w, h)
            rect.setBrush(QBrush(QColor(100, 150, 255)))
            rect.setPen(QPen(Qt.GlobalColor.black, 2))
            self.stack_scene.addItem(rect)

            txt = QGraphicsTextItem(str(val))
            txt.setDefaultTextColor(Qt.GlobalColor.white)
            txt.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            tb = txt.boundingRect()
            txt.setPos(x0 + w/2 - tb.width()/2, y + h/2 - tb.height()/2)
            self.stack_scene.addItem(txt)

            # top pointer
            if i == 0:
                top_text = QGraphicsTextItem("← TOP")
                top_text.setDefaultTextColor(Qt.GlobalColor.red)
                top_text.setFont(QFont("Arial", 12, QFont.Weight.Bold))
                top_text.setPos(x0 + w + 10, y + 10)
                self.stack_scene.addItem(top_text)

                # draw line to BST node
                if node in self.bst_positions:
                    bx, by = self.bst_positions[node]
                    self.stack_scene.addLine(
                        x0 + w/2, y + h/2,
                        bx, by,
                        QPen(Qt.GlobalColor.green, 2)
                    )

    # --- Draw BST with proper layout ---
    def draw_bst(self):
        self.bst_scene.clear()
        self.bst_positions.clear()
        if not self.bst.root:
            self.bst_scene.addText("BST is empty").setPos(150, 150)
            return

        level_y = 80
        spacing_x = 40

        # Compute width of subtree for positioning
        def compute_width(node):
            if not node:
                return 0
            lw = compute_width(node.left)
            rw = compute_width(node.right)
            return max(40, lw + rw + spacing_x)

        pos = {}

        def assign_positions(node, x, y):
            if not node:
                return
            lw = compute_width(node.left)
            rw = compute_width(node.right)
            if node.left:
                assign_positions(node.left, x - (lw + spacing_x)/2, y + level_y)
            pos[node] = (x, y)
            if node.right:
                assign_positions(node.right, x + (rw + spacing_x)/2, y + level_y)

        root_width = compute_width(self.bst.root)
        assign_positions(self.bst.root, 0, 0)
        self.bst_positions = pos  # store for stack pointer line

        pen = QPen(Qt.GlobalColor.black, 2)
        r = 24

        # draw edges
        for node, (x, y) in pos.items():
            if node.left:
                lx, ly = pos[node.left]
                self.bst_scene.addLine(x, y + r, lx, ly - r, pen)
            if node.right:
                rx, ry = pos[node.right]
                self.bst_scene.addLine(x, y + r, rx, ry - r, pen)

        # draw nodes
        for node, (x, y) in pos.items():
            self.bst_scene.addEllipse(x - r, y - r, r*2, r*2, pen, QBrush(QColor(255, 150, 100)))
            t = QGraphicsTextItem(str(node.value))
            t.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            br = t.boundingRect()
            t.setPos(x - br.width()/2, y - br.height()/2)
            self.bst_scene.addItem(t)


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
