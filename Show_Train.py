# -*- coding:UTF-8 -*-
# Create time: 2019-12-20
# Code by: hjfzzm
import re
import Show_HMM
import socket
import threading
import numpy as np

# 全局变量设置
dictionary_file = "Files/dictionary.txt"
words_file = "Files/pinyin_train.txt"
re_string = ""
host = '127.0.0.1'
port = 10085


class PyTrieNode(object):
    def __init__(self, key="", seq=None):
        if seq is None:
            seq = []
        self.key = key
        self.end = len(seq) == 0
        self.children = {}
        if len(seq) > 0:
            self.children[seq[0]] = PyTrieNode(seq[0], seq[1:])

    def add(self, seq):
        if len(seq) == 0:
            self.end = True
        else:
            key = seq[0]
            value = seq[1:]
            if key in self.children:
                self.children[key].add(value)
            else:
                self.children[key] = PyTrieNode(key, value)

    def find(self, sent):
        for i in range(len(sent)):
            i = len(sent) - i
            if len(sent) >= i:
                key = sent[:i]
                if key in self.children:
                    buf, succ = self.children[key].find(sent[i:])
                    if succ:
                        return key + buf, True
        return "", self.end


class PyTrie(object):
    def __init__(self):
        self.root = PyTrieNode()
        self.root.end = False

    def setup(self):
        self.add(["a"])
        self.add(["ai"])
        self.add(["an"])
        self.add(["ang"])
        self.add(["ao"])
        self.add(["e"])
        self.add(["ei"])
        self.add(["en"])
        self.add(["er"])
        self.add(["o"])
        self.add(["ou"])
        self.add(["b", "a"])
        self.add(["b", "ai"])
        self.add(["b", "an"])
        self.add(["b", "ang"])
        self.add(["b", "ao"])
        self.add(["b", "ei"])
        self.add(["b", "en"])
        self.add(["b", "eng"])
        self.add(["b", "i"])
        self.add(["b", "ian"])
        self.add(["b", "iao"])
        self.add(["b", "ie"])
        self.add(["b", "in"])
        self.add(["b", "ing"])
        self.add(["b", "o"])
        self.add(["b", "u"])
        self.add(["c", "a"])
        self.add(["c", "ai"])
        self.add(["c", "an"])
        self.add(["c", "ang"])
        self.add(["c", "ao"])
        self.add(["c", "e"])
        self.add(["c", "en"])
        self.add(["c", "eng"])
        self.add(["c", "i"])
        self.add(["c", "ong"])
        self.add(["c", "ou"])
        self.add(["c", "u"])
        self.add(["c", "uan"])
        self.add(["c", "ui"])
        self.add(["c", "un"])
        self.add(["c", "uo"])
        self.add(["ch", "a"])
        self.add(["ch", "ai"])
        self.add(["ch", "an"])
        self.add(["ch", "ang"])
        self.add(["ch", "ao"])
        self.add(["ch", "e"])
        self.add(["ch", "en"])
        self.add(["ch", "eng"])
        self.add(["ch", "i"])
        self.add(["ch", "ong"])
        self.add(["ch", "ou"])
        self.add(["ch", "u"])
        self.add(["ch", "uai"])
        self.add(["ch", "uan"])
        self.add(["ch", "uang"])
        self.add(["ch", "ui"])
        self.add(["ch", "un"])
        self.add(["ch", "uo"])
        self.add(["d", "a"])
        self.add(["d", "ai"])
        self.add(["d", "an"])
        self.add(["d", "ang"])
        self.add(["d", "ao"])
        self.add(["d", "e"])
        self.add(["d", "eng"])
        self.add(["d", "i"])
        self.add(["d", "ia"])
        self.add(["d", "ian"])
        self.add(["d", "iao"])
        self.add(["d", "ie"])
        self.add(["d", "ing"])
        self.add(["d", "iu"])
        self.add(["d", "ong"])
        self.add(["d", "ou"])
        self.add(["d", "u"])
        self.add(["d", "uan"])
        self.add(["d", "ui"])
        self.add(["d", "un"])
        self.add(["d", "uo"])
        self.add(["f", "a"])
        self.add(["f", "an"])
        self.add(["f", "ang"])
        self.add(["f", "ei"])
        self.add(["f", "en"])
        self.add(["f", "eng"])
        self.add(["f", "o"])
        self.add(["f", "ou"])
        self.add(["f", "u"])
        self.add(["g", "a"])
        self.add(["g", "ai"])
        self.add(["g", "an"])
        self.add(["g", "ang"])
        self.add(["g", "ao"])
        self.add(["g", "e"])
        self.add(["g", "ei"])
        self.add(["g", "en"])
        self.add(["g", "eng"])
        self.add(["g", "ong"])
        self.add(["g", "ou"])
        self.add(["g", "u"])
        self.add(["g", "ua"])
        self.add(["g", "uai"])
        self.add(["g", "uan"])
        self.add(["g", "uang"])
        self.add(["g", "ui"])
        self.add(["g", "un"])
        self.add(["g", "uo"])
        self.add(["h", "a"])
        self.add(["h", "ai"])
        self.add(["h", "an"])
        self.add(["h", "ang"])
        self.add(["h", "ao"])
        self.add(["h", "e"])
        self.add(["h", "ei"])
        self.add(["h", "en"])
        self.add(["h", "eng"])
        self.add(["h", "ong"])
        self.add(["h", "ou"])
        self.add(["h", "u"])
        self.add(["h", "ua"])
        self.add(["h", "uai"])
        self.add(["h", "uan"])
        self.add(["h", "uang"])
        self.add(["h", "ui"])
        self.add(["h", "un"])
        self.add(["h", "uo"])
        self.add(["j", "i"])
        self.add(["j", "ia"])
        self.add(["j", "ian"])
        self.add(["j", "iang"])
        self.add(["j", "iao"])
        self.add(["j", "ie"])
        self.add(["j", "in"])
        self.add(["j", "ing"])
        self.add(["j", "iong"])
        self.add(["j", "iu"])
        self.add(["j", "u"])
        self.add(["j", "uan"])
        self.add(["j", "ue"])
        self.add(["j", "un"])
        self.add(["k", "a"])
        self.add(["k", "ai"])
        self.add(["k", "an"])
        self.add(["k", "ang"])
        self.add(["k", "ao"])
        self.add(["k", "e"])
        self.add(["k", "en"])
        self.add(["k", "eng"])
        self.add(["k", "ong"])
        self.add(["k", "ou"])
        self.add(["k", "u"])
        self.add(["k", "ua"])
        self.add(["k", "uai"])
        self.add(["k", "uan"])
        self.add(["k", "uang"])
        self.add(["k", "ui"])
        self.add(["k", "un"])
        self.add(["k", "uo"])
        self.add(["l", "a"])
        self.add(["l", "ai"])
        self.add(["l", "an"])
        self.add(["l", "ang"])
        self.add(["l", "ao"])
        self.add(["l", "e"])
        self.add(["l", "ei"])
        self.add(["l", "eng"])
        self.add(["l", "i"])
        self.add(["l", "ia"])
        self.add(["l", "ian"])
        self.add(["l", "iang"])
        self.add(["l", "iao"])
        self.add(["l", "ie"])
        self.add(["l", "in"])
        self.add(["l", "ing"])
        self.add(["l", "iu"])
        self.add(["l", "ong"])
        self.add(["l", "ou"])
        self.add(["l", "u"])
        self.add(["l", "u:"])
        self.add(["l", "u:e"])
        self.add(["l", "uan"])
        self.add(["l", "un"])
        self.add(["l", "uo"])
        self.add(["m", ""])
        self.add(["m", "a"])
        self.add(["m", "ai"])
        self.add(["m", "an"])
        self.add(["m", "ang"])
        self.add(["m", "ao"])
        self.add(["m", "e"])
        self.add(["m", "ei"])
        self.add(["m", "en"])
        self.add(["m", "eng"])
        self.add(["m", "i"])
        self.add(["m", "ian"])
        self.add(["m", "iao"])
        self.add(["m", "ie"])
        self.add(["m", "in"])
        self.add(["m", "ing"])
        self.add(["m", "iu"])
        self.add(["m", "o"])
        self.add(["m", "ou"])
        self.add(["m", "u"])
        self.add(["n", "a"])
        self.add(["n", "ai"])
        self.add(["n", "an"])
        self.add(["n", "ang"])
        self.add(["n", "ao"])
        self.add(["n", "e"])
        self.add(["n", "ei"])
        self.add(["n", "en"])
        self.add(["n", "eng"])
        self.add(["n", "g"])
        self.add(["n", "i"])
        self.add(["n", "ian"])
        self.add(["n", "iang"])
        self.add(["n", "iao"])
        self.add(["n", "ie"])
        self.add(["n", "in"])
        self.add(["n", "ing"])
        self.add(["n", "iu"])
        self.add(["n", "ong"])
        self.add(["n", "ou"])
        self.add(["n", "u"])
        self.add(["n", "u:"])
        self.add(["n", "u:e"])
        self.add(["n", "uan"])
        self.add(["n", "uo"])
        self.add(["p", "a"])
        self.add(["p", "ai"])
        self.add(["p", "an"])
        self.add(["p", "ang"])
        self.add(["p", "ao"])
        self.add(["p", "ei"])
        self.add(["p", "en"])
        self.add(["p", "eng"])
        self.add(["p", "i"])
        self.add(["p", "ian"])
        self.add(["p", "iao"])
        self.add(["p", "ie"])
        self.add(["p", "in"])
        self.add(["p", "ing"])
        self.add(["p", "o"])
        self.add(["p", "ou"])
        self.add(["p", "u"])
        self.add(["q", "i"])
        self.add(["q", "ia"])
        self.add(["q", "ian"])
        self.add(["q", "iang"])
        self.add(["q", "iao"])
        self.add(["q", "ie"])
        self.add(["q", "in"])
        self.add(["q", "ing"])
        self.add(["q", "iong"])
        self.add(["q", "iu"])
        self.add(["q", "u"])
        self.add(["q", "uan"])
        self.add(["q", "ue"])
        self.add(["q", "un"])
        self.add(["r", "an"])
        self.add(["r", "ang"])
        self.add(["r", "ao"])
        self.add(["r", "e"])
        self.add(["r", "en"])
        self.add(["r", "eng"])
        self.add(["r", "i"])
        self.add(["r", "ong"])
        self.add(["r", "ou"])
        self.add(["r", "u"])
        self.add(["r", "uan"])
        self.add(["r", "ui"])
        self.add(["r", "un"])
        self.add(["r", "uo"])
        self.add(["s", "a"])
        self.add(["s", "ai"])
        self.add(["s", "an"])
        self.add(["s", "ang"])
        self.add(["s", "ao"])
        self.add(["s", "e"])
        self.add(["s", "en"])
        self.add(["s", "eng"])
        self.add(["s", "i"])
        self.add(["s", "ong"])
        self.add(["s", "ou"])
        self.add(["s", "u"])
        self.add(["s", "uan"])
        self.add(["s", "ui"])
        self.add(["s", "un"])
        self.add(["s", "uo"])
        self.add(["sh", "a"])
        self.add(["sh", "ai"])
        self.add(["sh", "an"])
        self.add(["sh", "ang"])
        self.add(["sh", "ao"])
        self.add(["sh", "e"])
        self.add(["sh", "ei"])
        self.add(["sh", "en"])
        self.add(["sh", "eng"])
        self.add(["sh", "i"])
        self.add(["sh", "ou"])
        self.add(["sh", "u"])
        self.add(["sh", "ua"])
        self.add(["sh", "uai"])
        self.add(["sh", "uan"])
        self.add(["sh", "uang"])
        self.add(["sh", "ui"])
        self.add(["sh", "un"])
        self.add(["sh", "uo"])
        self.add(["t", "a"])
        self.add(["t", "ai"])
        self.add(["t", "an"])
        self.add(["t", "ang"])
        self.add(["t", "ao"])
        self.add(["t", "e"])
        self.add(["t", "eng"])
        self.add(["t", "i"])
        self.add(["t", "ian"])
        self.add(["t", "iao"])
        self.add(["t", "ie"])
        self.add(["t", "ing"])
        self.add(["t", "ong"])
        self.add(["t", "ou"])
        self.add(["t", "u"])
        self.add(["t", "uan"])
        self.add(["t", "ui"])
        self.add(["t", "un"])
        self.add(["t", "uo"])
        self.add(["w", "a"])
        self.add(["w", "ai"])
        self.add(["w", "an"])
        self.add(["w", "ang"])
        self.add(["w", "ei"])
        self.add(["w", "en"])
        self.add(["w", "eng"])
        self.add(["w", "o"])
        self.add(["w", "u"])
        self.add(["x", "i"])
        self.add(["x", "ia"])
        self.add(["x", "ian"])
        self.add(["x", "iang"])
        self.add(["x", "iao"])
        self.add(["x", "ie"])
        self.add(["x", "in"])
        self.add(["x", "ing"])
        self.add(["x", "iong"])
        self.add(["x", "iu"])
        self.add(["x", "u"])
        self.add(["x", "uan"])
        self.add(["x", "ue"])
        self.add(["x", "un"])
        self.add(["y", "a"])
        self.add(["y", "an"])
        self.add(["y", "ang"])
        self.add(["y", "ao"])
        self.add(["y", "e"])
        self.add(["y", "i"])
        self.add(["y", "iao"])
        self.add(["y", "in"])
        self.add(["y", "ing"])
        self.add(["y", "o"])
        self.add(["y", "ong"])
        self.add(["y", "ou"])
        self.add(["y", "u"])
        self.add(["y", "uan"])
        self.add(["y", "ue"])
        self.add(["y", "un"])
        self.add(["z", "a"])
        self.add(["z", "ai"])
        self.add(["z", "an"])
        self.add(["z", "ang"])
        self.add(["z", "ao"])
        self.add(["z", "e"])
        self.add(["z", "ei"])
        self.add(["z", "en"])
        self.add(["z", "eng"])
        self.add(["z", "i"])
        self.add(["z", "ong"])
        self.add(["z", "ou"])
        self.add(["z", "u"])
        self.add(["z", "uan"])
        self.add(["z", "ui"])
        self.add(["z", "un"])
        self.add(["z", "uo"])
        self.add(["zh", "a"])
        self.add(["zh", "ai"])
        self.add(["zh", "an"])
        self.add(["zh", "ang"])
        self.add(["zh", "ao"])
        self.add(["zh", "e"])
        self.add(["zh", "en"])
        self.add(["zh", "eng"])
        self.add(["zh", "i"])
        self.add(["zh", "ong"])
        self.add(["zh", "ou"])
        self.add(["zh", "u"])
        self.add(["zh", "ua"])
        self.add(["zh", "uai"])
        self.add(["zh", "uan"])
        self.add(["zh", "uang"])
        self.add(["zh", "ui"])
        self.add(["zh", "un"])
        self.add(["zh", "uo"])

    def add(self, seq):
        self.root.add(seq)

    def scan(self, sent):
        words = []
        while len(sent) > 0:
            buf, succ = self.root.find(sent)
            # print("buf: {}, succ: {}".format(buf, succ))
            if succ:
                words.append(buf)
                sent = sent[len(buf):]
            else:
                words.append('invalid:' + sent[0])
                sent = sent[1:]
        return words


