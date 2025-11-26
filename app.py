import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QLabel, QGraphicsProxyWidget, QVBoxLayout
)
from PyQt6.QtGui import QPainter
from PyQt6 import uic

class ZoomView(QGraphicsView):
    def __init__(self):
        super().__init__()
        # Large scene for free panning
        self.scene = QGraphicsScene(-1000, -1000, 2000, 2000)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.current_scale = 1.0
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        # Stack parameters
        self.stack_x = 0
        self.top_y = 0
        self.box_spacing = 5

    def wheelEvent(self, event):
        zoom_in = 1.15
        zoom_out = 1 / 1.15
        scale_factor = zoom_in if event.angleDelta().y() > 0 else zoom_out
        self.current_scale *= scale_factor
        self.scale(scale_factor, scale_factor)

    def addStackedBoxes(self, stack):
        """Clear scene and re-add all boxes stacked top-down (LIFO)."""
        self.scene.clear()
        y = self.top_y
        # Reverse stack so last item is on top
        for text in reversed(stack):
            label = QLabel(text)
            label.setStyleSheet("""
                QLabel {
                    border: 2px solid black;
                                
                    background-color: black;
                    color: white;
                    font-size: 18px;
                    padding: 5px;
                }
            """)
            proxy = QGraphicsProxyWidget()
            proxy.setWidget(label)
            proxy.setFlag(QGraphicsProxyWidget.GraphicsItemFlag.ItemIsMovable, True)
            proxy.setFlag(QGraphicsProxyWidget.GraphicsItemFlag.ItemIsSelectable, True)
            proxy.setPos(self.stack_x, y)
            self.scene.addItem(proxy)
            # Move y down for next box
            y += label.sizeHint().height() + self.box_spacing

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("MainWindow.ui", self)

        self.stack = []

        # Create zoomable & draggable canvas
        self.view = ZoomView()
        if not self.canvasContainer.layout():
            self.canvasContainer.setLayout(QVBoxLayout())
        self.canvasContainer.layout().addWidget(self.view)

        # Connect buttons
        self.pushButton.clicked.connect(self.push_item)
        self.pushButton_2.clicked.connect(self.pop_item)

    def push_item(self):
        value = self.lineEdit.text()
        if value:
            self.stack.append(value)
            self.view.addStackedBoxes(self.stack)
            self.lineEdit.clear()

    def pop_item(self):
        if not self.stack:
            return
        self.stack.pop()
        self.view.addStackedBoxes(self.stack)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
