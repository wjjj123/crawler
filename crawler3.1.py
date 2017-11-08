#coding=utf-8

import threading
import re
import time
import urllib2
import urlparse
import MySQLdb
from bs4 import BeautifulSoup
import sys

reload(sys)
sys.setdefaultencoding( "utf8" )

g_mutex=threading.Condition()
g_queueURL=[] #等待爬取的url链接列表
g_existURL=[] #已经爬取过的url链接列表
g_totalcount=0 #下载过的页面数
inter_links = []#读取到的内部链接
external_links = []#读取到的外部链接

class Crawler:

    def __init__(self,url,threadnum,_if):
        self.url=url
        self.threadnum=threadnum
        self._if=_if
        self.threadpool=[]

    def craw(self):
        global g_queueURL
        g_queueURL.append (url)
        if self._if == "y":
            while (len (g_queueURL) != 0):
                self.downloadAll ()
                self.updateQueueURL ()
        else:
            while (len (g_queueURL) != 0):
                self.downloadAll ()
                self.updateQueueinterURL ()

    def downloadAll(self):
        global g_queueURL
        global g_totalcount
        i=0
        while i<len(g_queueURL):
            j=0
            while j<self.threadnum and i+j < len(g_queueURL) and len(g_existURL )<=100:
                g_totalcount+=1
                self.download(g_queueURL[i+j])
                j+=1
            i+=j
            for thread in self.threadpool:
                thread.join(30)

    def download(self,url):
        crawthread=CrawlerThread(url)
        self.threadpool.append(crawthread)
        crawthread.start()

    def updateQueueURL(self):
        global g_queueURL
        global g_existURL
        newUrlList=[]
        newUrlList += inter_links
        newUrlList += external_links
        g_queueURL=list(set(newUrlList)-set(g_existURL))

    def updateQueueinterURL(self):
        global g_queueURL
        global g_existURL
        newUrlList=[]
        newUrlList += inter_links
        g_queueURL=list(set(newUrlList)-set(g_existURL))


class CrawlerThread(threading.Thread):

    def __init__(self,url):
        threading.Thread.__init__(self)
        self.url=url

    def getCurrentTime(self):
        return time.strftime ('%Y-%m-%d %H:%M:%S', time.localtime (time.time ()))

    def run(self):
        global g_mutex
        global g_queueURL
        global inter_links
        global external_links
        db = MySQLdb.connect (host='127.0.0.1', port=3306, user='root', passwd='root', db='crawl_web_db',
                              charset='utf8')
        cursorDB = db.cursor ()
        try:
            user_agent = "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0"
            header = {"User-Agent": user_agent}
            request = urllib2.Request (self.url, headers=header)
            website = urllib2.urlopen (request)
            html = website.read ()
            soup = BeautifulSoup (html, "lxml")
            get_title = soup.title.string
            get_title.encode('GBK')
            res_url = r"(?<=charset=\").+?(?=\")|(?<=charset=\').+?(?=\')|(?<=charset=).+?(?=\")|(?<=charset=).+?(?=\')"
            get_charset = re.sub('"','',re.findall (res_url, html)[0])

            print self.url
            print get_title
            print get_charset
            print self.getCurrentTime ()

            cursorDB.execute ("SELECT Task_ID FROM crawl_web_crawl_data")
            rows = cursorDB.fetchall()
            if rows:
                task_id_list = []
                for row in rows:
                    task_id_list .append(row[0])
                task_id =  max(task_id_list)+1
            else:
                task_id = 1

            cursorDB.execute ("INSERT INTO crawl_web_crawl_data(Task_ID,crawl_domain,title, decode,date_time) VALUES (%s,%s,%s,%s,%s)", (task_id,self.url,get_title ,get_charset ,self.getCurrentTime ()))
            db.commit()
        except Exception,e:
            print 'Failed downloading and saving',self.url
            print e
            return None

        g_mutex.acquire()

        reg = r'href\=\"(http\:\/\/[a-zA-Z0-9\.\/]+)\"'
        regob = re.compile (reg, re.DOTALL)
        urllist = regob.findall (html)
        get_url = urlparse.urlparse (self.url)
        url_domain_list = re.split ("\.", get_url.netloc)
        for link in urllist:
            get_link = urlparse.urlparse (link)
            link_domain_list = re.split ("\.", get_link.netloc)
            if link_domain_list[-2:] == url_domain_list[-2:] or link_domain_list[-3:] == url_domain_list[-3:0]:
                inter_links.append (link)
            else:
                external_links.append (link)

        g_existURL.append(self.url)
        g_mutex.release()
        db.commit ()
        cursorDB.close ()
        db.close ()

if __name__=="__main__":
    #url=raw_input("请输入url入口:\n")
    url = "http://www.baidu.com"
    _if = raw_input ("是否爬取外域？y/n\n")
    threadnum=int(raw_input("设置线程数:"))
    crawler=Crawler(url,threadnum,_if)
    crawler.craw()