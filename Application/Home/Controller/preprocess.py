import json
import jieba
import time
import re
import os
import codecs
import networkx as nx
# import matplotlib.pyplot as plt
import matplotlib  
matplotlib.use('Agg')
import sys, getopt
# import community


def create_data(target):
    f = codecs.open('/usr/share/nginx/html/fin/Application/Home/Controller/com-dict-reverse.txt','r','utf8')
    # return f.read()[0]
    # return target
    company = eval(f.read())
    f.close()

    for c in company:
        company[c] = company[c][0]
    f = open('/usr/share/nginx/html/fin/Application/Home/Controller/larger_than_10.txt', 'r')
    pairs = [i.split(',') for i in f.readlines()]
    f.close()

    ppairs = []
    for i in pairs:
        ppairs.append([i[0], i[1], i[2]])
        ppairs.append([i[1], i[0], i[2]])
    # return(str(ppairs))
    father = target
    frontier = [(father, 0)]
    maxTier = 3
    result = []
    explored = []
    while frontier:
        node, tier = frontier[0]
        explored.append(node)
        del frontier[0]
        if tier > maxTier:
            break
        child = [[j, k] for i, j, k in ppairs if i == node]
        names = [i for i, j in frontier] + explored
        for c in child:
            if c[0] not in names:
                frontier.append((c[0], tier + 1))
                result.append((node, c[0], str(tier + 1), c[1]))
    f = codecs.open('/usr/share/nginx/html/fin/Public/css/4tier_nodes.txt', 'w','utf8')
    # f.write('111')
    f.write(company[result[0][0]]+'\t'+'0\n')
    f.write('\n'.join([company[i[1]] + '\t' + i[2] for i in result]))
    f.close()

    ##根据节点统计权重
    nodes = [father] + [i[1] for i in result]
    rel = []
    for pair in pairs:
        if pair[0] in nodes and pair[1] in nodes:
            rel.append(pair)
    f = codecs.open('/usr/share/nginx/html/fin/Public/css/4tier_edges.txt', 'w','utf8')
    for r in rel:
        f.write(company[r[0]]+'\t'+company[r[1]]+'\t'+r[2])
    f.close()


# 运用networkx生成复杂网络
def create_graph_2():
    G = nx.Graph()

    f1 = codecs.open('/usr/share/nginx/html/fin/Public/css/4tier_edges.txt', 'r','utf8')
    edges = {}
    for line in f1.readlines():
        li = line.split()
        edges[(li[0], li[1])] = int(li[2])
    f1.close()
    G.add_edges_from([(u, v, {"weight": edges[(u, v)]}) for (u, v) in edges])

    cname = ['#FF6600', '#FFCC33', '#009966', '#0099CC', '#FF6666']
    f1 = codecs.open('/usr/share/nginx/html/fin/Public/css/4tier_nodes.txt', 'r','utf8')
    nodes = {}
    for line in f1.readlines():
        li = line.split()
        G.add_node(li[0])
        G.node[li[0]]['size'] = (5-int(li[1]))*100
        G.node[li[0]]['color'] = cname[int(li[1])]
        nodes[li[0]] = int(li[1])
    f1.close()

    # print([s for (n, s) in G.nodes(data=True)])

    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, node_color=[s['color'] for (n, s) in G.nodes(data=True)], node_size=[s['size'] for (n, s) in G.nodes(data=True)])
    nx.draw_networkx_edges(G, pos, width=[float(d['weight'] * 0.05) for (u, v, d) in G.edges(data=True)])
    nx.draw_networkx_labels(G, pos, font_size=8)
    nx.write_gexf(G, '/usr/share/nginx/html/fin/Public/css/result.gexf')

opts, args = getopt.getopt(sys.argv[1:], "s", ["stock="])

for op, value in opts:
    if op == "--stock":
        # print(value)
        print(create_data(value))
        create_graph_2()
