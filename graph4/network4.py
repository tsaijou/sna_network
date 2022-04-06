# -*- coding: utf-8 -*-
"""
Graph4-2. E40-資訊工程(資訊)-E14-微電子工程學門前25大關鍵字網絡
  可設定篩選條件：
  1. 指定學門: discipline1, discipline2
  2. 與指定學們最相關的前幾名關鍵詞: top
  可增加篩選條件：年份
"""
import pandas as pd
import os, time
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt

toolspath = r"C:\成大專案\學研專家網絡\資料與繪圖\模組與資料表"    
os.chdir(toolspath)
#connect to database
import toolmodules as tools
database = "sna_network"

time_draw = time.time()

##從資料庫篩選資料匯入
disciplines = ["E40-資訊工程(資訊)","E14-微電子工程"]  #for計劃書
top = 25  #指定關鍵詞個數
##篩選多學門連線資料
def dataSelect (disciplines, top):
    con_en = tools.dbConnectEngine(database)
    df_links = pd.DataFrame()
    for discipline in disciplines:
        ##從篩選指定學門的關鍵詞
        sqlStr_keyword =\
            f"""
            SELECT discipline, keyword, SUM(amount) AS value 
            FROM `graph_engineerkeyword_links` a
            WHERE discipline = '{discipline}' 
            GROUP BY keyword
            ORDER BY value DESC LIMIT {top}
            """
        temp = pd.read_sql(sqlStr_keyword, con_en)
        df_links = pd.concat([df_links, temp])
    con_en.close()
    return df_links

df_links = dataSelect(disciplines, top)
dcp_round = list(set(df_links.discipline))

# 繪製網絡圖
G_disciplinekeywords = nx.Graph()
for row in df_links.values:
    G_disciplinekeywords.add_edge(row[0], row[1], value=row[-1])
##layout
keywordShare = list(df_links[df_links.duplicated(['keyword'], keep="first")]['keyword'])    
keywordunShare = list(set(df_links.keyword).difference(set(keywordShare)))
shell = [keywordShare, dcp_round, keywordunShare]  #設定各圈節點資料
pos_s = nx.shell_layout(G_disciplinekeywords, shell)
#利用邊的"value"屬性設定邊的粗細與顏色值
edge_colors = [value for (u, v, value) in G_disciplinekeywords.edges(G_disciplinekeywords, 'value')]
edge_widths = [value/5 for (u, v, value) in G_disciplinekeywords.edges(G_disciplinekeywords, 'value')]
##設定學門(中心)、關鍵字(外圈)節點標籤
labelKeywords = {n:n for n,lab in pos_s.items() if n not in dcp_round}
labelCenter = {n:n for n,lab in pos_s.items() if n in dcp_round}
##中文設定
matplotlib.rcParams['font.family']='SimSun'
plt.figure(figsize=(14.2,11.2))
##底圖
nx.draw(G_disciplinekeywords, pos_s, node_size=0, node_color="blue", alpha=1, width=0, font_size=12, with_labels=False)
##節點、連線、標籤設定
edges = nx.draw_networkx_edges(G_disciplinekeywords, pos_s, edge_color=edge_colors, edge_cmap=plt.cm.cool, edge_vmin=0.1, width=edge_widths, alpha=0.5)
nx.draw_networkx_labels(G_disciplinekeywords, pos_s, labels=labelCenter, font_size=25, font_color="k", font_family="SimSun")
nx.draw_networkx_labels(G_disciplinekeywords, pos_s, labels=labelKeywords, font_size=16, font_color="k", font_family="SimSun")
plt.colorbar(edges, shrink=0.5, label="colorbar of edges", pad=0.003)
plt.margins(x=0.11)
plt.show()

time_end = time.time()
print("繪製網絡圖：", time_end - time_draw)  # 1.2秒


