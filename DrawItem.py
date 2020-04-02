from PySide2.QtCore import QRect, Qt
from PySide2.QtGui import QPaintDevice, QPainter, QPen

from Bezier import bezier_curve
ID_PEN=1
ID_END=2
ID_CONTROL=4

def linearTrans(x,w0,w1):
    return x*w1/w0
    pass

class DrawItem:
    def __init__(self):
        self.width=0
        self.height=0
        self.id=0
        self.type=0
        self.pen=None
        self.brush=None
        print("init")
        pass

    def paint(self,painter:QPainter,pd:QPaintDevice):
        pass

    def setTool(self,painter):
        if self.pen !=None:
            painter.setPen(self.pen)
        if self.brush !=None:
            painter.setBrush(self.pen)




class ItemPoint(DrawItem):
    def __init__(self,x=0,y=0):
        super(ItemPoint,self).__init__()
        self.x=x
        self.y=y
        self.type="point"

        pass

    def paint(self,painter:QPainter,view:QPaintDevice):
        painter.begin(view)
        self.setTool(painter)
        x=linearTrans(self.x,self.width,view.width())
        y=linearTrans(self.y,self.height,view.height())
        painter.drawPoint(x,y)
        print("%s:(%d,%d)"%(self.type,x,y))
        print("id:%d"%self.id)
        print(id(self))
        painter.end()
        pass

    def disToPoint(self,x,y,r):
        if (self.x-x)*(self.x-x)+(self.y-y)*(self.y-y)<r*r:
            return True
        else:
            return False

    def onMouseIn(self):
        self.pen=QPen(Qt.blue,10)

    def onMouseOut(self):
        print("id")
        print(self.id)
        if self.id&ID_END!=0:
            self.pen=QPen(Qt.red,6)
        elif self.id&ID_CONTROL!=0:
            self.pen=QPen(Qt.green,6)


class ItemControlPoint(ItemPoint):
    def __init__(self,x=0,y=0,item=None):
        super(ItemControlPoint,self).__init__()
        self.x=x
        self.y=y
        self.type="control point"
        self.item=item

class ItemLine(DrawItem):
    def __init__(self,x1=0,y1=0,x2=0,y2=0):
        super(ItemLine,self).__init__()
        self.x1=x1
        self.y1=y1
        self.x2=x2
        self.y2=y2
        self.type="line"

        pass

    def paint(self,painter:QPainter,view:QPaintDevice):
        painter.begin(view)
        self.setTool(painter)
        x1=linearTrans(self.x1,self.width,view.width())
        y1=linearTrans(self.y1,self.height,view.height())
        x2=linearTrans(self.x2,self.width,view.width())
        y2=linearTrans(self.y2,self.height,view.height())
        painter.drawLine(x1,y1,x2,y2)
        print("line:(%d,%d),(%d,%d)"%(x1,y1,x2,y2))
        painter.end()
        pass

    def setP1(self,x1,y1):
        self.x1=x1
        self.y1=y1

    def setP2(self,x2,y2):
        self.x2=x2
        self.y2=y2

class ItemBezierLine(ItemLine):
    def __init__(self,num=20,x1=0,y1=0,x2=0,y2=0):
        super(ItemBezierLine,self).__init__()
        self.x1=x1
        self.y1=y1
        self.x2=x2
        self.y2=y2
        self.num=num
        self.hasControlP1=False
        self.hasControlP2=False
        self.controlP1=[(x1+x2)/2,(y1+y2)/2]
        self.controlP2=[(x1+x2)/2,(y1+y2)/2]
        self.xs=[x1,x2]
        self.ys=[y1,y2]
        self.type="bezier line"
        pass

    def paint(self,painter:QPainter,view:QPaintDevice):
        painter.begin(view)
        self.setTool(painter)
        xs=[self.x1]
        ys=[self.y1]
        if self.hasControlP1:
            xs.append(self.controlP1[0])
            ys.append(self.controlP1[1])
        if self.hasControlP2:
            xs.append(self.controlP2[0])
            ys.append(self.controlP2[1])
        xs.append(self.x2)
        ys.append(self.y2)
        bx,by=bezier_curve(xs,ys,self.num)
        for i in range(len(bx)-1):
            a1=linearTrans(bx[i],self.width,view.width())
            b1=linearTrans(by[i],self.height,view.height())
            a2=linearTrans(bx[i+1],self.width,view.width())
            b2=linearTrans(by[i+1],self.height,view.height())
            painter.drawLine(a1,b1,a2,b2)
        print("bezier line:(%d,%d),(%d,%d)"%(self.x1,self.y1,self.x2,self.y2))
        painter.end()
        pass

    def setControlP1(self,x1,y1):
        self.controlP1[0]=x1
        self.controlP1[1]=y1
        self.hasControlP1=True

    def setControlP2(self,x2,y2):
        self.controlP2[0]=x2
        self.controlP2[1]=y2
        self.hasControlP2=True

    def gradient(self,point,precision):
        bx,by=bezier_curve(self.xs,self.ys,1/precision)
        if point==0:
            return (bx[1]-self.x1,by[1]-self.y1)
        elif point==1:
            return (self.x2-bx[-2],self.y2-by[-2])
    def print(self):
        print("bezier line:(%d,%d),(%d,%d)"%(self.x1,self.y1,self.x2,self.y2))

class ItemImage(DrawItem):
    def __init__(self,img,x=0,y=0):
        super(ItemImage,self).__init__()
        self.x=x
        self.y=y
        self.img=img
        self.scaling=True
        self.type="image"

        pass

    def paint(self,painter:QPainter,view:QPaintDevice):
        if self.scaling:
            painter.begin(view)
            painter.drawImage(QRect(self.x,self.y,self.width,self.height),self.img)
            painter.end()
        pass

