import heapq
import numpy as np
import cv2

LaplaceZeroCrossingOp = np.array((
    [1, 1, 1],
    [1,-8, 1],
    [1, 1, 1]), dtype="float32")

IxOp = np.array((
    [-1, 0, 1],
    [-1, 0, 1],
    [-1, 0, 1]), dtype="float32")

IyOp = np.array((
    [-1, -1, -1],
    [0, 0, 0],
    [1, 1, 1]), dtype="float32")


Wz = 0.3
Wg = 0.3
Wd = 0.1

DEFAULT_SEARCh_LENGTH=100
# 根2
SQRT2 = 1.4142135623730950488016887242097
SQINV = 1.0 / SQRT2
PI = 3.141592654
_2Over3PI = 2.0 / (3.0*PI)

class node:
    def __init__(self):
        self.column = 0
        self.row = 0
        self.neighborCostList = 8 * [0.0]
        self.totalCost = 0.0
        # initial:0,expanded:1,active:2
        self.state = 0
        # 记录路径
        self.prevNode = None
        pass

    def nbrNodeOffset(self, linkIndex):
        """[3,2,1],
	       [4, ,0],
	       [5,6,7]
        """
        # return C,R
        if linkIndex == 0:
            return 1, 0
        elif linkIndex == 1:
            return 1, -1
        elif linkIndex == 2:
            return 0, -1
        elif linkIndex == 3:
            return -1, -1
        elif linkIndex == 1:
            return 1, -1
        elif linkIndex == 4:
            return -1, 0
        elif linkIndex == 5:
            return -1, 1
        elif linkIndex == 6:
            return 0, 1
        elif linkIndex == 7:
            return 1, 1
        pass

    def __lt__(self, other):
        return self.totalCost < other.totalCost

