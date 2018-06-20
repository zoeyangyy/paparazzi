# -*- coding: utf-8 -*-
"""
Created on Thu May 11 11:34:36 2017

@author: Ting
"""
import datetime
import tushare as ts
import sys, getopt
import json


def get_event_data(stock, date):
    """
    stock: string, e.g. '600000'
    time: string, e.g. :'2015-03-01'
    """
    time = datetime.datetime.strptime(date, '%Y-%m-%d')
    start = (time - datetime.timedelta(days=100)).isoformat()[:10]
    end = (time + datetime.timedelta(days=100)).isoformat()[:10]
    data = ts.get_k_data(stock,start=start,end=end)
    svalue = data['close'].values
    sdate = [datetime.datetime.strptime(d, '%Y-%m-%d') for d in data['date'].values]
    for i in range(len(sdate)):
        if sdate[i] >= time:
            break
    values = [round(float(str(v)),4) for v in svalue[i-30:i+31]]
    dates = [t.isoformat()[:10] for t in sdate[i-30:i+31]]

    dic = dict()
    dic['date'] = dates
    dic['value'] = values
    return json.dumps(dic)


opts, args = getopt.getopt(sys.argv[1:], "s:d:", ["stock=", "date="])

stock = ""

for op, value in opts:
    if op == "--stock":
        stock = value
    elif op == "--date":
        date = value
        print(get_event_data(stock, date))
        break
    