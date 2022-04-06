# -*- coding: utf-8 -*-
"""
Graph1. 2012年-2016年使用關鍵詞"深度學習"最多次的前10名PI，及各PI使用最多的前10個關鍵詞
  可設定篩選條件：
  1. 年份區間: yearFrom、yearTo
  2. 指定關鍵詞: keyword
  3. 使用關鍵詞最多次的前幾名學者: piTop
  4. 學者使用最多的前個幾關鍵詞: keywordAmount
  **第1,2項位於網頁篩選使用
"""
import pandas as pd
import os, time
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
#import math

toolspath = r"C:\成大專案\學研專家網絡\資料與繪圖\模組與資料表"    
os.chdir(toolspath)
import toolmodules as tools
database = "sna_network"

con_en = tools.dbConnectEngine(database)

time_draw = time.time()

# 從資料庫篩選資料匯入
def dataSelect(yearFrom, yearTo, keyword, piTop, pikeywordTop):
    con_en = tools.dbConnectEngine(database)    
    
    ###篩選使用指定關鍵詞的PI資料
    sqlstr_keywordpi =\
    f"""
    SELECT name, keyword, SUM(amount) AS value 
        FROM `graph_scholarkeyword_links`  
        WHERE (year BETWEEN {yearFrom} AND {yearTo}) 
            AND (keyword = '{keyword}')
        GROUP BY name, keyword
        ORDER BY value DESC LIMIT {piTop}
    """    
    keyword_pi = pd.read_sql(sqlstr_keywordpi, con_en)
    piList = sorted(list(keyword_pi.name), reverse = True)
    
    ###篩選各個PI使用的關鍵詞
    sqlstr_pikeyword =\
    """
    SELECT name, keyword, SUM(amount) AS value 
    FROM `graph_scholarkeyword_links` 
    WHERE (year BETWEEN %s AND %s) 
        AND (name = '%s') 
        AND (keyword <> '%s') 
        GROUP BY name, keyword
    ORDER BY value DESC LIMIT %s
    """
    df_links = keyword_pi
    for name in piList:
        pi_keyword = pd.read_sql(sqlstr_pikeyword %(yearFrom, yearTo, name, keyword, pikeywordTop), con_en)
        df_links = pd.concat([df_links, pi_keyword], ignore_index=True)
    con_en.close()

    df_links = df_links.sort_values(by=["name","value"], ascending=False).reset_index(drop=True)
    derivekeyword = list(set(df_links.keyword))
    derivekeyword.remove(keyword)
    return df_links, derivekeyword

keyword = "深度學習"  #指定關鍵詞
df_links, derivekeyword = dataSelect("2012", "2016", keyword, 10, 5)

# 繪製網絡圖
G_keywordSearchPI = nx.Graph()
for row in df_links.values:
    G_keywordSearchPI.add_edge(row[0], row[1], value=row[-1])
##layout 
pos = nx.spring_layout(G_keywordSearchPI, seed=33)
#利用邊的"value"屬性設定邊的粗細與顏色值
edge_colors = [value for (u, v, value) in G_keywordSearchPI.edges(G_keywordSearchPI, 'value')]
edge_widths = [value/1.7 for (u, v, value) in G_keywordSearchPI.edges(G_keywordSearchPI, 'value')]
##設定學門(中心)、關鍵字(外圈)節點標籤
labelkeyword = {n:n for n,lab in pos.items() if n == keyword}
labelderivekeyword= {n:n for n,lab in pos.items() if n in derivekeyword}
labelPI= {n:n for n,lab in pos.items() if n in list(df_links.name)}
##中文設定
matplotlib.rcParams['font.family']='SimSun'
plt.figure(figsize=(10,7))
##底圖
nx.draw(G_keywordSearchPI, pos, node_size = 0, node_color="blue", alpha=1, width=0, font_size=18, with_labels=False, font_color="w", font_family="SimSun")
##節點、連線、標籤設定
edges = nx.draw_networkx_edges(G_keywordSearchPI, pos, edge_color=edge_colors, edge_cmap=plt.cm.cool, edge_vmin=0.1, width=edge_widths, alpha=0.7)
nx.draw_networkx_labels(G_keywordSearchPI, pos, labels=labelkeyword, font_size=25, font_color="k", font_family="SimSun")
nx.draw_networkx_labels(G_keywordSearchPI, pos, labels=labelPI, font_size=20, font_color="k", font_family="SimSun")
nx.draw_networkx_labels(G_keywordSearchPI, pos, labels=labelderivekeyword, font_size=12, font_color="k", font_family="SimSun")
plt.margins(x=0.1)
plt.colorbar(edges, shrink=0.6, label="colorbar of edges", pad=0.005)
plt.show()


time_end = time.time()
print("繪製網絡圖：", time_end - time_draw)  # 2.2秒




