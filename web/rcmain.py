# -*-coding:UTF-8–*-

from scipy import integrate
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from web.rcdata import *
import os
import time

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIR = os.path.join(BASE_DIR, 'templates/web/images')


class RC:
    # def __init__(self, b, h, rc_type, A_s, steel_type, mode):
    def __init__(self, shape, rc_type, A_s, steel_type, mode):

        # 初始化RC样本
        _fcuk = [15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]
        _fc = [7.2, 9.6, 11.9, 14.3, 16.7, 19.1, 21.2, 23.1, 25.3, 27.5, 29.7, 31.8, 33.8, 35.9]
        _fy = [270, 300, 360, 435]
        _Es = [2.1 * 1e5, 2.0 * 1e5, 2.0 * 1e5, 2.0 * 1e5]

        self.timestamp = str(round(time.time() * 1000)) # timestamp
        # shape
        self.shape = shape['shape']
        if self.shape == Shape_Type.REC:
            self.b = shape['b']
            self.h = shape['h']
        elif self.shape == Shape_Type.T:
            self.b = shape['b']
            self.h = shape['h']
            self.bf = shape['bf']
            self.hf = shape['hf']
        elif self.shape == Shape_Type.CIR:
            self.h = shape['d_out']
            self.r = shape['d_out'] / 2
        elif self.shape == Shape_Type.RING:
            self.h = shape['d_out']
            self.r_in = shape['d_in'] / 2
            self.r_out = shape['d_out'] / 2
            self.thickness = self.r_out - self.r_in

        self.index = rc_type.value
        self.f_c = _fc[self.index]
        self.f_cuk = _fcuk[self.index]
        self.A_s = A_s
        self.f_y = _fy[steel_type.value]
        self.E_s = _Es[steel_type.value]
        self.mode = mode

        # TODO
        #    修改GZH
        if mode == Mode.GZH:
            # epsilon 10^-6
            _epsilon_0 = [1370, 1470, 1560, 1640, 1720, 1790, 1850, 1920, 1980, 2030, 2080, 2130, 2190, 2240]
            _alpha_a = [2.21, 2.15, 2.09, 2.03, 1.96, 1.9, 1.84, 1.78, 1.71, 1.65, 1.65, 1.65, 1.65]
            _alpha_d = [0.41, 0.74, 1.06, 1.36, 1.65, 1.94, 2.21, 2.48, 2.74, 3.00, 3.25, 3.50, 3.75]
            # epsilon_u_over_0 = [4.2, 3.0, 2.6, 2.3, 2.1, 2.0, 1.9, 1.9, 1.8, 1.8, 1.7, 1.7, 1.7, 1.6]
            self.epsilon_0 = _epsilon_0[self.index] * 1e-6
            self.alpha_a = _alpha_a[self.index]
            self.alpha_d = _alpha_d[self.index]
            # 此处实质上为epsilon_cu 注意和epsilon_u的区别，书P33，此处按GB取
            # self.epsilon_u = 3300
            self.epsilon_u = (0.0033 - (self.f_cuk - 50) * 1e-6) if (
                    0.0033 - (self.f_cuk - 50) * 1e-6 <= 0.0033) else 0.0033

            # 插值求参数
            # self.epsilon_0 = (_epsilon_0[self.index + 1] - _epsilon_0[self.index]) / 5 * (
            #         self.f_c - _fcuk[self.index]) + \
            #                  _epsilon_0[self.index]  # /5
            # self.alpha_a = (_alpha_a[self.index + 1] - _alpha_a[self.index]) / 5 * (
            #         self.f_c - _fcuk[self.index]) + _alpha_a[self.index]
            # self.alpha_d = (_alpha_d[self.index + 1] - _alpha_d[self.index]) / 5 * (
            #         self.f_c - _fcuk[self.index]) + _alpha_d[self.index]

        elif mode == Mode.GB:
            self.n = 2 - 1 / 60 * (self.f_cuk - 50) if 2 - 1 / 60 * (self.f_cuk - 50) <= 2 else 2
            self.epsilon_0 = (0.002 + 0.5 * (self.f_cuk - 50) * 1e-6) if (0.002 + 0.5 * (
                    self.f_cuk - 50) * 1e-6 >= 0.002) else 0.002
            self.epsilon_u = (0.0033 - (self.f_cuk - 50) * 1e-6) if (
                    0.0033 - (self.f_cuk - 50) * 1e-6 <= 0.0033) else 0.0033

        self.xn = self.get_xn()  # 计算中性轴高度
        self.alpha, self.beta = self.equiv_rec()  # 计算等效矩形应力图系数

    def equiv_rec(self):
        #   计算等效应力图形系数 alpha, beta
        xn = self.xn
        k1, err1 = integrate.quad(self.area, 0, xn, args=xn)
        k2, err2 = integrate.quad(self.inertia, 0, xn, args=xn)
        beta = 2 / xn * k2 / k1
        alpha = 1 / (beta * self.f_c * xn) * k1
        ab = (round(alpha, 4), round(beta, 4))
        return ab

    def sigma_epsilon(self, epsilon):
        #   2-22过镇海曲线
        #   epsilon 为10^-6
        if self.mode == Mode.GZH:
            x = epsilon / self.epsilon_0
            if 0 <= x <= 1:
                y = self.alpha_a * x + (3 - 2 * self.alpha_a) * x ** 2 + (self.alpha_a - 2) * x ** 3
            elif x > 1:
                y = x / (self.alpha_d * (x - 1) * (x - 1) + x)
            else:
                # 对epsilon小于0的取0
                y = 0
            return y * self.f_c
        # GB2010公式
        elif self.mode == Mode.GB:
            if epsilon > self.epsilon_0:
                return self.f_c if epsilon < self.epsilon_u else 0
            else:
                # 对epsilon小于0的取0
                return self.f_c * (1 - (1 - epsilon / self.epsilon_0) ** self.n) if epsilon > 0 else 0

    def get_b(self, x):
        if self.shape == Shape_Type.REC:
            return self.b
        elif self.shape == Shape_Type.T:
            return self.bf if x <= self.hf else self.b
        elif self.shape == Shape_Type.CIR:
            return 2 * (2 * self.r * x - x * x) ** 0.5
        elif self.shape == Shape_Type.RING:
            return 2 * ((2 * self.r_out * x - x * x) ** 0.5 - (
                    2 * self.r_in * (x - self.thickness) - (x - self.thickness) ** 2) ** 0.5) if (
                    self.thickness < x < self.h - self.thickness) else 2 * (2 * self.r_out * x - x * x) ** 0.5

    # def axis_force(self, x, xn):
    #     return self.get_b(x) * self.sigma_epsilon(-1 * self.epsilon_u / xn * x + self.epsilon_u)

    def axis_force(self, x, xn, epsilon_c):
        return self.get_b(x) * self.sigma_epsilon(-1 * epsilon_c / xn * x + epsilon_c)

    def get_xn(self):
        tolerance = 1e-10
        low = 0
        high = self.h
        flag = self.A_s * self.f_y
        while low + tolerance < high:
            xn = (low + high) / 2
            # k为轴力
            # k, err = integrate.quad(self.axis_force, 0, xn, args=xn)
            k, err = integrate.quad(self.axis_force, 0, xn, args=(xn, self.epsilon_u))
            if k < flag:
                low = xn
            else:
                high = xn
        return xn

    def area(self, x, xn):
        # sigma(x)
        return self.sigma_epsilon(-1 * self.epsilon_u / xn * x + self.epsilon_u)

    def inertia(self, x, xn):
        # x*sigma(x)
        return x * self.sigma_epsilon(-1 * self.epsilon_u / xn * x + self.epsilon_u)

    def plot(self):
        # plot
        plt.switch_backend('agg')   # NOT USE GUI
        fig = plt.figure()
        ax1 = plt.subplot(2, 1, 1)
        ax2 = plt.subplot(2, 1, 2)
        fig.tight_layout()  # 调整整体空白
        plt.subplots_adjust(wspace=0, hspace=0.3)  # 调整子图间距

        x = np.arange(0, self.h, 0.01)

        # plot epsilon-x
        plt.sca(ax1)
        ax1.set_title('ε-y', fontsize=12, color='black')
        epsilon = -1 * self.epsilon_u / self.xn * x + self.epsilon_u
        plt.plot(x, epsilon, color='blue')

        # plot sigma-x
        plt.sca(ax2)
        ax2.set_title('σ-y', fontsize=12, color='black')
        sigma = np.empty([0, 1])
        for i in x:
            sigma = np.append(sigma, self.area(i, self.xn))
        plt.plot(x, sigma, color='blue')
        plt.plot([0, self.beta * self.xn], [0, 0], color='red', linestyle='--')
        plt.plot([0, self.beta * self.xn], [self.alpha * self.f_c, self.alpha * self.f_c], color='red', linestyle='--')
        plt.plot([self.beta * self.xn, self.beta * self.xn], [0, self.alpha * self.f_c], color='red', linestyle='--')
        plt.plot([0, 0], [0, self.alpha * self.f_c], color='red', linestyle='--')

        IMAGE_NAME = 'plot' + self.timestamp + '.png'  # timestamp
        # print(IMAGE_NAME)
        # print(IMAGE_DIR)
        plt.savefig(IMAGE_DIR + '/' + IMAGE_NAME)
        # plt.show()
        return IMAGE_NAME

    def get_display_xn(self, phi, display_xn):
        tolerance = 1e-3    # set a larger num to accelerate
        low = 0
        high = display_xn   # add limit
        while low + tolerance < high:
            xn = (low + high) / 2
            epsilon_c = phi * xn
            epsilon_s = -(-phi * self.h + epsilon_c)  # positive
            steel_sigma = epsilon_s * self.E_s if epsilon_s * self.E_s < self.f_y else self.f_y  # yield or not
            flag = self.A_s * steel_sigma
            # k为轴力
            # k, err = integrate.quad(self.axis_force, 0, xn, args=xn)
            k, err = integrate.quad(self.axis_force, 0, xn, args=(xn, epsilon_c))
            if k < flag:
                low = xn
            else:
                high = xn
        return xn

    def display_area(self, x, xn, phi):
        # sigma(x)
        epsilon_c = phi * xn
        return self.sigma_epsilon(-1 * epsilon_c / xn * x + epsilon_c)

    def display(self):
        # plot
        plt.switch_backend('agg')   # NOT USE GUI
        fig, ax = plt.subplots()
        # ax1 = plt.subplot(2, 1, 1)
        # ax2 = plt.subplot(2, 1, 2)
        # fig.tight_layout()  # 调整整体空白
        # plt.subplots_adjust(wspace=0, hspace=0.3)  # 调整子图间距
        # x, sigma = [], []
        line, = plt.plot([], [], color='blue')
        limit_frame = int(self.epsilon_u / self.xn * 1e6)
        ax.set_xlim(0, self.h)
        ax.set_ylim(0, 1.2 * self.f_c)

        def init():
            return line,

        def update(step):
            # plt.sca(ax1)
            phi = step * 1e-6
            title = 'σ-y (phi = ' + str(round(phi, 6)) + ')'
            ax.set_title(title, fontsize=12, color='black')

            display_xn = self.display_xn  # initial temp
            if display_xn > self.xn:
                display_xn = self.get_display_xn(phi, display_xn)
            else:
                display_xn = self.xn

            self.display_xn = display_xn
            x = np.arange(0, self.h, 0.01)
            sigma = np.empty([0, 1])

            for i in x:
                sigma = np.append(sigma, self.display_area(i, display_xn, phi))

            # for i in x:
            #     sigma = np.append(sigma, self.area(i, self.xn))

            line.set_data(x, sigma)
            return line, display_xn,

        self.display_xn = self.h
        anime = FuncAnimation(fig, update, frames=range(1, limit_frame), init_func=init, interval=10)
        # plt.show()
        Anime_NAME = 'anime' + self.timestamp + '.gif'  # timestamp
        anime.save(IMAGE_DIR + '/' + Anime_NAME, writer='imagemagick', fps=20)
        return Anime_NAME


