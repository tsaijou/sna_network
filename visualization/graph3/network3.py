# -*- coding: utf-8 -*-
"""
Graph3. 關鍵詞-"再生能源"的研究技術網絡
  可設定篩選條件：
  1. 關鍵詞指定: keyword
  可增加篩選條件：年份區間、關鍵詞個數
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

# 從資料庫篩選資料匯入
keyword = "再生能源"
top = 30
##篩選關鍵詞資料
sql_nodes =\
    f"""
    SELECT keyword1, keyword2, SUM(amount) AS 'value' 
        FROM `graph_keyword_links` 
        WHERE keyword1='{keyword}' OR keyword2='{keyword}' 
        GROUP BY keyword1, keyword2
        ORDER BY value DESC LIMIT {top}
    """
for_nodes = pd.read_sql(sql_nodes, con_en)
nodes = list(for_nodes.keyword1)
nodes.extend(list(for_nodes.keyword2))
nodes = "','".join(list(set(nodes)))

##篩選關鍵詞連線資料
sql_links =\
    f"""
    SELECT keyword1, keyword2, SUM(amount) AS 'value' 
        FROM `graph_keyword_links` 
        WHERE keyword1 IN ('{nodes}') AND keyword2 IN ('{nodes}') 
        GROUP BY keyword1, keyword2
        ORDER BY value DESC
    """
df_links = pd.read_sql(sql_links, con_en)
con_en.close()

# 繪製網絡圖
Graph = nx.Graph()
for row in df_links.values:
    Graph.add_edge(row[0], row[1], value=row[-1])
## 繪製"keyword"為中心的關鍵字網絡圖，layout指定
pos = nx.spring_layout(Graph, seed=9)
##利用邊的"value"屬性設定邊的粗細與顏色值
edge_colors = [math.log(value, 10.5)+0.5 for (u, v, value) in Graph.edges(Graph, 'value')]
edge_widths = [math.log(value, 10.5)+0.5 for (u, v, value) in Graph.edges(Graph, 'value')]
##設定"中心-太陽能"與"外層-與太陽能相連關鍵字"關鍵字標籤資料 - 利用節點屬性"group" 區分
labelCenter = {n:n for n in Graph if n==keyword}
labelNeighbors = {n:n for n in Graph if n!=keyword}
##中文設定
matplotlib.rcParams['font.family']='SimSun'

plt.figure(figsize=(15,8))
##底圖
nx.draw(Graph, pos, node_size = 0, edge_color="white", width=0, with_labels=False)
##節點、邊、標籤設定
nx.draw_networkx_nodes(Graph, pos, node_size=80, node_color='white', alpha=0) 
edges = nx.draw_networkx_edges(Graph, pos, edge_color=edge_colors, edge_cmap=plt.cm.Blues, edge_vmin=0.1, width=edge_widths, alpha=1)
nx.draw_networkx_labels(Graph, pos, labels=labelNeighbors, font_size=15, font_color="k", font_family="SimSun")
nx.draw_networkx_labels(Graph, pos, labels=labelCenter, font_size=23, font_color="r", font_family="SimSun")
plt.margins(x=0.1)
plt.colorbar(edges, shrink=0.6, label="colorbar of edges", pad=0.005)

time_end = time.time()
print("繪製網絡圖：", time_end - time_draw)  # 3.2秒

con_en.close()