pyt = PyTrie()
pyt.setup()


# 除去字符串中的数字
def reduce_num(text):
    return re.sub("[^\u4e00-\u9fff]+", "", text)


# 预处理部分  以后会改为文章标注为拼音，再统计文章出现的文字
def precess_data():
    line_num = 0  # 统计行数
    pinyin_dict = {}
    ''' eg: pinyin_dict['a'] = 0 '''
    pinyin_char = {}
    ''' eg: pinyin_char[0] = ['啊', '阿', ...] '''
    pinyin_nums = 0

    state_seq = []
    state_seq_array = []
    line_seq = []
    line_seq_tmp = []
    line_seq_array = []
    len_seq = []

    # 读取字典信息
    with open(dictionary_file, "r", encoding='UTF-8') as dic:
        for line in dic:
            # 以分号为界分为两个部分字符串
            line = line.strip().split(":")

            # 建立拼音表，并对拼音标注序号
            pinyin_dict[line[0]] = pinyin_nums
            ''' eg: pinyin_dict['a'] = 0 '''

            # 建立每个拼音与隐状态的对应关系用于输出
            pinyin_char[pinyin_nums] = line[1]
            ''' eg: pinyin_char[0] = ['啊', '阿', ...] '''

            # 记录每个拼音所对应汉字的数量
            len_seq.append(len(line[1]))
            pinyin_nums += 1

    # 读取文章信息
    with open(words_file, "r", encoding="UTF-8") as art:
        for line in art:
            line_num += 1
            # 去掉每一行的数字
            line = reduce_num(line.strip())

            # 遍历文章中的每个汉字---k
            for k in range(len(line)):
                for i in range(len(pinyin_char)):
                    # 找到汉字k是否在序号为i的对应表中
                    j = pinyin_char[i].find(line[k])
                    if j is not -1:
                        # 记录拼音序号和汉字位置
                        line_seq_tmp.append(i)
                        state_seq.append(j)
                        break

            # 每行情况记录
            state_seq_array.append(np.array(state_seq))
            state_seq = []
            line_seq.append(line_seq_tmp)
            line_seq_tmp = []

        for i in range(line_num):
            line_seq_array.append(np.array([[line_seq[i][x]] for x in range(len(line_seq[i]))]))
    print("Process File data Done!")
    return line_seq_array, state_seq_array, pinyin_char, pinyin_dict, len_seq


