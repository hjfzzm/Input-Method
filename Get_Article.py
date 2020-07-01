# -*- coding:UTF-8 -*-
# Create time: 2019-12-20
# Code by: hjfzzm
import requests
from bs4 import BeautifulSoup

# 全局变量定义
list_url = []      # url库
list_news = []     # 新闻库
list_visit = []    # 已经访问的url
list_art = []      # 挑选后的可爬取规整文章url
list_vis_art = []  # 已经下载的新闻链接
list_garbage = ['【详细】', '推荐帖子', '@', 'xml', 'www', 'opyright', '微信号：', '许可证', '你的用户名',
                '修改密码', '来源：', '频道 20', '欢迎访问《领导留言板》', '………………', '视频 20', '日报 20',
                '网 20', '会 20', '发布 20', '客户端 20']
init_url = "http://www.people.com.cn/"
domain = "people.com.cn"
tmp_url = "http://politics.people.com.cn/n1/2020/0214/c1024-31586022.html"
pre_paragraph = "　　"
already_art = 0
plan_article = 20


class News:
    def __init__(self, n_title, n_text):
        self.title = n_title
        art = ""
        text = n_text.split('\n')
        for word in text:
            word = str(word.strip())
            if len(word) > 10:
                art += word + '\n'
        self.context = art

    def __eq__(self, other):
        return self.title == other.title and self.context == other.context


# 垃圾信息检测
def garbage(word):
    for dirty in list_garbage:
        if dirty in word:
            return True
    return False


# 递归查找页面中的所有rl
def spider_url(url):
    global list_url
    try:
        # Get方法获取到页面，解码为GB18030
        html = requests.get(url, timeout=1).content.decode('gb18030', 'ignore')
    except:
        print("Error: " + str(url))
        return
    # 解析Html为DOM文档
    soup = BeautifulSoup(html, 'html.parser')
    # 查找a标签内容
    for new_href in soup.find_all('a'):
        new_url = str(new_href.get('href')).strip()
        if new_url not in list_url and new_url != "" and domain in new_url and 'http' in new_url:
            list_url.append(new_url)


# 爬取页面内容
def spider_article(url):
    global already_art
    if url in list_vis_art:
        return
    # 这里有问题，其实上一步已经获取到了该url对应的html
    try:
        html = requests.get(url, timeout=1).content.decode('gb18030', 'ignore')
    except:
        print("Error: " + str(url))
        return
    soup = BeautifulSoup(html, 'html.parser')
    try:
        title = str(soup.title.string).split('--')[0]
        context = ""
        for word in soup.find_all('p'):
            word = str(word.get_text())
            if garbage(word):
                continue
            if pre_paragraph in word:
                word = word.strip()
                if len(word) > 10:
                    context += word + '\n'
            else:
                word = word.strip()
                if len(word) > 20:
                    context += word + '\n'
    except:
        return
    if context != "" and context != '\n':
        tmp_news = News(title, context)
        if tmp_news not in list_news:
            already_art += 1
            list_news.append(tmp_news)
            list_vis_art.append(url)
            print(tmp_news.title)
            print(tmp_news.context)


def main():
    global already_art
    num = 0
    while True:
        t = 0
        list_url.append(init_url)
        for url_i in list_url:
            if t == plan_article / 2:
                break
            if url_i not in list_visit:
                list_visit.append(url_i)
                num += 1
                print(str(num) + str("--Request: ") + url_i + str('\t\t') + str(len(list_art)))
                spider_url(url_i)
                if 'html' in url_i:
                    re_url = url_i
                    re_url = re_url.split('.')
                    try:
                        if len(re_url[3]) >= 29:
                            list_art.append(url_i)
                            t += 1
                    except:
                        continue

        print("\nMaybe Article URL: ")
        for url_i in list_art:
            print(url_i)
            spider_article(url_i)
            if already_art >= plan_article:
                with open("Files/People_News.txt", "a", encoding='UTF-8') as file:
                    for news in list_news:
                        file.write(news.title)
                        file.write('\n')
                        file.write(news.context)
                        file.write('\n')
                    # file.write(str("Sum: ") + str(len(list_news)))
                    print(str(len(list_news)) + "\tDone!")
                exit(0)
            else:
                continue


if __name__ == '__main__':
    main()
