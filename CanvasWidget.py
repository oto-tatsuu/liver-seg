import PySide2
from PySide2.QtCore import QRect
from PySide2.QtGui import QPainter, QPixmap, QPen, Qt, QImage, QPaintDevice, QBrush
from PySide2.QtWidgets import QLabel

import DrawItem
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
        self.img_w = 0
        self.img_h = 0
        self.drawItemList = {"images": [], "lines": [], "points": []}
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
        pen = QPen(Qt.red, 6)
        self.drawList(self.qp, self.opeView, self.drawItemList, pen)
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
        if self.state == 1:
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
        elif self.state == 2:
            print("state2")
            if not self.selectedItem["points"][0].disToPoint(pos.x(), pos.y(), 5):
                self.state = 1
                self.selectedItem["points"][0].onMouseOut()
                self.selectedItem["points"] = []
                self.selectedItem["in_lines"] = []
                self.selectedItem["out_lines"] = []
            self.update()
        elif self.state == 3:
            print("state3")
            self.selectedItem["points"][0].x = int(pos.x())
            self.selectedItem["points"][0].y = int(pos.y())
            for i in self.selectedItem["in_lines"]:
                i.setP2(int(pos.x()), int(pos.y()))
            print(self.selectedItem["out_lines"])
            for i in self.selectedItem["out_lines"]:
                i.setP1(int(pos.x()), int(pos.y()))
            cPoint=self.selectedItem["points"][0]
            if cPoint.id&DrawItem.ID_CONTROL!=0:
                if cPoint.item.controlP1[0]==cPoint.x and cPoint.item.controlP1[1]==cPoint.y:
                    cPoint.item.setControlP1(int(pos.x()),int(pos.y()))
                else:
                    cPoint.item.setControlP2(int(pos.x()),int(pos.y()))
            self.update()
        pass

    def mousePressEvent(self, event):
        pos = event.localPos()
        # 状态机实现
        if self.state == 0:
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
        elif self.state == 1:
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
        elif self.state == 2:
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
        elif self.state == 4:
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
            line=DrawItem.ItemLine(self.selectedItem["points"][0].x,self.selectedItem["points"][0].y,pos.x(),pos.y())
            line.width=self.width()
            line.height=self.height()
            line.pen=QPen(Qt.yellow,3)
            line.id=DrawItem.ID_PEN
            self.drawItemList["lines"].append(line)
            self.state=2
            self.update()
            pass

        pass

    def mouseReleaseEvent(self, event):
        if self.state == 3:
            self.state = 2
        pass

    def setImage(self, dir):
        img = QImage(dir)
        self.img_w = img.width()
        self.img_h = img.height()
        self.qp.begin(self.backView)
        self.qp.drawImage(self.backView.rect(), img)
        self.qp.end()

    # point: {'pos':(x,y),'width':w,'height':h}
    # curve:{'points':[],'width':w,'height':h}
    # image:{'scaling':True,'image':QImage,'pos':(x,y),'width':w,'height':h}
    def drawList(self, painter: QPainter, view: QPaintDevice, list, pen: QPen = None, brush: QBrush = None, ):
        if len(list) <= 0:
            return
        for keys, value in enumerate(list):
            if len(list[value]) > 0:
                for item in list[value]:
                    item.paint(painter, view)
                print("-----------------------")
        # if len(list["images"])>0:
        #     for item in list["images"]:
        #         item.paint(painter,view)
        #
        # if len(list["points"])>0:
        #     for item in list["points"]:
        #         item.paint(painter,view)
        #
        #         pass
        # if len(list["lines"])>0:
        #     for item in list["liness"]:
        #         item.paint(painter,view)
        #
        #         pass
        # painter.begin(view)
        # if pen!=None:
        #     painter.setPen(pen)
        # if brush!=None:
        #     painter.setBrush(brush)
        # if len(list)>0:
        #     for item in list:
        #         if "pen" in item.keys():
        #             painter.setPen(item["pen"])
        #         if "brush" in item.keys():
        #             painter.setBrush(item["brush"])
        #         if item['name']=="point":
        #             x,y=self.linearTrans(item['pos'][0],item['pos'][1],item['width'],item['height'],view.width(),view.height())
        #             painter.drawPoint(x,y)
        #         if item['name']=="curve":
        #             if len(item['points'])<=0:
        #                 continue
        #             elif len(item['points'])==1:
        #                 x,y=self.linearTrans(item['points'][0][0],item['points'][0][1],item['width'],item['height'],view.width(),view.height())
        #                 painter.drawPoint(x,y)
        #             else:
        #                 for i in range(len(item['points'])):
        #                     x1=0
        #                     x2=0
        #                     y1=0
        #                     y2=0
        #                     x1,y1=self.linearTrans(item['points'][i][0],item['points'][i][1],item['width'],item['height'],view.width(),view.height())
        #                     if i+1!=len(item['points']):
        #                         x2,y2=self.linearTrans(item['points'][i+1][0],item['points'][i+1][1],item['width'],item['height'],view.width(),view.height())
        #                         painter.drawLine(x1,y1,x2,y2)
        #                     else:
        #                         if item["closed"]:
        #                             x2,y2=self.linearTrans(item['points'][0][0],item['points'][0][1],item['width'],item['height'],view.width(),view.height())
        #                             painter.drawLine(x1,y1,x2,y2)
        #         if item["name"]=="image":
        #             if item["scaling"]:
        #                 painter.drawImage(QRect(item["pos"][0],item["pos"][1],item["width"],item["height"]),item["image"])
        # painter.end()
        pass

    def linearTrans(self, x, y, w0, h0, w1, h1):
        return (x * w1 / w0, y * h1 / h0)
