# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 11:45:49 2017

@author: admin
"""

from elasticsearch import Elasticsearch
import sys,getopt
import json
import re

es = Elasticsearch()

#es.indices.create(index='2016')

#es.index(index="test-index",doc_type="test-type",id=42,body={"any":"data","timestamp":datetime.now()})

def search_any(keyword,number):

    word = keyword.encode('latin-1').decode('unicode_escape')
    # print(keyword)
    # return(word)
    # res = es.search(index="first",body={"query":{"match":{"title":word}},"size": int(number)})
    res = es.search(index="first",body={"query":{"bool":{"must":[],"must_not":[],"should":[{"match":{"title":word}},{"match":{"content":word}}]}},"from":0,"size":int(number),"sort":[],"aggs":{}})
    # return res
    return json.dumps(res)
    # ensure_ascii=False
     
def search_com(keyword,number):

    if re.match(r'\d{6}',keyword):
        cp_code = keyword
    # else:
    #     word = keyword.encode('latin-1').decode('unicode_escape')
    #     cp_code = company[word]
   
    res = es.search(index="first",body={"query":{"term":{"stockname":cp_code}},"size": int(number)})
    return json.dumps(res)
     
     
opts, args = getopt.getopt(sys.argv[1:],"a:c:n",["number=","keywordany=","keywordcom="])

keywordany=""
keywordcom=""
number=""

for op,value in opts:
    if op == "--number":
        number = value
    elif op == "--keywordany":
        keywordany = value
        print(search_any(keywordany,number))
        break
    elif op == "--keywordcom":
        keywordcom = value
        print(search_com(keywordcom,number))
        break
    


        