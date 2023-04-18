import sqlite3
import pandas as pd

def insertexams():
    con=sqlite3.connect("kldatabase.db")
    cur=con.cursor()
    cur.execute("drop table facultyduties;")
    cur.execute("drop table studentdetails;")
    cur.execute("create table facultyduties(venue,strength,empid,empname,date,time,nature);")
    cur.execute("create table studentdetails(venue,coursecode,coursename,fromid,toid,total,date,time);")
    data_xls=pd.read_excel('EVEN sem Invigilation Chart.xlsx','Faculty Duties')
    data_xls=data_xls.values.tolist()
    print(data_xls[1])
    for li in data_xls:
        cur.execute("insert into facultyduties values('"+str(li[1])+"','"+str(li[2])+"','"+str(li[3]).strip(" ")+"','"+str(li[4])+"','"+str(li[5]).strip(" 00:00:00")+"','"+str(li[6])+"','"+str(li[7])+"')")
    con.commit()
    data_xls=pd.read_excel('EVEN sem Invigilation Chart.xlsx','Students Details')
    data_xls=data_xls.values.tolist()
    print(data_xls[1])
    for li in data_xls:
        cur.execute("insert into studentdetails values('"+str(li[1])+"','"+str(li[2])+"','"+str(li[3])+"','"+str(li[4])+"','"+str(li[5])+"','"+str(li[6])+"','"+str(li[7]).strip(" 00:00:00")+"','"+str(li[8])+"')")
    con.commit()
    con.close()
