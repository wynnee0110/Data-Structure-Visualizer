import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsScene, QGraphicsView,
    QGraphicsRectItem, QGraphicsTextItem, QVBoxLayout, QGraphicsEllipseItem,
    QGraphicsLineItem
)
from PyQt6.QtCore import Qt, QPointF, QRectF, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QPainter, QTextCursor, QLinearGradient
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


# --- Complete Binary Tree implementation ---
class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.parent = None
        self.height = 1


class CompleteBinaryTree:
    def __init__(self):
        self.root = None
        self.size = 0
        self.nodes = []  # Level-order list of nodes

    def insert(self, value):
        """Insert a value in level-order (complete binary tree)."""
        new_node = TreeNode(value)
        
        if not self.root:
            self.root = new_node
            self.nodes = [new_node]
            self.size = 1
            return new_node
        
        # Find the first node with an empty child slot
        for node in self.nodes:
            if not node.left:
                node.left = new_node
                new_node.parent = node
                self.nodes.append(new_node)
                self.size += 1
                self._update_heights(node)
                return new_node
            elif not node.right:
                node.right = new_node
                new_node.parent = node
                self.nodes.append(new_node)
                self.size += 1
                self._update_heights(node)
                return new_node
        
        return None

    def delete(self, value):
        """Delete a node by value (removes last node and replaces target)."""
        if not self.root:
            return False
        
        # Find the node to delete
        target = None
        for node in self.nodes:
            if node.value == value:
                target = node
                break
        
        if not target:
            return False
        
        # Get the last node
        last_node = self.nodes[-1]
        
        if target == last_node:
            # Just remove the last node
            self._remove_last_node()
        else:
            # Replace target's value with last node's value
            target.value = last_node.value
            self._remove_last_node()
        
        self.size -= 1
        return True

    def _remove_last_node(self):
        """Remove the last node in level order."""
        if not self.nodes:
            return
        
        last = self.nodes.pop()
        
        if last.parent:
            if last.parent.right == last:
                last.parent.right = None
            else:
                last.parent.left = None
            self._update_heights(last.parent)
        else:
            self.root = None

    def _update_heights(self, node):
        """Update heights from node to root."""
        while node:
            left_h = node.left.height if node.left else 0
            right_h = node.right.height if node.right else 0
            node.height = 1 + max(left_h, right_h)
            node = node.parent

    def get_height(self):
        """Get the height of the tree."""
        return self.root.height if self.root else 0

    def level_order(self):
        """Return level-order traversal."""
        return [node.value for node in self.nodes]


