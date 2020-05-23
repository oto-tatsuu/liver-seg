import PySide2
import cv2
from PySide2.QtCore import QRect
from PySide2.QtGui import QPainter, QPixmap, QPen, Qt, QImage, QPaintDevice, QBrush
from PySide2.QtWidgets import QLabel

import DrawItem
import IntelligentScissor
import IntelligentScissor2
from DrawItem import ItemPoint, ItemLine, ItemBezierLine

dir = "./src/test.jpg"
"""
state:
0:空
1：至少一个点
2：鼠标移入点
3：拖住点移动
4: 添加控制点
"""


class CanvasWidget(QLabel):
    def __init__(self, parent=None):
        super(CanvasWidget, self).__init__(parent)
        self.state = 0
        self.toolState = 0  # pen:1,scissor:2
        self.scissorLogic = None
        self.img_w = 0
        self.img_h = 0
        self.img = None
        self.drawItemList = {"images": [], "lines": [], "polylines": [], "points": []}
        self.makeCurve = False
        self.mouseInPoint = False
        self.makeControlP = False
        self.selectedItem = {"points": [], "in_lines": [], "out_lines": []}
        self.seleced = 0
        self.setMouseTracking(True)
        self.initUI()
        pass

    def initUI(self):
        self.qp = QPainter()
        self.backView = QImage(785, 703, QImage.Format_RGB888)
        self.opeView = QImage(785, 703, QImage.Format_RGB888)
        self.setImage(dir)
        pass

    # 槽函数
    def paintEvent(self, event):
        self.drawList(self.qp, self.opeView, self.drawItemList)
        self.qp.begin(self)
        self.qp.drawImage(event.rect(), self.opeView)
        self.qp.end()

        pass

    def drawBackView(self, i):
        self.qp.begin(self.backView)
        self.qp.end()
        pass

    def drawOpeView(self):
        self.qp.begin(self.opeView)
        self.qp.end()
        pass

    def mouseMoveEvent(self, event):
        pos = event.localPos()
        if self.state == 1 and self.toolState == 1:
            print("state1")
            self.selectedItem["points"] = []
            self.selectedItem["in_lines"] = []
            self.selectedItem["out_lines"] = []
            for item in self.drawItemList["points"]:
                if item.disToPoint(pos.x(), pos.y(), 5):
                    self.selectedItem["points"].append(item)
                    print("in point")
                    break
            print(id(self.selectedItem["points"]))
            if len(self.selectedItem["points"]) >= 1:
                print("in")
                self.state = 2
                self.selectedItem["points"][0].onMouseIn()
            self.update()
        elif self.state == 2 and self.toolState == 1:
            print("state2")
            if not self.selectedItem["points"][0].disToPoint(pos.x(), pos.y(), 5):
                self.state = 1
                self.selectedItem["points"][0].onMouseOut()
                self.selectedItem["points"] = []
                self.selectedItem["in_lines"] = []
                self.selectedItem["out_lines"] = []
            self.update()
        elif self.state == 3 and self.toolState == 1:
            print("state3")
            self.selectedItem["points"][0].x = int(pos.x())
            self.selectedItem["points"][0].y = int(pos.y())
            for i in self.selectedItem["in_lines"]:
                i.setP2(int(pos.x()), int(pos.y()))
            print(self.selectedItem["out_lines"])
            for i in self.selectedItem["out_lines"]:
                i.setP1(int(pos.x()), int(pos.y()))
            cPoint = self.selectedItem["points"][0]
            if cPoint.id & DrawItem.ID_CONTROL != 0:
                if cPoint.item.controlP1[0] == cPoint.x and cPoint.item.controlP1[1] == cPoint.y:
                    cPoint.item.setControlP1(int(pos.x()), int(pos.y()))
                else:
                    cPoint.item.setControlP2(int(pos.x()), int(pos.y()))
            self.update()
        # scissor
        elif self.state == 0 and self.toolState == 2:
            # list[0]=itemStaticList,list[1]=itemDynamicList
            list = [x for x in self.drawItemList["lines"] if x.id & DrawItem.ID_SCISSOR != 0]
            freeX = pos.x() / self.width() * self.img.shape[1]
            freeY = pos.y() / self.height() * self.img.shape[0]
            if self.scissorLogic.scissor.isSetSeed:
                xs, ys = self.scissorLogic.CalculateMininumPath(int(freeY), int(freeX))
                print("add")
                print(xs)
                list[1].xs = xs
                list[1].ys = ys
            self.update()
            pass
        pass

    def mousePressEvent(self, event):
        pos = event.localPos()
        # 状态机实现,Pen
        if self.state == 0 and self.toolState == 1:
            # 空状态
            print("state:0")
            item = ItemPoint(pos.x(), pos.y())
            item.width = self.width()
            item.height = self.height()
            item.id = DrawItem.ID_PEN | DrawItem.ID_END
            item.pen = QPen(Qt.red, 6)
            self.drawItemList["points"].append(item)
            self.state = 1
            self.update()
        elif self.state == 1 and self.toolState == 1:
            print("state:1")
            # 至少有一个点
            # 画点
            item = ItemPoint(pos.x(), pos.y())
            item.width = self.width()
            item.height = self.height()
            item.id = DrawItem.ID_PEN | DrawItem.ID_END
            item.pen = QPen(Qt.red, 6)
            self.drawItemList["points"].append(item)
            # 画一条线
            penPointlist = [x for x in self.drawItemList["points"] if (x.id ^ (DrawItem.ID_PEN | DrawItem.ID_END)) == 0]
            i = penPointlist[-2]
            print("pen id")
            print(penPointlist)
            print(i.id)
            line = ItemBezierLine(20, i.x, i.y, pos.x(), pos.y())
            line.width = self.width()
            line.height = self.height()
            line.pen = QPen(Qt.red, 3)
            line.id = DrawItem.ID_PEN
            print(i.x, i.y)
            self.drawItemList["lines"].append(line)
            self.update()
        elif self.state == 2 and self.toolState == 1:
            if event.button() == Qt.LeftButton:
                print("press left state 2")
                item = self.selectedItem["points"][0]
                penLineItem = [x for x in self.drawItemList["lines"] if x.id & DrawItem.ID_PEN != 0]
                for i in penLineItem:
                    if i.x1 == item.x and i.y1 == item.y:
                        self.selectedItem["out_lines"].append(i)
                    elif i.x2 == item.x and i.y2 == item.y:
                        self.selectedItem["in_lines"].append(i)
                self.state = 3
            elif event.button() == Qt.RightButton:
                print("press right state 2")
                item = self.selectedItem["points"][0]
                penLineItem = [x for x in self.drawItemList["lines"] if
                               (x.type == "bezier line" and x.id & DrawItem.ID_PEN != 0)]
                for i in penLineItem:
                    if i.x1 == item.x and i.y1 == item.y and not i.hasControlP1:
                        self.selectedItem["out_lines"].append(i)
                    elif i.x2 == item.x and i.y2 == item.y and not i.hasControlP2:
                        self.selectedItem["in_lines"].append(i)
                if len(self.selectedItem["in_lines"]) <= 0 and len(self.selectedItem["out_lines"]) <= 0:
                    return
                else:
                    self.state = 4
        elif self.state == 4 and self.toolState == 1:
            # 添加控制点
            print("state4")
            item = DrawItem.ItemControlPoint(pos.x(), pos.y())
            item.width = self.width()
            item.height = self.height()
            if len(self.selectedItem["out_lines"]) > 0:
                for line in self.selectedItem["out_lines"]:
                    line.setControlP1(pos.x(), pos.y())
                    item.item = line
            if len(self.selectedItem["in_lines"]) > 0:
                for line in self.selectedItem["in_lines"]:
                    line.setControlP2(pos.x(), pos.y())
                    item.item = line
            item.pen = QPen(Qt.green, 6)
            item.id = DrawItem.ID_PEN | DrawItem.ID_CONTROL
            self.drawItemList["points"].append(item)
            line = DrawItem.ItemLine(self.selectedItem["points"][0].x, self.selectedItem["points"][0].y, pos.x(),
                                     pos.y())
            line.width = self.width()
            line.height = self.height()
            line.pen = QPen(Qt.yellow, 3)
            line.id = DrawItem.ID_PEN
            self.drawItemList["lines"].append(line)
            self.state = 2
            self.update()
            pass
        # scissor
        elif self.state == 0 and self.toolState == 2:
            print("scissor set seed start")
            x = pos.x() * self.img_w / self.width()
            y = pos.y() * self.img_h / self.height()
            list = [item for item in self.drawItemList["lines"] if item.id & DrawItem.ID_SCISSOR != 0]
            l = IntelligentScissor.DEFAULT_SEARCh_LENGTH
            x1 = x - l / 2 if x - l / 2 >= 0 else 0
            y1 = y - l / 2 if y - l / 2 >= 0 else 0
            x2 = x + l / 2 if x + l / 2 < self.img_w else self.img_w - 1
            y2 = y + l / 2 if y + l / 2 < self.img_h else self.img_h - 1
            if not self.scissorLogic.scissor.isSetSeed:
                print("scissor set seed start")
                self.scissorLogic.SetSeed(int(y),int(x))
                list[0].xs.append(x)
                list[0].ys.append(y)
                rect = DrawItem.ItemRect(x1, y1, x2, y2)
                rect.height = self.img_h
                rect.width = self.img_w
                rect.id = DrawItem.ID_SCISSOR
                pen = QPen(Qt.yellow, 3)
                pen.setStyle(Qt.DashLine)
                rect.pen = pen
                self.drawItemList["polylines"].append(rect)
            else:
                seedx = self.scissorLogic.GetSeedC()
                seedy = self.scissorLogic.GetSeedR()
                print(seedx)
                print(seedy)
                if abs(x - seedx) > l/2 or abs(y - seedy) > l/2:
                    return
                print("scissor set seed start")
                self.scissorLogic.SetSeed(int(y),int(x))
                for i in range(len(list[1].xs)):
                    list[0].xs.append(list[1].xs[-1 - i])
                    list[0].ys.append(list[1].ys[-1 - i])
                list[1].xs = []
                list[1].ys = []
                rect = None
                for item in self.drawItemList["polylines"]:
                    if item.id & DrawItem.ID_SCISSOR != 0:
                        rect = item
                        break
                rect.setPos(x1, y1, x2, y2)
                print(x1, y1, x2, y2)
            print("top")
            print(list[0].xs[-1])
            print(list[0].ys[-1])
            self.scissorLogic.LiveWireDP(int(y), int(x))
            self.update()
        pass

    def mouseReleaseEvent(self, event):
        if self.state == 3 and self.toolState == 1:
            self.state = 2
        pass

    def setImage(self, dir):
        img = QImage(dir)
        self.img_w = img.width()
        self.img_h = img.height()
        self.img = cv2.imread(dir)
        self.qp.begin(self.backView)
        self.qp.drawImage(self.backView.rect(), img)
        self.qp.end()

    # {"images": [], "lines": [], "points": []}
    def drawList(self, painter: QPainter, view: QPaintDevice, list):
        if len(list) <= 0:
            return
        print("start draw item:")
        print("-----------------------")
        for keys, value in enumerate(list):
            if len(list[value]) > 0:
                for item in list[value]:
                    item.testType()
                    item.paint(painter, view)
                print("-----------------------")
        pass

    def linearTrans(self, x, y, w0, h0, w1, h1):
        return (x * w1 / w0, y * h1 / h0)

class scissorLogic():
    def __init__(self,scissor):
        self.scissor=scissor

    def LiveWireDP(self, seedRow, seedCol, searchLength=IntelligentScissor.DEFAULT_SEARCh_LENGTH):
        return self.scissor.LiveWireDP(seedRow,seedCol)

    def CalculateMininumPath(self, freePtRow, freePtCol):
        return self.scissor.CalculateMininumPath(freePtRow, freePtCol)

    def SetSeed(self,R,C):
        # self.scissor.originalSeedC.append(C)
        # self.scissor.originalSeedR.append(R)
        self.scissor.SetSeed(R,C)
        pass

    def GetSeedR(self):
        return self.scissor.getseedRow()
        pass

    def GetSeedC(self):
        return self.scissor.getseedCol()
        pass