# 将拼音转换成他的字典序号序列
def pinyin_trans(in_pinyin, pinyin_dic):
    pinyin_inc = []
    in_pinyin = in_pinyin.strip()
    pinyin_seq = []
    pinyin = in_pinyin.split('\'')  # 拼音输入时以单引号作为分割标志
    for n in range(len(pinyin)):
        pinyin_seq.append(pinyin_dic[pinyin[n]])
        pinyin_inc.append([pinyin_dic[pinyin[n]]])
    return pinyin_seq, np.array(pinyin_inc)


# 将拼音转汉字并输出
def char_trans_output(pinyin_seq1, char_seq, pinyin_to_char):
    global re_string
    print('1.')
    re_string += "1."
    for i in range(len(pinyin_seq1)):
        if len(pinyin_to_char[pinyin_seq1[i]]) > char_seq[i]:
            print(pinyin_to_char[pinyin_seq1[i]][char_seq[i]], end='')
            re_string += str(pinyin_to_char[pinyin_seq1[i]][char_seq[i]])
        else:
            print("\n目前语料库尚无此拼音对应的汉字出现")
            print("\n")
            re_string += "\n目前语料库尚无\n此拼音对应的汉字出现\n"
            return
    re_string += "\n"
    print('\n')


# 将拼音转汉字并输出2
def char_trans_output2(pinyin_seq2, chararray, pinyin_to_char):
    global re_string
    chars_list = []
    for i in range(len(chararray)):  # 行数，和拼音数一样多
        if len(pinyin_to_char[pinyin_seq2[i]]) < 2:
            print("您输入的拼音存在只对应1个或者没有对应汉字的情况")
            print("\n")
            re_string += "您输入的拼音存在只\n对应1个或者没有对应\n汉字的情况\n"
            return
    for i in range(len(chararray)):  # 行数，和拼音数一样多
        char_list = []
        for j in range(len(chararray[0])):  # 列数，固定位前len(chararray[0])个
            if len(pinyin_to_char[pinyin_seq2[i]]) > chararray[i][j]:
                char_list.append(pinyin_to_char[pinyin_seq2[i]][chararray[i][j]])
            else:
                re_string += "目前语料库只训练出以上结果\n"
                print("目前语料库只训练出以上结果")
                print("\n")
                return
        chars_list.append(char_list)
    # print(chars_list)
    if len(chararray) == 1:
        print('2.')
        print(chars_list[0][1], end='')
        print('\n')
        print('3.')
        print(chars_list[0][2], end='')
        print('\n')
        re_string += "2." + str(chars_list[0][1]) + "\n" + "3." + str(chars_list[0][2]) + "\n"
    if len(chararray) == 2:
        print('2.')
        print(chars_list[0][0], end='')
        print(chars_list[1][1], end='')
        print('\n')
        print('3.')
        print(chars_list[0][1], end='')
        print(chars_list[1][0], end='')
        print('\n')
        print('4.')
        print(chars_list[0][1], end='')
        print(chars_list[1][1], end='')
        print('\n')
        re_string += "2." + str(chars_list[0][0]) + str(chars_list[1][1]) + "\n" + \
                     "3." + str(chars_list[0][1]) + str(chars_list[1][0]) + "\n" + \
                     "4." + str(chars_list[0][1]) + str(chars_list[1][1]) + "\n"

    if len(chararray) == 3:
        print('2.')
        print(chars_list[0][0], end='')
        print(chars_list[1][0], end='')
        print(chars_list[2][1], end='')
        print('\n')
        print('3.')
        print(chars_list[0][0], end='')
        print(chars_list[1][1], end='')
        print(chars_list[2][0], end='')
        print('\n')
        print('4.')
        print(chars_list[0][1], end='')
        print(chars_list[1][0], end='')
        print(chars_list[2][0], end='')
        print('\n')
        re_string += "2." + str(chars_list[0][0]) + str(chars_list[1][0]) + str(chars_list[2][1]) + "\n" + \
                     "3." + str(chars_list[0][0]) + str(chars_list[1][1]) + str(chars_list[2][0]) + "\n" + \
                     "4." + str(chars_list[0][1]) + str(chars_list[1][0]) + str(chars_list[2][0]) + "\n"


