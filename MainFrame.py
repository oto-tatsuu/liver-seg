import cv2
from PySide2.QtGui import QPen, Qt
from PySide2.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTreeWidget, QAction, \
    QFileDialog

import DrawItem
from CanvasWidget import CanvasWidget, scissorLogic
from DrawItem import ItemImage
# from IntelligentScissor import scissor
from IntelligentScissor import scissor
from ToolsWidget import ToolsWidget
from Bezier import bezier_curve


class MainFrame(QMainWindow):

    def __init__(self, parent=None):
        super(MainFrame, self).__init__(parent)
        self.initUI()
        pass

    def initUI(self):

        self.setWindowTitle("My Form")
        self.mainWindowWidget=QWidget(self)

        self.mainLeftWidget =QWidget(self)
        self.mainRightWidget  =QWidget(self)
        self.i=0
        self.vlayout_left =QVBoxLayout()
        self.vlayout_right =QVBoxLayout()
        self.hlayout_all =QHBoxLayout()
        showFilePath = QLineEdit(self)
        self.tools =ToolsWidget(self)
        # tools.setStyleSheet("background:rgb(0,255,255)")
        toolBoxTree =QTreeWidget(self)
        self.canvas =CanvasWidget(self)
        self.canvas.setText("label")
        # self.canvas.setStyleSheet("background:rgb(255,0,255)")
        self.vlayout_left.addWidget(self.tools)
        self.vlayout_left.addWidget(toolBoxTree)
        self.vlayout_left.setStretchFactor(self.tools,1)
        self.vlayout_left.setStretchFactor(toolBoxTree,1)
        self.vlayout_right.addWidget(showFilePath)
        self.vlayout_right.addWidget(self.canvas)
        # self.vlayout_right.setStretchFactor(showFilePath,1)
        # self.vlayout_right.setStretchFactor(showSrcPicture,1)


        self.mainLeftWidget.setLayout(self.vlayout_left)
        self.mainRightWidget.setLayout(self.vlayout_right)
        self.hlayout_all.addWidget(self.mainLeftWidget)
        self.hlayout_all.addWidget(self.mainRightWidget)
        self.hlayout_all.setStretchFactor(self.mainLeftWidget,1)
        self.hlayout_all.setStretchFactor(self.mainRightWidget,3)
        self.mainWindowWidget.setLayout(self.hlayout_all)
        self.setCentralWidget(self.mainWindowWidget)

        #菜单
        menu=self.menuBar()
        openMenu=menu.addMenu("&Open")
        oFAct=QAction("Open File",self)
        openMenu.addAction(oFAct)

        testMenu=menu.addMenu("&Test")
        test1=QAction("Bezier",self)
        testMenu.addAction(test1)
        test2=QAction("test2",self)
        testMenu.addAction(test2)

        toolMenu=menu.addMenu("&Tools")
        penTool=QAction("Pen",self)
        toolMenu.addAction(penTool)
        scissorTool=QAction("Scissor",self)
        toolMenu.addAction(scissorTool)


        # 连接槽函数
        # self.tools.generate_contour.clicked.connect(self.generateContour)
        self.tools.generate_contour.clicked.connect(self.b1Click)
        self.tools.b2.clicked.connect(self.b2Click)
        self.tools.b3.clicked.connect(self.b3Click)
        self.tools.b4.clicked.connect(self.b4Click)
        # 打开文件
        oFAct.triggered.connect(self.onOpenFile)
        test1.triggered.connect(self.test1)
        test2.triggered.connect(self.test2)
        penTool.triggered.connect(self.penToolClick)
        scissorTool.triggered.connect(self.scissorTool)
        pass

    def generateContour(self):
        print("begin generate contour")
        if len(self.canvas.img)<=0:
            print("the pictuer empty")
        else:
            e=self.tools.contour_epsilon.value()
            #转灰度图
            gray = cv2.cvtColor(self.canvas.img,cv2.COLOR_BGR2GRAY)
            #ret 边界阈值，binary输出数组
            ret, binary = cv2.threshold(gray,15,255,cv2.THRESH_BINARY)
            contours, hierarchy = cv2.findContours(binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            self.canvas.has_contour=True
            for con in contours:
                contour=cv2.approxPolyDP(con,e,True)
                self.canvas.contours.append(contour)
            self.canvas.update()
            pass

    def b1Click(self):
        print("b1")
        # self.canvas.state=2
        self.canvas.update()
        pass

    def b2Click(self):
        print("b2")
        self.canvas.update()
        pass

    def b3Click(self):
        print("b3")
        canvas=self.canvas
        item=ItemImage(canvas.backView,0,0)
        item.width=canvas.opeView.width()
        item.height=canvas.opeView.height()
        canvas.drawItemList["images"].append(item)
        self.canvas.update()
        pass

    def b4Click(self):
        print("save")
        canvas=self.canvas
        canvas.qp.begin(self.canvas.backView)
        canvas.qp.drawImage(canvas.backView.rect(),canvas.opeView)
        canvas.qp.end()
        pass

    def penToolClick(self):
        self.canvas.toolState=1
        self.canvas.state=0
        pass

    def scissorTool(self):
        if self.canvas.toolState==2:
            return
        self.canvas.toolState=2
        self.canvas.state=0
        self.canvas.scissorLogic=scissorLogic(scissor(self.canvas.img))
        find=False
        for item in self.canvas.drawItemList["lines"]:
            # 当前列表中有且只有两个item，id为SICISSOR
            if item.id|DrawItem.ID_SCISSOR!=0:
                find=True
                item.xs=[]
                item.ys=[]
                break
        if not find:
            itemStaticList= DrawItem.ItemCurve([], [])
            itemStaticList.pen=QPen(Qt.green,1)
            itemStaticList.width=self.canvas.img.shape[1]
            itemStaticList.height=self.canvas.img.shape[0]
            itemStaticList.id=DrawItem.ID_SCISSOR|DrawItem.ID_STATIC
            itemDynamicList=DrawItem.ItemCurve([], [])
            itemDynamicList.pen=QPen(Qt.green,1)
            itemDynamicList.width=self.canvas.img.shape[1]
            itemDynamicList.height=self.canvas.img.shape[0]
            itemDynamicList.id=DrawItem.ID_SCISSOR
            self.canvas.drawItemList["lines"].append(itemStaticList)
            self.canvas.drawItemList["lines"].append(itemDynamicList)
        pass
    def onOpenFile(self):
        print("open file")
        file=QFileDialog()
        file.exec_()
    def test1(self):
        print("test1")
        canvas=self.canvas
        canvas.makeCurve=True

    def test2(self):
        # print("test2")
        # canvas=self.canvas
        # points=canvas.drawItemList[-1]["points"]
        # x_b,y_b=bezier_curve([x[0] for x in points],[x[1] for x in points],10)
        # item={}
        # item["name"]="curve"
        # item["points"]=[]
        # item["pen"]=QPen(Qt.blue,3)
        # item["id"]=1
        # item["closed"]=canvas.drawItemList[-1]["closed"]
        # for i in range(len(x_b)):
        #     item["points"].append((x_b[i],y_b[i]))
        #     item['width']=canvas.width()
        #     item['height']=canvas.height()
        # canvas.drawItemList.append(item)
        # self.update()
        pass
    pass





