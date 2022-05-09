# -*- coding: utf-8 -*-
"""
利用計畫主持人姓名在「科技部學術研究服務網研究人才查詢網頁」爬取計畫主持人個資與計畫標題
"""

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import logging
import time
import os


# database connection
toolspath = r"C:\成大專案\學研專家網絡\資料與繪圖\模組與資料表"    
os.chdir(toolspath)
import toolmodules as tools
database = "sna_network"
con_en = tools.dbConnectEngine(database)
conn = tools.dbConnect(database)
cur = conn.cursor()

# 建立資料表
import mostTables as m_table
m_table.mostCrawlerTable(database)
m_table.mostScholarTable(database)
m_table.mostProjectOverviewTable(database)

# 判斷資料型態，用於編輯sql語法
def insertItem(element):
    if type(element) == str:
        element = f"'{element}'"
    elif element == None:
        element = "NULL"
    return element


# 爬蟲執行日期
crawlDate = time.strftime("%Y/%m/%d")


# 篩選待爬取資料的姓名：以最後爬蟲日期為條件(lastCrawledDate)
cur.execute("SELECT name FROM ref_mosttalentsearch_crawler_log WHERE lastCrawledDate IS NULL OR number_of_name=0")
crawler_name = cur.fetchall()


# 引入 logging 配置
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


#讓ChromeDriver中不顯示“正受到自動測試軟體控制” 
chrome_options = webdriver.ChromeOptions(); 
chrome_options.add_experimental_option("excludeSwitches", ['enable-automation']);
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
chrome_options.add_argument('--user-agent=%s' % user_agent)
driver = webdriver.Chrome(r"chromedriver.exe", options=chrome_options);

# 載入網址
url_search = "https://arspb.most.gov.tw/NSCWebFront/modules/talentSearch/talentSearch.do?action=initSearchList&LANG=chi"
driver.get(url_search)
time.sleep(1)

# sql: 更新爬蟲日期
update_crawl = '''UPDATE `ref_mosttalentsearch_crawler_log` SET lastCrawledDate="%s", number_of_search=%s WHERE name="%s"''' 

for item in crawler_name:
    if tools.any_chinese(item[0]):
        #中文姓名清洗
        name = tools.select_chinese(item[0])
    else:
        name = item[0]
