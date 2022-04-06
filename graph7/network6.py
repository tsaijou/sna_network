# -*- coding: utf-8 -*-
"""
G7：PI的關鍵詞文字雲
    利用學者與關鍵詞關係，繪製指定PI的關鍵詞文字雲
     可設定篩選條件：
     1. 年份區間: yearFrom、yearTo
     2. 指定PI: piName
"""

import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import time, os


toolspath = r"C:\成大專案\學研專家網絡\資料與繪圖\模組與資料表"    
os.chdir(toolspath)
import toolmodules as tools
database = "sna_network"

time_draw = time.time()
##條件設定
piName = "鄧維光"  #搜尋PI
yearFrom = 2001
yearTo=2020

def dataSelect(yearFrom, yearTo, piName):
    con_en = tools.dbConnectEngine(database)
    ##篩選關鍵詞資料
    sqlstr_keywords =\
    f"""
    SELECT name, keyword, SUM(amount) AS value 
        FROM `graph_scholarkeyword_links`
        WHERE (name = '{piName}')
            AND (year BETWEEN {yearFrom} AND {yearTo}) 
        GROUP BY name, keyword 
        ORDER BY value DESC
    """    
    keywords = pd.read_sql(sqlstr_keywords, con_en)
    con_en.close
    return keywords

keywords = dataSelect(yearFrom, yearTo, piName)


# 編輯匯入文字雲的字串
words = []
for name, keyword, value in keywords.values:
    words.extend([keyword]*int(value))
words = " ".join(words)


# 中文設定
font = "C:\Windows\Fonts\SimSun.ttc"
# 繪製文字雲(白底)
plt.figure(figsize=(10,7))
wordcloud = WordCloud(random_state=16, background_color="white", colormap='copper', margin=2, font_path=font, max_font_size=60, scale=3)
wordcloud.generate(words)
#wordcloud.recolor(color_func=img_colors)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()


time_end = time.time()
print("繪製網絡圖：", time_end - time_draw)  # 1.2秒

