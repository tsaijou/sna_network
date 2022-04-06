# -*- coding: utf-8 -*-
"""
碩博士論文爬蟲
1. 從thesis_crawler_log資料表篩選欲爬取論文的PI紀錄資料
    → 預設篩選條件：最後爬蟲日期(lastCrawledDate)小於目前日期(crawlDate)的資料
2. 利用PI姓名碩博士於論文網搜尋並取得論文資料，存入thesis_rawdata資料表
3. 同步更新thesis_crawler_log資料表中，PI的論文數與爬蟲日期紀錄
"""
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import re
import logging
import time
import os
#import pymysql

# database connection
toolspath = r"C:\成大專案\學研專家網絡\資料與繪圖\模組與資料表"    
os.chdir(toolspath)
import toolmodules as tools
database = "sna_network"
conn = tools.dbConnect(database)
cur = conn.cursor()

# 建立thesis_rawdata資料表
#import thesisTables as t_table
#t_table.thesisCrawlerLogTable(database)
#t_table.thesisRawdataTable(database)

startTime = time.time()

# 引入 logging 配置
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# 爬蟲執行日期
crawlDate = time.strftime("%Y/%m/%d")

# 計算當前學年度
#year, month, day, hour, min = map(int, time.strftime("%Y %m %d %H %M").split())
#if (month < 7):
#    academicYear = year - 1912
#else:
#    academicYear = year - 1911


#讓ChromeDriver中不顯示“正受到自動測試軟體控制” 
chrome_options = webdriver.ChromeOptions(); 
chrome_options.add_experimental_option("excludeSwitches", ['enable-automation']);
#driver = webdriver.Chrome()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
chrome_options.add_argument('--user-agent=%s' % user_agent)
driver = webdriver.Chrome(r"chromedriver.exe", options=chrome_options);

# 爬蟲funtion
def crawlContent(professorName, thesesCrawled):
    driver.get("https://ndltd.ncl.edu.tw/cgi-bin/gs32/gsweb.cgi/ccd=.9yyI2/search?mode=basic")
    try:
        xpath = '//*[@id="indexsearch"]/table/tbody/tr[1]/td/span/a[2]'
        driver.find_element_by_xpath(xpath).click()
    except:
        time.sleep(2)
