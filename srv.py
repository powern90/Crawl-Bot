from socket import *
from bs4 import BeautifulSoup
import requests
import re
import queue
import threading
import time
from datetime import datetime
from dateutil.relativedelta import *

HOST = '127.0.0.1'
PORT = 10000
BUFSIZE = 1024
ADDR = (HOST, PORT)
keyword = [
    '저소득',
    '장애인',
    '다문화가정',
    '기초생활수급자',
    '고령자',
    '북한이탈주민',
    '한부모가족'
]


def change_date(day1, day2):
    text3 = day1.split('.')
    text4 = day2.split('.')
    year = text3[0]
    year2 = text4[0]
    if int(text3[1]) == 1:
        text3[1] = str(12)
        year = int(year) - 1
    else:
        text3[1] = str(int(text3[1]) - 1)
    if int(text4[1]) == 1:
        text4[1] = str(12)
        year2 = int(year2) - 1
    else:
        text4[1] = str(int(text4[1]) - 1)
    month1 = text3[1]
    month2 = text4[1]
    change_date1 = str(year) + '.' + str(month1) + '.' + text3[2]
    change_date2 = str(year2) + '.' + str(month2) + '.' + text3[2]
    return change_date1, change_date2


def get_url(que, now):
    url = requests.get("http://www.bokjiro.go.kr/nwel/helpus/welsha/selectWelShaInfoBbrdMngList.do")
    soup = BeautifulSoup(url.content, "lxml")
    a = soup.find("a", {"class": "num"})
    list_page_urls = [a['href']]
    page_token = list_page_urls[0].split('pageIndex=')[0]
    last_page = soup.find_all("a", {'class': 'goLast'})
    last_page_num = last_page[0].get('href').split('pageIndex=')[1]
    cnt = 41
    while cnt < int(last_page_num) + 1:
        urls = "http://www.bokjiro.go.kr"
        origin_urls = urls + page_token + 'pageIndex=' + str(cnt)
        page_urls = requests.get(origin_urls)
        soup = BeautifulSoup(page_urls.content, "lxml")
        for i in soup.find_all("a", {'class': 'point10'}):
            que.put(i['href'] + " b")
        cnt = cnt + 1
        print(now + " 복지로 " + origin_urls)
    # 여기까지 복지로
    #
    # page_token0 = "https://www.gov.kr/portal/locgovNews"
    # page_token1 = "?srchOrder=&sido=&signgu=&srchArea=&srchSidoArea=&srchStDtFmt="
    # page_token2 = "&srchEdDtFmt="
    # page_token3 = "&srchTxt="
    # page_token4 = "&initSrch=false&pageIndex="
    # date = datetime.now().date()
    # before_date = str(date + relativedelta(months=-1)).replace('-', '.')
    # date = str(date).replace('-', '.')
    # change_date1, change_date2 = before_date, date
    # for j in range(0, len(keyword)):
    #     start_url = page_token0 + page_token1 + change_date1 + page_token2 + change_date2 + page_token3 + str(
    #         keyword[j]) + page_token4 + '1'
    #     url = requests.get(start_url)
    #     soup = BeautifulSoup(url.content, "lxml")
    #     last_page_url = soup.select('.pagination li a')
    #     sp = re.split('pageIndex=', str(last_page_url[8]))[1]
    #     last_page_num = sp.split('"')[0]
    #     for i in soup.find_all("dt", {'class': 'pcb'}):
    #         que.put(str(i).split('"')[3] + " j")
    #     print(now + " 정부24 " + start_url)
    #     for term in range(1, 25):
    #         if term != 1:
    #             change_date1, change_date2 = change_date(change_date1, change_date2)  # 날짜 변경
    #         for count in range(2, int(last_page_num) + 1):
    #             origin_urls = page_token0 + page_token1 + change_date1 + page_token2 + change_date2 + page_token3 + str(
    #                 keyword[j]) + page_token4 + str(count)
    #             url = requests.get(origin_urls)
    #             soup = BeautifulSoup(url.content, "lxml")
    #             for i in soup.find_all("dt", {'class': 'pcb'}):
    #                 que.put(str(i).split('"')[3] + " j")
    #             print(now + " 정부24  " + origin_urls)
    #     # 여기까지 정부24


def socket_network(socket, que, now):
    if que.qsize() == 0:
        time.sleep(10)
    while que.qsize() != 0:
        result = ""
        for i in range(0, 10):
            result += que.get() + "///"
        socket.send(result.encode())
        time.sleep(10)
        print("소켓 전송 result = " + result)
        data = socket.recv(256)
        print("소켓 수신 result = " + data.decode())
    socket.send("finish".encode())


def thread(socket, que):
    t1 = threading.Thread(target=get_url, args=(que, "큐 쓰레드"))
    t2 = threading.Thread(target=socket_network, args=(socket, que, "소켓 쓰레드"))
    t1.start()
    time.sleep(10)
    t2.start()
    t1.join()
    t2.join()


if __name__ == "__main__":
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(ADDR)
    serverSocket.listen(100)
    clientSocket, addr_info = serverSocket.accept()
    que = queue.Queue()
    thread(clientSocket, que)

