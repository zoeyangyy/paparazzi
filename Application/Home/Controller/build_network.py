# -*- coding: utf-8 -*-
"""
Created on Thu May 11 13:29:45 2017

@author: Ting
"""
import nltk
import codecs
##第一步，通过新闻信息，将每条新闻涉及的股票进行全连接，生成关系信息，并保存
##对新闻进行筛选，去掉涉及到的股票多余maxN的新闻。
##最后只取权重大于 阈值n的显著关系
def first_step():
    maxN = 15
    minN = 2
    n = 10
    f = codecs.open('f:\\cailianpress\\allnews.neat','r','utf8')
    a = [eval(i) for i in f.readlines()]
    f.close()
    
    stocknames = [i['stockname'] for i in a if len(i['stockname'])>minN and len(i['stockname'])<maxN]
    relation = []
    for st in stocknames:
        s = sorted(list(set(st)))
        for i in range(len(s)-1):
            for j in range(i+1,len(s)):
                if int(s[i]) < int(s[j]):
                    relation.append([s[i],s[j]])
                else:
                    relation.append([s[j],s[i]])
    p = [','.join(r) for r in relation]
    fd = nltk.FreqDist(p)
    upper = [[i,j] for i,j in fd.most_common() if j>n]
    ##只保存阈值大于n的显著关系
    f = open('f:\\relation\\larger_than_10.txt','w')
    for i in upper:
        f.write(i[0]+','+str(i[1])+'\n')
    f.close()

##第二步，给定某个关注的股票，需要获取它的maxTier度节点
##即与该股票的关联，中间节点不超过maxTier个
##结果实例：（父节点，子节点，子节点所在层数，
def second_step():
    f = open('f:\\relation\\larger_than_10.txt','r')
    pairs = [i.split(',') for i in f.readlines()]
    f.close()
    
    ppairs = []
    for i in pairs:
        ppairs.append([i[0],i[1],i[2]])
        ppairs.append([i[1],i[0],i[2]])
        
    father = '600000'
    frontier = [(father,0)]
    maxTier = 3
    result = []
    explored = []
    while frontier:
        node,tier = frontier[0]
        explored.append(node)
        del frontier[0]
        if tier > maxTier:
            break
        child = [[j,k] for i,j,k in ppairs if i == node]
        names = [i for i,j in frontier]+explored
        for c in child:
            if c[0] not in names:
                frontier.append((c[0],tier+1))
                result.append((node,c[0],str(tier+1),c[1]))
                
    f = open('f:\\relation\\4tier_nodes.txt','w')
    f.write('\n'.join([i[1]+'\t'+i[2] for i in result]))
    f.close()
    
    ##根据节点统计权重
    nodes = [i[1] for i in result]
    rel = []
    for pair in pairs:
        if pair[0] in nodes and pair[1] in nodes:
            rel.append(pair)
            break
    f = open('f:\\relation\\4tier_edges.txt','w')
    for r in rel:
        f.write('\t'.join(r))
    f.close()

