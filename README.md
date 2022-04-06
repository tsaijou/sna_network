# 學研專家分析網絡
目標：利用*科技部計畫清單*與*碩博士論文資料*建立**異質資訊網路**，來表現學者與研究技術間的整體關係，更進而分析出熱門技術與學者社群

說明：
1. 碩博士論文資料：利用前項計畫主持人姓名，在碩博士論文網爬取該姓名擔任指導老師的論文資料
   - 碩博士論文爬蟲檔案：[/project_code/thesesCrawler.py](https://github.com/tsaijou/sna_network/blob/main/project_code/thesesCrawler.py)
2. 異質資訊網路：每一篇研究文獻中(論文/計畫)，學者姓名、文獻關鍵詞等不同類型資料(節點node)之間建立的關係(連線link)網絡
 ![image](https://user-images.githubusercontent.com/54679167/162044453-dd6de77a-4f76-47f4-a6f9-9c1108d8398a.png)

成果：將分析結果視覺化
1. 分為7大主題，可依照設定輸入欲查詢的學者姓名、年分...等條件
2. 靜態視覺化圖片利用python的**networkx套件**繪製，網頁視覺化利用**amCharts套件**繪製

## Graph1 歷年熱門關鍵詞網絡
1. 呈現單一年份研究文獻中出現次數前幾名的關鍵詞，與關鍵詞之間的連結關係
2. 篩選條件：年份、關鍵詞數量
- 網頁視覺化範例：[/graph1/graph1](https://tsaijou.github.io/sna_network/graph1/graph1)
- 網頁視覺化檔案：[/graph1/graph1.html](https://github.com/tsaijou/sna_network/blob/main/graph1/graph1.html)

## Graph2 重點技術學者查詢
- 網頁視覺化範例：[/graph2/graph2](https://tsaijou.github.io/sna_network/graph2/graph2)
- 網頁視覺化檔案：[/graph2/graph2.html](https://github.com/tsaijou/sna_network/blob/main/graph2/graph2.html)

## Graph3 研究技術(關鍵詞)網絡
- 網頁視覺化範例：[/graph3/graph3](https://tsaijou.github.io/sna_network/graph3/graph3)
- 網頁視覺化檔案：[/graph3graph3.html](https://github.com/tsaijou/sna_network/blob/main/graph3/graph3.html)

## Graph4 工程學門研究技術網絡
- 網頁視覺化範例：[/graph4/graph4](https://tsaijou.github.io/sna_network/graph4/graph4)
- 網頁視覺化檔案：[/graph4/graph4.html](https://github.com/tsaijou/sna_network/blob/main/graph4/graph4.html)

## Graph5 工程學門之間的合作網絡
- 網頁視覺化範例：[/graph5/graph5](https://tsaijou.github.io/sna_network/graph5/graph5)
- 網頁視覺化檔案：[/graph5/graph5.html](https://github.com/tsaijou/sna_network/blob/main/graph5/graph5.html)

## Graph6 學者關係網絡
- 網頁視覺化範例：[/graph6/graph6](https://tsaijou.github.io/sna_network/graph2/graph2)
- 網頁視覺化檔案：[/graph6/graph62.html](https://github.com/tsaijou/sna_network/blob/main/graph6/graph6.html)

## Graph7 學者的關鍵詞文字雲
- 網頁視覺化範例：[/graph7/graph7](https://tsaijou.github.io/sna_network/graph7/graph7)
- 網頁視覺化檔案：[/graph7/graph7.html](https://github.com/tsaijou/sna_network/blob/main/graph7/graph7.html)