def test():
    #   default: C30混凝土
    # shape, rc_type, A_s, steel_type, mode
    # rc_set = RC({'shape': Shape_Type.REC, 'b': 250, 'h': 500}, RC_Type.C30, 1256, Steel_Type.HRB335, Mode.GZH)
    # print(rc_set.alpha, rc_set.beta, '\n')
    # rc_set.plot()

    rc_set2 = RC({'shape': Shape_Type.T, 'b': 250, 'h': 500, 'bf': 600, 'hf': 100}, RC_Type.C40, 2147,
                 Steel_Type.HRB400, Mode.GB)
    print(rc_set2.alpha, rc_set2.beta, '\n')
    rc_set2.plot()
    # rc_set2.display()

    #
    # rc_set3 = RC({'shape': Shape_Type.CIR, 'd_out': 400}, RC_Type.C50, 1212, Steel_Type.HRB335, Mode.GB)
    # print(rc_set3.alpha, rc_set3.beta, '\n')
    # rc_set3.plot()
    #
    # rc_set4 = RC({'shape': Shape_Type.RING, 'd_in': 300, 'd_out': 500}, RC_Type.C30, 1212, Steel_Type.HRB335, Mode.GB)
    # print(rc_set4.alpha, rc_set4.beta, '\n')
    # rc_set4.plot()

    return


