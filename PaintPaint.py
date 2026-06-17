import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget
from PyQt6.QtGui import QImage, QPainter, QPen, QColor
from PyQt6.QtCore import Qt, QPoint

class Canvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None
        self.drawing = False
        self.brushSize = 10

        self.hue = 0
        self.saturation = 0
        self.value = 0

        self.brushColour = QColor.fromHsv(0, 255, 255)
        self.lastPoint = QPoint()
        self.penStyle = Qt.PenCapStyle.RoundCap

        self.tooltype = 'brush'

    def showEvent(self, event):
        if self.image is None:
            self.image = QImage(self.size(), QImage.Format.Format_RGB32)
            self.image.fill(QColor(255, 255, 255))

    def paintEvent(self, event):
        if self.image is None:
            return
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)

    def mousePressEvent(self, event):
        if self.tooltype == 'brush':
            if event.button() == Qt.MouseButton.LeftButton:
                self.drawing = True
                self.lastPoint = event.position()
                painter = QPainter(self.image)
                painter.setPen(QPen(self.brushColour, self.brushSize, Qt.PenStyle.SolidLine, self.penStyle))
                painter.drawPoint(event.position())
                self.update()
        if self.tooltype == 'eyedropper':
            colour = self.image.pixel(int(event.position().x()), int(event.position().y()))
            self.Window.setColour(QColor(colour))

    def mouseMoveEvent(self, event):
        if self.tooltype == 'brush':
            if (event.buttons() & Qt.MouseButton.LeftButton) and self.drawing:
                if self.image is None:
                    return
                painter = QPainter(self.image)
                painter.setPen(QPen(self.brushColour, self.brushSize, Qt.PenStyle.SolidLine, self.penStyle))
                painter.drawLine(self.lastPoint, event.position())
                self.lastPoint = event.position()
                self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.lastPoint = event.position()
            self.drawing = False

    def save(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "saved art", "Images (*.png *.jpg *.bmp *.qrc)")
        if filePath == "":
            return
        else:
            self.image.save(filePath)

    def clear(self):
        self.image.fill(QColor(255, 255, 255))
        self.update()


class Window(QMainWindow):
    def __init__(self):

        super(Window, self).__init__()

        self.ui = uic.loadUi('PaintPaintUi.ui', self)

        self.Canvas = self.ui.Canvas

        self.window = QImage(self.size(), QImage.Format.Format_RGB32)
        self.window.fill(QColor(200, 200, 200))

        self.ui.SizeSlider.setValue(self.Canvas.brushSize)

        self.SizeLabel.setText(str(self.Canvas.brushSize))
        self.ui.SizeFrame.setFixedSize(self.Canvas.brushSize, self.Canvas.brushSize)
        self.ui.SizeFrame.setStyleSheet(f"border-radius:{self.Canvas.brushSize / 2}px; ;")

        self.ui.actionSave.triggered.connect(self.Canvas.save)
        self.ui.actionClear_Canvas.triggered.connect(self.Canvas.clear)

        self.ui.actioneyedropper.triggered.connect(self.eyedropper)

        self.ui.actionblack.triggered.connect(self.blackb)
        self.ui.actionred.triggered.connect(self.redb)
        self.ui.actionorange.triggered.connect(self.orangeb)
        self.ui.actionyellow.triggered.connect(self.yellowb)
        self.ui.actiongreen.triggered.connect(self.greenb)
        self.ui.actionblue.triggered.connect(self.blueb)
        self.ui.actionpurple.triggered.connect(self.purpleb)
        self.ui.actionwhite.triggered.connect(self.whiteb)
        self.ui.actiongrey.triggered.connect(self.greyb)
        self.ui.actionpink.triggered.connect(self.pinkb)
        self.ui.actionlime.triggered.connect(self.limeb)
        self.ui.actionbrown.triggered.connect(self.brownb)
        self.ui.actionlightblue.triggered.connect(self.lightblueb)

        self.ui.SizeSlider.sliderMoved.connect(self.sizechange)

        self.ui.hueslide.sliderMoved.connect(self.hue)
        self.ui.saturationslide.sliderMoved.connect(self.saturation)
        self.ui.valueslide.sliderMoved.connect(self.value)

        self.setColour(self.Canvas.brushColour)

        self.Canvas.Window = self

    def sizechange(self, value):
        self.Canvas.brushSize = value
        self.SizeLabel.setText(str(self.Canvas.brushSize))
        self.SizeFrame.setFixedSize(value, value)
        self.setColour(self.Canvas.brushColour)

    def eyedropper(self):
        if self.Canvas.tooltype != 'eyedropper':
            self.Canvas.tooltype = 'eyedropper'
        else:
            self.Canvas.tooltype = 'brush'

    def setColour(self, colour):
        self.Canvas.brushColour = colour
        radius = self.Canvas.brushSize // 2  # rounds to whole number because .5 doesn't work for stylesheet
        self.SizeFrame.setStyleSheet(f"background-color: rgb(0,0,0);border-radius:{radius}px;")
        self.ColourFrame.setStyleSheet(f"background-color: {colour.name()}")
        self.Canvas.hue = self.Canvas.brushColour.hue()
        self.Canvas.saturation = self.Canvas.brushColour.saturation()
        self.Canvas.value = self.Canvas.brushColour.value()

        self.ui.hueslide.setValue(self.Canvas.brushColour.hue())
        self.ui.saturationslide.setValue(self.Canvas.brushColour.saturation())
        self.ui.valueslide.setValue(self.Canvas.brushColour.value())

    def blackb(self):
        self.setColour(QColor(0, 0, 0))

    def redb(self):
        self.setColour(QColor(255, 0, 0))

    def orangeb(self):
        self.setColour(QColor(255, 160, 16))

    def yellowb(self):
        self.setColour(QColor(255, 224, 32))

    def greenb(self):
        self.setColour(QColor(0, 192, 0))

    def blueb(self):
        self.setColour(QColor(0, 32, 255))

    def purpleb(self):
        self.setColour(QColor(160, 32, 255))

    def whiteb(self):
        self.setColour(QColor(255, 255, 255))

    def greyb(self):
        self.setColour(QColor(128, 128, 128))

    def pinkb(self):
        self.setColour(QColor(255, 96, 208))

    def limeb(self):
        self.setColour(QColor(0, 255, 0))

    def brownb(self):
        self.setColour(QColor(150, 75, 0))

    def lightblueb(self):
        self.setColour(QColor(80, 208, 255))

    def hue(self, value):
        self.Canvas.hue = value
        self.customb()

    def saturation(self, value):
        self.Canvas.saturation = value
        self.customb()

    def value(self, value):
        self.Canvas.value = value
        self.customb()

    def customb(self):
        hue = self.Canvas.hue
        sat = self.Canvas.saturation
        val = self.Canvas.value
        self.setColour(QColor.fromHsv(hue, sat, val))


app = QApplication(sys.argv)
app.setStyle("windowsvista")
window = Window()
window.show()
sys.exit(app.exec())
