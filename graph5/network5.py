# -*- coding: utf-8 -*-
"""
Graph5. 跨學門合作
  可設定篩選條件：
  1. 最低合作次數限制: value
  2. 合作類型: relationship (自我跨學門/學者間跨學門)
"""
import pandas as pd
import os, time
import math
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt

toolspath = r"C:\成大專案\學研專家網絡\資料與繪圖\模組與資料表"    
os.chdir(toolspath)
import toolmodules as tools
database = "sna_network"

time_draw = time.time()
con_en = tools.dbConnectEngine(database)

# 最低合作次數限制
value = 200
# 合作類型
#relationship = "= 'pi-self'" #自我跨學門
relationship = "<> 'pi-self'" #學者間跨學門

# 工程學門
sqlstr_engineer = "SELECT CONCAT(code, '-', discipline) AS discipline FROM project_engineer_discipline"
engineerDiscipline = pd.read_sql(sqlstr_engineer, con_en)

# 篩選學門連結關係資料
sqlstr =\
f"""
SELECT discipline1, discipline2, SUM(amount) AS value
    FROM graph_engineercoopertion_links
    WHERE relationship {relationship}
    GROUP BY discipline1, discipline2
    HAVING value >= 10
"""
df_link = pd.read_sql(sqlstr, con_en)
con_en.close()


# 繪製網絡圖
G_ETdiscipline = nx.Graph()
G_ETdiscipline.add_nodes_from(sorted(list(engineerDiscipline.discipline)))
for dcp1, dcp2, value in df_link.values: 
    G_ETdiscipline.add_edge(dcp1, dcp2, weight = value)
edges_weight_index = nx.get_edge_attributes(G_ETdiscipline, 'weight')
colors = [v for k, v in edges_weight_index.items()]
#widths = [math.log(v*100, 3) for k, v in edges_weight_index.items()] #自我跨學門
widths = [math.log(v, 5) for k, v in edges_weight_index.items()] #學者間跨學門
#pos = nx.spring_layout(G_ETdiscipline, seed=seed)  #seed = 33
#plt.figure(figsize=(11,7))
pos = nx.circular_layout(G_ETdiscipline)
labels = {n:n for n,lab in pos.items()}
##中文設定
matplotlib.rcParams['font.family']='SimSun'
plt.figure(figsize=(8.1,6.3))
nx.draw(G_ETdiscipline, pos, node_size = 300, node_color='grey', width=0, alpha=0.3, with_labels=False)
edges = nx.draw_networkx_edges(G_ETdiscipline, pos, edge_color=colors, edge_cmap=plt.cm.coolwarm, edge_vmin=0.1, width=widths, alpha=0.5)
nx.draw_networkx_labels(G_ETdiscipline, pos, labels=labels, font_size=9.5, font_color="k",font_weight='heavy', font_family="SimSun", horizontalalignment="center")
plt.margins(x=0.09)
plt.colorbar(edges, shrink=0.5, label="colorbar of edges", pad=0.005)

time_end = time.time()
print("繪製網絡圖：", time_end - time_draw)  # 0.2秒



