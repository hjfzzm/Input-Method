# -*- coding:UTF-8 -*-
# Create time: 2019-12-20
# Code by: hjfzzm
import numpy as np
from abc import ABCMeta, abstractmethod, ABC


class _BaseHMM(metaclass=ABCMeta):
    """
    基本HMM虚类，需要重写关于发射概率的相关虚函数
    n_state    : 隐藏状态的数目
    n_iter     : 迭代次数
    x_size     : 观测值维度
    start_prob : 初始概率
    trans_prob : 状态转换概率
    """
    def __init__(self, n_state=1, x_size=1, times=20):
        self.n_state = n_state
        self.x_size = x_size
        self.start_prob = np.ones(n_state) * (1.0 / n_state)             # 初始状态概率
        self.trans_prob = np.ones((n_state, n_state)) * (1.0 / n_state)  # 状态转换概率矩阵
        self.trained = False  # 是否需要重新训练
        self.n_iter = times   # EM训练的迭代次数

    # 初始化发射参数
    @abstractmethod
    def _init(self, x):
        pass

    # 虚函数：返回发射概率
    @abstractmethod
    def emit_prob(self, x):  # 求x在状态k下的发射概率 P(X|Z)
        return np.array([0])

    # 虚函数
    @abstractmethod
    def generate_x(self, z):  # 根据隐状态生成观测值x p(x|z)
        return np.array([0])

    # 虚函数：发射概率的更新
    @abstractmethod
    def emit_prob_updated(self, x, post_state):
        pass

    # 通过HMM生成序列
    def generate_seq(self, seq_length):
        x = np.zeros((seq_length, self.x_size))
        z = np.zeros(seq_length)
        z_pre = np.random.choice(self.n_state, 1, p=self.start_prob)  # 采样初始状态
        x[0] = self.generate_x(z_pre)  # 采样得到序列第一个值
        z[0] = z_pre
        for i in range(seq_length):
            if i is 0:
                continue
            # 公式 P(Zn + 1) = P(Zn + 1 | Zn) * P(Zn)
            z_next = np.random.choice(self.n_state, 1, p=self.trans_prob[z_pre, :][0])
            z_pre = z_next
            # P(Xn + 1 | Zn + 1)
            x[i] = self.generate_x(z_pre)
            z[i] = z_pre
        return x, z

    def decode(self, x, is_train=True):
        """
        利用维特比算法，已知序列求其隐藏状态值
        :param x: 观测值序列
        :param is_train: 是否根据该序列进行训练
        :return: 隐藏状态序列
        """
        if self.trained is False or is_train is False:  # 需要根据该序列重新训练
            self.train(x)

        x_length = len(x)  # 序列长度
        state = np.zeros(x_length)  # 隐藏状态

        pre_state = np.zeros((x_length, self.n_state))  # 保存转换到当前隐藏状态的最可能的前一状态
        max_pro_state = np.zeros((x_length, self.n_state))  # 保存传递到序列某位置当前状态的最大概率

        _, c = self.forward(x, np.ones((x_length, self.n_state)))
        max_pro_state[0] = self.emit_prob(x[0]) * self.start_prob * (1/c[0])  # 初始概率

        # 前向过程
        for i in range(x_length):
            if i == 0:
                continue
            for k in range(self.n_state):
                prob_state = self.emit_prob(x[i])[k] * self.trans_prob[:, k] * max_pro_state[i - 1]
                max_pro_state[i][k] = np.max(prob_state) * (1/c[i])
                pre_state[i][k] = np.argmax(prob_state)

        # 后向过程
        state = np.argmax(max_pro_state, axis=1).T
        for i in reversed(list(range(x_length))):
            if i == x_length - 1:
                continue
            state[i] = pre_state[i + 1][int(state[i + 1])]
        state2 = np.argsort(-max_pro_state, axis=1)
        state2 = state2[:, 0:3]

        return state, state2

    # 针对于多个序列的训练问题
    def train_batch(self, x, z_seq=None):
        # 针对于多个序列的训练问题，其实最简单的方法是将多个序列合并成一个序列，而唯一需要调整的是初始状态概率
        # 输入X类型：list(array)，数组链表的形式
        # 输入Z类型: list(array)，数组链表的形式，默认为空列表（即未知隐状态情况）
        if z_seq is None:
            z_seq = []
        self.trained = True
        x_num = len(x)  # 序列个数
        self._init(self.expand_list(x))  # 发射概率的初始化

        # 状态序列预处理，将单个状态转换为1-to-k的形式
        # 判断是否已知隐藏状态
        if z_seq == list():
            z = []  # 初始化状态序列list
            for n in range(x_num):
                z.append(list(np.ones((len(x[n]), self.n_state))))
        else:
            z = []
            for n in range(x_num):
                z.append(np.zeros((len(x[n]), self.n_state)))
                for i in range(len(z[n])):
                    z[n][i][int(z_seq[n][i])] = 1

        for e in range(self.n_iter):  # EM步骤迭代
            # 更新初始概率过程
            #  E步骤
            print(("iter: ", e), str('EM'))
            b_post_state = []  # 批量累积：状态的后验概率，类型list(array)
            b_post_adj_state = np.zeros((self.n_state, self.n_state))  # 批量累积：相邻状态的联合后验概率，数组
            b_start_prob = np.zeros(self.n_state)  # 批量累积初始概率
            for n in range(x_num):  # 对于每个序列的处理
                x_length = len(x[n])
                alpha, c = self.forward(x[n], z[n])  # P(x, z)
                beta = self.backward(x[n], z[n], c)  # P(x|z)

                post_state = alpha * beta / np.sum(alpha * beta)  # 归一化！
                b_post_state.append(post_state)
                post_adj_state = np.zeros((self.n_state, self.n_state))  # 相邻状态的联合后验概率
                for i in range(x_length):
                    if i == 0:
                        continue
                    if c[i] == 0:
                        continue
                    post_adj_state += (1 / c[i]) * np.outer(alpha[i - 1],
                                                            beta[i] * self.emit_prob(x[n][i])) * self.trans_prob

                if np.sum(post_adj_state) != 0:
                    post_adj_state = post_adj_state / np.sum(post_adj_state)  # 归一化！
                b_post_adj_state += post_adj_state  # 批量累积：状态的后验概率
                b_start_prob += b_post_state[n][0]  # 批量累积初始概率

            # M步骤，估计参数，最好不要让初始概率都为0出现，这会导致alpha也为0
            b_start_prob += 0.001*np.ones(self.n_state)
            self.start_prob = b_start_prob / np.sum(b_start_prob)
            b_post_adj_state += 0.001
            for k in range(self.n_state):
                if np.sum(b_post_adj_state[k]) == 0:
                    continue
                self.trans_prob[k] = b_post_adj_state[k] / np.sum(b_post_adj_state[k])

            self.emit_prob_updated(self.expand_list(x), self.expand_list(b_post_state))

    @staticmethod
    def expand_list(x):
        # 将list(array)类型的数据展开成array类型
        c = []
        for i in range(len(x)):
            c += list(x[i])
        return np.array(c)

    # 求向前传递因子
    def forward(self, x, z):
        x_length = len(x)
        alpha = np.zeros((x_length, self.n_state))  # P(x,z)
        alpha[0] = self.emit_prob(x[0]) * self.start_prob * z[0]  # 初始值
        # 归一化因子
        c = np.zeros(x_length)
        c[0] = np.sum(alpha[0])
        alpha[0] = alpha[0] / c[0]
        # 递归传递
        for i in range(x_length):
            if i == 0:
                continue
            alpha[i] = self.emit_prob(x[i]) * np.dot(alpha[i - 1], self.trans_prob) * z[i]
            c[i] = np.sum(alpha[i])
            if c[i] == 0:
                continue
            alpha[i] = alpha[i] / c[i]

        return alpha, c

    # 求向后传递因子
    def backward(self, x, z, c):
        x_length = len(x)
        beta = np.zeros((x_length, self.n_state))  # P(x|z)
        beta[x_length - 1] = np.ones(self.n_state)
        # 递归传递
        for i in reversed(list(range(x_length))):
            if i == x_length - 1:
                continue
            beta[i] = np.dot(beta[i + 1] * self.emit_prob(x[i + 1]), self.trans_prob.T) * z[i]
            if c[i + 1] == 0:
                continue
            beta[i] = beta[i] / c[i + 1]
        return beta


