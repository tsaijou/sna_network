# -*- coding: utf-8 -*-
"""
Graph1. 2019年前50大關鍵字網絡
  可設定篩選條件：
  1. 年份: year
  2. 關鍵詞個數: top
"""

import pandas as pd
import os, time
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import math

toolspath = r"C:\成大專案\學研專家網絡\資料與繪圖\模組與資料表"    
os.chdir(toolspath)
import toolmodules as tools
database = "sna_network"

time_draw = time.time()
con_en = tools.dbConnectEngine(database)
# 條件設定
year = "2019"
top = 50

###篩選節點資料
sqlstr_nodes =\
f"""
SELECT keyword, amount AS value 
    FROM `graph_keywords`
    WHERE year = {year}
    ORDER BY value DESC Limit {top}
"""
df_nodes =  pd.read_sql(sqlstr_nodes, con_en)
nodes = "','".join(list(df_nodes["keyword"]))

##篩選連線資料
sqlstr_links =\
f"""
SELECT keyword1, keyword2, amount AS value 
    FROM `graph_keyword_links`
    WHERE (year = {year}) 
        AND (keyword1 IN ('{nodes}') AND keyword2 IN ('{nodes}'))
    ORDER BY value DESC
"""
df_links = pd.read_sql(sqlstr_links, con_en)
con_en.close()

##建立網絡
def keywordsNetwork(df_nodes, year, df_links):
    G_keywordsNetwork = nx.Graph()
    ##匯入節點資料
    for row in df_nodes.values:
        G_keywordsNetwork.add_node(row[0], year=year, value=row[-1])
    ##匯入連線資料
    for row in df_links.values:
        G_keywordsNetwork.add_edge(row[0], row[1], year=year, value=row[-1])
    ##新增節點屬性：degree
    for (node, degree) in G_keywordsNetwork.degree():
        G_keywordsNetwork.node[node]["degree"] = degree
    ##layout    
#    pos = nx.spring_layout(G_keywordsNetwork, seed=47) 
    pos_c = nx.circular_layout(G_keywordsNetwork)
    #利用邊的"value"屬性設定邊的粗細與顏色值
    edge_colors = [math.log(value*10, 3) for (u, v, value) in G_keywordsNetwork.edges(G_keywordsNetwork, 'value')]
    edge_widths = [math.log(value*10, 7) for (u, v, value) in G_keywordsNetwork.edges(G_keywordsNetwork, 'value')]
    node_colors = [G_keywordsNetwork.node[node]["value"] for node in G_keywordsNetwork]
    #labels = {n:str(G_keywordsNetwork.node[n]["degree"]) for n,lab in pos.items()}
    ##中文設定
    matplotlib.rcParams['font.family']='SimSun'
    plt.figure(figsize=(15,10))
    ##底圖
    nx.draw(G_keywordsNetwork, pos_c, node_size=1000, cmap=plt.cm.cool, node_color=node_colors, alpha=0.4, edge_color="white", width=0, with_labels=False)
    ##節點、連線、標籤設定
    nodes = nx.draw_networkx_nodes(G_keywordsNetwork, pos_c, node_size=1000, cmap=plt.cm.cool, node_color=node_colors, alpha=0.3)
    edges = nx.draw_networkx_edges(G_keywordsNetwork, pos_c, edge_color=edge_colors, edge_cmap=plt.cm.Blues, edge_vmin=0.1, width=edge_widths, alpha=0.7)
    nx.draw_networkx_labels(G_keywordsNetwork, pos_c, font_size=15, font_color="k", font_family="SimSun")
    #nx.draw_networkx_labels(G_keywordsNetwork, pos_c, labels=labels, font_size=25, font_color="r", alpha=0.7, font_family="SimSun")
    plt.margins(x=0.1)
    plt.colorbar(edges, shrink=0.6, location="left", label="colorbar of edges", pad=0.005)
    plt.colorbar(nodes, shrink=0.6, location="right", label="colorbar of nodes", pad=0.005)
    plt.show()
    return G_keywordsNetwork

# 繪製網絡圖
G_keywordsNetwork = keywordsNetwork(df_nodes, year, df_links)

time_end = time.time()
print("繪製網絡圖：", time_end - time_draw)  # 5.8秒

con_en.close()