X, Z, pinyin_to_char_dic, pinyin_dic, len_seq = precess_data()
word_seg_hmm = Show_HMM.DiscreteHMM(len_seq, max(len_seq), len(pinyin_dic), 1)
word_seg_hmm.train_batch(X, Z)


def trans(pinyin):
    sentence_1 = str(pinyin)
    pinyin_seq, z = pinyin_trans(sentence_1, pinyin_dic)
    Z, Z2 = word_seg_hmm.decode(z)
    Z = Z.astype(int)
    Z2 = Z2.astype(int)
    char_trans_output(pinyin_seq, Z, pinyin_to_char_dic)
    char_trans_output2(pinyin_seq, Z2, pinyin_to_char_dic)


def interactive(client, addr):
    global re_string, pyt
    while True:
        try:
            text = client.recv(1024).decode('UTF-8')
            text = text.split('\t')[1]
            re_string = ""
            if text == "" or text == "send":
                text = 'send\t' + ""
                client.send(text.encode('UTF-8'))
                print("Text is NULL but send")
            else:
                words = pyt.scan(str(text))
                '''
                text = text.split('\'')
                tmp = ""
                for item in text:
                    tmp += item
                '''
                tmp = ""
                for item in words:
                    if "invalid" not in item:
                        tmp += item + "\'"
                tmp = tmp[0: len(tmp) - 1]
                print("Recv: " + tmp)
                re_string = ""
                try:
                    re_string = ""
                    trans(tmp)
                    re_string = "send\t" + re_string
                    client.send(re_string.encode('UTF-8'))
                    print(re_string)
                except:
                    print("Recv Error")
        except:
            print(str(addr) + 'is out')
            client.close()
            break


def link():
    global host, port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)
    print("Wait for connect")
    while True:
        client, addr = sock.accept()
        print(str(addr) + 'call in')
        t = threading.Thread(target=interactive, args=(client, addr, ))
        t.start()


def main():
    # 训练
    X, Z, pinyin_to_char_dic, pinyin_dic, len_seq = precess_data()
    word_seg_hmm = Show_HMM.DiscreteHMM(len_seq, max(len_seq), len(pinyin_dic), 1)
    word_seg_hmm.train_batch(X, Z)

    '''
    print(("startprob_prior: ", wordseg_hmm.start_prob))
    print(("transmit: ", wordseg_hmm.transmat_prob))
    '''

    # 交互
    while True:
        sentence_1 = input("请输入拼音：")
        pinyin_seq, z = pinyin_trans(sentence_1, pinyin_dic)
        Z, Z2 = word_seg_hmm.decode(z)
        Z = Z.astype(int)
        Z2 = Z2.astype(int)
        char_trans_output(pinyin_seq, Z, pinyin_to_char_dic)
        char_trans_output2(pinyin_seq, Z2, pinyin_to_char_dic)


if __name__ == '__main__':
    link()
