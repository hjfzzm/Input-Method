# -*- coding:UTF-8 -*-
# Create time: 2019-12-20
# Code by: hjfzzm
import socket
import threading
from Pinyin2Hanzi import DefaultHmmParams
from Pinyin2Hanzi import is_pinyin
from Pinyin2Hanzi import simplify_pinyin
from Pinyin2Hanzi import viterbi

# 全局变量
re_string = ""
# host = '172.17.228.35'
host = '127.0.0.1'
port = 10086
hmm = DefaultHmmParams()


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
        with open("Files/pinyin_rule.txt", "r", encoding='UTF-8') as read:
            for line in read:
                word = line.strip().split(' ')
                if len(word) == 1:
                    self.add([word[0], ])
                else:
                    self.add([word[0], word[1], ])

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


def interactive(client, addr):
    global re_string, pyt
    seq = []
    with open("Files/simple_words.txt", "r", encoding='UTF-8') as read:
        for line in read:
            line = line.strip()
            seq.append(line)
    voca = {}
    with open("Files/vocabulary.txt", "r", encoding='UTF-8') as read:
        for line in read:
            line = line.strip().split(":")
            voca[line[0]] = line[1]

    while True:
        try:
            text = client.recv(4096).decode('UTF-8')
            text = text.split('\t')[1]
            re_string = ""
            if text == "" or text == "send":
                text = 'send\t' + ""
                client.send(text.encode('UTF-8'))
                print("Text is NULL but send")
            else:
                if "send" in text:
                    text = text[0: len(text) - 4]
                words = pyt.scan(str(text))
                re_tup = tuple()
                for item in words:
                    if "invalid" not in item:
                        # tmp += item + "\'"
                        if not is_pinyin(item):
                            item = simplify_pinyin(item)
                        tmp = (item,)
                        re_tup += tmp
                print("Recv: ", end="")
                print(re_tup)
                re_string = ""
                try:
                    re_string = ""
                    result = viterbi(hmm_params=hmm, observations=re_tup, path_num=3, log=True)
                    n = 0
                    for item in result:
                        n += 1
                        string_t = str(n) + "."
                        re_string += string_t
                        for word in item.path:
                            re_string += word
                        re_string += "\n"
                    tmp = ""
                    for item in result:
                        for word in item.path:
                            tmp += word
                        break
                    for i in range(0, len(seq)):
                        if tmp in seq[i][0:len(tmp)] and len(seq[i]) > len(tmp):
                            n += 1
                            string_t = str(n) + "."
                            re_string += string_t + seq[i] + "\n"
                            if n == 6:
                                break
                    if text in voca.keys():
                        n += 1
                        string_t = str(n) + "."
                        re_string += string_t + voca[text] + "\n"
                    dan_tup = (re_tup[0], )
                    result = viterbi(hmm_params=hmm, observations=dan_tup, path_num=100, log=True)
                    for item in result:
                        n += 1
                        if n == 9:
                            n = 1
                        string_t = str(n) + "."
                        re_string += string_t
                        for word in item.path:
                            re_string += word
                        re_string += "\n"
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


if __name__ == '__main__':
    link()
