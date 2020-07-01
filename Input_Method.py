# -*- coding:UTF-8 -*-
# Create time: 2019-12-20
# Code by: hjfzzm
import time
import socket
import threading
import pyperclip
from tkinter import *
import tkinter.messagebox
from pynput import keyboard
from pykeyboard import PyKeyboard
from pynput.keyboard import Key, Listener
import unicodedata

# 全局变量
# Socket相关
host = '123.56.106.176'
# host = '127.0.0.1'
port = 10086
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))
# 中转字符串
se_string = ""  # 用于发送字符串
single_key = ""  # 监听按压字符
re_string = ""  # 用于接收字符串
status = 1  # 中英切换状态
english = False  # 中英切换状态
page = 0
length = 0
null_time = 0
k = PyKeyboard()  # 创建键盘
# 创建主窗体与位置信息
windows = Tk(className='1')
screenwidth = windows.winfo_screenwidth()
screenheight = windows.winfo_screenheight()
width = 200
height = 30
position = "{}x{}+{}+{}".format(width, height, int((screenwidth - width) / 4 * 3), int((screenheight - height) / 4 * 3))
windows.geometry(position)
windows.overrideredirect(True)
windows.wm_attributes('-topmost', 1)
# 创建子窗口与位置信息
sub = Toplevel()
sub.overrideredirect(True)
sub.wm_attributes('-topmost', 1)
wid = 200
hei = 200
pos = "{}x{}+{}+{}".format(wid, hei, int((screenwidth - width) / 4 * 3 + width), int((screenheight - height) / 4 * 3))
sub.geometry(pos)


# 主窗口自刷新线程
def refresh():
    global se_string, windows, english
    py_label = tkinter.Label(windows, bg='green', font=('Arial', 12), width=200, height=30)
    py_label.pack()
    while True:
        if english is False:
            py_label.config(text=se_string)
        else:
            py_label.config(text="English Mode")
        windows.update()
        time.sleep(0.05)


def trans_to_C(string):
    E_pun = u',.!?[]()<>"\''
    C_pun = u'，。！？【】（）《》“‘'
    table = {ord(f): ord(t) for f, t in zip(E_pun, C_pun)}
    return string.translate(table)


# 得到键入的值
def get_key_name(key):
    global se_string, windows, english, status, sub, re_string, k, page, length
    if isinstance(key, keyboard.KeyCode):
        if str(0) <= str(key.char) <= str(9):
            try:
                re_string = re_string.split('\n')[int(key.char) - 1 + page * 8].split('.')[1]
                pyperclip.copy(re_string)
                for i in range(len(se_string) + 1 + length):
                    k.tap_key(k.backspace_key)
                k.press_key(k.control_r_key)
                k.tap_key('v')
                k.release_key(k.control_r_key)
                se_string = ""
                length = 0
            except:
                se_string = ""
                length = 0
            return key.char
        if str(key.char) == "]":
            if se_string != "":
                send(client, se_string)
                length += 1
                page += 1
            return key.char
        if str(key.char) == "[":
            if se_string != "":
                send(client, se_string)
                if page > 0:
                    page -= 1
                length += 1
            return key.char
        if english is False and (str(key.char) > str(9) or str(key.char) < str(0)) and ('a' <= str(key.char) <= 'z'):
            se_string += str(key.char)
            send(client, se_string)
            page = 0
        if len(se_string) == 1 and se_string == "v":
            se_string = ""
        if key.char in u',.!?[]()<>"\'' and english is False:
            char = trans_to_C(key.char)
            pyperclip.copy(char)
            k.tap_key(k.backspace_key)
            k.press_key(k.control_r_key)
            k.tap_key('v')
            k.release_key(k.control_r_key)
            se_string = ""
            length = 0
        return key.char
    elif str(key) == "Key.backspace" and english is False:
        try:
            se_string = se_string[0: len(se_string) - 1]
        except:
            se_string = ""
        send(client, se_string)
        return str(key)
    elif str(key) == "Key.shift":
        if english:
            english = False
            se_string = ""
        else:
            english = True
            se_string = "English Mode"
            sub.withdraw()
        print("English:", english)
        return str(key)

    elif str(key) == "Key.space":
        try:
            re_string = re_string.split('\n')[0].split('.')[1]
            pyperclip.copy(re_string)
            for i in range(len(se_string) + 1):
                k.tap_key(k.backspace_key)
            k.press_key(k.control_r_key)
            k.tap_key('v')
            k.release_key(k.control_r_key)
            se_string = ""
        except:
            se_string = ""
        return str(key)
    else:
        # send(client, se_string)
        return str(key)


# 监听按压
def on_press(key):
    global windows, status, single_key, sub
    single_key = get_key_name(key)
    print(single_key, end="\n")
    if single_key == "Key.ctrl_l":
        status *= -1
        if status < 0:
            windows.withdraw()
            sub.withdraw()
        else:
            windows.update()
            windows.deiconify()


# 监听释放
def on_release(key):
    # print(get_key_name(key), end="")
    if key == Key.esc:
        # 停止监听
        return False


# 开始监听
def start_listen():
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


# 全局发送函数
def send(clients, text):
    global null_time
    if text != "":
        text = "send\t" + text
        clients.send(text.encode('UTF-8'))
        print("\nSend Success")
        null_time = 0
    elif null_time < 1:
        null_time += 1
        text = "send\t" + text
        clients.send(text.encode('UTF-8'))
        print("\nSend Success")


# 子窗口自刷新线程
def sub_refresh():
    global single_key, client, re_string, status, page
    sub_label = tkinter.Label(sub, bg='blue', font=('Arial', 12), width=200, height=30)
    sub_label.pack()
    sub.withdraw()
    while True:
        try:
            text = client.recv(4096).decode('UTF-8').split('\t')[1]
            sub_label.config(text="")
            print("Sub window recv: ", text)
            tmp = str(text)
            # print(len(tmp), type(text))
            text_list = []
            pre = 0
            pos = 0
            for i in range(0, len(tmp)):
                if tmp[i] == "\n":
                    pos += 1
                if pos == 8:
                    text_list.append(tmp[pre: i + 1])
                    pre = i + 1
                    pos = 0
            if pos != 0 and pos != 8:
                text_list.append(tmp[pre:])
            # print(text_list)
            if text != "" and text != "send" and status > 0:
                re_string = text
                try:
                    text = text_list[page]
                except:
                    text = text_list[len(text_list) - 1]
                    page = len(text_list) - 1
                sub_label.config(text=text)
                sub.update()
                sub.deiconify()
            else:
                sub.withdraw()
        except:
            break
        # time.sleep(0.01)


if __name__ == '__main__':
    # send(client, "start")
    # 监听线程
    t = threading.Thread(target=start_listen)
    t.start()
    # 自刷新线程
    t = threading.Thread(target=refresh)
    t.start()
    # 子窗口线程
    t = threading.Thread(target=sub_refresh)
    t.start()
    # 主窗口线程
    windows.mainloop()
