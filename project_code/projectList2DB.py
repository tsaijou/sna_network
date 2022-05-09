# -*- coding: utf-8 -*-
"""
科技部計畫清單檔案資料匯入資料庫
PARTA. 讀取工程中心提供的科技部計畫清單excel檔案資料匯入project_rawdata table
PARTB. 與DB中既有姓名比對，匯入新增的姓名(thesis_crawler_log, most_talentsearch_crawler_log)
PARTC. 匯入科技部工程司學門代碼3碼project_engineer_discipline
"""
import pandas as pd
import os
import pymysql

toolspath = r"C:\成大專案\學研專家網絡\資料與繪圖\模組與資料表"    
os.chdir(toolspath)
# database connection
import toolmodules as tools
database = "sna_network"
con_en = tools.dbConnectEngine(database)
conn = tools.dbConnect(database)
cur = conn.cursor()

################# PARTA. new data into project_rawdata #################  
# 建立 project_rawdata table in sna_network database
import projectTables as p_table
p_table.projectRawdataTable(database)

# 利用project_code獲取資料庫中已存在的計畫年份
cur.execute("SELECT DISTINCT SUBSTRING_INDEX(project_code, '-' ,1) AS year FROM project_rawdata")
existingYears = [year[0] for year in cur.fetchall()]

# 篩選待匯入的計畫清單(條件：檔案名稱中中的年份、檔案類型為excel)
file_list = [i for i in os.listdir("../科技部計畫/科技部計畫資料/科技部核定計畫") if ((".xl" in i) and i[0:3] not in existingYears)] 

# 資料表的欄位名稱
cur.execute("SHOW columns FROM project_rawdata")
columnsDB = [columns[0] for columns in cur.fetchall() if columns[0] != "dataProcessed"]

# 載入檔案資料與database資料表欄位名稱對照表
columnsTransDF = pd.read_excel("../科技部計畫/科技部計畫資料/科技部計畫欄位對照.xlsx", encoding='utf8', sheetname=0, header=None, index_col=1, skiprows=2, usecols=[1,2])
columnsTrans = columnsTransDF.to_dict()[1]

# 讀取&編結計畫清單
projectData = pd.DataFrame()
for file in file_list:
    # 載入計畫檔案 
    projectFile = pd.read_excel("../科技部計畫/科技部計畫資料/科技部核定計畫/"+file, encoding='utf8', sheetname=0, header=0)
    # 去掉表格末端提供者資訊
    try:
        rows = list((projectFile.isnull()).sum(axis = 1)).index(len(projectFile.columns))-1
        projectFile = projectFile.loc[:rows, :]
    except:
        pass
    # 將"學門"欄位改名為"學門5碼"
    if "學門" in projectFile.columns:
        projectFile = projectFile.rename(columns={"學門":"學門5碼"})
    # 將欄位名稱改為與DB中使用的相同，並補上檔案中缺乏、DB中有的欄位
    columnReviseDF = pd.DataFrame()
    for col in columnsDB:
        try:
            columnReviseDF[col] = projectFile[columnsTrans[col]]
        except:
            columnReviseDF[col] = None
    projectData = pd.concat([projectData, columnReviseDF], axis=0, ignore_index=True)


#"""
#針對102-104年清單：取出projectID重複出現的計畫-102/103清單 vs 104清單兩邊重複(1422/2844筆)
#相同計畫(projectID)，"years","gender"欄位104年有資料102年無，中英文摘要/關鍵字欄位102年有資料104年多數無
#"""
#columns = ["Pkeyword_ch", "Pkeyword_en", "Pabstract_ch", "Pabstract_en"]
#duplicate = projectData[projectData.duplicated("project_code", keep=False)].sort_index(by = ['project_code', "year_execution"])
#duplicate102 = duplicate[duplicate["year_execution"] != 104]
#duplicate104 = duplicate[duplicate["year_execution"] == 104]
#duplicate_final = duplicate104.copy()
#def copyData_102to104(col):
#    templist = []
#    for item2, item4 in zip(duplicate102[col], duplicate104[col]):
#        if type(item4) is str:
#            templist.append(item4)
#        else:
#            templist.append(item2)
#    duplicate_final[col] = templist
# 
#for col in columns:
#    copyData_102to104(col)    
## 將重複資料完全刪除 (keep=False)
#projectData = projectData.drop_duplicates(subset=['project_code'], keep=False)
## 重新合併102-104資料
#projectData = pd.concat([projectData, duplicate_final], axis = 0)


# 匯入資料庫
for row in projectData.values: 
    sql_projectData = f"""INSERT IGNORE INTO project_rawdata ({", ".join(columnsDB)}) VALUES ("""
    for item in row:
        if pd.isna(item) or item in ["null", "Null", "NULL", "no"]:
            sql_projectData += "NULL,"
        elif type(item) == str:
            item = item.strip()
            sql_projectData += f'"{pymysql.escape_string(item)}",'
        else:
            sql_projectData += f"{item}," 
    sql_projectData = sql_projectData[:-1] + ")"
    cur.execute(sql_projectData)
    conn.commit()

################# PARTB. new name to thesis_crawler_log/most_talentsearch_crawler_log table #################
# 新匯入資料中的姓名(計畫主持人,pi/總計畫主持人,ci)
pi_cleanName = tools.dfNameClean(projectData, "principal_investigator")
ci_cleanName = tools.dfNameClean(projectData, "chief_investigator")
nameList = list(set(pi_cleanName + ci_cleanName))

tools.newName2Crawl(conn, cur, "thesis_crawler_log", nameList)
tools.newName2Crawl(conn, cur, "most_talentsearch_crawler_log", nameList)

################# PARTC. project engineer discipline to database #################
# 建立資料表
p_table.projectEngineerDisciplineTable(database)
# 讀取檔案資料
engineerDiscipline = pd.read_excel("../科技部計畫/科技部計畫資料/工程司學門與計劃學門對照_正芳更新.xlsx", encoding='utf8', sheetname=0, usecols=[4,5])
engineerDiscipline.columns = ["code", "discipline"]
engineerDiscipline = engineerDiscipline.drop_duplicates("code", keep="first")
engineerDiscipline = engineerDiscipline[~engineerDiscipline["code"].isnull()]
engineerDiscipline = engineerDiscipline.sort_index(by = ['code'])
# 匯入資料庫
try:
    engineerDiscipline.to_sql(name='project_engineer_discipline', con=con_en, if_exists='append', index=False)
except Exception as e:
    print(e)

conn.close()
con_en.close()
    