#        driver.find_element_by_css_selector("span.schfunc a[title='指令查詢']").click()
        driver.find_element_by_link_text(u"指令查詢").click()
    time.sleep(1)
    driver.find_element_by_id("ysearchinput0").click()
    driver.find_element_by_id("ysearchinput0").clear()
    
    #以教授名稱查詢
    driver.find_element_by_id("ysearchinput0").send_keys(u"\"" + professorName + "\".ad")
    time.sleep(1)
    driver.find_element_by_id("gs32search").click()
    time.sleep(1)
    
    paperAmount = driver.find_element_by_xpath(
        "//*[@id='bodyid']/form/div/table/tbody/tr[1]/td[2]/table/tbody/tr[4]/td/div[1]/table/tbody/tr[2]/td/table[2]/tbody/tr[2]/td[2]/span[2]").text
    paperAmount = int(paperAmount.lstrip().rstrip()) # 檢索結果的資料筆數
    cur.execute('UPDATE `thesis_crawler_log` set thesesAmount=%s where name=%s', (paperAmount, professorName))
    conn.commit()

    if (paperAmount == 0) or (thesesCrawled >= paperAmount):
        return
    
    try:
        driver.find_element_by_name("sortby").click()
        Select(driver.find_element_by_name("sortby")).select_by_visible_text(u"畢業學年度(遞增)")
        driver.find_element_by_name("sortby").click()
        time.sleep(1)
    except Exception as e:
        print(e)
        pass
    
    xpath = "//table[@id='tablefmt1']/tbody/tr[2]/td[3]/div/div/table/tbody/tr/td/a/span"
    driver.find_element_by_xpath(xpath).click()
    
    if thesesCrawled != 0:
        startPage = thesesCrawled+1
        driver.find_element_by_name("jmpage").click()
        driver.find_element_by_name("jmpage").clear()
        driver.find_element_by_name("jmpage").send_keys(startPage)
        driver.find_element_by_name("jumpfmt0page").click()
        time.sleep(2)
    else:
        startPage = 1
        

    for j in range(startPage+1, paperAmount + 2):
        try:
            li = driver.find_elements_by_xpath('//*[@id="gs32_levelrecord"]/ul/li')
            URL = 'null'
            studentName_ch = 'null'
            studentName_en = 'null'
            thesisName_ch = 'null'
            thesisName_en = 'null'
            professorName_ch = 'null'
            professorName_en = 'null'
            oralTestCommitteeName_ch = 'null'
            oralTestCommitteeName_en = 'null'
            oralTestDate = 'null'
            degreeType = 'null'
            schoolName = 'null'
            departmentName = 'null'
            discipline = 'null'
            educationType = 'null'
            publishYear = 'null'
            graduationYear = 'null'
            languageType = 'null'
            pageCount = 'null'
            Tkeyword_ch = 'null'
            Tkeyword_en = 'null'
            Tabstract_ch = 'null'
            Tabstract_en = 'null'
            tableOfContents = 'null'
            refs = 'null'

            for i in range(0, len(li) - 1):
                if (li[i].text == "論文基本資料"):
                    li[i].click()
                    URL = str(driver.find_element_by_xpath('//*[@id="fe_text1"]').get_attribute('value'))
                    tableList = driver.find_element_by_xpath('//*[@id="gs32_levelrecord"]/div').text.splitlines()
                    # 做字串處理
                    for data in tableList:
                        if ('研究生:' in data):
                            studentName_ch = re.sub("\"", "`", re.split('[: ]', data, maxsplit=1)[1]).lstrip()
                        if ('研究生(外文):' in data):
                            studentName_en = re.sub("\"", "`", re.split('[: ]', data, maxsplit=1)[1]).lstrip()
                        if ('論文名稱:' in data):
                            thesisName_ch = re.sub("\"", "`", re.split('[: ]', data, maxsplit=1)[1]).lstrip()
                        if ('論文名稱(外文):' in data):
                            thesisName_en = re.sub("\"", "`", re.split('[: ]', data, maxsplit=1)[1]).lstrip()
                        if ('指導教授:' in data):
                            professorName_ch = re.sub("\"", "`", re.split('[: ]', data, maxsplit=1)[1]).lstrip()
                        if ('指導教授(外文):' in data):
                            professorName_en = re.sub("\"", "`", re.split('[: ]', data, maxsplit=1)[1]).lstrip()
                        if ('口試委員:' in data):
                            oralTestCommitteeName_ch = re.sub("\"", "`", re.split('[: ]', data, maxsplit=1)[1]).lstrip()
                        if ('口試委員(外文):' in data):
                            oralTestCommitteeName_en = re.sub("\"", "`", re.split('[: ]', data, maxsplit=1)[1]).lstrip()
                        if ('口試日期:' in data):
                            oralTestDate = re.sub("\"", "`", re.split('[: ]', data, maxsplit=1)[1]).lstrip()
                        if ('學位類別:' in data):
                            degreeType = re.sub("\"", "`", re.split('[: ]', data, maxsplit=1)[1]).lstrip()
                        if ('校院名稱:' in data):
                            schoolName = re.sub("\"", "`", re.split('[: ]', data, maxsplit=1)[1]).lstrip()
                        if ('系所名稱:' in data):
                            departmentName = re.sub("\"", "`", re.split('[: ]', data, maxsplit=1)[1]).lstrip()
                        if ('學門:' in data):
                            discipline = re.sub("\"", "`", re.split('[: ]', data, maxsplit=1)[1]).lstrip()
                        if ('學類:' in data):
                            educationType = re.sub("\"", "`", re.split('[: ]', data, maxsplit=1)[1]).lstrip()
                        if ('論文出版年:' in data):
                            publishYear = re.sub("\"", "`", re.split('[: ]', data, maxsplit=1)[1]).lstrip()
                        if ('畢業學年度:' in data):
                            graduationYear = re.sub("\"", "`", re.split('[: ]', data, maxsplit=1)[1]).lstrip()
                        if ('語文別:' in data):
                            languageType = re.sub("\"", "`", re.split('[:  ]', data, maxsplit=1)[1]).lstrip()
                        if ('論文頁數:' in data):
                            pageCount = re.sub("\"", "`", re.split('[:  ]', data, maxsplit=1)[1]).lstrip()
                        if ('中文關鍵詞:' in data):
                            Tkeyword_ch = re.sub("\"", "`", re.split('[:  ]', data, maxsplit=1)[1]).lstrip()
                        if ('外文關鍵詞:' in data):
                            Tkeyword_en = re.sub("\"", "`", re.split('[:  ]', data, maxsplit=1)[1]).lstrip()
                elif (li[i].text == "摘要"):
                    li[i].click()
                    Tabstract_ch = re.sub("\"", "`",
                                         driver.find_element_by_xpath('//*[@id="gs32_levelrecord"]/div').text).lstrip()
                elif (li[i].text == "外文摘要"):
                    li[i].click()
                    Tabstract_en = re.sub("\"", "`",
                                         driver.find_element_by_xpath('//*[@id="gs32_levelrecord"]/div').text).lstrip()
                elif (li[i].text == "目次"):
                    li[i].click()
                    tableOfContents = re.sub("\"", "`", driver.find_element_by_xpath(
                        '//*[@id="gs32_levelrecord"]/div').text).lstrip()
                elif (li[i].text == "參考文獻"):
                    li[i].click()
                    refs = re.sub("\"", "`",
                                  driver.find_element_by_xpath('//*[@id="gs32_levelrecord"]/div').text).lstrip()
                else:
                    pass

            insertThesesInfo = '''INSERT IGNORE INTO `thesis_rawdata` (URL, studentName_ch, studentName_en, thesisName_ch, thesisName_en,\
                    advisor_ch, advisor_en, oralTestCommittee_ch,\
                    oralTestCommittee_en, oralTestDate, degreeType, schoolName,\
                    departmentName, discipline, educationType, publishYear,\
                    graduationYear, languageType, pageCount, Tkeyword_ch, Tkeyword_en,\
                    Tabstract_ch, Tabstract_en, tableOfContents, refs)\
                    VALUES \
                    ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")''' % \
                               (URL, studentName_ch, studentName_en, thesisName_ch, thesisName_en, professorName_ch,
                                professorName_en, oralTestCommitteeName_ch,
                                oralTestCommitteeName_en, oralTestDate, degreeType, schoolName, departmentName,
                                discipline, educationType, publishYear,
                                graduationYear, languageType, pageCount, Tkeyword_ch, Tkeyword_en, Tabstract_ch,
                                Tabstract_en, tableOfContents, refs)
            updateCrawl_log = '''UPDATE `thesis_crawler_log` SET thesesCrawled=%s WHERE name="%s"''' % (j-1, professorName)

            logging.info('教授:{},{}/{},論文:{}'.format(professorName, (j-1), paperAmount, thesisName_ch))
            try:
                cur.execute(insertThesesInfo)
                conn.commit()
                cur.execute(updateCrawl_log)
                conn.commit()                
            except Exception as e:
                print(e)
                pass

            driver.find_element_by_name("jmpage").click()
            driver.find_element_by_name("jmpage").clear()
            driver.find_element_by_name("jmpage").send_keys(j)
            driver.find_element_by_name("jumpfmt0page").click()
            time.sleep(2)

        except Exception as e:
            print(e)
            pass


# 以日期query需爬蟲資料，執行爬蟲，更新爬蟲紀錄
with conn.cursor() as cursor:
    # 尚未下載過論文的PI & 下載論文數不完整的PI 
    selectCommand =\
         f"""SELECT name, lastCrawledDate, thesesAmount, thesesCrawled 
            FROM `thesis_crawler_log`
            WHERE (lastCrawledDate < '{crawlDate}')"""
            
    cursor.execute(selectCommand)
    results = cursor.fetchall()
    for row in results:
        professorName = row[0]
        # Crawl all data

        crawlContent(professorName, row[-1])
        
        # 爬完這個教授的所有論文資料後更新爬蟲日期
        cur.execute("UPDATE `thesis_crawler_log` SET lastCrawledDate=%s WHERE name=%s", (crawlDate, professorName))
        conn.commit()
                
endtTime = time.time()
takeTime = endtTime-startTime
print(takeTime)

                
driver.quit()
conn.close()        