class DiscreteHMM(_BaseHMM, ABC):
    """
    发射概率为离散分布的HMM
    参数：
    emit_prob : 离散概率分布
    x_num：表示观测值的种类
    此时观测值大小x_size默认为1
    """
    def __init__(self, len_seq, n_state=1, x_num=1, times=20):
        _BaseHMM.__init__(self, n_state=n_state, x_size=1, times=times)
        list_tmp = []
        list_sum = []
        for i in range(0, x_num):
            for j in range(0, len_seq[i]):
                list_tmp.append((1.0 / x_num))
            for k in range(0, n_state - len_seq[i]):
                list_tmp.append(0)
        list_sum.append(list_tmp)
        list_tmp = []
        self.emission_prob = np.array(list_sum)
        self.emission_prob.shape = (x_num, n_state)
        emission_prob = self.emission_prob.T
        # self.emission_prob = np.ones((n_state, x_num)) * (1.0/x_num)  # 初始化发射概率均值
        self.x_num = x_num

    def _init(self, x):
        self.emission_prob = np.random.random(size=(self.n_state, self.x_num))
        for k in range(self.n_state):
            self.emission_prob[k] = self.emission_prob[k] / np.sum(self.emission_prob[k])

    def emit_prob(self, x):  # 求x在状态k下的发射概率
        prob = np.zeros(self.n_state)
        for i in range(self.n_state):
            prob[i] = self.emission_prob[i][int(x[0])]
        return prob

    def generate_x(self, z):  # 根据状态生成x p(x|z)
        return np.random.choice(self.x_num, 1, p=self.emission_prob[z][0])

    def emit_prob_updated(self, x, post_state):  # 更新发射概率
        self.emission_prob = np.zeros((self.n_state, self.x_num))
        x_length = len(x)
        for n in range(x_length):
            self.emission_prob[:, int(x[n])] += post_state[n]

        self.emission_prob += 0.1 / self.x_num
        for k in range(self.n_state):
            if np.sum(post_state[:, k]) == 0:
                continue
            self.emission_prob[k] = self.emission_prob[k] / np.sum(post_state[:, k])
