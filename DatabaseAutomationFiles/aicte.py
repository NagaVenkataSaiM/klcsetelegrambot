import sqlite3
import pandas as pd

def insertaicte():
    con=sqlite3.connect("kldatabase.db")
    cur=con.cursor()
    cur.execute("drop table aictecohort;")
    cur.execute("create table aictecohort(sno,id,domainname);")
    data_xls=pd.read_excel('COHORT_4_AICTE_VIRTUAL_INTERNSHIP_KLU-BOT.xlsx','ALL Details')
    data_xls=data_xls.values.tolist()
    print(data_xls[1])
    for li in data_xls:
        cur.execute("insert into aictecohort values('"+str(li[0])+"','"+str(li[1])+"','"+str(li[2])+"')")
    con.commit()
    con.close()
