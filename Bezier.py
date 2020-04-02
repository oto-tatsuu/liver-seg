import numpy as np
import matplotlib.pyplot as plt


def one_bezier(a, b, t):
    return (1 - t) * a + t * b


# p_list 点集
# n 阶数
# k 当前点索引
def n_bezier(p_list, n, k, t):
    if n == 1:
        return one_bezier(p_list[k], p_list[k + 1], t)
    else:
        return (1 - t) * n_bezier(p_list, n - 1, k, t) + t * n_bezier(p_list, n - 1, k + 1, t)


def bezier_curve(xs, ys, num):
    t_step = 1.0 / (num - 1)
    n=len(xs)-1
    t = np.arange(0.0, 1 + t_step, t_step)
    b_xs = []
    b_ys = []
    for each in t:
        b_xs.append(n_bezier(xs, n, 0, each))
        b_ys.append(n_bezier(ys, n, 0, each))
    return b_xs, b_ys


# def func():
#     xs = [1.0, 2.1, 3.0, 4.0, 5.0, 6.0]
#     ys = [0, 1.1, 1.5, 1.0, 0.2, 0]
#     num = 20
#
#     b_xs, b_ys = bezier_curve(xs, ys,20)  # 将计算结果加入到列表中
#     print(b_xs, b_ys)
#     plt.figure()
#     plt.plot(b_xs, b_ys,'r')  # bezier曲线
#     plt.plot(xs, ys)  # 原曲线
#     plt.show()
#
#
# func()
