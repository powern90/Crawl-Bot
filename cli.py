from socket import *
import sys
import threading
from bs4 import BeautifulSoup
import requests
import re
import queue
import mysql.connector

list_titles_b = []  # 글 제목
list_content_b = []  # 글 내용
list_during_b = []  # 기간
list_page_urls_b = []  # 페이지 url
list_url_b = []  # 게시글 url
list_html_b = []  # 글 내용 html
list_titles_j = []  # 글 제목
list_content_j = []  # 글 내용
list_during_j = []  # 기간
list_page_urls_j = []  # 페이지 url
list_url_j = []  # 게시글 url
list_html_j = []  # 글 내용 html
urls_bok = "http://www.bokjiro.go.kr"
urls_jung = "https://www.gov.kr"
HOST = '127.0.0.1'
PORT = 10000
BUFSIZE = 1024
ADDR = (HOST, PORT)


def save_content(que, t):
    while que.qsize() != 0:
        list_urls = que.get()
        confirm = list_urls.split(" ")[1]
        list_urls = list_urls.split(" ")[0]
        if confirm == 'b':  # 복지로
            next_urls = urls_bok + list_urls
            list_url_b.append(next_urls)
            New_url = requests.get(next_urls)
            soup = BeautifulSoup(New_url.content, "lxml")
            titles = str(soup.select('.serviceName'))
            during = str(soup.select('table tbody tr td')[2])
            list_during_b.append(re.sub('<.+?>', '', during, 0).strip())  # 태그 지우기
            content = str(soup.select('.shareServiceCont'))
            list_html_b.append(content)
            content2 = re.sub('<.+?>', '', content, 0).strip()  # 태그 지우기
            list_content_b.append(re.sub('&nbsp; | &nbsp; | \n|\t|\r', '', content2))  # 개행, tab 지우기
            print(t + " 복지로 " + titles)
        elif confirm == 'j':  # 정부24
            next_urls = urls_jung + list_urls
            list_url_j.append(next_urls)
            New_url = requests.get(next_urls)
            soup = BeautifulSoup(New_url.content, "lxml")
            content = soup.select('body > div.contentsWrap.r2n > .contents > .cont-inner > '
                                  '.tbl-view.gallery-detail > .view-contents')
            list_html_j.append(str(content))  # 게시글 html
            list_content_j.append(re.sub('<.+?>', '', str(content), 0).strip())  # 게시글 내용
            list_during_j.append(re.sub('<.+?>', '', str(soup.select('.date')), 0).strip())
            list_titles_j.append(re.sub('<.+?>', '', str(soup.select('.tit2')), 0).strip())
            list_page_urls_j.append(list_urls)
            print(t + " 정부 24 " + re.sub('<.+?>', '', str(soup.select('.tit2')), 0).strip())


def thread(que):
    t1 = threading.Thread(target=save_content, args=(que, "쓰레드1"))
    t2 = threading.Thread(target=save_content, args=(que, "쓰레드2"))
    t3 = threading.Thread(target=save_content, args=(que, "쓰레드3"))
    t4 = threading.Thread(target=save_content, args=(que, "쓰레드4"))
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()


if __name__ == "__main__":
    config = {
        'user': 'ryeoly2',
        'password': '2045ydr!',
        'host': '192.168.1.4',
        'database': 'crolls',
        'port': '3306'
    }

    sql = 'INSERT INTO bokjiro (Title, Content, URL, Target, Support, Etc) VALUES(%s, %s, %s, %s, %s, %s)'
    conn = mysql.connector.connect(**config)
    _cursor = conn.cursor(dictionary=True)
    _cursor.execute(sql, ('4', '4', '4', '4', '4', '4'))
    conn.commit()
    conn.close()

    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect(ADDR)
    que = queue.Queue()
    while True:
        data = clientSocket.recv(8192)
        if data.decode() == 'finish':
            break
        data = data.decode().split("///")
        data.remove('')
        for i in data:
            que.put(i)
        thread(que)
        if que.qsize() == 0:
            print("큐 비음")
            clientSocket.send("re".encode())
