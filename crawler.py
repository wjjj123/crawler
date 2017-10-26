#coding=utf-8
import re
import thread
from bs4 import BeautifulSoup
import MySQLdb
import urllib2
import urlparse

all_links = []
def mysql_connect(self):
    db = MySQLdb.connect ("127.0.0.1", "root", "toot", "crawler_lrean", charset='utf8')
    return db
    cursorDB = db.cursor ()
    return cursorDB

def entry_address(url):
    user_agent = "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0"
    header = {"User-Agent": user_agent}
    request = urllib2.Request (url, headers=header)
    website = urllib2.urlopen (request)
    html = website.read ()
    return website,html

def if_html(url):
    global all_links
    html = entry_address(url)[1]
    all_links.append (url)
    '''soup = BeautifulSoup (html, "html.parser")
    links = []
    soup2 = soup.select('a')
    links.append(soup2['href'])'''
    # pattern = re.compile (r'<"a",href="(http://|https://.*?)"')
    #links = html.xpath ('//div/a/@href')
    links = re.findall (r'href\=\"(http\:\/\/[a-zA-Z0-9\.\/]+)\"', html)
    #links = re.findall (r'<a.*?href="([^"]*)".*?>([\S\s]*?)</a>',html)
    # links = html.findAll ("a", href=re.compile ('"(https?://.*?)"'))
    # links = html.findall ("a",href=re.compile("^(/|.*"+"https?://.*?"+")"))
    # links = re.findall ('"(https?://.*?)"', html)
    soup = BeautifulSoup (html, "lxml")
    get_title = soup.title.string
    print get_title
    res_url = r"(?<=charset=\").+?(?=\")|(?<=charset=\').+?(?=\')|(?<=charset=).+?(?=\")|(?<=charset=).+?(?=\')"
    get_charset = re.findall (res_url, html)
    print get_charset
    return links

def get_links(url):
    inter_links = []
    external_links = []
    for link in if_html(url):
        # print link

        get_url = urlparse.urlparse (link)
        # print url.netloc
        # print url.netloc[-9:]
        if (get_url.netloc[:2] == "ss") or (get_url.netloc[:2] == "sp"):
            continue
        elif get_url.netloc[-9:] == "baidu.com":
            inter_links.append (link)
        else:
            external_links.append (link)
    print inter_links
    print external_links
    return inter_links,external_links

def get_inter_links(url):

    for inter_link in get_links(url)[0]:
        if inter_link not in all_links:
            HttpMessage = entry_address(url)[0].info ()
            ContentType = HttpMessage.gettype ()
            if ContentType != "text/html":
                print "不是有效链接"
                continue
            else:
                #entry_address (inter_link)
                #get_links(inter_link)
                get_inter_links(inter_link)
        else:
            continue

def get_external_links(url):

    for external_link in get_links(url)[1]:
        if external_link not in all_links:
            HttpMessage = entry_address(url)[0].info ()
            ContentType = HttpMessage.gettype ()
            if ContentType != "text/html":
                print "不是有效网页链接！"
                continue
            else:
                get_external_links(external_link)
        else:
            continue


#url = raw_input("请输入入口地址：")
url = "http://www.baidu.com"
#entry_address(url)
#get_links(url)
all_links.append (url)
get_inter_links(url)
get_external_links(url)
print all_links

