# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 11:53:50 2017

@author: admin
"""

##信息已抽取
import requests
import os
import re
import datetime
import time
import json
import codecs

from bs4 import BeautifulSoup
import demjson
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

import platform
           
           
def append_txt(store_dir,text):
    f = open(store_dir,"ab")
    f.write(bytes(text+'\n',encoding="utf8"))
    f.close()


def write_txt(store_dir, text):
    f = codecs.open(store_dir, "w", 'utf8')
    f.write(text + '\n')
    f.close()
    
    
def extract_from_html(html, i, driver):
    #try:        
    soup = BeautifulSoup(html,'html.parser')
    '''
    2017.10.09改版后，无法获取文章类别
    category = re.findall('class=".*on".*>(.*?)</a>',str(soup.find("div",{"class":"header"})))  
    title = re.findall("【(.*?)】",soup.title.string)
    '''
    category = ['快讯']
    ##json数据内容
    pub_time = soup.find("div",{"class":"ctime"}).text
    # pub_time = re.findall('class="time">(.*?)<',html)[0]
    source = soup.find("span",{"class":"writer"}).text
    # source = re.findall('class="from">(.*?)<',html)[0]

    '''
    2017.10.09改版后，无法获取文章类别
    if len(category)==0:    ##以下几种文章特殊
        for cate in ['早报','猜想','新闻联播','盘后重要公告']:
            if title[0].find(cate):
                category.append(cate)
                break
    '''
            
    ##纯净内容
    content = soup.find("div",{"class":"thisContent"}).text.strip()
    try:
        title = soup.title.text
        if not title:
            title = re.findall('【(.*?)】',content)[0]
    except:
        try:
            title = re.findall('【(.*?)】',content)[0]
        except:
            title = ''
    ##保留格式的写法
    ##content = str(soup.find_all("li",{"class":"content"})[0])
    ##下行也可去掉，作用为 去除<li class="content"></li>标签
    ##content = re.sub('<li class="content">|</li>','',content).strip()
    read_num = soup.find("div",{"class":"readNum"}).text.split()[-1]
    # read_num = re.findall('class="pconly">已阅 (.*?)<',html)[0]
    store_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    '''
    2017.10.09 评论功能被删除
    if re.findall('<div class="empty">暂无评论</div>',html) :
        comment_num = 0
        comment = ''
    else:
        url = "http://www.cailianpress.com/v2/comment/get_comments?staid=999999&count=5&articleid=" + str(i)
        #chtml = requests.get(url,headers = headers).text.strip()
        driver.get(url)
        r_comment = demjson.decode(re.sub('<.*?>','',driver.page_source))
        comment_num = r_comment['total_number']
        next_cur = r_comment['next_cursor']
        comment = r_comment['data']
        total_number = r_comment["total_number"]
        total_cursor = r_comment["total_cursor"]
        while total_cursor < total_number:
            url = "http://www.cailianpress.com/v2/comment/get_comments?staid=" + next_cur + "&count=4&articleid=" + str(i)
            #cchtml = requests.get(url,headers = headers).text.strip()
            driver.get(url)
            raw_comment = demjson.decode(re.sub('<.*?>','',driver.page_source))
            try:
                total_number = raw_comment["total_number"]
            except:
                break
            total_cursor = raw_comment["total_cursor"]
            cur_comment = raw_comment["data"]
            try:
                comment += cur_comment
            except:
                for s in list(comment):
                    c += comment[s]
                comment = c + cur_comment
            next_cur = raw_comment["next_cursor"]
    '''
    comment = []
    comment_num = 0
    data = {'id':i,'title':title,'time':pub_time,'source':source,'content':content,
         'read_num':read_num,'store_time':store_time,'comment':comment,
         'comment_num':comment_num,'category':category[0]}
    ##json_data = demjson.encode(data)
    append_txt('new.txt',str(data))
    write_txt('oldID.txt',str(int(i)+1))
    f = open('log.txt','a')
    f.write("complete "+ str(i)+'\n')
    f.close()
    print("complete "+ str(i))
    ##write_txt(category[0]+str(i)+'.txt',json_data)
    '''
    except:
    print(str(i)+'extract_failed')
    f = open('log.txt','a')
    f.write(str(i)+"extract_failed"+'\n')
    f.close()
    append_txt('extract_failed.txt',str(i))
    '''

    
def get_articles(id_list, driver):
    stop = 0
    for i in id_list:
        if stop == 1:
            break
        times = 0
        while times < max_retry_times:     
            try:
                rurl = "http://www.cailianpress.com/single/" + str(i) + ".html"
                try:
                    driver.get(rurl)
                except TimeoutException:
                    print("timeout")
                    driver.execute_script('window.stop()')   #当页面加载时间超过设定时间，通过执行Javascript来stop加载，即可执行后续动作              

                html = driver.page_source
                if re.findall('请证明您不是机器人',html):
                    print("爬虫被禁了！" + time.ctime())
                    stop = 1
                else:
                    if driver.current_url == "https://www.cailianpress.com/":    #如果相等说明是空白页
                        append_txt("blank2.txt",str(i))
                    else:
                        extract_from_html(html, i, driver)
                        time.sleep(2)
                break
            except:
                times += 1
        if not times < max_retry_times: 
            append_txt("failed.txt",str(i))
            continue
    

##重新爬取
def retry(txt_dir):
    f = open(txt_dir,'r')
    lines = f.readlines()
    f.close()
    os.remove(txt_dir)
    id_lists = [eval(i.strip()) for i in lines]
    for id_list in id_lists:
        get_articles(id_list)
        
##读物数据
def read_txt(txt_dir):
    f = codecs.open(txt_dir,'r','utf8')
    s = f.readlines()
    f.close()
    data = [eval(q) for q in s]
    return data
    

def write_neat_data(file):
    """
    read in all data, but only write useful attribute to file '.neat'
    :param file:
    :return:
    """
    data = read_txt(file)
    f = codecs.open(file.split('.')[0] + '.neat', 'w', 'utf8')
    for d in data:
        a = dict()
        d['content'] = re.sub('\u2028','',d['content'])
        for i in ['id', 'title', 'time', 'url', 'source', 'stockname','content']:
            a[i] = d[i]
        f.write(str(a)+'\n')
        
        
def txt_to_json(file):
    index = {"index": {}}
    data = read_txt(file)
    f = codecs.open(file + '.json', 'w', 'utf8')
    for d in data:
        f.write(json.dumps(index)+'\n')
        f.write(json.dumps(d, ensure_ascii=False)+'\n')
    f.close()
    

def update_attribute(data, attribute_name, func):
    """
    update an attribute using given function
    :param data: [dict, dict,...]
    :param attribute_name:
    :param func: a lambda function
    :return: data
    """
    for d in data:
        d[attribute_name] = func(d)
    return data


def update_url(store_dir):
    """
    read in all data, and add a new attribute('url'),then save in file '.neat'
    :param data:
    """
    data = read_txt(store_dir)
    func = lambda x: 'http://www.cailianpress.com/single/'+str(x['id'])+'.html'
    data = update_attribute(data, 'url', func)
    return data
    
    
def update_stockname(news):
    for new in news:
        new['stockname'] = []


    for new in news:
        for stock in stocks:
            for name in stocks[stock]:
                if name in new['title']+new['content']:
                    new['stockname'].append(stock)
    return news
    

def update_week(data):
    stocknames = read_txt('stocknames.txt')[0]
    for d in data:
        year, month, day = (d['time'].split()[0]).split('-')
        w = int((datetime.datetime(int(year), int(month), int(day)) - datetime.datetime(2015, 1, 5)).days / 7)
        while len(stocknames) <= w:
            stocknames.append([])
        stocknames[w] += d['stockname']
    write_txt('stocknames.txt',str(stocknames))

    percents = dict()
    for stock in stocks.keys():
        percent = [0 for i in range(len(stocknames))]
        for i in range(len(stocknames)):
            if stocknames[i]:
                w = [s for s in stocknames[i] if s == stock]
                percent[i] = len(w)/len(stocknames)
        percents[stock] = percent

    smooths = dict()
    for stock in percents.keys():
        p = percents[stock]
        smooth = [0 for i in range(len(p))]
        smooth[0] = round(sum(p[:2])/2,4)
        for i in range(1,len(p)-1):
            smooth[i] = round(sum(p[i-1:i+2])/3,4)
        smooth[-1] = round(sum(p[-2:])/2,4)
        smooths[stock] = smooth

    f = open('week_percent.txt','w')
    f.write(json.dumps(smooths))
    f.close()
    
    f = codecs.open('/usr/share/nginx/html/fin/Application/Home/Controller/week_percent.txt','w','utf8')
    f.write(json.dumps(smooths))
    f.close()



while True:
    if platform.system()== 'Windows':
        os.chdir('E:\cailianRT')
        driver = webdriver.Chrome()
    else:
        os.chdir("/home/ting/cailianRT")
        driver = webdriver.phantomjs.webdriver.WebDriver(executable_path='/home/ting/cailianRT/phantomjs')
    
    max_retry_times = 5
    f = codecs.open('stocks.txt','r','utf8')
    stocks = eval(f.read())
    f.close() 
    
    driver.set_page_load_timeout(10)
    times = 0
    try:
        while times < max_retry_times:     
            try:
                driver.get('http://cailianpress.com/')
                print('complete')
                break
            except:
                driver.refresh()
                times += 1
        if times < max_retry_times:
            break
        else:
            driver.quit()
    except:
        driver.quit()

    
html = driver.page_source
soup = BeautifulSoup(html,'html.parser') 
'''
10.9页面发生更改，代码失效
div = soup.find('div',{'class':'entries'})
new_id = int(re.findall('articleid="(\d+)"',str(div.ul))[0])
'''
div = soup.find_all('div')[-2].script.text
new_id = int(re.findall('article_id=(\d+)',div)[0])
    
f = open('oldID.txt','r')
old_id = int(f.read())
f.close()

if old_id < new_id + 1:
    get_articles(range(old_id, new_id+1), driver)
    '''
    f = open('oldID.txt','w')
    f.write(str(new_id+1))
    f.close()
    '''
    if os.path.exists('new.txt'):
        data = update_url('new.txt')
        data = update_stockname(data)
        update_week(data)
        write_txt('new.all', '\n'.join([str(d) for d in data]))
        write_neat_data('new.all')
    
        txt_to_json('new.neat')
        os.system('curl -XPOST "localhost:9200/first/news/_bulk?pretty" --data-binary @new.neat.json')
        for d in data:
            append_txt(d['time'][:4]+'.txt',str(d))
        os.remove('new.txt')    

    
driver.quit()
