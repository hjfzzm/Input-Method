# -*- coding:UTF-8 -*-
# Create time: 2019-12-20
# Code by: hjfzzm
from pypinyin import pinyin, Style

s = ''
list_word = []
list_pinyin = []
for i in range(0x4e00, 0x9fa5):
    s += chr(i)
    list_word.append(chr(i))
list_pinyin = pinyin(s, style=Style.NORMAL, heteronym=True)
# print(list_word)
# print(list_pinyin)

dict_dic = {}
for i in range(0, len(list_word)):
    word = list_word[i]
    pinyin = list_pinyin[i]
    for py in pinyin:
        if py in dict_dic:
            dict_dic[py].append(list_word[i])
        else:
            tmp_list = [list_word[i], ]
            dict_dic[py] = tmp_list

tuple_dic = sorted(dict_dic.items(), key=lambda x: x[0])

with open("Files/dictionary.txt", "w", encoding='UTF-8') as file:
    for tup in tuple_dic:
        py = tup[0]
        word = tup[1]
        file.write(py)
        file.write(":")
        for zi in word:
            file.write(zi)
        file.write("\n")

# 手动删除最后几行不能识别的汉字