class scissor:
    def __init__(self, img: np.ndarray):
        self.originImg = img
        self.row = img.shape[0]
        self.column = img.shape[1]
        if len(img.shape) == 2:
            self.channel = 1
        elif len(img.shape) == 3:
            self.channel = img.shape[2]
        self.nodes = None
        self.init()
        self.isSetSeed = False
        self.originalSeedR = []
        self.originalSeedC = []
        self.priorityQueue=[]
        self.hasReset=False
        self.Reset()
        pass

    def init(self):
        self.nodes = []
        for i in range(self.row * self.column):
            self.nodes.append(node())
        cnt = 0;
        for i in range(self.row):
            for j in range(self.column):
                self.nodes[cnt].row = i
                self.nodes[cnt].column = j
                self.nodes[cnt].totalCost = 0.0
                cnt = cnt + 1
        pass

     # 辅助函数
    def GetPixelNode(self, r, c, w):
        return self.nodes[r * w + c]

    def SetSeed(self,seedPtRow, seedPtCol):
        if seedPtRow < 0 or seedPtRow > self.row-1 or seedPtCol < 0 or seedPtCol >= self.column-1:
            return
        self.Reset()
        self.originalSeedR.append(seedPtRow)
        self.originalSeedC.append(seedPtCol)
        self.isSetSeed=True
        pass

    def getseedRow(self):
        if not self.isSetSeed:
            print("get seed error")
            return -1
        if len(self.originalSeedR)==0:
            print("get seed error")
            return -1
        if len(self.originalSeedR)!=len(self.originalSeedC):
            print("get seed error")
            return -1
        return self.originalSeedR[-1]
        pass

    def getseedCol(self):
        if not self.isSetSeed:
            print("get seed error")
            return -1
        if len(self.originalSeedC)==0:
            print("get seed error")
            return -1
        if len(self.originalSeedR)!=len(self.originalSeedC):
            print("get seed error")
            return -1
        return self.originalSeedC[-1]
        pass

    def Reset(self):
        for index in range(self.row * self.column):
            self.nodes[index].state = 0
            self.nodes[index].totalCost=0.0
        self.priorityQueue=[]
        self.hasReset=True
        pass

    def CalculateMininumPath(self, freePtRow, freePtCol):
        if freePtRow < 0 or freePtRow >= self.row-1 or freePtCol < 0 or freePtCol >= self.column-1:
            return [], []
        freeNode = self.GetPixelNode(freePtRow, freePtCol, self.column)
        xs = []
        ys = []
        # 如果没找到最短路径
        if freeNode.state!=1:
            self.LiveWireDP(freePtRow, freePtCol)
        while freeNode != None:
            xs.append(freeNode.column)
            ys.append(freeNode.row)
            freeNode = freeNode.prevNode
        print("hh")
        print(xs,ys)
        return xs, ys
        pass

    # 计算最短路径
    def LiveWireDP(self, freePtRow, freePtCol):
        if freePtRow < 0 or freePtRow > self.row-1 or freePtCol < 0 or freePtCol >= self.column-1:
            return
        seedRow=self.getseedRow()
        seedCol=self.getseedCol()
        if seedRow==-1:
            return
        if seedCol==-1:
            return
        seed=self.GetPixelNode(seedRow, seedCol, self.column)
        if self.hasReset:
            seed.totalCost = 0.0
            self.hasReset=False
            self.priorityQueue.append(seed)
        # seed.totalCost = 0.0
        # self.hasReset=False
        # self.priorityQueue.append(seed)
        while len(self.priorityQueue) != 0:
            minNode = heapq.heappop(self.priorityQueue)
            minNode.state = 1
            if minNode.column==freePtCol and minNode.row==freePtRow:
                return
            for i in range(8):
                nbrCol, nbrRow = minNode.nbrNodeOffset(i)
                nbrRow += minNode.row
                nbrCol += minNode.column
                # 安全检测
                if nbrRow < 0 or nbrRow >= self.row-1 or nbrCol < 0 or nbrCol >= self.column-1:
                    continue
                # 获得结点
                nbrNode = self.GetPixelNode(nbrRow, nbrCol, self.column)
                if nbrNode.state != 1:
                    if nbrNode.state == 0:
                        nbrNode.totalCost = minNode.totalCost + self.getCost(minNode,i)
                        nbrNode.state = 2
                        nbrNode.prevNode = minNode
                        heapq.heappush(self.priorityQueue, nbrNode)
                    elif nbrNode.state == 2:
                        totalTempCost = minNode.totalCost + self.getCost(minNode,i)
                        if totalTempCost < nbrNode.totalCost:
                            nbrNode.totalCost = totalTempCost
                            nbrNode.prevNode = minNode
                            heapq.heapify(self.priorityQueue)
        seed.prevNode = None
        pass


    def getCost(self, p, q_offset):
        cost=0.0
        offC,offR=p.nbrNodeOffset(q_offset)
        # fz
        cost+=Wz*self.fz(p.column+offC,p.row+offR)
        # fg
        cost+=Wg*self.fg(p.column+offC,p.row+offR)
        # fd
        cost+=Wd*self.fd(p.column+offC,p.row+offR)
        return cost
        pass

    def fz(self,column,row):
        def fun(val):
            if abs(val) < 15:
                return 1.0
            else:
                return 0.0
            pass
        cost=0.0
        if self.channel==1:

            for i in range(LaplaceZeroCrossingOp.shape[0]):
                for j in range(LaplaceZeroCrossingOp.shape[1]):
                    if i+row-1<0 or i+row-1>self.row-1 or j+column-1<0 or j+column-1>self.column-1:
                        continue
                    cost+=LaplaceZeroCrossingOp[i][j] *self.originImg[i+row-1][j+column-1]
            cost=fun(cost)
        else:
            for i in range(LaplaceZeroCrossingOp.shape[0]):
                for j in range(LaplaceZeroCrossingOp.shape[1]):
                    if i+row-1<0 or i+row-1>self.row-1 or j+column-1<0 or j+column-1>self.column-1:
                        continue
                    r,g,b=self.originImg[i+row-1][j+column-1]
                    n=max(r, g, b)
                    cost+=n
        return float(cost)

    def fg(self,column,row):
        def fun(valIx,valIy):
            return (int(valIx)*int(valIx)+int(valIy)*int(valIy))/255
        pass
        cost=0
        if self.channel==1:
            Ix=0
            Iy=0
            for i in range(IxOp.shape[0]):
                for j in range(IxOp.shape[1]):
                    if i+row-1<0 or i+row-1>self.row-1 or j+column-1<0 or j+column-1>self.column-1:
                        continue
                    Ix+=IxOp[i][j] *self.originImg[i+row-1][j+column-1]
                    Iy+=IyOp[i][j] *self.originImg[i+row-1][j+column-1]
            cost=fun(cost)
        else:
            for i in range(LaplaceZeroCrossingOp.shape[0]):
                for j in range(LaplaceZeroCrossingOp.shape[1]):
                    if i+row-1<0 or i+row-1>self.row-1 or j+column-1<0 or j+column-1>self.column-1:
                        continue
                    r,g,b=self.originImg[i+row-1][j+column-1]
                    n=max(r, g, b)
                    cost+=n
        return cost
        pass

    def fd(self,column,row):
        cost=0
        return cost
        pass


