# -*- coding: utf-8 -*-
"""
Graph6. 2010年-2018年與指定PI有某種關係的PI
  可設定篩選條件：
  1. 年份區間: yearFrom、yearTo
  2. 指定PI: piName
  3. 指定PI間的關係: linkType
"""
import pandas as pd
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import math
import os, time

toolspath = r"C:\成大專案\學研專家網絡\資料與繪圖\模組與資料表"    
os.chdir(toolspath)
import toolmodules as tools
database = "sna_network"

time_draw = time.time()

def dataSelect(yearFrom, yearTo, piName, relationship):
    ##篩選連線資料
    con_en = tools.dbConnectEngine(database)

    ###篩選研究資料
    sqlstr =\
    f"""
    SELECT name1, name2, SUM(amount) AS value 
        FROM `graph_scholarrelationship_links`
        WHERE (name1 = '{piName}' OR name2 = '{piName} {relationship}')
            AND (year BETWEEN {yearFrom} AND {yearTo})
        GROUP BY name1, name2
        ORDER BY value DESC Limit 30
    """
    ##query資料
    for_nodes = pd.read_sql(sqlstr, con_en)
    ##取得ID名單
    piList = list(for_nodes.name1)
    piList.extend(list(for_nodes.name2))
    nodes = "','".join(set(piList))
    
    sqlstr =\
    f"""
    SELECT name1, name2, SUM(amount) AS value 
        FROM `graph_scholarrelationship_links`
        WHERE (name1 IN ('{nodes}') AND name2 IN ('{nodes}') {relationship})
            AND (year BETWEEN {yearFrom} AND {yearTo})
        GROUP BY name1, name2
        ORDER BY value DESC
    """
    df_links = pd.read_sql(sqlstr, con_en)

    con_en.close()
    return list(set(piList)), df_links

piName = "鄧維光"
yearFrom = "2010"
yearTo = "2018"
linkType = "all"
if linkType == "all":
    relationship = ""
else:
    relationship = "AND relationship = '{linkType}'"
piList, df_links = dataSelect("2010", "2018", piName, relationship)
# 網絡圖
G_piRelationship = nx.Graph()
##匯入連線資料
for name1, name2, value in df_links.values:
    G_piRelationship.add_edge(name1, name2, value=value)
##layout 
pos = nx.spring_layout(G_piRelationship, seed=33)
#shell = [[piName], list(G_piRelationship.neighbors(piName))]  #設定各圈節點資料
#pos_s = nx.shell_layout(G_piRelationship, shell)
#利用邊的"value"屬性設定邊的粗細與顏色值
if df_links.value.min() < 5:
    n = 8/df_links.value.min()
else:
    n = 1
edge_colors = [value for (u, v, value) in G_piRelationship.edges(G_piRelationship, 'value')]
edge_widths = [math.log(value*n, 5) for (u, v, value) in G_piRelationship.edges(G_piRelationship, 'value')]
##設定學門(中心)、關鍵字(外圈)節點標籤
labelpi= {n:n for n,lab in pos.items() if n == piName}
labelothers= {n:n for n,lab in pos.items() if n != piName}
##中文設定
matplotlib.rcParams['font.family']='SimSun'
plt.figure(figsize=(11,7))
##底圖
nx.draw(G_piRelationship, pos, node_size = 0, node_color="blue", alpha=1, width=0, font_size=18, with_labels=False, font_color="w", font_family="SimSun")
##節點、連線、標籤設定
edges = nx.draw_networkx_edges(G_piRelationship, pos, edge_color=edge_colors, edge_cmap=plt.cm.Blues, edge_vmin=0.1, width=edge_widths, alpha=0.5)
nx.draw_networkx_labels(G_piRelationship, pos, labels=labelpi, font_size=25, font_color="k", font_family="SimSun")
nx.draw_networkx_labels(G_piRelationship, pos, labels=labelothers, font_size=13, font_color="k", font_family="SimSun")
plt.margins(x=0.05)
# colorbar
plt.colorbar(edges)
plt.show()

time_end = time.time()
print("繪製網絡圖：", time_end - time_draw)  #1.1秒


