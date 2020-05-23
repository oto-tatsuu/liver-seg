# -*- coding: utf-8 -*-
import heapq

import numpy as np
import cv2


Wz = 0.3
Wg = 0.3
Wd = 0.1
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
        self.fzCostMap = None
        self.fgCostMap = None
        self.Ix = None
        self.Iy = None
        self.isSetSeed = False
        self.originalSeedR = []
        self.originalSeedC = []
        self.nodes = None
        self.init()
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
        print("init fz map")
        self.fzCostMap = cv2.filter2D(self.originImg, -1, LaplaceZeroCrossingOp)
        print("init Ix")
        self.Ix = cv2.filter2D(self.originImg, -1, IxOp)
        print("init Iy")
        self.Iy = cv2.filter2D(self.originImg, -1, IyOp)
        # self.ComputeAndCumulateFzCostMap()
        self.ComputeAndCumulateFgCostMap()
        self.ComputeAndCumulateFdCostMap()
        print("scissor init ok")
        pass

    # 辅助函数
    def GetPixelNode(self, r, c, w):
        return self.nodes[r * w + c]

    def CumulateLinkCost(self, node: node, linkIndex, Qr, Qc, costMap, scale=1.0):
        if Qc < 0 or Qc >= self.column or Qr < 0 or Qr >= self.row:
            return
        val = costMap[Qr][Qc]
        node.neighborCostList[linkIndex] += val * scale
        pass

    def ComputeAndCumulateFzCostMap(self):
        def fz(val):
            if abs(val) < 15:
                return 1.0
            else:
                return 0.0
            pass
        # def fz(val):
        #     if abs(val) < 0.00001:
        #         return 1.0
        #     else:
        #         return 0.0
        #     pass

        # def fz(val):
        #     return val
        #     pass
        if self.channel == 1:
            for i in range(self.fzCostMap.shape[0]):
                for j in range(self.fzCostMap.shape[1]):
                    self.fzCostMap[i][j] = fz(self.fzCostMap[i][j]) * Wz
        elif self.channel == 3:
            img = np.empty(self.fzCostMap.shape[0:2], dtype="float32")
            for i in range(self.fzCostMap.shape[0]):
                for j in range(self.fzCostMap.shape[1]):
                    r = fz(self.fzCostMap[i][j][0])
                    g = fz(self.fzCostMap[i][j][1])
                    b = fz(self.fzCostMap[i][j][2])
                    img[i][j] = max(r, g, b)
            self.fzCostMap = img
        else:
            print("there has some error")
            return
        for i in range(self.fzCostMap.shape[0]):
            for j in range(self.fzCostMap.shape[1]):
                node = self.GetPixelNode(i, j, self.column)
                for n in range(8):
                    offsetX, offsetY = node.nbrNodeOffset(n)
                    self.CumulateLinkCost(node, n, i + offsetY, j + offsetX, self.fzCostMap,Wz)
        print("fz map ok")
        pass

    def ComputeAndCumulateFgCostMap(self):
        self.fgCostMap=np.empty(self.Ix.shape[0:2],dtype="float32")
        print("init fg map")
        def fg(valIx,valIy):
            return (int(valIx)*int(valIx)+int(valIy)*int(valIy))/255
        if self.channel==1:
            for i in range(self.fgCostMap.shape[0]):
                for j in range(self.fgCostMap.shape[1]):
                    self.fgCostMap[i][j] = fg(self.Ix[i][j],self.Iy[i][j])
            pass
        elif self.channel==3:
            for i in range(self.fzCostMap.shape[0]):
                for j in range(self.fzCostMap.shape[1]):
                    Ix_r,Ix_g,Ix_b=self.Ix[i][j]
                    Iy_r,Iy_g,Iy_b=self.Iy[i][j]
                    self.fgCostMap[i][j] = max(
                        fg(Ix_r,Iy_r),
                        fg(Ix_g,Iy_g),
                        fg(Ix_b,Iy_b)
                    )
            pass
        else:
            print("there has some error")
            return

        # 最大值最小值标准化
        print("fg map min-max standardize")
        self.fgCostMap=1-(self.fgCostMap-self.fgCostMap.min())/(self.fgCostMap.max()-self.fgCostMap.min())
        #计算linkCost
        for i in range(self.fgCostMap.shape[0]):
            for j in range(self.fgCostMap.shape[1]):
                node = self.GetPixelNode(i, j, self.column)
                for n in range(8):
                    offsetX, offsetY = node.nbrNodeOffset(n)
                    w=Wg*SQINV if (i%2==0) else Wg
                    self.CumulateLinkCost(node, n, i + offsetY, j + offsetX, self.fgCostMap,w)
        print("fg map ok")
        pass

    def SetSeed(self,R,C):
        self.originalSeedC.append(C)
        self.originalSeedR.append(R)
        self.isSetSeed=True
        pass
    def getseedCol(self):
        return self.originalSeedC[-1]

    def getseedRow(self):
        return self.originalSeedR[-1]

    def ComputeAndCumulateFdCostMap(self):
        print("init fd map")
        RotateDMat=np.zeros((self.originImg.shape[0],self.originImg.shape[1],2),dtype="float32")
        if self.channel==1:
            for i in range(RotateDMat.shape[0]):
                for j in range(RotateDMat.shape[1]):
                    vec=np.asarray([self.Iy[i][j],-self.Ix[i][j]])
                    #梯度向量标准化：v(Iy,-Ix)
                    RotateDMat[i][j]=cv2.normalize(vec,()).reshape(2)

            pass
        elif self.channel==3:
            for i in range(RotateDMat.shape[0]):
                for j in range(RotateDMat.shape[1]):
                    Ix_r,Ix_g,Ix_b=self.Ix[i][j]
                    Iy_r,Iy_g,Iy_b=self.Iy[i][j]
                    sumIx=(int(Ix_r)+int(Ix_g)+int(Ix_b))/3
                    sumIy=(int(Iy_r)+int(Iy_g)+int(Iy_b))/3
                    vec=np.asarray([sumIy,-sumIx])
                    #D'(p)梯度向量标准化：v(Iy,-Ix)
                    RotateDMat[i][j]=cv2.normalize(vec,()).reshape(2)
            pass
        else:
            print("there have some error")
        def GenLpq(rotateDp:np.ndarray,qMinusp:np.ndarray):
            # k=sqrtinv?
            k = 1.0 / qMinusp.dot(qMinusp)**0.5
            if  rotateDp.dot(qMinusp) >= 0.0:
                return k * qMinusp
            else:
                return -k * qMinusp
            pass

        for r in range(self.row-1):
            for c in range(self.column-1):
                node=self.GetPixelNode(r,c,self.column)
                Dp=RotateDMat[r][c]
                for i in range(8):
                    qMinusp=np.asarray(node.nbrNodeOffset(i),dtype="float32")
                    Dq=RotateDMat[int(r+qMinusp[1])][int(c+qMinusp[0])]
                    Lpq = GenLpq(Dp, qMinusp);
                    dp=Lpq.dot(Dq)
                    dq=Dq.dot(Lpq)

                    node.neighborCostList[i] += ((_2Over3PI * (np.math.acos(dp) + np.math.acos(dq))) * Wd);
        print("fd map ok")
        pass

    def CalculateMininumPath(self, freePtRow, freePtCol):
        if freePtRow < 0 or freePtRow >= self.row or freePtCol < 0 or freePtCol >= self.column:
            return [], []
        freeNode = self.GetPixelNode(freePtRow, freePtCol, self.column)
        xs = []
        ys = []
        while freeNode != None:
            xs.append(freeNode.column)
            ys.append(freeNode.row)
            freeNode = freeNode.prevNode
        return xs, ys
        pass

     # 只在一定范围内生成最短路径
    def FasterCalculateMininumPath(self, freePtRow, freePtCol):
        if freePtRow < 0 or freePtRow >= self.row or freePtCol < 0 or freePtCol >= self.column:
            return [], []
        freeNode = self.GetPixelNode(freePtRow, freePtCol, self.column)
        xs = []
        ys = []
        if freeNode.prevNode==None:
            return xs,ys
        while freeNode != None:
            xs.append(freeNode.column)
            ys.append(freeNode.row)
            freeNode = freeNode.prevNode
        return xs, ys
        pass


    # 计算最短路径
    def LiveWireDP(self, seedRow, seedCol):
        if seedRow < 0 or seedRow > self.row or seedCol < 0 or seedCol >= self.column:
            return
        for index in range(self.row * self.column):
            self.nodes[index].state = 0
        seed = self.GetPixelNode(seedRow, seedCol, self.column)
        seed.totalCost = 0.0
        pq = []
        pq.append(seed)
        while len(pq) != 0:
            minNode = heapq.heappop(pq)
            minNode.state = 1
            for i in range(8):
                nbrCol, nbrRow = minNode.nbrNodeOffset(i)
                nbrRow += minNode.row
                nbrCol += minNode.column
                if nbrRow < 0 or nbrRow >= self.row or nbrCol < 0 or nbrCol >= self.column:
                    continue
                nbrNode = self.GetPixelNode(nbrRow, nbrCol, self.column)
                if nbrNode.state != 1:
                    if nbrNode.state == 0:
                        nbrNode.totalCost = minNode.totalCost + minNode.neighborCostList[i]
                        nbrNode.state = 2
                        nbrNode.prevNode = minNode
                        heapq.heappush(pq, nbrNode)
                    elif nbrNode.state == 2:
                        totalTempCost = minNode.totalCost + minNode.neighborCostList[i]
                        if totalTempCost < nbrNode.totalCost:
                            nbrNode.totalCost = totalTempCost
                            nbrNode.prevNode = minNode
                            heapq.heapify(pq)
        seed.prevNode = None
        self.isSetSeed = True
        print("min path calculate ok")
        pass

    # 只在一定范围内计算最短路径
    def FasterLiveWireDP(self, seedRow, seedCol,searchLength=DEFAULT_SEARCh_LENGTH):
        if seedRow < 0 or seedRow > self.row or seedCol < 0 or seedCol >= self.column:
            return
        for index in range(self.row * self.column):
            row=int(index/self.column)
            column=int(index%self.column)
            if row>=seedRow-searchLength/2 and row<=seedRow+searchLength/2 and column>=seedCol-searchLength/2 and column<=seedCol+searchLength/2:
                self.nodes[index].state = 0
            else:
                self.nodes[index].state=1
                self.nodes[index].prevNode=None
        seed = self.GetPixelNode(seedRow, seedCol, self.column)
        seed.totalCost = 0.0
        pq = []
        pq.append(seed)
        while len(pq) != 0:
            minNode = heapq.heappop(pq)
            minNode.state = 1
            for i in range(8):
                nbrCol, nbrRow = minNode.nbrNodeOffset(i)
                nbrRow += minNode.row
                nbrCol += minNode.column
                if nbrRow < 0 or nbrRow >= self.row or nbrCol < 0 or nbrCol >= self.column:
                    continue
                nbrNode = self.GetPixelNode(nbrRow, nbrCol, self.column)
                if nbrNode.state != 1:
                    if nbrNode.state == 0:
                        nbrNode.totalCost = minNode.totalCost + minNode.neighborCostList[i]
                        nbrNode.state = 2
                        nbrNode.prevNode = minNode
                        heapq.heappush(pq, nbrNode)
                    elif nbrNode.state == 2:
                        totalTempCost = minNode.totalCost + minNode.neighborCostList[i]
                        if totalTempCost < nbrNode.totalCost:
                            nbrNode.totalCost = totalTempCost
                            nbrNode.prevNode = minNode
                            heapq.heapify(pq)
        seed.prevNode = None
        self.isSetSeed = True
        print("faster min path calculate ok")
        pass

if __name__ == '__main__':
    a=np.arange(24)
    b=np.arange(24)
    sumIy=a[3]
    sumIx=a[4]
    print(sumIy)
    print(type(sumIx))
    vec=np.asarray([sumIy,-sumIx])
    c=cv2.normalize(vec,()).reshape(2)
    print(c)