# --- Main Window ---
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.stack = []  # list of tuples: (value, TreeNode)
        self.tree = CompleteBinaryTree()
        self.tree_positions = {}  # store positions of nodes

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

        # TREE VIEW
        self.tree_scene = QGraphicsScene()
        self.tree_view = ZoomableGraphicsView()
        bst_layout = QVBoxLayout(self.BstView)
        bst_layout.setContentsMargins(0, 0, 0, 0)
        bst_layout.addWidget(self.tree_view)
        self.tree_view.setScene(self.tree_scene)
        self.tree_scene.setSceneRect(-2000, -2000, 5000, 5000)

        # Buttons
        self.pushButton.clicked.connect(self.push_action)
        self.popButton.clicked.connect(self.pop_action)
        self.peekButton.clicked.connect(self.peek_action)
        self.clearButton.clicked.connect(self.clear_action)

        self.draw_stack()
        self.draw_tree()

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

        tree_node = self.tree.insert(num)
        if tree_node:
            self.stack.append((num, tree_node))
            self.lineEdit.clear()
            self.draw_stack()
            self.draw_tree()
            self.show_code(f"PUSH {num}")
            self.statusbar.showMessage(f"Pushed {num} | Tree Size: {self.tree.size} | Height: {self.tree.get_height()}", 3000)
        else:
            self.statusbar.showMessage(f"Could not insert {num}", 2000)

    def pop_action(self):
        if not self.stack:
            self.statusbar.showMessage("Stack empty", 2000)
            return
        val, node = self.stack.pop()
        
        # Delete from tree if this was the last reference
        should_delete = not any(n == node for _, n in self.stack)
        if should_delete:
            self.tree.delete(val)
        
        self.draw_stack()
        self.draw_tree()
        self.show_code(f"POP {val}")
        self.statusbar.showMessage(f"Popped {val} | Tree Size: {self.tree.size} | Height: {self.tree.get_height()}", 3000)

    def peek_action(self):
        if not self.stack:
            self.statusbar.showMessage("Stack empty", 2000)
            return
        top_val, top_node = self.stack[-1]
        level_order = self.tree.level_order()
        self.show_code(f"PEEK -> {top_val} | Level-order: {level_order}")
        self.statusbar.showMessage(f"Top: {top_val} | Tree Level-order: {level_order}", 4000)

    def clear_action(self):
        self.stack.clear()
        self.tree = CompleteBinaryTree()
        self.tree_positions.clear()
        self.draw_stack()
        self.draw_tree()
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
            txt = self.stack_scene.addText("Stack is empty")
            txt.setFont(QFont("Arial", 12))
            txt.setPos(150, 150)
            return

        w, h = 120, 50
        x0, y0 = 50, 40
        spacing = 12

        for i, (val, node) in enumerate(reversed(self.stack)):
            y = y0 + i * (h + spacing)
            rect = QGraphicsRectItem(x0, y, w, h)
            
            # Gradient fill
            gradient = QLinearGradient(x0, y, x0, y + h)
            gradient.setColorAt(0, QColor(120, 170, 255))
            gradient.setColorAt(1, QColor(80, 130, 220))
            rect.setBrush(QBrush(gradient))
            rect.setPen(QPen(QColor(40, 90, 180), 2))
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
                top_text.setDefaultTextColor(QColor(220, 50, 50))
                top_text.setFont(QFont("Arial", 12, QFont.Weight.Bold))
                top_text.setPos(x0 + w + 10, y + 10)
                self.stack_scene.addItem(top_text)

                # draw line to tree node
                if node in self.tree_positions:
                    bx, by = self.tree_positions[node]
                    line = self.stack_scene.addLine(
                        x0 + w/2, y + h/2,
                        bx, by,
                        QPen(QColor(50, 200, 100), 3, Qt.PenStyle.DashLine)
                    )

    # --- Draw Complete Binary Tree ---
    def draw_tree(self):
        self.tree_scene.clear()
        self.tree_positions.clear()
        if not self.tree.root:
            txt = self.tree_scene.addText("Tree is empty")
            txt.setFont(QFont("Arial", 12))
            txt.setPos(150, 150)
            return

        # Dynamic spacing based on tree size
        base_level_y = 100
        base_spacing_x = max(80, 200 / (self.tree.get_height() + 1))

        # Compute width of subtree for positioning
        def compute_width(node, level=0):
            if not node:
                return 0
            factor = max(0.6, 1.0 - level * 0.1)  # Reduce spacing at deeper levels
            lw = compute_width(node.left, level + 1)
            rw = compute_width(node.right, level + 1)
            return max(60 * factor, lw + rw + base_spacing_x * factor)

        pos = {}
        node_levels = {}

        def assign_positions(node, x, y, level=0):
            if not node:
                return
            factor = max(0.6, 1.0 - level * 0.1)
            lw = compute_width(node.left, level + 1)
            rw = compute_width(node.right, level + 1)
            
            if node.left:
                assign_positions(node.left, x - (lw + base_spacing_x * factor)/2, 
                               y + base_level_y, level + 1)
            pos[node] = (x, y)
            node_levels[node] = level
            
            if node.right:
                assign_positions(node.right, x + (rw + base_spacing_x * factor)/2, 
                               y + base_level_y, level + 1)

        assign_positions(self.tree.root, 0, 50)
        self.tree_positions = pos

        r = 28
        edge_pen = QPen(QColor(100, 100, 100), 2.5)

        # Draw edges with better styling
        for node, (x, y) in pos.items():
            if node.left:
                lx, ly = pos[node.left]
                line = QGraphicsLineItem(x, y + r, lx, ly - r)
                line.setPen(edge_pen)
                self.tree_scene.addItem(line)
                
            if node.right:
                rx, ry = pos[node.right]
                line = QGraphicsLineItem(x, y + r, rx, ry - r)
                line.setPen(edge_pen)
                self.tree_scene.addItem(line)

        # Draw nodes with gradient and depth-based coloring
        for node, (x, y) in pos.items():
            level = node_levels[node]
            
            # Color based on depth
            hue = (200 - level * 15) % 360
            color1 = QColor.fromHsv(hue, 180, 255)
            color2 = QColor.fromHsv(hue, 200, 220)
            
            ellipse = QGraphicsEllipseItem(x - r, y - r, r*2, r*2)
            gradient = QLinearGradient(x - r, y - r, x + r, y + r)
            gradient.setColorAt(0, color1)
            gradient.setColorAt(1, color2)
            ellipse.setBrush(QBrush(gradient))
            ellipse.setPen(QPen(QColor(80, 80, 80), 2.5))
            self.tree_scene.addItem(ellipse)
            
            # Value text
            t = QGraphicsTextItem(str(node.value))
            t.setFont(QFont("Arial", 13, QFont.Weight.Bold))
            t.setDefaultTextColor(Qt.GlobalColor.white)
            br = t.boundingRect()
            t.setPos(x - br.width()/2, y - br.height()/2)
            self.tree_scene.addItem(t)

        # Add tree statistics
        stats_text = QGraphicsTextItem(
            f"Nodes: {self.tree.size}  |  Height: {self.tree.get_height()}  |  "
            f"Type: Complete Binary Tree (Level-Order Insertion)"
        )
        stats_text.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        stats_text.setDefaultTextColor(QColor(60, 60, 60))
        stats_text.setPos(-250, -40)
        self.tree_scene.addItem(stats_text)


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()