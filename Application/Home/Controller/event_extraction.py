import jieba
import json
import sys, getopt
import jieba.posseg as pseg
import time
import re
from elasticsearch import Elasticsearch
import codecs

# jieba.load_userdict(r'D:\user1.txt')


def extraction(sentence):
    word = sentence.encode('latin-1').decode('unicode_escape')
    # return(sentence)

    f = codecs.open('/usr/share/nginx/html/fin/Application/Home/Controller/com-dict-reverse.txt','r','utf8')
    company = eval(f.read())
    f.close()
    for c in company:
        jieba.add_word(company[c][0], 100, 'nt')

    jieba.add_word("全国两会", 1, 'n')
    jieba.add_word("央行降息", 1, 'n')
    words = pseg.cut(word)
    dic = dict()
    dic['object'] = '浦发银行'
    # 提取主语谓语
    i = 0
    for w in words:
        # print(w.word+" "+w.flag)
        if 'n' in w.flag.strip() and i==0:
            i += 1
            dic['subject'] = w.word
            continue
        if 'nt' in w.flag.strip() and i==1:
            dic['object'] = w.word
            break

    # 到elastic找数据
    # es = Elasticsearch()
    # res = es.search(index="first", body={"query": {
    #     "bool": {"must": [], "must_not": [], "should": [{"match": {"title": word}}, {"match": {"content": word}}]}},
    #                                      "from": 0, "size": 10, "sort": [], "aggs": {}})

    final = dict()
    final['object'] = dic['object']
    res = dict()
    if dic['subject'] == '央行降息':
        res[0] = dict()
        res[0]['url'] = 'http://www.cailianpress.com/single/73484.html'
        res[0]['title'] = '央行：2月29日起下调存款准备金率0.5个百分点'
        res[0]['time'] = '2016-02-29'
        res[1] = dict()
        res[1]['url'] = 'http://bj.bendibao.com/news/2015827/199818.shtm'
        res[1]['title'] = '2015年8月26日起央行降息降准调整表最新消息'
        res[1]['time'] = '2015-08-26'
        res[2] = dict()
        res[2]['url'] = 'http://news.xinhuanet.com/house/hf/2015-06-27/c_1115742429.htm?from=timeline&isappinstalled=0'
        res[2]['title'] = '央行宣布6月28日起降息定向降低存款准备金率'
        res[2]['time'] = '2015-06-27'
    elif dic['subject'] == '全国两会':
        res[0] = dict()
        res[0]['url'] = 'http://www.cailianpress.com/single/145444.html'
        res[0]['title'] = '第十二届全国人大五次会议开幕'
        res[0]['time'] = '2017-03-05'
        res[1] = dict()
        res[1]['url'] = 'http://www.cailianpress.com/single/74242.html'
        res[1]['title'] = '李克强两会首次发声：赤字率将大幅提高'
        res[1]['time'] = '2016-03-04'
        res[2] = dict()
        res[2]['url'] = 'http://zixun.ymt.com/glsj/866212_1.html'
        res[2]['title'] = '2015全国两会代表关注热点'
        res[2]['time'] = '2015-03-03'
    else:
        res[0] = dict()
        res[0]['url'] = 'http://finance.qq.com/a/20161223/030382.htm'
        res[0]['title'] = '证监会责令国泰君安等五家机构限期整改'
        res[0]['time'] = '2016-12-23'
        res[1] = dict()
        res[1]['url'] = 'http://finance.sina.com.cn/stock/2016-10-07/doc-ifxwrhpm2489939.shtml'
        res[1]['title'] = '证监会释放“最严”监管思路 强监管苦券商'
        res[1]['time'] = '2016-10-07'
        res[2] = dict()
        res[2]['url'] = 'http://www.cailianpress.com/single/96562.html'
        res[2]['title'] = '证监会合并券商基金风控规章 划合规底线'
        res[2]['time'] = '2016-07-15'


    final['news'] = res
    # print(json.dumps(res))
    return json.dumps(final)


opts, args = getopt.getopt(sys.argv[1:], "s", ["sentence="])

sentence = ""

for op, value in opts:
    if op == "--sentence":
        sentence = value
        print(extraction(sentence))
