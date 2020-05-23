import numpy as np
import cv2
a = np.array((
    [0,1,0],
    [1,-4,1],
    [0,1,0]))



# b=np.array((
#     [1, 2, 3],
#     [4, 5, 6],
#     [7, 8, 9]
#     ), dtype="float32")

def fz(column,row):
        def fun(val):
            # if abs(val) < 15:
            #     return 1.0
            # else:
            #     return 0.0
            return val
            pass

        if len(img.shape)==2:
            cost=0.0
            for i in range(a.shape[0]):
                for j in range(a.shape[1]):
                    if i+row-1<0 or i+row-1>img.shape[1] or j+column-1<0 or j+column-1>img.shape[1]:
                        continue
                    cost+=a[i][j] *img[i+row-1][j+column-1]
            cost=fun(cost)
        else:
            cost=[0,0,0]
            for i in range(a.shape[0]):
                for j in range(a.shape[1]):
                    if i+row-1<0 or i+row-1>img.shape[1]-1 or j+column-1<0 or j+column-1>img.shape[1]-1:
                        continue
                    ro,go,bo=img[i+row-1][j+column-1]

                    cost[0]+=a[i][j]*ro
                    cost[1]+=a[i][j]*go
                    cost[2]+=a[i][j]*bo
            # cost=fun(cost)

        return cost
        pass
img=cv2.imread("src/hsm.jpg")

c=np.zeros(img.shape)
for i in range(c.shape[0]):
    for j in range(c.shape[1]):
        c[i][j]=fz(j,i)
# c=cv2.filter2D(img, -1, a,None,(1,1),0,cv2.BORDER_CONSTANT)
# cv2.imshow("a",img)
# cv2.waitKey(0)
cv2.imshow("img",c)
# print(c.shape)
cv2.waitKey(0)


