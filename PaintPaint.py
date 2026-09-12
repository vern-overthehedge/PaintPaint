import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget
from PyQt6.QtGui import QImage, QPainter, QPen, QColor, QPixmap,QCursor
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

        self.history = []

    def showEvent(self, event):
        if self.image is None:
            self.image = QImage(self.size(), QImage.Format.Format_RGB32)
            self.image.fill(QColor.fromHsv(0, 0,255))
            self.setFixedSize(self.image.width(), self.image.height())
            self.history.append(QPixmap(self.image))


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
            self.Window.ui.actioneyedropper.blockSignals(True)
            self.Window.ui.actioneyedropper.setChecked(False)
            self.Window.ui.actioneyedropper.blockSignals(False)
            self.history.pop(-1)
            self.tooltype = 'brush'
        if self.tooltype == 'filltool':
            self.floodfill(int(event.position().x()), int(event.position().y()), self.brushColour)


    def mouseMoveEvent(self, event):
        if self.tooltype == 'brush': # doesnt draw while eyedropping or filling
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
            self.history.append(QPixmap(self.image)) #doesnt add to history until line has been completed

    def save(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "saved art", "Images (*.png *.jpg *.bmp *.qrc)")
        if filePath == "":
            return
        else:
            self.image.save(filePath)

    def load(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Load", "saved art","Images (*.png *.jpg *.bmp *.qrc)")
        if filePath == "":
            return
        else:
            self.image = QImage(filePath).scaled(960,540,Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.setFixedSize(self.image.width(), self.image.height())
            self.update()
            self.history.append(QPixmap(self.image))



    def clear(self):
        self.image.fill(QColor.fromHsv(0, 0, 255))
        self.image = self.image.scaled(960,540)
        self.setFixedSize(self.image.width(), self.image.height())
        self.update()
        self.history.append("clear")
        print(self.history)


    def undo(self):
        if len(self.history) > 0:
            if len(self.history) == 1:
                self.image = QImage(self.history[-1]) #will always be blank canvas, undoing past here may try to delete in an empty list, causing crash
            else:
                self.history.pop(-1)
                if self.history[-1] == "clear": #cleared canvas doesnt work correctly for some reason
                    self.image = QImage(self.history[0])
                else:
                    self.image = QImage(self.history[-1])
            self.setFixedSize(self.image.width(), self.image.height())
            self.update()

    def floodfill(self,x,y,newcolour):
        oldcolour = self.image.pixel(x, y)
        newcolour = QColor(newcolour).rgb()
        if self.image.pixel(x,y) == newcolour:
            return
        stack = [(x,y)]
        visited = set()
        while stack:
            px, py = stack.pop()
            if (px, py) in visited:
                continue
            visited.add((px, py))
            if not ((px < 0 or px >= self.image.width() or
                    py < 0 or py >= self.image.height() or
                    self.image.pixel(px, py) != oldcolour)):
                self.image.setPixel(px,py, newcolour)
                stack.append((px + 1,py))
                stack.append((px - 1, py))
                stack.append((px, py + 1))
                stack.append((px, py - 1))
        self.update()


    def updateCursor(self):
        size = self.brushSize
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setPen(QPen(QColor(0,0,0), 1))
        painter.setBrush(QColor.fromHsv(self.hue,self.saturation,self.value,255 - (self.brushSize+50)))
        painter.drawEllipse(0, 0, size - 1, size - 1)

        self.setCursor(QCursor(pixmap))










class Window(QMainWindow):
    def __init__(self):

        super(Window, self).__init__()

        self.ui = uic.loadUi('PaintPaintUi.ui', self)

        self.Canvas = self.ui.Canvas



        self.ui.SizeSlider.setValue(self.Canvas.brushSize)

        self.SizeLabel.setText(str(self.Canvas.brushSize))
        self.ui.SizeFrame.setFixedSize(self.Canvas.brushSize, self.Canvas.brushSize)
        self.ui.SizeFrame.setStyleSheet(f"border-radius:{self.Canvas.brushSize / 2}px; ;")

            #affects canvas
        self.ui.actionSave.triggered.connect(self.Canvas.save)
        self.ui.actionLoad.triggered.connect(self.Canvas.load)
        self.ui.actionClear_Canvas.triggered.connect(self.Canvas.clear)
        self.ui.actionUndo.triggered.connect(self.Canvas.undo)

            #tools
        self.ui.actioneyedropper.triggered.connect(self.eyedropper)
        self.ui.actionFill.triggered.connect(self.filltool)
            #colours
        self.ui.blackpush.clicked.connect(self.blackb)
        self.ui.redpush.clicked.connect(self.redb)
        self.ui.orangepush.clicked.connect(self.orangeb)
        self.ui.yellowpush.clicked.connect(self.yellowb)
        self.ui.greenpush.clicked.connect(self.greenb)
        self.ui.bluepush.clicked.connect(self.blueb)
        self.ui.purplepush.clicked.connect(self.purpleb)
        self.ui.whitepush.clicked.connect(self.whiteb)
        self.ui.greypush.clicked.connect(self.greyb)
        self.ui.pinkpush.clicked.connect(self.pinkb)
        self.ui.limepush.clicked.connect(self.limeb)
        self.ui.brownpush.clicked.connect(self.brownb)
        self.ui.cyanpush.clicked.connect(self.cyanb)

        self.ui.SizeSlider.valueChanged.connect(self.sizechange)

        self.ui.hueslide.valueChanged.connect(self.hue)
        self.ui.saturationslide.valueChanged.connect(self.saturation)
        self.ui.valueslide.valueChanged.connect(self.value)

        self.setColour(self.Canvas.brushColour)

        self.Canvas.Window = self

    def sizechange(self, value):
        self.Canvas.brushSize = value
        self.SizeLabel.setText(str(self.Canvas.brushSize))
        self.SizeFrame.setFixedSize(value, value)
        self.setColour(self.Canvas.brushColour)

    def eyedropper(self):
        if self.Canvas.tooltype != 'eyedropper':
            self.ui.actionFill.blockSignals(True)
            self.ui.actionFill.setChecked(False) #doesnt activate fill tool
            self.ui.actionFill.blockSignals(False) #unchecks filltool so it doesnt get confused
            self.Canvas.tooltype = 'eyedropper'
        else:
            self.Canvas.tooltype = 'brush'

    def filltool(self):
        if self.Canvas.tooltype != 'filltool':
            self.ui.actioneyedropper.blockSignals(True)
            self.ui.actioneyedropper.setChecked(False)
            self.ui.actioneyedropper.blockSignals(False)
            self.Canvas.tooltype = 'filltool'
        else:
            self.Canvas.tooltype = 'brush'

    def setColour(self, colour):
        self.Canvas.brushColour = colour
        radius = self.Canvas.brushSize // 2  # rounds to whole number because .5 doesn't work for stylesheet
        self.SizeFrame.setStyleSheet(f"background-color: rgb(0,0,0);border-radius:{radius}px;")
        self.ColourFrame.setStyleSheet(f"background-color: {colour.name()}")
        self.Canvas.hue = self.Canvas.brushColour.hue()
        if self.Canvas.hue < 0: #white and black are achromatic, it has no hue and will try to change the hue slider to -1
            self.Canvas.hue = 0
        self.Canvas.saturation = self.Canvas.brushColour.saturation()
        self.Canvas.value = self.Canvas.brushColour.value()

#most of the slider will stay the same, just gives feedback on what colour is being chosen
        self.ui.hueslide.setStyleSheet(f"""QSlider::handle:horizontal {{
border: 1px solid rgb(0,0,0);
width: 15px;
border-radius: 2px;
background:hsv({self.Canvas.hue},255,255);
}}

QSlider::groove:horizontal {{
border-radius: 10px;
border:1px solid rgb(0,0,0);
background:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(255, 0, 0, 255), stop:0.166 rgba(255, 255, 0, 255), stop:0.333 rgba(0, 255, 0, 255), stop:0.5 rgba(0, 255, 255, 255), stop:0.666 rgba(0, 0, 255, 255), stop:0.833 rgba(255, 0, 255, 255), stop:1 rgba(255, 0, 0, 255));
}}
""")

        self.ui.saturationslide.setStyleSheet(f"""QSlider::handle:horizontal {{
border: 1px solid rgb(0,0,0);
width: 15px;
border-radius: 2px;
background:hsv({self.Canvas.hue},{self.Canvas.saturation},255);
}}

QSlider::groove:horizontal {{
border-radius: 10px;
border:1px solid rgb(0,0,0);
background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 hsv({self.Canvas.hue},0,255), stop:1 hsv({self.Canvas.hue},255,255));
}}
""")
        self.ui.valueslide.setStyleSheet(f"""QSlider::handle:horizontal {{
border: 1px solid rgb(255,255,255);
width: 15px;
border-radius: 2px;
background: hsv({self.Canvas.hue},255,{self.Canvas.value});
}}

QSlider::groove:horizontal {{
border-radius: 10px;
border:1px solid rgb(0,0,0);
 background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 hsv({self.Canvas.hue},0,0), stop:1 hsv({self.Canvas.hue},255,255))
}}
"""
)



        self.ui.hueslide.setValue(self.Canvas.brushColour.hue()) #for if a preset colour is chosen, sets sliders to relevant place
        self.ui.saturationslide.setValue(self.Canvas.brushColour.saturation())
        self.ui.valueslide.setValue(self.Canvas.brushColour.value())
        self.Canvas.updateCursor()

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
        self.setColour(QColor(144, 0, 121))

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

    def cyanb(self):
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
window.showMaximized()
sys.exit(app.exec())