#    name = "陳太平"
    
    #姓名查詢
    driver.find_element_by_id("nameChi").click()
    driver.find_element_by_id("nameChi").clear()
    driver.find_element_by_id("nameChi").send_keys(name)
    time.sleep(1)
    
    driver.find_element_by_name("send").click()
    time.sleep(2)
    
    try:
        #查詢的姓名資料
        name_amount = int(driver.find_element_by_xpath('//*[@id="zone.content11"]/div/div[1]/span/em[1]').text)
        if name_amount > 10:
            xpath = '//*[@id="zone.content11"]/div/div[1]/select'
            driver.find_element_by_xpath(xpath).click()
            Select(driver.find_element_by_xpath(xpath)).select_by_visible_text(u"100")
            driver.find_element_by_xpath(xpath).click()
            page_amount = int(driver.find_element_by_xpath('//*[@id="zone.content11"]/div/div[1]/span/em[2]').text.split("/")[-1])
        else:
            page_amount = 1
        time.sleep(1)
        logging.info('姓名: {}, 人數: {}'.format(item[0], name_amount))
        
        #編輯姓名資料
        scholarData = []
        for page in range(1, page_amount+1):  
            soup_s = bs(driver.page_source,'html.parser')
            for tr in soup_s.find('div',{'class':'c30Tblist2'}).find_all("tr"):
                if tr.find('td'):
                    data_list = []
                    for td in tr.find_all('td'):
                        data = td.text.strip()
                        if data == "[不公開]":
                            data = "不公開"
                        elif data == "":
                            data = None
                        data_list.append(data)
                    data_list[0] = tr.a.get_text("、").split("、")[0]                    
                    if tr.find('input',{'value':'計畫總覽'}):
                        code = tr.find('input',{'value':'計畫總覽'})["onclick"]
                        url = url_search[0:(url_search.rfind("/")+1)] + code[(code.find('=')+2):-1]
                        data_list[-2] = url
                    else:
                        data_list.append(None)                                                      
                    scholarData.append(data_list[0:-1])
            
            page += 1
            if page < page_amount+1:
                xpath = '//*[@id="zone.content11"]/div/div[1]/span/select'
                driver.find_element_by_xpath(xpath).click()
                Select(driver.find_element_by_xpath(xpath)).select_by_visible_text(str(page))
                driver.find_element_by_xpath(xpath).click()
                
        scholar_col = ["name", "institution", "position", "telephone", "url_Ptitle"]
        scholarDF = pd.DataFrame(scholarData, columns = scholar_col)                
        
        #去除與資料庫重複的姓名資料、更新資料庫既有姓名資料(學者個資更新)
        url_list = list(scholarDF.url_Ptitle)
        name_list = list(set(scholarDF.name))
        #資料庫既有姓名資料
        sql_exist = f"""SELECT * FROM ref_mosttalentsearch_scholar_info WHERE name IN ('{"','".join(name_list)}') AND url_Ptitle IN ('{"','".join(url_list)}')"""
        mostExist = pd.read_sql(sql_exist, con_en) 
        #既有姓名資料更新
        if len(mostExist) > 0:
            for row in mostExist.values:
                oldCrawl = list(row)[2:5]
                newCrawl = list(scholarDF[scholarDF["url_Ptitle"]==row[-1]].values[0])[1:4]
                if oldCrawl != newCrawl:
                    try:
                        update_most = '''UPDATE `ref_mosttalentsearch_scholar_info` SET institution=%s, position=%s, telephone=%s WHERE Mid=%s''' 
                        cur.execute(update_crawl% (insertItem(row[2]), insertItem(row[3]), insertItem(row[4]), row[0]))
                        conn.commit()
                        print(f"{row[0]} {row[1]}：基本資料更新")  
                    except Exception as e:
                        print(e)                    
        #待匯入的新姓名資料
        scholar2DB = scholarDF[~scholarDF["url_Ptitle"].isin(mostExist.url_Ptitle)]
        #新姓名資料匯入資料庫
        try:
            cur.execute(update_crawl% (crawlDate, name_amount, item[0]))
            conn.commit()
            if len(scholar2DB)>0:
                scholar2DB.to_sql(name='ref_mosttalentsearch_scholar_info', con=con_en, if_exists='append', index=False)       
                print(f"{item[0]}：基本資料匯入成功")                
        except Exception as e:
            print(e)
        
        #爬取新增姓名的計畫標題：利用計畫總覽連結
        sql_url = f"""SELECT * FROM ref_mosttalentsearch_scholar_info WHERE url_Ptitle IN ('{"','".join(url_list)}') AND url_Ptitle IS NOT NULL"""
        mostData = pd.read_sql(sql_url, con_en)
        for row in mostData.values:
            r = requests.get(row[-1], verify=False )
            soup_p = bs(r.text,'html.parser') 
            try:
                projectData = []
                for tr in soup_p.find('div',{'class':'c30Tblist2'}).find_all("tr"):
                    if tr.find('td'):
                        project_list = [row[0], row[1]]
                        for td in tr.find_all('td'):
                            data = td.text.strip().replace('\n','').replace('\t','').replace('\r','').replace(' ','')
                            if data == "":
                                data = None
                            project_list.append(data)
                        projectData.append(project_list)
                project_col = ["Mid", "name", "year", "type", "discipline", "Ptitle", "role", "amount_approved"]
                projectDF = pd.DataFrame(projectData, columns = project_col)
                projectDF = projectDF.drop(columns=["amount_approved"])
                projectDF = projectDF.drop_duplicates(subset=["name", "year", "type", "discipline", "Ptitle", "role"], keep="last")
                projectDF['year'] = projectDF['year'].astype('int')
                projectDF['year'] = [int(y)+1911 for y in projectDF.year]
                try:
                    sql_projectData = f"""INSERT IGNORE INTO ref_mosttalentsearch_project_overview ({", ".join(projectDF.columns)}) VALUES """
                    values = "(%s, %s, %s, %s, %s, %s, %s),"
                    for row in projectDF.values:
                        sql_projectData += values %(row[0], insertItem(row[1]), row[2], insertItem(row[3]), insertItem(row[4]), insertItem(row[5]), insertItem(row[6]))
                    cur.execute(sql_projectData[:-1])
                    conn.commit()
                    print(f"{row[1]}：計畫總覽匯入成功")
                except: 
                    pass                                         
            except Exception as e:
                print(row[1], "：無符合計畫資料\n", e)                   
    except Exception as e:
        print(name, "：無符合姓名的資料\n", e)
        #無符合姓名的資料
        name_amount = 0
        cur.execute(update_crawl% (crawlDate, name_amount, item[0]))
        conn.commit()
        

driver.close()

con_en.close()
conn.close()


